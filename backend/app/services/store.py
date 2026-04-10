from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class InMemoryStore:
    posts: list[dict] = field(default_factory=list)
    comments: dict[str, list[dict]] = field(default_factory=dict)
    recent_keywords: list[str] = field(default_factory=list)
    messages_likes: list[dict] = field(default_factory=list)
    messages_saved: list[dict] = field(default_factory=list)
    knowledge_bases: list[dict] = field(default_factory=list)
    documents: list[dict] = field(default_factory=list)
    tasks: list[dict] = field(default_factory=list)
    qa_logs: list[dict] = field(default_factory=list)
    chunks: dict[int, list[dict]] = field(default_factory=dict)


def _now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def create_seed_store() -> InMemoryStore:
    store = InMemoryStore()

    store.posts = [
        {
            "id": "p-1",
            "category": "study",
            "author": "@清晨图书馆人",
            "avatar": "图书",
            "level": "Lv.4",
            "time": "刚刚",
            "title": "A1-307 晚上 8 点后插座充足",
            "content": "空调稳定，噪音中低，建议先占靠窗区域，灯光更柔和。",
            "tags": ["#自习室", "#图书馆周边", "#夜间学习"],
            "likes": 63,
            "comments": 18,
            "liked": False,
            "commented": False,
            "adopted": True,
            "updated_at": "2026-04-07 00:00",
        },
        {
            "id": "p-2",
            "category": "canteen",
            "author": "@二食堂探店组",
            "avatar": "食堂",
            "level": "Lv.3",
            "time": "10 分钟前",
            "title": "麻辣烫窗口 12:30 以后明显拥挤",
            "content": "建议先走北门清汤窗口，平均快 6-8 分钟，口味也更稳定。",
            "tags": ["#食堂避雷", "#排队时间", "#午高峰"],
            "likes": 41,
            "comments": 12,
            "liked": False,
            "commented": False,
            "adopted": False,
            "updated_at": "2026-04-06 19:12",
        },
        {
            "id": "p-3",
            "category": "academic",
            "author": "@课表救援队",
            "avatar": "教务",
            "level": "Lv.5",
            "time": "22 分钟前",
            "title": "周三晚自习教室有临时调度",
            "content": "系统将在 17:00 前同步并推送提醒，建议提前确认课程地点。",
            "tags": ["#教务通知", "#调课提醒", "#课程安排"],
            "likes": 82,
            "comments": 20,
            "liked": False,
            "commented": False,
            "adopted": True,
            "updated_at": "2026-04-06 17:54",
        },
        {
            "id": "p-4",
            "category": "study",
            "author": "@考研作战组",
            "avatar": "自习",
            "level": "Lv.2",
            "time": "35 分钟前",
            "title": "A2-402 更安静但距离稍远",
            "content": "若以长时复习为优先，建议选 A2-402；若重视通勤，优先 A1-307。",
            "tags": ["#考研复习", "#教室体验", "#晚间学习"],
            "likes": 29,
            "comments": 9,
            "liked": False,
            "commented": False,
            "adopted": False,
            "updated_at": "2026-04-05 21:16",
        },
    ]

    store.comments = {
        "p-1": [
            {
                "id": "c-1-1",
                "author": "@夜读组",
                "content": "A1-307 我昨晚 9 点去还有位，体验不错。",
                "time": "3 分钟前",
                "created_at": _now(),
            },
            {
                "id": "c-1-2",
                "author": "@晚自习观察员",
                "content": "靠窗位置确实更舒服，推荐。",
                "time": "12 分钟前",
                "created_at": _now(),
            },
        ],
        "p-2": [
            {
                "id": "c-2-1",
                "author": "@食堂地图",
                "content": "补充一下，周五 12:00 以后麻辣烫更慢。",
                "time": "8 分钟前",
                "created_at": _now(),
            }
        ],
    }

    store.messages_likes = [
        {
            "id": "l-1",
            "main": "@清晨图书馆人 赞了你：A1-307 晚间自习位反馈",
            "meta": "2 分钟前 · 来自帖子互动",
            "post_id": "p-1",
            "source_type": "feed",
            "is_read": False,
        },
        {
            "id": "l-2",
            "main": "@二食堂探店组 赞了你：食堂错峰窗口清单",
            "meta": "18 分钟前 · 来自食堂频道",
            "post_id": "p-2",
            "source_type": "feed",
            "is_read": False,
        },
    ]

    store.messages_saved = [
        {
            "id": "s-1",
            "main": "@考研作战组 马住了你：A2-402 安静时段建议",
            "meta": "12 分钟前 · 收藏到自习清单",
            "post_id": "p-4",
            "source_type": "feed",
            "is_read": False,
        }
    ]

    store.knowledge_bases = [
        {
            "id": 1,
            "name": "校园通用知识库",
            "description": "教务、图书馆、生活服务",
            "status": "active",
            "doc_count": 0,
            "chunk_count": 0,
        }
    ]

    store.qa_logs = [
        {
            "id": 1,
            "query_text": "今晚哪里自习安静？",
            "answer_text": "推荐 A1-307 与 A2-402。",
            "model_name": "local-fallback",
            "latency_ms": 320,
            "status": "success",
            "created_at": _now(),
        }
    ]

    return store


store = create_seed_store()
