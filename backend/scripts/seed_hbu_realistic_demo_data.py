from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from sqlalchemy import delete, func, or_, select  # noqa: E402

from app.core.database import SessionLocal  # noqa: E402
from app.core.passwords import hash_password  # noqa: E402
from app.models.comment import Comment  # noqa: E402
from app.models.comment_asset import CommentAsset  # noqa: E402
from app.models.comment_like import CommentLike  # noqa: E402
from app.models.errand_task import ErrandTask  # noqa: E402
from app.models.evolution_review import EvolutionReview  # noqa: E402
from app.models.message import MessageNotification  # noqa: E402
from app.models.post import Post  # noqa: E402
from app.models.post_adoption import PostAdoption  # noqa: E402
from app.models.post_asset import PostAsset  # noqa: E402
from app.models.post_like import PostLike  # noqa: E402
from app.models.post_save import PostSave  # noqa: E402
from app.models.recent_search import RecentSearchKeyword  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services.bootstrap_service import bootstrap_database  # noqa: E402
from app.services.post_service import is_public_feed_artifact  # noqa: E402
from app.services.user_service import user_service  # noqa: E402


SEED_PREFIX = "hbu_real_seed_"
SEED_TAG = "#HBU真实数据"
DEFAULT_POSTS = 520
DEFAULT_COMMENTS = 260
DEFAULT_ERRANDS = 90
MIN_PRIMARY_ROWS = 300
MAX_PRIMARY_ROWS = 900
CHINA_TZ = ZoneInfo("Asia/Shanghai")
DEMO_NOW_UTC_TIME = datetime.now(timezone.utc).replace(microsecond=0)
DEMO_NOW_LOCAL_TIME = DEMO_NOW_UTC_TIME.astimezone(CHINA_TZ)
DEMO_LATEST_POST_TIME = DEMO_NOW_UTC_TIME - timedelta(minutes=12)
DEMO_EARLIEST_POST_TIME = DEMO_LATEST_POST_TIME - timedelta(hours=18)
DEMO_LATEST_TASK_TIME = DEMO_NOW_UTC_TIME - timedelta(minutes=8)
DEMO_EARLIEST_TASK_TIME = DEMO_LATEST_TASK_TIME - timedelta(hours=12)
BASE_LOCAL_TIME = DEMO_EARLIEST_POST_TIME


@dataclass(frozen=True)
class SeedUser:
    username: str
    display_name: str
    nickname: str


CORE_USERS = [
    SeedUser(f"{SEED_PREFIX}service_nav", "校园服务导航员", "校园服务导航员"),
    SeedUser(f"{SEED_PREFIX}jwc_helper", "教务办理互助站", "教务办理互助站"),
    SeedUser(f"{SEED_PREFIX}lib_helper", "图书馆资源记录员", "图书馆资源记录员"),
    SeedUser(f"{SEED_PREFIX}qiyi_observer", "七一路校区观察员", "七一路校区观察员"),
    SeedUser(f"{SEED_PREFIX}wusi_observer", "五四路校区观察员", "五四路校区观察员"),
    SeedUser(f"{SEED_PREFIX}yuhua_observer", "裕华路校区观察员", "裕华路校区观察员"),
    SeedUser(f"{SEED_PREFIX}info_center", "信息化服务答疑员", "信息化服务答疑员"),
    SeedUser(f"{SEED_PREFIX}course_review", "课程评价记录员", "课程评价记录员"),
    SeedUser(f"{SEED_PREFIX}market_guard", "校园集市验机员", "校园集市验机员"),
    SeedUser(f"{SEED_PREFIX}runner_station", "校园跑腿互助站", "校园跑腿互助站"),
    SeedUser(f"{SEED_PREFIX}career_helper", "就业创新提醒员", "就业创新提醒员"),
    SeedUser(f"{SEED_PREFIX}mental_support", "心理支持小助手", "心理支持小助手"),
]

EXTRA_USERS = [
    SeedUser(
        username=f"{SEED_PREFIX}student_{index:03d}",
        display_name=f"河大同学{index:03d}",
        nickname=user_service.build_default_public_name(f"河大同学{index:03d}"),
    )
    for index in range(1, 121)
]

SEED_USERS = CORE_USERS + EXTRA_USERS

OFFICIAL_BLUEPRINTS = [
    {
        "category": "academic",
        "title": "河北大学三个校区地址一次整理",
        "content": "公开信息整理：五四路校区在保定市五四东路180号，七一路校区在保定市七一东路2666号，裕华路校区在裕华东路342号。涉及报到、办事、快递和访客预约时，先确认校区再出发。",
        "tags": ["#校区地址", "#校园服务", "#五四路校区", "#七一路校区"],
    },
    {
        "category": "academic",
        "title": "校园服务入口里哪些最常用",
        "content": "官网校园服务页集中列出统一认证、学生事务、办事大厅、财务系统、缴费平台、档案查询、后勤服务、企业微信、WEBVPN、信息化流程和密码找回。强时效事项仍以当期通知为准。",
        "tags": ["#校园服务", "#统一认证", "#办事大厅", "#WEBVPN"],
    },
    {
        "category": "academic",
        "title": "统一认证账号怎么理解更稳",
        "content": "信息技术中心指南说明，统一认证为主要业务系统提供统一账号密码服务，本科生和研究生通常以学号作为用户名。本科教务、研究生教务、WEBVPN、上网认证等都应优先走统一认证。",
        "tags": ["#统一认证", "#信息化服务", "#教务系统"],
    },
    {
        "category": "academic",
        "title": "教务系统入口建议从官网或教务处进",
        "content": "入口整理：本科教务系统可从河北大学主页教育教学入口或教务处网站进入，也可从企业微信工作台 S1 智慧教务进入。遇到补退选、成绩或考试安排，优先看系统和教务处通知。",
        "tags": ["#教务系统", "#补退选", "#考试安排"],
    },
    {
        "category": "academic",
        "title": "成绩单打印三条官方路径",
        "content": "教务处公开说明：校内学生可用校园卡到一卡通中心自助打印终端打印成绩单，也可联系学院教学秘书；校内学生和毕业生还可到五四路校区主楼603办理，线下办理需按要求带身份证件。",
        "tags": ["#成绩单", "#五四路校区", "#主楼603", "#教务处"],
    },
    {
        "category": "study",
        "title": "图书馆入口和资源入口怎么找",
        "content": "河北大学图书馆网站为 lib.hbu.cn，信息技术中心指南也列出电子资源入口。查馆藏、数据库、校外访问、共享空间预约、论文查收查引时，优先从图书馆官网进入。",
        "tags": ["#图书馆", "#电子资源", "#校外访问", "#共享空间"],
    },
    {
        "category": "study",
        "title": "校外查文献先确认 WEBVPN",
        "content": "学习提醒：校外访问校内资源时，先确认统一认证和 WEBVPN 是否可用，再进入图书馆电子资源。论文检索、数据库访问和文献传递不要只靠群里旧链接。",
        "tags": ["#WEBVPN", "#图书馆", "#文献检索"],
    },
    {
        "category": "academic",
        "title": "学生事务平台和易班的使用边界",
        "content": "信息技术中心指南提到，本科生可通过学生事务网上服务平台或易班进入学生事务服务。请假、事务办理、消息确认这类事项，建议从官方平台进入，避免错过状态回执。",
        "tags": ["#学生事务", "#易班", "#一站式服务"],
    },
    {
        "category": "academic",
        "title": "缴费相关问题先回到财务处入口",
        "content": "缴费提醒：涉及学费、住宿费和缴费记录时，优先从校园服务页的财务系统、缴费平台或财务处网站进入。具体金额、发票和欠费明细以平台显示为准。",
        "tags": ["#缴费平台", "#财务系统", "#校园服务"],
    },
    {
        "category": "academic",
        "title": "学生邮箱申请路径",
        "content": "信息技术中心学生邮箱常见问题说明，确需申请学生邮箱时，可从河北大学主页校园服务栏目进入办事大厅，找到学生电子邮箱开通申请，按要求填写并提交材料。",
        "tags": ["#学生邮箱", "#办事大厅", "#信息化服务"],
    },
    {
        "category": "academic",
        "title": "访客预约系统怎么进",
        "content": "公开说明提到，来校访客可微信搜索 HBU访客预约 小程序进入，审批通过后按要求刷身份证和人脸识别入校。接待单位要提前审核，访客也要确认到访校区。",
        "tags": ["#访客预约", "#校园安全", "#企业微信"],
    },
    {
        "category": "academic",
        "title": "学校办学规模适合怎么介绍",
        "content": "河北大学是教育部与河北省人民政府部省合建高校，学校学科覆盖12大门类。官网学校简介列有89个本科专业，信息公开网2024统计口径列有86个本科专业；涉及专业数量时建议说明统计口径并以当年公开信息为准。",
        "tags": ["#学校概况", "#学科专业", "#河北大学"],
    },
    {
        "category": "academic",
        "title": "河北大学历史沿革速记",
        "content": "学校始建于1921年，1960年改建为综合性大学并定名河北大学，1970年迁址河北省保定市。答辩介绍学校背景时，这几个节点最稳。",
        "tags": ["#学校概况", "#校史", "#河北大学"],
    },
    {
        "category": "academic",
        "title": "国际交流和 ISEC 项目该怎么查",
        "content": "公开资料显示学校与130多所高校建立合作交流关系，国际学院开展 ISEC 项目。具体招生专业、学费和交流条件要以国际学院当年招生简章为准。",
        "tags": ["#国际交流", "#ISEC", "#招生信息"],
    },
    {
        "category": "academic",
        "title": "心理支持问题不要只看经验贴",
        "content": "如果同学出现持续焦虑、失眠或明显情绪风险，优先联系辅导员、学院或学校心理健康相关支持渠道。经验贴只能帮助定位入口，不能替代专业支持。",
        "tags": ["#心理支持", "#学生发展", "#辅导员"],
    },
    {
        "category": "study",
        "title": "图书馆论文服务入口整理",
        "content": "图书馆公开服务包含科技查新、论文查收查引、博硕论文提交、文献传递和讲座培训等。写论文或做毕设时，不要只查普通网页，图书馆入口更系统。",
        "tags": ["#论文写作", "#图书馆", "#文献传递"],
    },
]

STUDY_SPACES = [
    ("七一路校区", "图书馆东侧自习区", "靠近图书馆资源入口，适合查资料和写综述"),
    ("五四路校区", "主楼周边自习区", "适合办理教务事项前后顺路学习"),
    ("裕华路校区", "教学楼公共自习区", "适合短时整理课堂笔记"),
    ("七一路校区", "A区教学楼公共区", "适合课间补作业和小组讨论"),
    ("五四路校区", "学院楼自习角", "适合找教学秘书前后核对材料"),
    ("七一路校区", "图书馆共享空间", "适合需要讨论但又不想影响他人的小组任务"),
]

COURSE_TOPICS = [
    ("软件工程导论", "平时展示和项目文档要同步准备"),
    ("数据结构", "实验和刷题最好不要分开推进"),
    ("计算机网络", "概念题和实验题都要回到课堂例题"),
    ("操作系统", "实验报告越早整理越省心"),
    ("数据库系统", "SQL 练习要跟课程设计一起看"),
    ("大学英语", "小组展示提前分工更稳"),
    ("高等数学", "补退选后跟课要先补例题"),
    ("离散数学", "证明题需要单独留复习时间"),
]

CANTEEN_TOPICS = [
    ("七一路校区", "午高峰想节省时间，建议错开12:10到12:35这段集中流量"),
    ("五四路校区", "办完教务手续后再吃饭，通常能避开一波排队"),
    ("裕华路校区", "晚课前半小时更适合买轻食，避免赶不上上课"),
    ("七一路校区", "图书馆学习日适合提前买水，晚间再出来会多走一趟"),
]

MARKET_TOPICS = [
    ("二手显示器", "先看亮点、漏光和接口，再现场接电脑试五分钟"),
    ("二手教材", "先确认版次、出版社和是否有大量划线"),
    ("机械键盘", "先问轴体和空格键手感，再看键帽磨损"),
    ("台灯", "优先选色温可调、底座稳定的款式"),
    ("路由器", "确认是否千兆口，老款双百兆口不建议高价入"),
    ("耳机", "当场听左右声道和底噪，充电仓也要试"),
]

GROUP_TOPICS = [
    ("软件测试复习资料互换", "期末重点和历年题", "实验报告模板、题型变化和复习顺序"),
    ("空教室情报互助", "三校区空位报点", "七一路、五四路、裕华路三个校区的实时空位"),
    ("课程评价共建", "选课避坑信息", "平时分、作业量、点名频率和期末体验"),
    ("考研自习打卡", "晚间学习状态", "晚间空位、插座和安静程度"),
    ("跨校竞赛组队", "项目分工招募", "算法、前端、文案和答辩分工"),
    ("毕业设计互助", "开题到答辩资料", "需求文档、系统截图、测试记录和论文图表"),
    ("英语四六级经验交换", "听力设备和报名提醒", "报名入口、考场注意事项和复习节奏"),
    ("实习材料互助", "证明材料和系统填报", "学院审核、材料归档和线上平台填报顺序"),
]

RECENT_KEYWORDS = [
    "河北大学三个校区地址",
    "五四路校区主楼603成绩单",
    "河北大学统一认证密码找回",
    "河北大学WEBVPN怎么进",
    "图书馆电子资源入口",
    "学生事务网上服务平台",
    "办事大厅学生邮箱申请",
    "校园缴费平台入口",
    "HBU访客预约小程序",
    "七一路校区图书馆共享空间",
    "软件工程导论课程评价",
    "二手显示器验机建议",
    "校园跑腿任务",
    "河北大学补退选提醒",
    "河北大学心理支持入口",
]
LEGACY_RECENT_KEYWORDS = [
    "5\u670818\u65e5\u8dd1\u817f\u4efb\u52a1",
]

ERRAND_PICKUPS = [
    "七一路校区快递柜",
    "五四路校区主楼门口",
    "裕华路校区门口",
    "七一路校区图书馆东门",
    "办事大厅材料领取点",
    "打印店门口",
]

ERRAND_DESTINATIONS = [
    "七一路校区兰芷6号楼",
    "五四路校区学院楼一层",
    "裕华路校区教学楼门口",
    "图书馆共享空间入口",
    "A区教学楼门口",
    "主楼603附近",
]

COMMENT_POOLS = {
    "academic": [
        "这个整理很实用，尤其是强时效事项一定要回到官网或系统确认。",
        "补充一下，涉及材料办理最好提前截图保存提交状态。",
        "我按这个路径找过入口，比直接翻群消息稳很多。",
        "如果是截止日前一天操作，建议至少提前半小时登录系统。",
    ],
    "study": [
        "图书馆和WEBVPN这两块确实应该放在一起看，查文献会顺很多。",
        "共享空间适合小组任务，单人复习还是找安静区更舒服。",
        "我也准备按这个路线试一下，省得临时找入口。",
        "文献传递和论文查收查引入口很容易被忽略，这条有用。",
    ],
    "canteen": [
        "错峰这个建议靠谱，赶课时最怕卡在点单环节。",
        "如果从图书馆出来，最好提前规划路线，不然来回走很耗时间。",
        "中午高峰别硬挤，晚十分钟体验会好很多。",
        "这类经验适合作为参考，具体还是看当天人流。",
    ],
    "market": [
        "线下面交一定要当场试，别只看截图和口头描述。",
        "二手教材要确认版次，这点比价格低十块更重要。",
        "显示器验机建议加一条：把亮度拉满看坏点。",
        "校园交易最好在公共区域完成，保留聊天记录。",
    ],
}


def _stable_digest(text: str) -> int:
    return int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:12], 16)


def _dedupe_ints(values: list[int]) -> list[int]:
    result: list[int] = []
    seen: set[int] = set()
    for value in values:
        safe_value = int(value or 0)
        if not safe_value or safe_value in seen:
            continue
        result.append(safe_value)
        seen.add(safe_value)
    return result


def _post_like_target(seed_score: int, offset: int, total: int) -> int:
    base = 7 + seed_score % 36
    if offset % 13 == 0:
        base += 8
    if offset >= total - 5:
        base += 26
    return min(base, 78)


def _next_id(db, model) -> int:
    current = db.scalar(select(func.max(model.id)))
    return int(current or 0) + 1


def _spread_time(index: int, total: int, start: datetime, end: datetime, second_step: int) -> datetime:
    span_seconds = max(1, int((end - start).total_seconds()))
    offset_seconds = int((index / max(1, total - 1)) * span_seconds)
    return start + timedelta(seconds=offset_seconds + (index * second_step) % 60)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _interaction_time(base_time: datetime, minutes: int) -> datetime:
    latest = DEMO_NOW_UTC_TIME - timedelta(minutes=1)
    value = _as_utc(base_time) + timedelta(minutes=minutes)
    return value if value <= latest else latest


def _seed_time(index: int, total: int) -> datetime:
    return _spread_time(index, total, DEMO_EARLIEST_POST_TIME, DEMO_LATEST_POST_TIME, 17)


def _task_time(index: int, total: int) -> datetime:
    return _spread_time(index, total, DEMO_EARLIEST_TASK_TIME, DEMO_LATEST_TASK_TIME, 11)


def _reset_previous_seed(db) -> dict[str, int]:
    seed_user_ids = list(
        db.execute(select(User.id).where(User.username.like(f"{SEED_PREFIX}%"))).scalars().all()
    )
    marker_post_ids = list(
        db.execute(select(Post.id).where(Post.tags_json.like(f"%{SEED_TAG}%"))).scalars().all()
    )
    seed_post_ids = set(marker_post_ids)
    if seed_user_ids:
        seed_post_ids.update(
            db.execute(select(Post.id).where(Post.author_id.in_(seed_user_ids))).scalars().all()
        )
    seed_post_ids_list = list(seed_post_ids)

    seed_comment_ids = set()
    if seed_post_ids_list:
        seed_comment_ids.update(
            db.execute(select(Comment.id).where(Comment.post_id.in_(seed_post_ids_list))).scalars().all()
        )
    if seed_user_ids:
        seed_comment_ids.update(
            db.execute(select(Comment.id).where(Comment.author_id.in_(seed_user_ids))).scalars().all()
        )
    seed_comment_ids_list = list(seed_comment_ids)

    deleted = {"posts": len(seed_post_ids_list), "comments": len(seed_comment_ids_list), "users": len(seed_user_ids)}

    if seed_comment_ids_list:
        db.execute(delete(CommentAsset).where(CommentAsset.comment_id.in_(seed_comment_ids_list)))
        db.execute(
            delete(CommentLike).where(
                or_(
                    CommentLike.comment_id.in_(seed_comment_ids_list),
                    CommentLike.user_id.in_(seed_user_ids or [-1]),
                )
            )
        )
        db.execute(delete(Comment).where(Comment.id.in_(seed_comment_ids_list)))

    if seed_post_ids_list:
        db.execute(delete(PostAsset).where(PostAsset.post_id.in_(seed_post_ids_list)))
        db.execute(delete(PostLike).where(PostLike.post_id.in_(seed_post_ids_list)))
        db.execute(delete(PostSave).where(PostSave.post_id.in_(seed_post_ids_list)))
        db.execute(delete(PostAdoption).where(PostAdoption.post_id.in_(seed_post_ids_list)))
        db.execute(delete(EvolutionReview).where(EvolutionReview.post_id.in_(seed_post_ids_list)))
        db.execute(delete(MessageNotification).where(MessageNotification.source_post_id.in_(seed_post_ids_list)))
        db.execute(delete(Post).where(Post.id.in_(seed_post_ids_list)))

    if seed_user_ids:
        db.execute(delete(PostLike).where(PostLike.user_id.in_(seed_user_ids)))
        db.execute(delete(PostSave).where(PostSave.user_id.in_(seed_user_ids)))
        db.execute(delete(MessageNotification).where(MessageNotification.receiver_user_id.in_(seed_user_ids)))
        db.execute(delete(MessageNotification).where(MessageNotification.source_user_id.in_(seed_user_ids)))
        db.execute(
            delete(ErrandTask).where(
                or_(
                    ErrandTask.publisher_id.in_(seed_user_ids),
                    ErrandTask.runner_id.in_(seed_user_ids),
                )
            )
        )
        db.execute(delete(User).where(User.id.in_(seed_user_ids)))

    db.execute(delete(RecentSearchKeyword).where(RecentSearchKeyword.keyword.in_(RECENT_KEYWORDS + LEGACY_RECENT_KEYWORDS)))
    return deleted


def _insert_seed_users(db) -> dict[str, int]:
    next_user_id = _next_id(db, User)
    user_map: dict[str, int] = {}
    for offset, item in enumerate(SEED_USERS):
        user_id = next_user_id + offset
        salt = f"hbu-real-seed-{offset + 1:03d}"
        db.add(
            User(
                id=user_id,
                username=item.username,
                display_name=item.display_name,
                nickname=item.nickname,
                password_hash=hash_password("demo123", salt=salt),
                password_salt=salt,
                role="client",
                status="active",
                wechat_openid=None,
                created_at=BASE_LOCAL_TIME - timedelta(days=3, minutes=offset),
            )
        )
        user_map[item.username] = user_id
    return user_map


def _author_ids(user_map: dict[str, int]) -> list[int]:
    return [user_map[item.username] for item in SEED_USERS]


def _build_official_post(index: int, author_id: int, cycle: int) -> dict:
    base = OFFICIAL_BLUEPRINTS[index % len(OFFICIAL_BLUEPRINTS)]
    suffixes = ["入口版", "办理版", "答辩演示版", "新生友好版", "避坑版", "材料核对版"]
    title = base["title"] if cycle == 0 else f"{base['title']}｜{suffixes[cycle % len(suffixes)]}"
    addition = [
        "如果信息涉及截止时间、收费金额或当年政策，仍建议回到学校官网、教务处或学院通知确认。",
        "这条适合放进校园知识库，也适合作为答辩演示时的真实公开信息样例。",
        "同学实际操作前，建议同时保存系统回执或页面截图，后续沟通更稳。",
    ][cycle % 3]
    return {
        "author_id": author_id,
        "category": base["category"],
        "title": title,
        "content": f"{base['content']} {addition}",
        "tags": [SEED_TAG, "#河北大学", *base["tags"]],
    }


def _build_study_post(index: int, author_id: int) -> dict:
    campus, place, note = STUDY_SPACES[index % len(STUDY_SPACES)]
    topic, scope, detail = GROUP_TOPICS[index % len(GROUP_TOPICS)]
    if index % 4 == 0:
        return {
            "author_id": author_id,
            "category": "study",
            "title": f"{topic}：{scope}",
            "content": f"今天继续整理 {topic}，重点是{detail}。如果你在{campus}附近学习，可以在评论里补充实时情况，后面我汇总到帖子里。",
            "tags": [SEED_TAG, "#学习互助", "#跨校小组", f"#{campus}"],
        }
    return {
        "author_id": author_id,
        "category": "study",
        "title": f"{campus}{place}学习体验：{note}",
        "content": f"学习记录：{place}更适合{note}。如果要查论文和数据库，建议提前确认图书馆官网、WEBVPN和统一认证是否正常。",
        "tags": [SEED_TAG, "#自习教室", "#图书馆", f"#{campus}"],
    }


def _build_academic_post(index: int, author_id: int) -> dict:
    course, tip = COURSE_TOPICS[index % len(COURSE_TOPICS)]
    if index % 2 == 0:
        return {
            "author_id": author_id,
            "category": "academic",
            "title": f"课程评价：{course} 补充",
            "content": f"想收集上过 {course} 的同学反馈，尤其是平时分、作业量、实验或展示占比。当前建议是：{tip}。欢迎按真实上课体验补充。",
            "tags": [SEED_TAG, "#课程评价", f"#{course}", "#选课参考"],
        }
    base = OFFICIAL_BLUEPRINTS[index % len(OFFICIAL_BLUEPRINTS)]
    return _build_official_post(index=index, author_id=author_id, cycle=index // len(OFFICIAL_BLUEPRINTS) + 1)


def _build_canteen_post(index: int, author_id: int) -> dict:
    campus, tip = CANTEEN_TOPICS[index % len(CANTEEN_TOPICS)]
    return {
        "author_id": author_id,
        "category": "canteen",
        "title": f"{campus}午晚高峰经验",
        "content": f"同学实测经验：{tip}。这类帖子只作为生活参考，不替代后勤公告；如果遇到食品安全、价格或服务问题，建议走后勤服务入口反馈。",
        "tags": [SEED_TAG, "#食堂避雷", "#生活服务", f"#{campus}"],
    }


def _build_market_post(index: int, author_id: int) -> dict:
    item, tip = MARKET_TOPICS[index % len(MARKET_TOPICS)]
    return {
        "author_id": author_id,
        "category": "market",
        "title": f"校园集市：{item}交易前先确认什么",
        "content": f"二手交易提醒：{tip}。尽量选择校内公共区域面交，保留聊天记录，不提前转大额定金。",
        "tags": [SEED_TAG, "#二手交易", "#校园集市", f"#{item}"],
    }


def _build_posts(total_posts: int, user_map: dict[str, int], primary_author_id: int | None = None) -> list[dict]:
    author_ids = _author_ids(user_map)
    posts: list[dict] = []
    builders = [_build_official_post, _build_study_post, _build_academic_post, _build_canteen_post, _build_market_post]
    curated_titles = {
        "河北大学校园服务入口总整理": (
            "academic",
            "统一认证、学生事务、办事大厅、财务系统、缴费平台、档案查询、后勤服务、企业微信、WEBVPN、信息化流程和密码找回都能从官网校园服务页统一定位。答辩演示时，这条可以体现系统把真实校园入口结构化展示出来。",
            ["#校园服务", "#统一认证", "#WEBVPN", "#办事大厅"],
        ),
        "成绩单打印办理路线": (
            "academic",
            "校内学生可用校园卡到一卡通中心自助打印，也可联系学院教学秘书；需要到教务处线下办理时，公开说明地点为五四路校区主楼603，并按要求携带身份证件或委托材料。",
            ["#成绩单", "#主楼603", "#教务处"],
        ),
        "河北大学图书馆与WEBVPN学习资源路线": (
            "study",
            "查馆藏、数据库、共享空间预约、论文查收查引和文献传递时，优先从图书馆官网与学校WEBVPN入口进入，校外访问不要只依赖群内旧链接。",
            ["#图书馆", "#WEBVPN", "#电子资源"],
        ),
        "三校区办事前先确认地址": (
            "academic",
            "五四路校区、七一路校区和裕华路校区承担的办事场景不同，去办成绩单、图书馆服务、报到或访客预约前，先确认校区和入口，能减少跑错校门的情况。",
            ["#校区地址", "#五四路校区", "#七一路校区", "#裕华路校区"],
        ),
        "课程评价共建帖": (
            "study",
            "这条集中收集课程评价：平时分、作业量、实验难度、点名频率和期末复习压力。请尽量写真实上课体验，不要只写情绪化判断。",
            ["#课程评价", "#选课参考", "#学习互助"],
        ),
    }

    normal_total = total_posts - len(curated_titles)
    for index in range(normal_total):
        author_id = author_ids[index % len(author_ids)]
        builder = builders[index % len(builders)]
        if builder is _build_official_post:
            post = builder(index, author_id, index // len(OFFICIAL_BLUEPRINTS))
        else:
            post = builder(index, author_id)
        posts.append(post)

    for title, (category, content, tags) in curated_titles.items():
        posts.append(
            {
                "author_id": int(primary_author_id or author_ids[len(posts) % len(author_ids)]),
                "category": category,
                "title": title,
                "content": content,
                "tags": [SEED_TAG, "#河北大学", *tags],
            }
        )
    return posts


def _insert_posts(db, posts: list[dict]) -> list[int]:
    next_post_id = _next_id(db, Post)
    total = len(posts)
    post_ids: list[int] = []
    for offset, post in enumerate(posts):
        post_id = next_post_id + offset
        seed_score = _stable_digest(str(post["title"]))
        likes_count = _post_like_target(seed_score, offset, total)
        row = Post(
            id=post_id,
            author_id=int(post["author_id"]),
            category=str(post["category"]),
            title=str(post["title"])[:255],
            content=str(post["content"]),
            tags_json=json.dumps(post["tags"], ensure_ascii=False),
            likes_count=int(likes_count),
            comments_count=0,
            adopted=bool(offset % 8 == 0 or offset >= total - 5),
            status="published",
            created_at=_seed_time(offset, total),
        )
        db.add(row)
        post["id"] = post_id
        post["created_at"] = row.created_at
        post["likes_count"] = row.likes_count
        post["adopted"] = row.adopted
        post_ids.append(post_id)
    return post_ids


def _insert_comments(db, posts: list[dict], user_map: dict[str, int], target_comments: int) -> list[int]:
    author_ids = _author_ids(user_map)
    next_comment_id = _next_id(db, Comment)
    comment_ids: list[int] = []
    comment_count_by_post: dict[int, int] = {}
    comment_index = 0

    selected_posts = sorted(posts, key=lambda item: int(item["likes_count"]), reverse=True)[: max(1, target_comments // 2)]
    for post in selected_posts:
        if comment_index >= target_comments:
            break
        for local_index in range(2):
            if comment_index >= target_comments:
                break
            author_id = author_ids[(int(post["id"]) + local_index + comment_index) % len(author_ids)]
            if author_id == int(post["author_id"]):
                author_id = author_ids[(local_index + comment_index + 7) % len(author_ids)]
            pool = COMMENT_POOLS.get(str(post["category"]), COMMENT_POOLS["academic"])
            content = pool[(comment_index + local_index) % len(pool)]
            comment_id = next_comment_id + comment_index
            db.add(
                Comment(
                    id=comment_id,
                    post_id=int(post["id"]),
                    author_id=int(author_id),
                    parent_comment_id=None,
                    reply_to_author_id=None,
                    reply_to_user_name=None,
                    content=content,
                    status="visible",
                    likes_count=0,
                    created_at=_interaction_time(post["created_at"], 8 + local_index * 9),
                )
            )
            comment_ids.append(comment_id)
            comment_count_by_post[int(post["id"])] = comment_count_by_post.get(int(post["id"]), 0) + 1
            comment_index += 1

    db.flush()
    for post_id, count in comment_count_by_post.items():
        row = db.get(Post, post_id)
        if row:
            row.comments_count = count
            db.add(row)
    return comment_ids


def _insert_likes_saves_notifications(
    db,
    posts: list[dict],
    comment_ids: list[int],
    user_map: dict[str, int],
) -> dict[str, int]:
    seed_user_ids = _author_ids(user_map)
    viewer_id = int(db.scalar(select(User.id).where(User.id == 1)) or seed_user_ids[0])
    liker_pool = _dedupe_ints([viewer_id, *seed_user_ids])
    top_posts = sorted(posts, key=lambda item: int(item["likes_count"]), reverse=True)
    next_like_id = _next_id(db, PostLike)
    next_save_id = _next_id(db, PostSave)
    next_comment_like_id = _next_id(db, CommentLike)
    next_message_id = _next_id(db, MessageNotification)
    db.flush()

    liked_count = 0
    saved_count = 0
    comment_like_count = 0
    notification_count = 0
    post_like_actor_map: dict[int, list[int]] = {}

    for offset, post in enumerate(top_posts):
        post_id = int(post["id"])
        author_id = int(post["author_id"])
        target_likes = min(int(post.get("likes_count") or 0), max(0, len(liker_pool) - 1))
        start = _stable_digest(f"post-like:{post_id}:{post['title']}") % max(1, len(liker_pool))
        actors: list[int] = []
        for step in range(len(liker_pool)):
            if len(actors) >= target_likes:
                break
            liker_id = liker_pool[(start + step) % len(liker_pool)]
            if int(liker_id) == author_id or int(liker_id) in actors:
                continue
            actors.append(int(liker_id))
            db.add(
                PostLike(
                    id=next_like_id + liked_count,
                    post_id=post_id,
                    user_id=int(liker_id),
                    created_at=_interaction_time(post["created_at"], 18 + len(actors)),
                )
            )
            liked_count += 1
        post_like_actor_map[post_id] = actors
        row = db.get(Post, post_id)
        if row:
            row.likes_count = len(actors)
            db.add(row)
        post["likes_count"] = len(actors)

    for offset, post in enumerate(top_posts[:96]):
        db.add(
            PostSave(
                id=next_save_id + saved_count,
                post_id=int(post["id"]),
                user_id=int(viewer_id if offset < 48 else seed_user_ids[(offset + 3) % len(seed_user_ids)]),
                created_at=_interaction_time(post["created_at"], 23),
            )
        )
        saved_count += 1

    comment_rows = (
        db.execute(select(Comment).where(Comment.id.in_(comment_ids)).order_by(Comment.id.asc())).scalars().all()
        if comment_ids
        else []
    )
    for offset, comment in enumerate(comment_rows):
        target_likes = int(_stable_digest(f"comment-like:{comment.id}") % 5)
        if offset < 48:
            target_likes = max(1, target_likes)
        actors: list[int] = []
        start = _stable_digest(f"comment-like-start:{comment.id}") % max(1, len(liker_pool))
        for step in range(len(liker_pool)):
            if len(actors) >= target_likes:
                break
            liker_id = liker_pool[(start + step) % len(liker_pool)]
            if int(liker_id) == int(comment.author_id) or int(liker_id) in actors:
                continue
            actors.append(int(liker_id))
            db.add(
                CommentLike(
                    id=next_comment_like_id + comment_like_count,
                    comment_id=int(comment.id),
                    user_id=int(liker_id),
                    created_at=_interaction_time(comment.created_at, 12 + len(actors)),
                )
            )
            comment_like_count += 1
        comment.likes_count = len(actors)
        db.add(comment)

    for offset, post in enumerate(top_posts[:24]):
        receiver_id = int(post["author_id"])
        actor_candidates = post_like_actor_map.get(int(post["id"]), [])
        actor_id = int(actor_candidates[0]) if actor_candidates else seed_user_ids[(offset + 5) % len(seed_user_ids)]
        if actor_id == receiver_id:
            actor_id = seed_user_ids[(offset + 17) % len(seed_user_ids)]
        db.add(
            MessageNotification(
                id=next_message_id + notification_count,
                receiver_user_id=receiver_id,
                type="likes",
                source_post_id=int(post["id"]),
                source_user_id=int(actor_id),
                content=f"帖子赞：{str(post['title'])[:48]}",
                is_read=offset > 6,
                created_at=_interaction_time(post["created_at"], 31),
            )
        )
        notification_count += 1

    return {
        "post_likes": liked_count,
        "post_saves": saved_count,
        "comment_likes": comment_like_count,
        "notifications": notification_count,
    }


def _insert_recent_keywords(db) -> int:
    viewer_id = int(db.scalar(select(User.id).where(User.id == 1)) or 0)
    if not viewer_id:
        return 0
    next_recent_id = _next_id(db, RecentSearchKeyword)
    for offset, keyword in enumerate(RECENT_KEYWORDS):
        db.add(
            RecentSearchKeyword(
                id=next_recent_id + offset,
                user_id=viewer_id,
                keyword=keyword,
                updated_at=DEMO_LATEST_POST_TIME - timedelta(minutes=offset * 3),
                created_at=DEMO_LATEST_POST_TIME - timedelta(minutes=offset * 3),
            )
        )
    return len(RECENT_KEYWORDS)


def _insert_errands(db, total_errands: int, user_map: dict[str, int]) -> list[int]:
    seed_user_ids = _author_ids(user_map)
    next_errand_id = _next_id(db, ErrandTask)
    statuses = ["open"] * 24 + ["inprogress"] * 14 + ["waiting_confirm"] * 10 + ["done"] * 10 + ["canceled"] * 2
    task_types = ["quick", "delivery", "print", "other"]
    titles = [
        "七一路校区快递代取",
        "五四路校区材料顺路带取",
        "裕华路校区打印件代送",
        "图书馆资料帮带到共享空间",
        "办事大厅回执帮送",
        "主楼603附近材料代交提醒",
    ]
    notes = [
        "站内私信发送取件码或材料说明，送达后拍照确认。",
        "不涉及证件原件，只帮带普通材料或学习用品。",
        "如果现场排队超过十分钟，先站内沟通再继续。",
        "按约定时间完成，遇到排队或路线变化及时站内沟通。",
    ]
    errand_ids: list[int] = []
    for offset in range(total_errands):
        created_at = _task_time(offset, total_errands)
        # Newest demo errands should be claimable, otherwise the default "待接单"
        # view looks stale even after reseeding.
        recency_rank = total_errands - 1 - offset
        status = statuses[recency_rank % len(statuses)]
        publisher_id = seed_user_ids[offset % len(seed_user_ids)]
        runner_id = None
        accepted_at = None
        delivered_at = None
        confirmed_at = None
        canceled_at = None
        if status in {"inprogress", "waiting_confirm", "done"}:
            runner_id = seed_user_ids[(offset + 11) % len(seed_user_ids)]
            if runner_id == publisher_id:
                runner_id = seed_user_ids[(offset + 13) % len(seed_user_ids)]
            accepted_at = _interaction_time(created_at, 9)
        if status in {"waiting_confirm", "done"}:
            delivered_at = _interaction_time(created_at, 37)
        if status == "done":
            confirmed_at = _interaction_time(created_at, 58)
        if status == "canceled":
            canceled_at = _interaction_time(created_at, 17)

        errand_id = next_errand_id + offset
        db.add(
            ErrandTask(
                id=errand_id,
                publisher_id=publisher_id,
                runner_id=runner_id,
                task_type=task_types[offset % len(task_types)],
                title=f"{titles[offset % len(titles)]}｜校内互助",
                reward=f"￥{4 + offset % 7}",
                eta=["15分钟内", "20分钟内", "40分钟内", "尽快"][offset % 4],
                pickup_location=ERRAND_PICKUPS[offset % len(ERRAND_PICKUPS)],
                destination=ERRAND_DESTINATIONS[(offset + 2) % len(ERRAND_DESTINATIONS)],
                note=notes[offset % len(notes)],
                contact=f"站内私信 @{SEED_USERS[offset % len(SEED_USERS)].nickname}",
                status=status,
                created_at=created_at,
                accepted_at=accepted_at,
                delivered_at=delivered_at,
                confirmed_at=confirmed_at,
                canceled_at=canceled_at,
            )
        )
        errand_ids.append(errand_id)
    return errand_ids


def _summarize(db, user_map: dict[str, int], post_ids: list[int], errand_ids: list[int]) -> dict[str, object]:
    category_rows = db.execute(
        select(Post.category, func.count()).where(Post.id.in_(post_ids)).group_by(Post.category)
    ).all()
    status_rows = db.execute(
        select(ErrandTask.status, func.count()).where(ErrandTask.id.in_(errand_ids)).group_by(ErrandTask.status)
    ).all()
    comment_count = int(db.scalar(select(func.count()).select_from(Comment).where(Comment.post_id.in_(post_ids))) or 0)
    return {
        "seed_users": len(user_map),
        "posts": len(post_ids),
        "comments": comment_count,
        "errands": len(errand_ids),
        "primary_rows": len(post_ids) + len(errand_ids) + comment_count,
        "post_categories": {str(key): int(value) for key, value in category_rows},
        "errand_statuses": {str(key): int(value) for key, value in status_rows},
    }


def _hide_obvious_public_artifacts(db) -> int:
    rows = (
        db.execute(
            select(Post, User)
            .join(User, User.id == Post.author_id)
            .where(Post.status == "published")
        )
        .all()
    )
    hidden = 0
    for post, user in rows:
        if str(user.username or "").startswith(SEED_PREFIX):
            continue
        if not is_public_feed_artifact(post, author_username=user.username, author_name=user_service.get_public_name(user)):
            continue
        post.status = "hidden"
        db.add(post)
        hidden += 1
    return hidden


def seed_hbu_realistic_demo_data(
    total_posts: int = DEFAULT_POSTS,
    total_comments: int = DEFAULT_COMMENTS,
    total_errands: int = DEFAULT_ERRANDS,
) -> dict[str, object]:
    primary_rows = total_posts + total_comments + total_errands
    if primary_rows < MIN_PRIMARY_ROWS or primary_rows > MAX_PRIMARY_ROWS:
        raise ValueError(f"primary content rows must be {MIN_PRIMARY_ROWS}-{MAX_PRIMARY_ROWS}, got {primary_rows}")

    bootstrap_database()
    with SessionLocal() as db:
        hidden_public_artifacts = _hide_obvious_public_artifacts(db)
        deleted = _reset_previous_seed(db)
        user_map = _insert_seed_users(db)
        primary_author_id = int(db.scalar(select(User.id).where(User.id == 1)) or 0) or None
        posts = _build_posts(total_posts=total_posts, user_map=user_map, primary_author_id=primary_author_id)
        post_ids = _insert_posts(db, posts)
        comment_ids = _insert_comments(db, posts, user_map=user_map, target_comments=total_comments)
        interaction_counts = _insert_likes_saves_notifications(db, posts, comment_ids, user_map=user_map)
        recent_count = _insert_recent_keywords(db)
        errand_ids = _insert_errands(db, total_errands=total_errands, user_map=user_map)
        db.commit()

        summary = _summarize(db, user_map=user_map, post_ids=post_ids, errand_ids=errand_ids)
        summary["deleted_previous_seed"] = deleted
        summary["hidden_public_artifacts"] = hidden_public_artifacts
        summary["recent_keywords"] = recent_count
        summary.update(interaction_counts)
        summary["visible_date_policy"] = "no explicit date in generated titles or bodies"
        summary["time_window"] = {
            "earliest_post_at": DEMO_EARLIEST_POST_TIME.isoformat(),
            "latest_post_at": DEMO_LATEST_POST_TIME.isoformat(),
            "earliest_errand_at": DEMO_EARLIEST_TASK_TIME.isoformat(),
            "latest_errand_at": DEMO_LATEST_TASK_TIME.isoformat(),
            "generated_at": DEMO_NOW_LOCAL_TIME.isoformat(),
        }
        summary["seed_prefix"] = SEED_PREFIX
        return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed 500+ HBU realistic public-fact campus demo content rows."
    )
    parser.add_argument("--posts", type=int, default=DEFAULT_POSTS)
    parser.add_argument("--comments", type=int, default=DEFAULT_COMMENTS)
    parser.add_argument("--errands", type=int, default=DEFAULT_ERRANDS)
    args = parser.parse_args()

    result = seed_hbu_realistic_demo_data(
        total_posts=args.posts,
        total_comments=args.comments,
        total_errands=args.errands,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
