from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json

from sqlalchemy import delete, func, inspect, select, text

from app.core.config import settings
from app.core.passwords import hash_password, needs_password_rehash, new_salt
from app.core.database import Base, SessionLocal, engine
from app.models.admin_login_guard import AdminLoginGuard  # noqa: F401
from app.models.comment import Comment
from app.models.comment_asset import CommentAsset  # noqa: F401
from app.models.comment_like import CommentLike  # noqa: F401
from app.models.errand_task import ErrandTask  # noqa: F401
from app.models.evolution_review import EvolutionReview  # noqa: F401
from app.models.knowledge import KnowledgeBase
from app.models.message import MessageNotification
from app.models.moderation_log import ModerationLog  # noqa: F401
from app.models.post_adoption import PostAdoption  # noqa: F401
from app.models.post_asset import PostAsset  # noqa: F401
from app.models.post import Post
from app.models.post_like import PostLike  # noqa: F401
from app.models.post_save import PostSave  # noqa: F401
from app.models.qa_log import QALog  # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401
from app.models.recent_search import RecentSearchKeyword  # noqa: F401
from app.models.task import IngestTask  # noqa: F401
from app.models.token_revocation import TokenRevocation  # noqa: F401
from app.models.user import User
from app.models.web_login_code import WebLoginCode  # noqa: F401


DEMO_USERS = [
    {"id": 1, "username": "zhaoyi", "display_name": "赵毅", "wechat_openid": "wx_mock_40a90c79dcede007aec46d6b"},
    {"id": 2, "username": "library_morning", "display_name": "清晨图书馆人"},
    {"id": 3, "username": "canteen_team", "display_name": "二食堂探店组"},
    {"id": 4, "username": "schedule_help", "display_name": "课表救援队"},
    {"id": 5, "username": "kaoyan_team", "display_name": "考研作战组"},
]


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def _post_time(minutes_ago: int) -> datetime:
    return _utcnow() - timedelta(minutes=minutes_ago)


DEMO_POSTS = [
    {
        "id": 1,
        "author_id": 2,
        "category": "study",
        "title": "A1-307 晚上 8 点后插座充足",
        "content": "空调稳定、噪音中低，适合整理作业和复习。建议先占靠窗区域，灯光更柔和。",
        "tags": ["#自习室", "#图书馆周边", "#夜间学习"],
        "likes_count": 64,
        "comments_count": 3,
        "adopted": True,
        "created_at": _post_time(95),
    },
    {
        "id": 2,
        "author_id": 3,
        "category": "canteen",
        "title": "麻辣烫窗口 12:30 以后明显拥挤",
        "content": "建议先走北门清汤窗口，平均快 6 到 8 分钟。周一和周三中午人流最稳。",
        "tags": ["#食堂避雷", "#排队时间", "#午高峰"],
        "likes_count": 41,
        "comments_count": 2,
        "adopted": False,
        "created_at": _post_time(82),
    },
    {
        "id": 3,
        "author_id": 4,
        "category": "academic",
        "title": "周三晚自习教室有临时调度",
        "content": "教务系统会在 17:00 前同步新教室，晚课同学建议在出发前再确认一次地点。",
        "tags": ["#教务通知", "#调课提醒", "#课程安排"],
        "likes_count": 83,
        "comments_count": 2,
        "adopted": True,
        "created_at": _post_time(74),
    },
    {
        "id": 4,
        "author_id": 5,
        "category": "study",
        "title": "A2-402 更安静但距离稍远",
        "content": "如果目标是长时间复习，A2-402 更安静；如果重视通勤效率，A1-307 会更平衡。",
        "tags": ["#考研复习", "#教室体验", "#晚间学习"],
        "likes_count": 29,
        "comments_count": 2,
        "adopted": False,
        "created_at": _post_time(58),
    },
    {
        "id": 5,
        "author_id": 1,
        "category": "study",
        "title": "跑腿需求：西门快递代取，今晚 7 点前",
        "content": "有一个顺丰快递放在西门驿站，今晚 19:00 前能帮忙代取的同学私信我，酬谢 5 元。",
        "tags": ["#跑腿", "#西门驿站", "#今晚截止"],
        "likes_count": 8,
        "comments_count": 2,
        "adopted": False,
        "created_at": _post_time(34),
    },
    {
        "id": 6,
        "author_id": 1,
        "category": "academic",
        "title": "课程评价：软件工程导论平时分给得稳吗",
        "content": "想听听上过这门课的同学真实反馈，尤其是平时分构成、作业压力和期末复习难度。",
        "tags": ["#课程评价", "#软件工程", "#选课参考"],
        "likes_count": 14,
        "comments_count": 3,
        "adopted": False,
        "created_at": _post_time(22),
    },
    {
        "id": 7,
        "author_id": 1,
        "category": "academic",
        "title": "补退选提醒：周五 18:00 关闭当前窗口",
        "content": "教务系统这轮补退选本周五 18:00 截止，想换课的同学记得把备选方案先存好。",
        "tags": ["#补退选", "#教务提醒", "#时间节点"],
        "likes_count": 11,
        "comments_count": 1,
        "adopted": False,
        "created_at": _post_time(14),
    },
    {
        "id": 8,
        "author_id": 3,
        "category": "canteen",
        "title": "一食堂二楼烤盘饭 13:00 后基本不用排队",
        "content": "如果错过了中午高峰，一食堂二楼烤盘饭 13:00 以后基本 3 分钟内能取到餐。",
        "tags": ["#一食堂", "#错峰吃饭", "#午后窗口"],
        "likes_count": 22,
        "comments_count": 2,
        "adopted": False,
        "created_at": _post_time(9),
    },
    {
        "id": 9,
        "author_id": 2,
        "category": "market",
        "title": "二手显示器验机建议：先看亮点和接口，再谈价格",
        "content": "校内二手显示器优先确认亮点、漏光、接口是否齐全，再现场接电脑试 5 分钟。24 寸办公屏 180 到 260 元更稳，不要只看外观新旧。",
        "tags": ["#二手交易", "#显示器", "#验机建议"],
        "likes_count": 33,
        "comments_count": 2,
        "adopted": False,
        "created_at": _post_time(49),
    },
]


DEMO_COMMENTS = [
    {"post_id": 1, "author_id": 2, "content": "我昨晚 9 点去还有位，靠窗区确实更适合久坐。"},
    {"post_id": 1, "author_id": 4, "content": "插座够用，但 8 点前先占位更稳。"},
    {"post_id": 1, "author_id": 1, "content": "周末去过一次，整体体验比图书馆大厅安静。"},
    {"post_id": 2, "author_id": 3, "content": "补充一下，周五 12:00 以后麻辣烫会更慢。"},
    {"post_id": 2, "author_id": 1, "content": "北门清汤窗口今天中午确实快很多。"},
    {"post_id": 3, "author_id": 1, "content": "已经收到推送了，地点改到 A3-201。"},
    {"post_id": 3, "author_id": 5, "content": "考试周最好提前 20 分钟确认教室。"},
    {"post_id": 4, "author_id": 2, "content": "A2-402 适合长时间复习，就是离食堂远一点。"},
    {"post_id": 4, "author_id": 1, "content": "如果只自习两小时，我还是更偏向 A1-307。"},
    {"post_id": 5, "author_id": 2, "content": "我 18:30 会路过西门，可以顺手帮你带。"},
    {"post_id": 5, "author_id": 3, "content": "驿站今天排队不长，五分钟内能取到。"},
    {"post_id": 6, "author_id": 4, "content": "平时分占比不低，作业认真做基本不吃亏。"},
    {"post_id": 6, "author_id": 5, "content": "老师讲得细，期末复习压力不算大。"},
    {"post_id": 6, "author_id": 2, "content": "如果想冲高分，课堂展示最好主动一点。"},
    {"post_id": 7, "author_id": 4, "content": "补退选高峰会卡，建议 17:30 前就登录。"},
    {"post_id": 8, "author_id": 1, "content": "13:10 去试过一次，确实比一楼快很多。"},
    {"post_id": 8, "author_id": 5, "content": "烤盘饭出餐速度很稳，适合赶下午课。"},
    {"post_id": 9, "author_id": 1, "content": "线下验机时记得让卖家把亮度拉满，亮点和偏色更容易看出来。"},
    {"post_id": 9, "author_id": 3, "content": "如果是 HDMI 老接口机型，最好顺手问清有没有电源线和转接头。"},
]


DEMO_MESSAGES = [
    {
        "type": "likes",
        "source_post_id": 6,
        "source_user_id": 4,
        "content": "课程评价：软件工程导论平时分给得稳吗",
        "is_read": False,
        "created_at": _post_time(11),
    },
    {
        "type": "likes",
        "source_post_id": 5,
        "source_user_id": 2,
        "content": "跑腿需求：西门快递代取，今晚 7 点前",
        "is_read": False,
        "created_at": _post_time(27),
    },
    {
        "type": "saved",
        "source_post_id": 4,
        "source_user_id": 5,
        "content": "A2-402 更安静但距离稍远",
        "is_read": False,
        "created_at": _post_time(41),
    },
]

DEMO_ERRANDS = [
    {
        "id": 1,
        "publisher_id": 2,
        "runner_id": None,
        "task_type": "quick",
        "title": "南门驿站代取顺丰",
        "reward": "￥6",
        "eta": "20 分钟内",
        "pickup_location": "南门驿站",
        "destination": "七一路校区 兰苑 6 号楼",
        "note": "取件码私聊发，袋子有点大。",
        "contact": "微信：library_morning",
        "status": "open",
        "created_at": _post_time(26),
        "accepted_at": None,
        "delivered_at": None,
        "confirmed_at": None,
        "canceled_at": None,
    },
    {
        "id": 2,
        "publisher_id": 3,
        "runner_id": None,
        "task_type": "delivery",
        "title": "北食堂外卖代拿",
        "reward": "￥4",
        "eta": "15 分钟内",
        "pickup_location": "北食堂骑手取餐点",
        "destination": "A 区教学楼门口",
        "note": "到楼下后电话提醒即可。",
        "contact": "手机号：139****6612",
        "status": "open",
        "created_at": _post_time(18),
        "accepted_at": None,
        "delivered_at": None,
        "confirmed_at": None,
        "canceled_at": None,
    },
    {
        "id": 3,
        "publisher_id": 1,
        "runner_id": 1,
        "task_type": "print",
        "title": "打印实验报告 30 页",
        "reward": "￥8",
        "eta": "1 小时内",
        "pickup_location": "教学楼 A4 打印点",
        "destination": "五四路校区 图书馆门口",
        "note": "双面黑白打印，完成后站内联系。",
        "contact": "站内私信 @赵同学",
        "status": "inprogress",
        "created_at": _post_time(62),
        "accepted_at": _post_time(55),
        "delivered_at": None,
        "confirmed_at": None,
        "canceled_at": None,
    },
]

DEMO_RECENT_SEARCHES = [
    "A1-307 晚间自习位反馈",
    "二手交易",
    "课程评价里推荐哪位老师？",
    "二食堂清汤窗口排队快吗",
    "最近校园趣事热帖有哪些？",
    "补退选提醒",
]

DEMO_LIKED_POST_IDS = [1, 3, 8]
DEMO_SAVED_POST_IDS = [4, 9]

def _password_hash(raw: str, salt: str) -> str:
    return hash_password(raw, salt=salt)


def _next_id(db, model, col_name: str = "id") -> int:
    col = getattr(model, col_name)
    current = db.scalar(select(func.max(col)))
    return int(current or 0) + 1


def _ensure_schema_extensions() -> None:
    with engine.begin() as conn:
        inspector = inspect(conn)
        tables = set(inspector.get_table_names())
        if "comments" not in tables:
            return

        columns = {col["name"] for col in inspector.get_columns("comments")}
        if "parent_comment_id" not in columns:
            conn.execute(text("ALTER TABLE comments ADD COLUMN parent_comment_id BIGINT"))
        if "reply_to_author_id" not in columns:
            conn.execute(text("ALTER TABLE comments ADD COLUMN reply_to_author_id BIGINT"))
        if "reply_to_user_name" not in columns:
            conn.execute(text("ALTER TABLE comments ADD COLUMN reply_to_user_name VARCHAR(120)"))
        if "likes_count" not in columns:
            conn.execute(text("ALTER TABLE comments ADD COLUMN likes_count INTEGER DEFAULT 0"))

        if "comment_likes" not in tables:
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS comment_likes (
                      id BIGINT PRIMARY KEY,
                      comment_id BIGINT NOT NULL,
                      user_id BIGINT NOT NULL,
                      created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                      CONSTRAINT uq_comment_like UNIQUE (comment_id, user_id)
                    )
                    """
                )
            )

        if "post_likes" not in tables:
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS post_likes (
                      id BIGINT PRIMARY KEY,
                      post_id BIGINT NOT NULL,
                      user_id BIGINT NOT NULL,
                      created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                      CONSTRAINT uq_post_like UNIQUE (post_id, user_id)
                    )
                    """
                )
            )

        if "post_saves" not in tables:
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS post_saves (
                      id BIGINT PRIMARY KEY,
                      post_id BIGINT NOT NULL,
                      user_id BIGINT NOT NULL,
                      created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                      CONSTRAINT uq_post_save UNIQUE (post_id, user_id)
                    )
                    """
                )
            )

        if "moderation_logs" not in tables:
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS moderation_logs (
                      id BIGINT PRIMARY KEY,
                      action VARCHAR(64) NOT NULL,
                      actor_id BIGINT NOT NULL,
                      target_type VARCHAR(32) NOT NULL,
                      target_id VARCHAR(64) NOT NULL,
                      detail TEXT NOT NULL,
                      created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            )

        if "refresh_tokens" not in tables:
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS refresh_tokens (
                      id BIGINT PRIMARY KEY,
                      user_id BIGINT NOT NULL,
                      jti VARCHAR(64) NOT NULL UNIQUE,
                      revoked BOOLEAN NOT NULL DEFAULT 0,
                      expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                      created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            )

        if "token_revocations" not in tables:
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS token_revocations (
                      id BIGINT PRIMARY KEY,
                      jti VARCHAR(64) NOT NULL UNIQUE,
                      token_type VARCHAR(32) NOT NULL,
                      revoked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                      expires_at TIMESTAMP WITH TIME ZONE NOT NULL
                    )
                    """
                )
            )

        user_columns = {col["name"] for col in inspector.get_columns("users")} if "users" in tables else set()
        if "wechat_openid" not in user_columns and "users" in tables:
            conn.execute(text("ALTER TABLE users ADD COLUMN wechat_openid VARCHAR(128)"))
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ux_users_wechat_openid ON users (wechat_openid)"))
        if "password_salt" not in user_columns and "users" in tables:
            conn.execute(text("ALTER TABLE users ADD COLUMN password_salt VARCHAR(64)"))
        if "nickname" not in user_columns and "users" in tables:
            conn.execute(text("ALTER TABLE users ADD COLUMN nickname VARCHAR(128)"))


def _upsert_users(db) -> None:
    for spec in DEMO_USERS:
        row = db.get(User, int(spec["id"]))
        salt = f"seed-{spec['id']}"
        if row is None:
            row = User(
                id=int(spec["id"]),
                username=str(spec["username"]),
                display_name=str(spec["display_name"]),
                nickname=None,
                password_hash=_password_hash("demo", salt),
                password_salt=salt,
                role="client",
                status="active",
                wechat_openid=spec.get("wechat_openid"),
            )
        else:
            row.username = str(spec["username"])
            row.display_name = str(spec["display_name"])
            row.role = "client"
            row.status = "active"
            row.password_salt = row.password_salt or salt or new_salt()
            if needs_password_rehash(row.password_hash, row.password_salt):
                row.password_hash = _password_hash("demo", row.password_salt)
            if spec.get("wechat_openid") and not row.wechat_openid:
                row.wechat_openid = str(spec["wechat_openid"])
        db.add(row)


def _upsert_demo_posts(db) -> list[int]:
    post_ids: list[int] = []
    for spec in DEMO_POSTS:
        row = db.get(Post, int(spec["id"]))
        if row is None:
            row = Post(id=int(spec["id"]), author_id=int(spec["author_id"]))
        row.author_id = int(spec["author_id"])
        row.category = str(spec["category"])
        row.title = str(spec["title"])
        row.content = str(spec["content"])
        row.tags_json = json.dumps(spec["tags"], ensure_ascii=False)
        row.likes_count = int(spec["likes_count"])
        row.comments_count = int(spec["comments_count"])
        row.adopted = bool(spec["adopted"])
        row.status = "published"
        row.created_at = spec["created_at"]
        db.add(row)
        post_ids.append(int(spec["id"]))
    return post_ids


def _reset_demo_post_artifacts(db, post_ids: list[int]) -> None:
    if not post_ids:
        return
    db.execute(delete(PostAsset).where(PostAsset.post_id.in_(post_ids)))
    db.execute(delete(PostAdoption).where(PostAdoption.post_id.in_(post_ids)))


def _reset_demo_comments(db, post_ids: list[int]) -> None:
    if not post_ids:
        return

    existing_comment_ids = db.execute(select(Comment.id).where(Comment.post_id.in_(post_ids))).scalars().all()
    if existing_comment_ids:
        db.execute(delete(CommentAsset).where(CommentAsset.comment_id.in_(existing_comment_ids)))
        db.execute(delete(CommentLike).where(CommentLike.comment_id.in_(existing_comment_ids)))
    db.execute(delete(Comment).where(Comment.post_id.in_(post_ids)))

    next_comment_id = _next_id(db, Comment)
    counts: dict[int, int] = {}
    for spec in DEMO_COMMENTS:
        row = Comment(
            id=next_comment_id,
            post_id=int(spec["post_id"]),
            author_id=int(spec["author_id"]),
            content=str(spec["content"]),
            status="visible",
            likes_count=0,
        )
        db.add(row)
        counts[row.post_id] = counts.get(row.post_id, 0) + 1
        next_comment_id += 1

    for post_spec in DEMO_POSTS:
        row = db.get(Post, int(post_spec["id"]))
        if row:
            row.comments_count = counts.get(int(post_spec["id"]), 0)
            db.add(row)


def _reset_demo_messages(db) -> None:
    db.execute(delete(MessageNotification).where(MessageNotification.receiver_user_id == 1))
    next_message_id = _next_id(db, MessageNotification)
    for spec in DEMO_MESSAGES:
        db.add(
            MessageNotification(
                id=next_message_id,
                receiver_user_id=1,
                type=str(spec["type"]),
                source_post_id=int(spec["source_post_id"]),
                source_user_id=int(spec["source_user_id"]),
                content=str(spec["content"]),
                is_read=bool(spec["is_read"]),
                created_at=spec["created_at"],
            )
        )
        next_message_id += 1


def _reset_recent_searches(db) -> None:
    db.execute(delete(RecentSearchKeyword).where(RecentSearchKeyword.user_id == 1))
    next_recent_id = _next_id(db, RecentSearchKeyword)
    for index, keyword in enumerate(DEMO_RECENT_SEARCHES):
        db.add(
            RecentSearchKeyword(
                id=next_recent_id + index,
                user_id=1,
                keyword=str(keyword),
                updated_at=_utcnow() - timedelta(minutes=index),
                created_at=_utcnow() - timedelta(minutes=index),
            )
        )


def _upsert_demo_errands(db) -> None:
    for spec in DEMO_ERRANDS:
        row = db.get(ErrandTask, int(spec["id"]))
        if row is None:
            row = ErrandTask(id=int(spec["id"]))
        row.publisher_id = int(spec["publisher_id"])
        row.runner_id = int(spec["runner_id"]) if spec.get("runner_id") else None
        row.task_type = str(spec["task_type"])
        row.title = str(spec["title"])
        row.reward = str(spec["reward"])
        row.eta = str(spec["eta"])
        row.pickup_location = str(spec["pickup_location"])
        row.destination = str(spec["destination"])
        row.note = str(spec["note"])
        row.contact = str(spec["contact"])
        row.status = str(spec["status"])
        row.created_at = spec["created_at"]
        row.accepted_at = spec.get("accepted_at")
        row.delivered_at = spec.get("delivered_at")
        row.confirmed_at = spec.get("confirmed_at")
        row.canceled_at = spec.get("canceled_at")
        db.add(row)


def _reset_demo_likes(db) -> None:
    db.execute(delete(PostLike).where(PostLike.user_id == 1))
    next_like_id = _next_id(db, PostLike)
    for offset, post_id in enumerate(DEMO_LIKED_POST_IDS):
        db.add(
            PostLike(
                id=next_like_id + offset,
                post_id=int(post_id),
                user_id=1,
                created_at=_utcnow() - timedelta(minutes=offset + 3),
            )
        )


def _reset_demo_saves(db) -> None:
    db.execute(delete(PostSave).where(PostSave.user_id == 1))
    next_save_id = _next_id(db, PostSave)
    for offset, post_id in enumerate(DEMO_SAVED_POST_IDS):
        db.add(
            PostSave(
                id=next_save_id + offset,
                post_id=int(post_id),
                user_id=1,
                created_at=_utcnow() - timedelta(minutes=offset + 5),
            )
        )


def _ensure_knowledge_base(db) -> None:
    existing = db.execute(select(KnowledgeBase).order_by(KnowledgeBase.id.asc())).scalars().first()
    if existing:
        existing.name = "校园通用知识库"
        existing.description = "教务、图书馆、生活服务"
        existing.status = "active"
        existing.visibility = "private"
        existing.doc_count = int(existing.doc_count or 0)
        existing.chunk_count = int(existing.chunk_count or 0)
        existing.created_by = int(existing.created_by or 1)
        db.add(existing)
        return

    db.add(
        KnowledgeBase(
            id=_next_id(db, KnowledgeBase),
            name="校园通用知识库",
            description="教务、图书馆、生活服务",
            status="active",
            visibility="private",
            doc_count=0,
            chunk_count=0,
            created_by=1,
        )
    )


def bootstrap_database() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_schema_extensions()

    with SessionLocal() as db:
        if settings.bootstrap_demo_data:
            _upsert_users(db)
            has_seeded_content = bool(
                (db.scalar(select(func.count()).select_from(Post)) or 0)
                or (db.scalar(select(func.count()).select_from(ErrandTask)) or 0)
            )
            if not has_seeded_content:
                post_ids = _upsert_demo_posts(db)
                _reset_demo_post_artifacts(db, post_ids)
                _reset_demo_comments(db, post_ids)
                _reset_demo_likes(db)
                _reset_demo_saves(db)
                _reset_demo_messages(db)
                _reset_recent_searches(db)
                _upsert_demo_errands(db)
        _ensure_knowledge_base(db)
        db.commit()
