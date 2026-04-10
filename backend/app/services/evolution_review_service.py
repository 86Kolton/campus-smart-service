from __future__ import annotations

import json
import re

import httpx

from app.core.config import settings


def _clamp_score(value: object, default: int = 0) -> int:
    try:
        raw = int(float(value))
    except Exception:
        raw = int(default)
    return max(0, min(100, raw))


def _normalize_model_score(value: object, default: int = 0) -> int:
    try:
        numeric = float(value)
    except Exception:
        return _clamp_score(default, default=default)

    if numeric <= 10:
        numeric *= 10
    return _clamp_score(numeric, default=default)


class EvolutionReviewService:
    _JSON_RE = re.compile(r"\{.*\}", re.S)
    _BAD_HINTS = ("测试", "test", "111", "占位", "哈哈", "随便", "顶")

    def _provider_config(self) -> dict:
        provider = str(settings.evolution_ai_review_provider or "qa_reuse").strip().lower()
        if provider in {"", "qa_reuse"}:
            return {
                "provider": "qa_reuse",
                "base_url": str(settings.evolution_ai_review_base_url or settings.qa_base_url or "").strip().rstrip("/"),
                "api_key": str(settings.evolution_ai_review_api_key or settings.qa_api_key or "").strip(),
                "model": str(settings.evolution_ai_review_model or settings.qa_model or "").strip(),
                "timeout": max(
                    5,
                    int(
                        settings.evolution_ai_review_timeout_seconds
                        or settings.qa_timeout_seconds
                        or 25
                    ),
                ),
            }

        return {
            "provider": provider,
            "base_url": str(settings.evolution_ai_review_base_url or "").strip().rstrip("/"),
            "api_key": str(settings.evolution_ai_review_api_key or "").strip(),
            "model": str(settings.evolution_ai_review_model or "").strip(),
            "timeout": max(5, int(settings.evolution_ai_review_timeout_seconds or 25)),
        }

    def _default_summary(self, post: dict) -> str:
        content = str(post.get("content") or "").strip()
        if not content:
            return str(post.get("title") or "").strip()
        return content[:96] + ("..." if len(content) > 96 else "")

    def _heuristic_review(self, post: dict, threshold: int) -> dict:
        title = str(post.get("title") or "").strip()
        content = str(post.get("content") or "").strip()
        tags = post.get("tags") or []
        likes = int(post.get("likes_count") or 0)
        comments = int(post.get("comments_count") or 0)
        adopted = bool(post.get("adopted"))
        category = str(post.get("category") or "").strip()

        score = 32
        score_breakdown: list[dict[str, object]] = [{"label": "base", "delta": 32}]
        if len(title) >= 8:
            score += 12
            score_breakdown.append({"label": "title_length", "delta": 12})
        if len(content) >= 40:
            score += 16
            score_breakdown.append({"label": "content_density", "delta": 16})
        if len(content) >= 90:
            score += 8
            score_breakdown.append({"label": "content_detail_bonus", "delta": 8})
        if tags:
            tag_bonus = min(10, len(tags) * 3)
            score += tag_bonus
            score_breakdown.append({"label": "tag_bonus", "delta": tag_bonus})
        if likes >= 30:
            score += 10
            score_breakdown.append({"label": "likes_threshold", "delta": 10})
        if comments >= 5:
            score += 10
            score_breakdown.append({"label": "comments_threshold", "delta": 10})
        if adopted:
            score += 12
            score_breakdown.append({"label": "forum_adoption_signal", "delta": 12})
        if category in {"academic", "study", "canteen", "market"}:
            score += 6
            score_breakdown.append({"label": "campus_category_bonus", "delta": 6})

        compact = f"{title} {content}".lower()
        if any(hint in compact for hint in self._BAD_HINTS):
            score -= 28
            score_breakdown.append({"label": "noise_penalty", "delta": -28})
        if len(content) < 18:
            score -= 20
            score_breakdown.append({"label": "short_content_penalty", "delta": -20})

        overall = _clamp_score(score, default=0)
        passed = bool(overall >= threshold)
        return {
            "decision": "pass" if passed else "reject",
            "overall_score": overall,
            "reviewer_model": "heuristic-review",
            "reason": "内容结构、校园相关性、互动质量和噪声风险综合评估。",
            "clean_summary": self._default_summary(post),
            "key_points": list(tags[:4]),
            "raw": {
                "threshold": threshold,
                "forum_adopted": adopted,
                "score_breakdown": score_breakdown,
                "review_mode": "heuristic_fallback",
            },
        }

    def _normalize_payload(self, payload: dict, post: dict, threshold: int, reviewer_model: str) -> dict:
        clean_summary = str(payload.get("clean_summary") or payload.get("summary") or "").strip()
        if not clean_summary:
            clean_summary = self._default_summary(post)

        reason = str(payload.get("reason") or payload.get("rationale") or "").strip()
        if not reason:
            reason = "模型未返回明确理由，已按综合评分结果处理。"

        key_points = payload.get("key_points") or payload.get("points") or []
        if not isinstance(key_points, list):
            key_points = []
        key_points = [str(item).strip() for item in key_points if str(item).strip()][:5]

        decision = str(payload.get("decision") or "").strip().lower()
        overall = _normalize_model_score(payload.get("overall_score"), default=0)
        passed = decision in {"pass", "approve", "accept"} and overall >= threshold
        if decision not in {"pass", "approve", "accept", "reject", "deny"}:
            passed = overall >= threshold

        return {
            "decision": "pass" if passed else "reject",
            "overall_score": overall,
            "reviewer_model": reviewer_model,
            "reason": reason,
            "clean_summary": clean_summary,
            "key_points": key_points,
            "raw": {
                **payload,
                "threshold": threshold,
                "forum_adopted": bool(post.get("adopted")),
                "review_mode": "model_json",
            },
        }

    def review_post(self, post: dict) -> dict:
        threshold = _clamp_score(settings.evolution_ai_review_min_score, default=72)
        fallback = self._heuristic_review(post, threshold)
        if not bool(settings.evolution_ai_review_enabled):
            fallback["reason"] = "AI 审核已关闭，当前按规则评分直接处理。"
            return fallback

        provider = self._provider_config()
        if not provider["base_url"] or not provider["api_key"] or not provider["model"]:
            fallback["reason"] = "AI 审核模型未完整配置，当前按规则评分直接处理。"
            return fallback

        prompt_payload = {
            "title": post.get("title"),
            "content": post.get("content"),
            "category": post.get("category"),
            "tags": post.get("tags") or [],
            "likes_count": int(post.get("likes_count") or 0),
            "comments_count": int(post.get("comments_count") or 0),
            "adopted": bool(post.get("adopted")),
            "adopted_comment": str(post.get("adopted_comment") or "").strip(),
            "top_comments": post.get("top_comments") or [],
        }
        payload = {
            "model": provider["model"],
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是校园论坛知识库审核员。"
                        "你要判断一条校园论坛帖子是否适合进入长期知识库。"
                        "重点看校园相关性、信息密度、可复用性、事实稳定性、垃圾信息/刷赞风险。"
                        "拒绝测试贴、灌水贴、情绪宣泄、无具体信息的闲聊、明显广告、可能被刷赞的低质内容。"
                        "overall_score 必须返回 0 到 100 的整数，不要用 0 到 10。"
                        "decision 只能返回 pass 或 reject。"
                        "只返回 JSON，不要返回解释性前缀。"
                        "JSON 字段必须包含 decision, overall_score, reason, clean_summary, key_points。"
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(prompt_payload, ensure_ascii=False),
                },
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }
        headers = {"Authorization": f"Bearer {provider['api_key']}"}
        try:
            with httpx.Client(timeout=provider["timeout"]) as client:
                resp = client.post(f"{provider['base_url']}/chat/completions", json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            content = str(data["choices"][0]["message"]["content"]).strip()
            match = self._JSON_RE.search(content)
            parsed = json.loads(match.group(0) if match else content)
            return self._normalize_payload(parsed, post=post, threshold=threshold, reviewer_model=provider["model"])
        except Exception:
            fallback["reason"] = "AI 审核调用失败，已自动回退到规则评分。"
            return fallback


evolution_review_service = EvolutionReviewService()
