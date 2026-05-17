from __future__ import annotations

import re

import httpx

from app.core.config import settings

# 匹配 Qwen3 等模型可能返回的 <think>...</think> 思考标签
_THINK_TAG_RE = re.compile(r"<think>.*?</think>\s*", re.S)


class QAProvider:
    @staticmethod
    def _strip_think_tags(text: str) -> str:
        """剥离模型可能返回的 <think>...</think> 思考标签，只保留正式回答。"""
        return _THINK_TAG_RE.sub("", text).strip()

    async def generate(self, query: str, contexts: list[str]) -> tuple[str, str]:
        if not settings.qa_base_url or not settings.qa_api_key or not settings.qa_model:
            top = contexts[0][:120] if contexts else "暂无命中文档片段"
            return (f"基于知识库，建议优先参考：{top}", "local-fallback")

        payload = {
            "model": settings.qa_model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是校园知识库问答助手。"
                        "只能基于给定上下文作答，不得编造。"
                        '若上下文足够，第一句必须直接给出结论，不要先说"基于知识库"或"建议参考"。'
                        "若问题是在问地址、时间、电话、数量、是否、名单等明确事实，优先给出精确答案，再补一到两句说明。"
                        '若上下文不足，明确回答"信息不足"，并指出缺的是什么。'
                        "回复使用简洁中文，控制在 120 字内。"
                    ),
                },
                {
                    "role": "user",
                    "content": f"问题：{query}\n\n上下文：\n" + "\n---\n".join(contexts),
                },
            ],
            "temperature": 0.2,
            # 关闭 Qwen3 系列模型的内置思考模式，避免返回 <think> 标签
            "enable_thinking": False,
        }
        headers = {"Authorization": f"Bearer {settings.qa_api_key}"}
        async with httpx.AsyncClient(timeout=settings.qa_timeout_seconds) as client:
            resp = await client.post(f"{settings.qa_base_url.rstrip('/')}/chat/completions", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        raw_answer = data["choices"][0]["message"]["content"]
        # 兜底过滤：即使 enable_thinking 未生效，也剥离 think 标签
        answer = self._strip_think_tags(raw_answer)
        return answer, settings.qa_model


qa_provider = QAProvider()
