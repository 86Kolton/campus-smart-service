from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from sqlalchemy import delete, func, select  # noqa: E402

from app.core.database import SessionLocal  # noqa: E402
from app.models.comment import Comment  # noqa: E402
from app.models.comment_asset import CommentAsset  # noqa: E402
from app.models.comment_like import CommentLike  # noqa: E402
from app.models.errand_task import ErrandTask  # noqa: E402
from app.models.message import MessageNotification  # noqa: E402
from app.models.moderation_log import ModerationLog  # noqa: E402
from app.models.post import Post  # noqa: E402
from app.models.post_adoption import PostAdoption  # noqa: E402
from app.models.post_asset import PostAsset  # noqa: E402
from app.models.post_like import PostLike  # noqa: E402
from app.models.post_save import PostSave  # noqa: E402
from app.models.qa_log import QALog  # noqa: E402
from app.models.recent_search import RecentSearchKeyword  # noqa: E402
from app.models.refresh_token import RefreshToken  # noqa: E402
from app.models.token_revocation import TokenRevocation  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services.bootstrap_service import bootstrap_database  # noqa: E402
from app.services.user_service import user_service  # noqa: E402


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def _hash_password(raw: str, salt: str) -> str:
    digest = hashlib.sha256(f"{salt}:{raw}".encode("utf-8")).hexdigest()
    return f"sha256${salt}${digest}"


@dataclass(frozen=True)
class SeedUser:
    id: int
    username: str
    display_name: str
    nickname: str
    wechat_openid: str | None = None


CORE_USERS = [
    SeedUser(1, "zhaoyi", "赵毅", "赵同学", "wx_mock_40a90c79dcede007aec46d6b"),
    SeedUser(2, "library_morning", "清晨图书馆人", "清晨图书馆人"),
    SeedUser(3, "canteen_team", "二食堂探店组", "二食堂探店组"),
    SeedUser(4, "schedule_help", "课表情报站", "课表情报站"),
    SeedUser(5, "kaoyan_team", "考研作战组", "考研作战组"),
    SeedUser(6, "emptyroom_watch", "空教室观察站", "空教室观察站"),
    SeedUser(7, "northgate_runner", "北门跑腿站", "北门跑腿站"),
    SeedUser(8, "market_helper", "校园集市助手", "校园集市助手"),
]

STUDENT_NAMES = [
    "陈曦", "李萌", "王珂", "孙悦", "周洋", "许诺", "韩森", "郭宁", "刘畅", "马琳",
    "谢安", "曹雨", "郑爽", "冯涵", "唐悦", "董航", "彭晨", "梁潇", "秦朗", "胡越",
    "邱然", "吕桐", "蒋妍", "姜宇", "宋祺", "田禾", "罗川", "高霖",
]

EXTRA_USERS = [
    SeedUser(
        id=9 + index,
        username=f"seed_user_{index + 1:02d}",
        display_name=name,
        nickname=user_service.build_default_public_name(name),
    )
    for index, name in enumerate(STUDENT_NAMES)
]

ALL_USERS = CORE_USERS + EXTRA_USERS
USER_IDS = [item.id for item in ALL_USERS]
ACTIVE_AUTHOR_IDS = [item.id for item in ALL_USERS if item.id != 1]

STUDY_SPACES = [
    ("七一路校区", "A1-307", "插座比较集中", "晚八点后更稳", "适合写实验报告"),
    ("七一路校区", "A2-402", "整体更安静", "靠后排更适合背书", "适合长时间复习"),
    ("五四路校区", "主楼 302", "网络稳定", "中午换教室时波动小", "适合查资料"),
    ("裕华路校区", "图书馆二层东侧", "灯光柔和", "靠窗区晚上更舒服", "适合整理笔记"),
    ("七一路校区", "图书馆三层北区", "温度稳定", "晚间人流下降更快", "适合考研复习"),
    ("五四路校区", "理综楼 118", "空位刷新快", "课间十分钟也能坐下", "适合短时自习"),
    ("七一路校区", "B3-205", "前排插排充足", "晚自习后半段更空", "适合小组讨论后转单人复习"),
    ("七一路校区", "文科楼 406", "安静度高", "但距离食堂稍远", "适合一坐就是两小时"),
]

CANTEEN_WINDOWS = [
    ("二食堂", "麻辣烫窗口", "12:20 后排队明显变长", "想快一点就先去清汤窗口"),
    ("一食堂二层", "烤盘饭", "13:00 后基本不用排", "适合赶下午课前解决午饭"),
    ("北食堂", "兰州拉面", "11:40 前出餐最稳", "汤面速度比盖饭快一些"),
    ("二食堂", "石锅拌饭", "晚六点一到会卡住", "六点半后回落明显"),
    ("北食堂", "轻食档", "晚上七点后更空", "鸡胸肉和玉米经常最先卖完"),
    ("一食堂", "清汤窗口", "12:30 左右仍然保持快节奏", "适合想快吃完去自习的人"),
    ("教工食堂旁小卖部", "关东煮", "晚自习前半小时最抢手", "适合临时垫一口"),
]

COURSE_REVIEWS = [
    ("软件工程导论", "平时分给得稳吗", "老师讲课清楚", "平时展示占比不低"),
    ("数据结构", "作业量到底大不大", "实验周会更忙", "刷题和上机要同步"),
    ("计算机网络", "期末会不会偏概念", "课堂例题和期末题型关联大", "平时签到偶发"),
    ("操作系统", "实验报告会不会拖很久", "实验难度中等偏上", "后期复习要回到课件"),
    ("大学英语", "口语展示占分高不高", "老师更看重参与度", "小组任务最好提前分工"),
    ("高等数学", "补退选后跟不跟得上", "课堂节奏偏快", "最好带着习题册一起听"),
    ("离散数学", "考前重点怎么抓", "证明题分值稳定", "真题复用度还可以"),
    ("软件测试", "课程评价里最关心什么", "老师会看平时练习完成度", "案例题比纯记忆题更关键"),
]

ACADEMIC_NOTICES = [
    ("补退选", "本周五 18:00 关闭当前窗口", "建议先把备选方案保存好"),
    ("成绩单打印", "五四路校区主楼 603 可线下办理", "急用前先确认接收单位要求"),
    ("教务系统", "下午 16:00 到 17:00 可能短时维护", "提交申请前先保存截图"),
    ("考试安排", "本周会再同步一次考场", "出发前再核对楼层和教室"),
    ("毕业实习", "系统填报时间延长到周日中午", "指导老师审批通常当天完成"),
    ("创新学分", "补录窗口下周一开放", "材料最好按项目顺序整理"),
]

MARKET_ITEMS = [
    ("24 寸显示器", "先看亮点和接口，再谈价格", "180 到 260 元比较稳"),
    ("机械键盘", "先问轴体和空格手感", "带原盒通常更容易转出"),
    ("校园卡小电车", "电池循环次数比外观更关键", "试骑时要看刹车和灯"),
    ("二手教材", "先确认版次和是否有划线", "专业课教材回收速度快"),
    ("台灯", "优先选色温可调的", "宿舍使用看底座稳不稳"),
    ("路由器", "先确认千兆口和电源适配器", "老款双百兆口基本不建议买"),
    ("耳机", "先听左右声道和底噪", "无线款一定要看充电仓状态"),
]

GROUP_TOPICS = [
    ("跨校竞赛组队", "算法 / 前端 / 文案", "需要能稳定投入两周"),
    ("软件测试复习资料互换", "期末重点和历年题", "适合这周集中复习"),
    ("空教室情报互助", "七一路和五四路都可报点", "晚上时效性更重要"),
    ("课程评价共建", "平时分 / 作业量 / 点名频率", "希望是真实上过课的反馈"),
    ("考研自习打卡", "晚上 8 点后互相报空位", "偏向长期稳定的小组"),
]

ERRAND_CONTACTS = [
    "手机号：13912345678 / 微信：hbu_runner01",
    "手机号：13890125678 / 微信：campus_pick02",
    "手机号：13777895612 / 微信：northgate_help",
    "站内私信 @北门跑腿站",
    "站内私信 @赵同学",
]

RECENT_KEYWORDS = [
    "A1-307 晚间自习反馈",
    "二食堂麻辣烫排队",
    "课程评价 软件工程导论",
    "二手显示器验机建议",
    "北门代拿外卖",
    "跨校竞赛组队",
]


def _reset_content(db) -> None:
    db.execute(delete(CommentLike))
    db.execute(delete(CommentAsset))
    db.execute(delete(PostLike))
    db.execute(delete(PostSave))
    db.execute(delete(PostAsset))
    db.execute(delete(PostAdoption))
    db.execute(delete(MessageNotification))
    db.execute(delete(Comment))
    db.execute(delete(ErrandTask))
    db.execute(delete(RecentSearchKeyword))
    db.execute(delete(QALog))
    db.execute(delete(ModerationLog))
    db.execute(delete(RefreshToken))
    db.execute(delete(TokenRevocation))
    db.execute(delete(Post))


def _upsert_users(db) -> None:
    for spec in ALL_USERS:
        row = db.get(User, spec.id)
        salt = f"seed-large-{spec.id}"
        password_hash = _hash_password("demo123", salt)
        if row is None:
            row = User(
                id=spec.id,
                username=spec.username,
                display_name=spec.display_name,
                nickname=spec.nickname,
                password_hash=password_hash,
                password_salt=salt,
                role="client",
                status="active",
                wechat_openid=spec.wechat_openid,
            )
        else:
            row.username = spec.username
            row.display_name = spec.display_name
            row.nickname = spec.nickname
            row.password_hash = password_hash
            row.password_salt = salt
            row.role = "client"
            row.status = "active"
            if spec.wechat_openid:
                row.wechat_openid = spec.wechat_openid
        db.add(row)


def _post_timestamp(index: int) -> datetime:
    return _utcnow() - timedelta(minutes=18 * index + (index % 7) * 3 + 10)


def _build_study_post(index: int, author_id: int) -> dict:
    campus, room, trait, timing, scene = STUDY_SPACES[index % len(STUDY_SPACES)]
    title_modes = [
        f"{room} 晚上 8 点后还有空位吗",
        f"{campus}{room} 自习体验：{trait}",
        f"空教室反馈：{campus}{room} {timing}",
        f"{room} 这周适合冲刺吗：{scene}",
    ]
    title = title_modes[index % len(title_modes)]
    content = (
        f"{campus}实测 {room} {trait}，{timing}。"
        f"如果你是想找{scene}的地方，这里比一楼公共区更稳，"
        f"但最好在整点前后看一眼空位变化。"
    )
    tags = ["#自习教室", "#空教室", f"#{campus}", "#晚间学习"]
    if index % 5 == 0:
        topic, roles, desc = GROUP_TOPICS[index % len(GROUP_TOPICS)]
        title = f"{topic}：还缺 {roles}"
        content = f"{topic} 这周继续拉人，主要围绕 {desc}。如果你也在七一路校区附近学习，可以直接站内回复。"
        tags = ["#跨校", "#互助", "#组队"]
    return {
        "author_id": author_id,
        "category": "study",
        "title": title,
        "content": content,
        "tags": tags,
    }


def _build_academic_post(index: int, author_id: int) -> dict:
    if index % 3 == 0:
        course, focus, tone, tip = COURSE_REVIEWS[index % len(COURSE_REVIEWS)]
        return {
            "author_id": author_id,
            "category": "academic",
            "title": f"课程评价：{course} {focus}",
            "content": f"想收集这门课的真实反馈。当前已知是 {tone}，{tip}。如果你上过课，欢迎补充平时分、作业量和期末体验。",
            "tags": ["#课程评价", f"#{course}", "#选课参考"],
        }

    action, status, tip = ACADEMIC_NOTICES[index % len(ACADEMIC_NOTICES)]
    return {
        "author_id": author_id,
        "category": "academic",
        "title": f"{action} 提醒：{status}",
        "content": f"教务相关更新已同步到同学群和系统入口。{tip}，避免临近截止时再补材料。",
        "tags": ["#教务通知", f"#{action}", "#时间节点"],
    }


def _build_canteen_post(index: int, author_id: int) -> dict:
    canteen, window, queue_tip, extra_tip = CANTEEN_WINDOWS[index % len(CANTEEN_WINDOWS)]
    title_modes = [
        f"{canteen}{window} {queue_tip}",
        f"{canteen} 错峰建议：{window}",
        f"{window} 今天还稳吗：{extra_tip}",
    ]
    return {
        "author_id": author_id,
        "category": "canteen",
        "title": title_modes[index % len(title_modes)],
        "content": f"今天实测 {canteen}{window}，{queue_tip}。{extra_tip}，如果只是赶课，最好提前五到十分钟下楼。",
        "tags": ["#食堂避雷", f"#{canteen}", "#排队时间"],
    }


def _build_market_post(index: int, author_id: int) -> dict:
    item, advice, price = MARKET_ITEMS[index % len(MARKET_ITEMS)]
    if index % 4 == 0:
        title = f"二手{item} 验货建议：{advice}"
        content = f"校内交易 {item} 时，{advice}。按最近几次成交看，{price}，不要只看外观新旧。"
    elif index % 4 == 1:
        title = f"转让：{item} 一件，准备线下看货"
        content = f"准备把手上的 {item} 转出去，想先听听大家对当前成交价的判断。{price} 区间比较容易谈成。"
    elif index % 4 == 2:
        title = f"求购：{item}，最好这周能面交"
        content = f"最近想收一个 {item}，重点看成色和配件是否齐。{advice}，七一路和五四路都能面交。"
    else:
        title = f"校园集市提醒：{item} 最近别只看低价"
        content = f"这两天看到几条 {item} 的低价帖，最好先按 {advice} 检查，再决定是否成交。{price} 更接近真实成交带。"
    return {
        "author_id": author_id,
        "category": "market",
        "title": title,
        "content": content,
        "tags": ["#二手交易", f"#{item.replace(' ', '')}", "#校园集市"],
    }


def _build_posts(total_posts: int) -> list[dict]:
    curated = [
        {
            "author_id": 2,
            "category": "study",
            "title": "A1-307 晚上 8 点后插座充足",
            "content": "七一路校区 A1-307 晚八点后前两排基本还能补到位置，适合写实验报告和改 PPT。靠窗一侧更安静，网速也稳定。",
            "tags": ["#自习教室", "#七一路校区", "#晚间学习"],
        },
        {
            "author_id": 4,
            "category": "academic",
            "title": "周三晚自习教室有临时调度",
            "content": "教务口刚同步，今晚原定 A2-402 的自习安排改到 B3-205，建议出发前再核对一次课表或群通知。",
            "tags": ["#教务通知", "#调课提醒", "#自习安排"],
        },
        {
            "author_id": 3,
            "category": "canteen",
            "title": "麻辣烫窗口 12:30 以后明显拥挤",
            "content": "二食堂今天中午 12:25 以后排队增长很快，想快一点的话先走清汤窗口，再从一楼回教室更省时间。",
            "tags": ["#食堂避雷", "#排队时间", "#二食堂"],
        },
        {
            "author_id": 1,
            "category": "academic",
            "title": "课程评价：软件工程导论 平时分给得稳吗",
            "content": "想听听上过这门课的同学真实反馈，尤其是平时展示、作业量和期末复习压力。准备补退选前做个判断。",
            "tags": ["#课程评价", "#软件工程导论", "#选课参考"],
        },
        {
            "author_id": 8,
            "category": "market",
            "title": "二手显示器验机建议：先看亮点和接口，再谈价格",
            "content": "校内交易显示器时，先确认亮点、漏光和接口，再现场接电脑试五分钟。24 寸办公屏 180 到 260 元更接近真实成交价。",
            "tags": ["#二手交易", "#显示器", "#校园集市"],
        },
        {
            "author_id": 5,
            "category": "study",
            "title": "跨校小组：软件测试复习资料互换",
            "content": "想拉一个这周集中复习的软件测试互助组，主要交换重点、题型和老师风格。河北大学本校和邻校同学都可以进。",
            "tags": ["#跨校", "#互助", "#组队"],
        },
    ]

    builders = [
        _build_study_post,
        _build_academic_post,
        _build_canteen_post,
        _build_market_post,
    ]
    posts: list[dict] = list(curated)
    for index in range(len(curated), total_posts):
        builder = builders[index % len(builders)]
        if index % 17 == 0:
            author_id = 1
        else:
            author_id = ACTIVE_AUTHOR_IDS[index % len(ACTIVE_AUTHOR_IDS)]
        posts.append(builder(index, author_id))

    for index, post in enumerate(posts, start=1):
        post["id"] = index
        post["likes_count"] = max(0, 6 + ((total_posts - index) % 58))
        post["comments_count"] = 0
        post["adopted"] = False
        post["status"] = "published"
        post["created_at"] = _post_timestamp(index)
    return posts


def _comment_text(category: str, title: str, index: int) -> str:
    if category == "study":
        pool = [
            "我刚从现场回来，靠窗一排确实还剩两三个位置。",
            "如果只是写作业，这里比图书馆大厅安静很多。",
            "补充一下，九点后人流会再掉一波，插座更好抢。",
            "今天实测空调温度正常，待两个小时没问题。",
        ]
    elif category == "academic":
        pool = [
            "这个提醒很有用，补退选窗口临近结束时系统容易卡。",
            "我上过这门课，平时分主要看作业和展示，不会只看签到。",
            "建议把备选课提前列好，不然最后一小时很容易手忙脚乱。",
            "线下问过教学秘书，最新通知还是以系统同步为准。",
        ]
    elif category == "canteen":
        pool = [
            "今天 12:35 去看过，确实比前面半小时慢很多。",
            "如果赶时间，隔壁窗口的清汤和盖饭会更稳。",
            "晚饭时段这条经验同样适用，六点半后会顺很多。",
            "补一句，窗口阿姨最近出餐其实挺快，主要卡在点单。",
        ]
    else:
        pool = [
            "线下验机时记得让卖家把亮度拉满，坏点和偏色会更明显。",
            "这条建议靠谱，校内面交还是先把配件和序列号问清楚。",
            "如果能当场试五分钟，基本能排掉大部分明显问题。",
            "最近成交价差不多就在这个区间，太低反而要警惕。",
        ]
    return pool[index % len(pool)]


def _build_comments(posts: list[dict], target_comments: int) -> tuple[list[dict], dict[int, int], list[dict]]:
    comments: list[dict] = []
    comment_counts: dict[int, int] = {}
    adoptions: list[dict] = []
    comment_id = 1

    for post in posts:
        base_count = 1 if post["id"] <= 16 else (post["id"] % 4)
        if post["id"] % 9 == 0:
            base_count += 1
        base_count = min(base_count, 4)

        local_ids: list[int] = []
        for index in range(base_count):
            author_id = ACTIVE_AUTHOR_IDS[(post["id"] + index) % len(ACTIVE_AUTHOR_IDS)]
            if author_id == int(post["author_id"]):
                author_id = ACTIVE_AUTHOR_IDS[(post["id"] + index + 3) % len(ACTIVE_AUTHOR_IDS)]
            comments.append(
                {
                    "id": comment_id,
                    "post_id": int(post["id"]),
                    "author_id": int(author_id),
                    "parent_comment_id": None,
                    "reply_to_author_id": None,
                    "reply_to_user_name": None,
                    "content": _comment_text(str(post["category"]), str(post["title"]), index + post["id"]),
                    "status": "visible",
                    "likes_count": (post["id"] + index) % 5,
                    "created_at": post["created_at"] + timedelta(minutes=25 + index * 6),
                }
            )
            local_ids.append(comment_id)
            comment_id += 1

        if local_ids and post["id"] % 7 == 0:
            parent_comment_id = local_ids[0]
            parent_author_id = next(item["author_id"] for item in comments if item["id"] == parent_comment_id)
            reply_author = next(item.nickname for item in ALL_USERS if item.id == parent_author_id)
            comments.append(
                {
                    "id": comment_id,
                    "post_id": int(post["id"]),
                    "author_id": 1 if int(post["author_id"]) != 1 else 2,
                    "parent_comment_id": parent_comment_id,
                    "reply_to_author_id": int(parent_author_id),
                    "reply_to_user_name": reply_author,
                    "content": "补充一下，我刚又看了一遍现场，和楼主说的情况基本一致。",
                    "status": "visible",
                    "likes_count": post["id"] % 4,
                    "created_at": post["created_at"] + timedelta(minutes=58),
                }
            )
            local_ids.append(comment_id)
            comment_id += 1

        comment_counts[int(post["id"])] = len(local_ids)
        if local_ids and post["id"] % 23 == 0:
            post["adopted"] = True
            first_comment = next(item for item in comments if item["id"] == local_ids[0])
            adoption_user = next(item for item in ALL_USERS if item.id == int(first_comment["author_id"]))
            post_author = next(item for item in ALL_USERS if item.id == int(post["author_id"]))
            adoptions.append(
                {
                    "post_id": int(post["id"]),
                    "post_title": str(post["title"]),
                    "post_author_id": int(post["author_id"]),
                    "post_author_name": post_author.nickname,
                    "adopted_comment_id": int(first_comment["id"]),
                    "adopted_user_id": int(first_comment["author_id"]),
                    "adopted_user_name": adoption_user.nickname,
                    "adopted_comment_text": str(first_comment["content"]),
                    "adopted_at": first_comment["created_at"] + timedelta(minutes=2),
                    "created_at": first_comment["created_at"] + timedelta(minutes=2),
                }
            )

        if len(comments) >= target_comments:
            break

    return comments[:target_comments], comment_counts, adoptions


def _build_errands(total_errands: int) -> list[dict]:
    errands: list[dict] = []
    task_types = ["quick", "delivery", "print", "other"]
    pick_locations = ["南门驿站", "北食堂骑手取餐点", "A4 打印店", "七一路校区快递柜", "五四路校区主楼门口"]
    destinations = ["兰芷 6 号楼", "A 区教学楼门口", "图书馆东门", "荷园 2 号楼", "理综楼一层大厅"]
    notes = [
        "到楼下后电话提醒即可。",
        "取件码和尾号会在站内补发。",
        "如果打印店排队超过十分钟请先站内联系。",
        "尽量在晚八点前送到，到了直接发消息。",
    ]
    status_cycle = ["open", "inprogress", "waiting_confirm", "done", "canceled"]
    for index in range(total_errands):
        created_at = _utcnow() - timedelta(minutes=42 * index + 12)
        status = status_cycle[index % len(status_cycle)]
        publisher_id = 1 if index % 6 == 0 else ACTIVE_AUTHOR_IDS[index % len(ACTIVE_AUTHOR_IDS)]
        runner_id = None
        accepted_at = None
        delivered_at = None
        confirmed_at = None
        canceled_at = None
        if status in {"inprogress", "waiting_confirm", "done"}:
            runner_id = ACTIVE_AUTHOR_IDS[(index + 5) % len(ACTIVE_AUTHOR_IDS)]
            if runner_id == publisher_id:
                runner_id = ACTIVE_AUTHOR_IDS[(index + 9) % len(ACTIVE_AUTHOR_IDS)]
            accepted_at = created_at + timedelta(minutes=9)
        if status in {"waiting_confirm", "done"}:
            delivered_at = created_at + timedelta(minutes=35)
        if status == "done":
            confirmed_at = created_at + timedelta(minutes=54)
        if status == "canceled":
            canceled_at = created_at + timedelta(minutes=16)

        task_type = task_types[index % len(task_types)]
        errands.append(
            {
                "id": index + 1,
                "publisher_id": int(publisher_id),
                "runner_id": int(runner_id) if runner_id else None,
                "task_type": task_type,
                "title": [
                    "南门驿站代取顺丰",
                    "北食堂外卖代拿",
                    "打印实验报告 30 页",
                    "帮带一杯热美式到图书馆",
                ][index % 4],
                "reward": f"￥{4 + (index % 5)}",
                "eta": ["15 分钟内", "20 分钟内", "40 分钟内", "尽快"][index % 4],
                "pickup_location": pick_locations[index % len(pick_locations)],
                "destination": destinations[index % len(destinations)],
                "note": notes[index % len(notes)],
                "contact": ERRAND_CONTACTS[index % len(ERRAND_CONTACTS)],
                "status": status,
                "created_at": created_at,
                "accepted_at": accepted_at,
                "delivered_at": delivered_at,
                "confirmed_at": confirmed_at,
                "canceled_at": canceled_at,
            }
        )
    return errands


def _insert_posts(db, posts: list[dict]) -> None:
    for post in posts:
        db.add(
            Post(
                id=int(post["id"]),
                author_id=int(post["author_id"]),
                category=str(post["category"]),
                title=str(post["title"]),
                content=str(post["content"]),
                tags_json=json.dumps(post["tags"], ensure_ascii=False),
                likes_count=int(post["likes_count"]),
                comments_count=int(post["comments_count"]),
                adopted=bool(post["adopted"]),
                status="published",
                created_at=post["created_at"],
            )
        )


def _insert_comments(db, comments: list[dict]) -> None:
    for item in comments:
        db.add(
            Comment(
                id=int(item["id"]),
                post_id=int(item["post_id"]),
                author_id=int(item["author_id"]),
                parent_comment_id=item["parent_comment_id"],
                reply_to_author_id=item["reply_to_author_id"],
                reply_to_user_name=item["reply_to_user_name"],
                content=str(item["content"]),
                status="visible",
                likes_count=int(item["likes_count"]),
                created_at=item["created_at"],
            )
        )


def _insert_adoptions(db, adoptions: list[dict]) -> None:
    for index, item in enumerate(adoptions, start=1):
        db.add(
            PostAdoption(
                id=index,
                post_id=int(item["post_id"]),
                post_title=str(item["post_title"]),
                post_author_id=int(item["post_author_id"]),
                post_author_name=str(item["post_author_name"]),
                adopted_comment_id=int(item["adopted_comment_id"]),
                adopted_user_id=int(item["adopted_user_id"]),
                adopted_user_name=str(item["adopted_user_name"]),
                adopted_comment_text=str(item["adopted_comment_text"]),
                adopted_at=item["adopted_at"],
                created_at=item["created_at"],
            )
        )


def _insert_likes_and_saves(db, posts: list[dict], comments: list[dict]) -> tuple[int, int]:
    candidate_post_ids = [int(item["id"]) for item in posts if int(item["author_id"]) != 1]
    liked_ids = candidate_post_ids[:28]
    saved_ids = candidate_post_ids[28:48]
    for index, post_id in enumerate(liked_ids, start=1):
        db.add(PostLike(id=index, post_id=post_id, user_id=1, created_at=_utcnow() - timedelta(minutes=index + 6)))
    for index, post_id in enumerate(saved_ids, start=1):
        db.add(PostSave(id=index, post_id=post_id, user_id=1, created_at=_utcnow() - timedelta(minutes=index + 12)))

    for index, item in enumerate(comments[:24], start=1):
        if int(item["author_id"]) == 1:
            continue
        db.add(
            CommentLike(
                id=index,
                comment_id=int(item["id"]),
                user_id=1,
                created_at=_utcnow() - timedelta(minutes=index + 20),
            )
        )
    return len(liked_ids), len(saved_ids)


def _insert_notifications(db, posts: list[dict], comments: list[dict]) -> int:
    my_posts = [item for item in posts if int(item["author_id"]) == 1][:12]
    my_comments = [item for item in comments if int(item["author_id"]) == 1][:8]
    next_id = 1
    for offset, post in enumerate(my_posts, start=1):
        actor = ACTIVE_AUTHOR_IDS[offset % len(ACTIVE_AUTHOR_IDS)]
        db.add(
            MessageNotification(
                id=next_id,
                receiver_user_id=1,
                type="likes",
                source_post_id=int(post["id"]),
                source_user_id=int(actor),
                content=f"帖子赞：{str(post['title'])[:48]}",
                is_read=offset > 5,
                created_at=post["created_at"] + timedelta(hours=2),
            )
        )
        next_id += 1

    for offset, comment in enumerate(my_comments, start=1):
        actor = ACTIVE_AUTHOR_IDS[(offset + 7) % len(ACTIVE_AUTHOR_IDS)]
        body = str(comment["content"]).replace("\n", " ").strip()
        db.add(
            MessageNotification(
                id=next_id,
                receiver_user_id=1,
                type="likes",
                source_post_id=int(comment["post_id"]),
                source_user_id=int(actor),
                content=f"评论赞：{body[:48]}",
                is_read=offset > 3,
                created_at=comment["created_at"] + timedelta(hours=1),
            )
        )
        next_id += 1
    return next_id - 1


def _insert_recent_keywords(db) -> None:
    for index, keyword in enumerate(RECENT_KEYWORDS, start=1):
        db.add(
            RecentSearchKeyword(
                id=index,
                user_id=1,
                keyword=keyword,
                updated_at=_utcnow() - timedelta(minutes=index),
                created_at=_utcnow() - timedelta(minutes=index),
            )
        )


def _insert_errands(db, errands: list[dict]) -> None:
    for item in errands:
        db.add(
            ErrandTask(
                id=int(item["id"]),
                publisher_id=int(item["publisher_id"]),
                runner_id=int(item["runner_id"]) if item["runner_id"] else None,
                task_type=str(item["task_type"]),
                title=str(item["title"]),
                reward=str(item["reward"]),
                eta=str(item["eta"]),
                pickup_location=str(item["pickup_location"]),
                destination=str(item["destination"]),
                note=str(item["note"]),
                contact=str(item["contact"]),
                status=str(item["status"]),
                created_at=item["created_at"],
                accepted_at=item["accepted_at"],
                delivered_at=item["delivered_at"],
                confirmed_at=item["confirmed_at"],
                canceled_at=item["canceled_at"],
            )
        )


def seed_large_demo_data(total_posts: int = 520, total_comments: int = 860, total_errands: int = 48) -> dict[str, int]:
    bootstrap_database()
    posts = _build_posts(total_posts=total_posts)
    comments, comment_counts, adoptions = _build_comments(posts=posts, target_comments=total_comments)
    errands = _build_errands(total_errands=total_errands)

    for post in posts:
        post["comments_count"] = int(comment_counts.get(int(post["id"]), 0))

    with SessionLocal() as db:
        _reset_content(db)
        _upsert_users(db)
        _insert_posts(db, posts)
        _insert_comments(db, comments)
        _insert_adoptions(db, adoptions)
        liked_count, saved_count = _insert_likes_and_saves(db, posts, comments)
        notification_count = _insert_notifications(db, posts, comments)
        _insert_recent_keywords(db)
        _insert_errands(db, errands)
        db.commit()

    return {
        "users": len(ALL_USERS),
        "posts": len(posts),
        "comments": len(comments),
        "errands": len(errands),
        "adoptions": len(adoptions),
        "liked_posts": liked_count,
        "saved_posts": saved_count,
        "notifications": notification_count,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed large realistic campus demo data.")
    parser.add_argument("--posts", type=int, default=520)
    parser.add_argument("--comments", type=int, default=860)
    parser.add_argument("--errands", type=int, default=48)
    args = parser.parse_args()

    result = seed_large_demo_data(total_posts=args.posts, total_comments=args.comments, total_errands=args.errands)
    print(
        "seed_large_demo_data "
        f"users={result['users']} posts={result['posts']} comments={result['comments']} "
        f"errands={result['errands']} adoptions={result['adoptions']} "
        f"liked_posts={result['liked_posts']} saved_posts={result['saved_posts']} notifications={result['notifications']}"
    )


if __name__ == "__main__":
    main()
