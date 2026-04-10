from __future__ import annotations

import re
import time

from app.core.config import settings
from app.rag.retriever.context_builder import context_builder
from app.rag.retriever.hybrid_retriever import hybrid_retriever
from app.services.qa_provider import qa_provider
from app.services.rerank_provider import rerank_provider


class RAGPipeline:
    _AMBIGUOUS_RE = re.compile(r"^[\dA-Za-z\W_]{1,4}$")
    _CJK_RE = re.compile(r"[\u4e00-\u9fff]")
    _SPACE_RE = re.compile(r"\s+")
    _GREETINGS = {
        "hi",
        "hello",
        "你好",
        "您好",
        "哈喽",
        "在吗",
        "有人吗",
    }
    _INTENT_HINTS = {
        "选课": ("河北大学", "选课", "教务系统", "课程安排", "校园服务"),
        "课表": ("河北大学", "课表", "课程表", "教务系统", "校园服务"),
        "课程表": ("河北大学", "课程表", "课表", "教务系统", "校园服务"),
        "成绩单": ("河北大学", "成绩单", "打印", "教务", "校园服务"),
        "成绩": ("河北大学", "成绩查询", "教务", "校园服务"),
        "教务": ("河北大学", "教务", "教务处", "教务系统", "校园服务"),
        "考试": ("河北大学", "考试安排", "考场", "教务", "校园服务"),
        "空教室": ("河北大学", "空教室", "自习", "教学楼", "校园服务"),
        "图书馆": ("河北大学", "图书馆", "开放时间", "借阅", "校园服务"),
        "校区": ("河北大学", "校区", "七一路校区", "五四路校区", "裕华路校区"),
        "邮编": ("河北大学", "邮编", "七一路校区", "五四路校区", "裕华路校区"),
        "学院": ("河北大学", "学院", "院系", "专业", "校园服务"),
        "宿舍": ("河北大学", "宿舍", "生活服务", "校园服务"),
        "食堂": ("河北大学", "食堂", "校园生活", "校园服务"),
    }

    _GENERAL_INTENT_ANSWERS = {
        "选课": "选课可以先从河北大学官网“校园服务”页进入统一入口，再进入学生事务系统或教务相关模块。如果你想确认补退选时间、入口异常、课程筛选规则或具体学院要求，可以继续补充。",
        "课表": "课表、课程安排和教室变更一般都在教务或学生事务系统里查看。如果你要问的是今天的课表、空教室、某门课或特定校区，可以直接补全具体条件。",
        "成绩单": "成绩单打印可优先看三条路径：一卡通中心自助终端、所在学院教学秘书、教务处线下办理。如果你是毕业生、需要盖章版或者问的是具体校区地点，可以继续说明。",
        "教务": "教务类问题建议先从河北大学官网“校园服务”页进入统一入口，再进入教务或学生事务相关系统。如果你要问的是选课、成绩、考试或证明办理，直接把事项说具体，我可以继续细化。",
    }

    def _compact(self, text: str) -> str:
        return self._SPACE_RE.sub("", str(text or "")).strip()

    def _best_item_label(self, item: dict, index: int) -> str:
        raw_title = str(item.get("title") or "").strip()
        if raw_title and len(raw_title) <= 80:
            return raw_title

        raw_text = str(item.get("text") or "").strip()
        if raw_text:
            preferred = ""
            for line in raw_text.splitlines():
                clean = line.strip()
                if len(clean) >= 6:
                    preferred = clean
                    break
            candidate = preferred or raw_text
            return candidate[:44] + ("..." if len(candidate) > 44 else "")

        return f"相关资料 {index}"

    def _is_greeting(self, query: str) -> bool:
        compact = self._compact(query).lower()
        return compact in self._GREETINGS

    def _strip_school_prefix(self, query: str) -> str:
        compact = self._compact(query)
        for prefix in ("河北大学", "hbu"):
            if compact.lower().startswith(prefix.lower()):
                return compact[len(prefix):]
        return compact

    def _generic_intent_key(self, query: str) -> str:
        compact = self._strip_school_prefix(query)
        suffixes = ("怎么办", "怎么办理", "在哪", "入口", "入口在哪", "怎么进", "怎么打印")
        for suffix in suffixes:
            if compact.endswith(suffix):
                compact = compact[: -len(suffix)]
                break
        compact = self._compact(compact)
        if compact in self._GENERAL_INTENT_ANSWERS and len(compact) <= 4:
            return compact
        return ""

    def _build_intent_answer(self, intent_key: str) -> str:
        return self._GENERAL_INTENT_ANSWERS.get(intent_key, "")

    def _should_offer_guidance(self, query: str) -> bool:
        compact = self._compact(query)
        if not compact:
            return True
        if self._is_greeting(compact):
            return True
        if len(compact) <= 2:
            return True
        if compact in self._INTENT_HINTS:
            return True
        if self._AMBIGUOUS_RE.fullmatch(compact):
            return True
        return bool(self._CJK_RE.search(compact) and len(compact) <= 4 and compact.endswith(("表", "课", "考", "院", "馆")))

    def _build_guidance_answer(self, items: list[dict]) -> str:
        if not items:
            return "当前问题还不够具体。你可以直接问“成绩单怎么打印”“选课入口在哪”“五四路校区邮编”“图书馆开放到几点”这类问题，我会更容易命中正确资料。"
        lines = ["当前问题还不够具体，我先给你列出最可能有用的方向："]
        for index, item in enumerate(items[:3], start=1):
            title = self._best_item_label(item, index)
            lines.append(f"{index}. {title}")
        lines.append("如果你补上地点、时间、课程名或具体事项，回答会明显更准。")
        return "\n".join(lines)

    def _build_greeting_answer(self) -> str:
        return "可以直接问我校区、教务、课表、选课、成绩单、图书馆、学院信息和校园服务。像“成绩单打印”“选课入口”“五四路校区邮编”这样问，回答会更快更准。"

    def _recent_user_topic(self, history: list[dict], current_query: str) -> str:
        current = self._compact(current_query)
        for item in reversed(history or []):
            if str(item.get("role") or "") != "user":
                continue
            text = self._compact(item.get("text") or "")
            if not text or text == current:
                continue
            if 4 <= len(text) <= 28:
                return text
        return ""

    def _rewrite_query(self, query: str, history: list[dict]) -> str:
        raw_query = str(query or "").strip()
        compact = self._compact(raw_query)
        if not compact:
            return raw_query

        hints: list[str] = []
        for key, expansions in self._INTENT_HINTS.items():
            if key in compact:
                hints.extend(expansions)

        if len(compact) <= 4:
            recent_topic = self._recent_user_topic(history, raw_query)
            if recent_topic:
                hints.append(recent_topic)

        if self._is_greeting(compact):
            hints.extend(("河北大学", "校园服务", "教务", "图书馆", "学院"))

        if not hints:
            return raw_query

        merged: list[str] = [raw_query]
        seen = {self._compact(raw_query)}
        for item in hints:
            clean = str(item or "").strip()
            if not clean:
                continue
            marker = self._compact(clean)
            if marker in seen:
                continue
            seen.add(marker)
            merged.append(clean)
        return " ".join(merged)

    def _merge_candidates(self, primary: list[dict], expanded: list[dict], limit: int) -> list[dict]:
        merged: dict[str, dict] = {}
        for rank, item in enumerate(primary or []):
            chunk_id = str(item.get("chunk_id", ""))
            if not chunk_id:
                continue
            payload = {**item, "_rank": rank, "_boost": float(item.get("score", 0.0) or 0.0) + 1.2}
            merged[chunk_id] = payload

        for rank, item in enumerate(expanded or []):
            chunk_id = str(item.get("chunk_id", ""))
            if not chunk_id:
                continue
            score = float(item.get("score", 0.0) or 0.0)
            if chunk_id in merged:
                merged[chunk_id]["_boost"] = max(float(merged[chunk_id].get("_boost", 0.0)), score + 0.6)
                if not merged[chunk_id].get("text"):
                    merged[chunk_id]["text"] = item.get("text", "")
                if not merged[chunk_id].get("jump_url"):
                    merged[chunk_id]["jump_url"] = item.get("jump_url", "")
                if not merged[chunk_id].get("source_type"):
                    merged[chunk_id]["source_type"] = item.get("source_type", "kb")
            else:
                merged[chunk_id] = {**item, "_rank": rank + len(primary or []), "_boost": score}

        ranked = sorted(
            merged.values(),
            key=lambda item: (float(item.get("_boost", 0.0)), -int(item.get("_rank", 0))),
            reverse=True,
        )
        for item in ranked:
            item.pop("_boost", None)
            item.pop("_rank", None)
        return ranked[:limit]

    async def ask(self, query: str, history: list[dict], kb_id: int, deep_thinking: bool = False) -> dict:
        start = time.perf_counter()
        original_query = str(query or "").strip()
        generic_intent = self._generic_intent_key(original_query)
        retrieval_query = self._rewrite_query(original_query, history)
        top_k = 30 if deep_thinking else 20

        primary_candidates = hybrid_retriever.retrieve(query=original_query, kb_id=kb_id, top_k=top_k)
        if self._compact(retrieval_query) != self._compact(original_query):
            expanded_candidates = hybrid_retriever.retrieve(query=retrieval_query, kb_id=kb_id, top_k=top_k)
            candidates = self._merge_candidates(primary_candidates, expanded_candidates, limit=top_k)
        else:
            candidates = primary_candidates

        if deep_thinking and settings.rerank_provider != "none":
            reranked = await rerank_provider.rerank(query=original_query, candidates=candidates, top_k=12)
            route_label = "深度思考 · 检索 + Rerank"
            source = "来源：知识库检索 + QA API + Rerank"
            rerank_used = True
        elif deep_thinking:
            reranked = candidates[:12]
            route_label = "深度思考 · 扩展检索"
            source = "来源：知识库检索 + QA API（已预留 Rerank）"
            rerank_used = False
        else:
            reranked = candidates[:8]
            route_label = "智能路由 · 向量检索"
            source = "来源：知识库检索 + QA API"
            rerank_used = False

        contexts = context_builder.build(reranked, limit=6)

        if self._is_greeting(original_query):
            answer = self._build_greeting_answer()
            model_name = "kb-guide"
        elif generic_intent and contexts:
            answer = self._build_intent_answer(generic_intent)
            model_name = "kb-intent"
        elif not contexts and self._should_offer_guidance(original_query):
            answer = self._build_guidance_answer(reranked)
            model_name = "kb-guide"
        elif not contexts:
            answer = "知识库中未检索到可支撑该问题的内容，请换一个更具体的问题或先补充知识库文档。"
            model_name = "kb-guard"
        else:
            answer, model_name = await qa_provider.generate(query=original_query, contexts=contexts)
            if "知识库中未检索到可支撑该问题的内容" in str(answer) and self._should_offer_guidance(original_query):
                answer = self._build_guidance_answer(reranked)
                model_name = "kb-guide"

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        citations = []
        related_answers = []
        for item in reranked[:5]:
            raw_title = str(item.get("title", "")).strip()
            raw_text = str(item.get("text", "")).replace("\n", " ").strip()
            if not raw_title:
                if raw_text:
                    raw_title = raw_text[:36] + ("..." if len(raw_text) > 36 else "")
                else:
                    raw_title = str(item.get("chunk_id", "知识片段"))

            citations.append(
                {
                    "id": str(item.get("chunk_id", "")),
                    "title": raw_title,
                    "jump_url": str(item.get("jump_url", "")),
                    "source_type": str(item.get("source_type", "kb")),
                }
            )
            related_answers.append(
                {
                    "id": str(item.get("chunk_id", "")),
                    "title": raw_title,
                    "snippet": raw_text[:180] + ("..." if len(raw_text) > 180 else ""),
                    "source_type": str(item.get("source_type", "kb")),
                    "jump_url": str(item.get("jump_url", "")),
                    "score": float(item.get("score", 0.0) or 0.0),
                }
            )

        return {
            "answer": answer,
            "route": "cloud",
            "route_label": route_label,
            "source": source,
            "model_name": model_name,
            "latency_ms": elapsed_ms,
            "contexts": contexts,
            "citations": citations,
            "related_answers": related_answers,
            "rerank_used": rerank_used,
        }


rag_pipeline = RAGPipeline()
