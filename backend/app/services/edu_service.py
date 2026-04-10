from __future__ import annotations

from copy import deepcopy


TERM_ORDER = [
    "2025-2026秋学期",
    "2024-2025春学期",
    "2024-2025秋学期",
    "2023-2024春学期",
    "2023-2024秋学期",
    "2022-2023春学期",
    "2022-2023秋学期",
]
CURRENT_TERM = TERM_ORDER[0]
CURRENT_WEEK = 1
TOTAL_WEEKS = 18
DEFAULT_CAMPUS = "七一路校区"

TERM_GRADES = {
    "2025-2026秋学期": [
        {"course_name": "中华民族共同体概论", "credit": 2.0, "grade_point": 4.5, "score": 90, "status": "passed"},
        {"course_name": "形势与政策7", "credit": 0.3, "grade_point": 5.0, "score": 97, "status": "passed"},
        {"course_name": "软件测试实验", "credit": 1.0, "grade_point": 3.8, "score": 83, "status": "passed"},
        {"course_name": "软件测试", "credit": 2.0, "grade_point": 3.5, "score": 80, "status": "passed"},
        {"course_name": "软件项目管理", "credit": 2.0, "grade_point": 4.0, "score": 85, "status": "passed"},
        {"course_name": "数据库系统原理", "credit": 3.0, "grade_point": 3.7, "score": 82, "status": "passed"},
        {"course_name": "软件工程经济学", "credit": 2.0, "grade_point": 3.3, "score": 78, "status": "passed"},
        {"course_name": "学科前沿讲座", "credit": 1.0, "grade_point": 3.1, "score": 76, "status": "passed"},
        {"course_name": "实习实训", "credit": 4.0, "grade_point": 3.9, "score": 84, "status": "passed"},
        {"course_name": "人机交互与可视化技术", "credit": 3.0, "grade_point": 4.2, "score": 88, "status": "passed"},
        {"course_name": "软件质量保证", "credit": 2.7, "grade_point": 3.2, "score": 77, "status": "passed"},
        {"course_name": "职业发展与创新实践", "credit": 2.0, "grade_point": 4.0, "score": 85, "status": "passed"},
    ],
    "2024-2025春学期": [
        {"course_name": "操作系统", "credit": 4.0, "grade_point": 3.8, "score": 84, "status": "passed"},
        {"course_name": "计算机网络", "credit": 3.5, "grade_point": 3.7, "score": 82, "status": "passed"},
        {"course_name": "编译原理", "credit": 3.0, "grade_point": 3.3, "score": 78, "status": "passed"},
        {"course_name": "软件需求工程", "credit": 2.0, "grade_point": 4.1, "score": 86, "status": "passed"},
        {"course_name": "软件体系结构", "credit": 2.5, "grade_point": 3.6, "score": 81, "status": "passed"},
        {"course_name": "数字图像处理", "credit": 2.0, "grade_point": 3.4, "score": 79, "status": "passed"},
        {"course_name": "毛泽东思想和中国特色社会主义理论体系概论", "credit": 3.0, "grade_point": 4.0, "score": 85, "status": "passed"},
        {"course_name": "体育4", "credit": 1.0, "grade_point": 4.5, "score": 90, "status": "passed"},
        {"course_name": "专业英语", "credit": 2.0, "grade_point": 3.8, "score": 84, "status": "passed"},
    ],
    "2024-2025秋学期": [
        {"course_name": "数据结构", "credit": 4.0, "grade_point": 4.0, "score": 85, "status": "passed"},
        {"course_name": "算法设计与分析", "credit": 3.0, "grade_point": 3.9, "score": 84, "status": "passed"},
        {"course_name": "计算机组成原理", "credit": 3.5, "grade_point": 3.5, "score": 80, "status": "passed"},
        {"course_name": "Java 程序设计", "credit": 3.0, "grade_point": 4.3, "score": 89, "status": "passed"},
        {"course_name": "数据库原理", "credit": 3.0, "grade_point": 3.6, "score": 81, "status": "passed"},
        {"course_name": "概率论与数理统计", "credit": 3.0, "grade_point": 3.2, "score": 77, "status": "passed"},
        {"course_name": "大学物理A", "credit": 3.5, "grade_point": 3.4, "score": 79, "status": "passed"},
        {"course_name": "体育3", "credit": 1.0, "grade_point": 4.0, "score": 85, "status": "passed"},
        {"course_name": "软件工程导论", "credit": 2.6, "grade_point": 4.1, "score": 86, "status": "passed"},
    ],
    "2023-2024春学期": [
        {"course_name": "离散数学", "credit": 3.0, "grade_point": 4.2, "score": 88, "status": "passed"},
        {"course_name": "线性代数", "credit": 3.0, "grade_point": 3.7, "score": 82, "status": "passed"},
        {"course_name": "面向对象程序设计", "credit": 3.5, "grade_point": 4.0, "score": 85, "status": "passed"},
        {"course_name": "数字逻辑", "credit": 2.5, "grade_point": 3.3, "score": 78, "status": "passed"},
        {"course_name": "大学英语2", "credit": 3.0, "grade_point": 3.9, "score": 84, "status": "passed"},
        {"course_name": "高等数学A2", "credit": 5.0, "grade_point": 3.5, "score": 80, "status": "passed"},
        {"course_name": "中国近现代史纲要", "credit": 3.0, "grade_point": 4.1, "score": 86, "status": "passed"},
        {"course_name": "体育2", "credit": 1.0, "grade_point": 4.2, "score": 88, "status": "passed"},
        {"course_name": "创新创业基础", "credit": 0.4, "grade_point": 4.0, "score": 85, "status": "passed"},
    ],
    "2023-2024秋学期": [
        {"course_name": "高等数学A1", "credit": 5.0, "grade_point": 3.9, "score": 84, "status": "passed"},
        {"course_name": "大学英语1", "credit": 3.0, "grade_point": 3.7, "score": 82, "status": "passed"},
        {"course_name": "C语言程序设计", "credit": 4.0, "grade_point": 4.1, "score": 86, "status": "passed"},
        {"course_name": "程序设计实践", "credit": 2.5, "grade_point": 4.0, "score": 85, "status": "passed"},
        {"course_name": "思想道德与法治", "credit": 3.0, "grade_point": 4.4, "score": 89, "status": "passed"},
        {"course_name": "军事理论", "credit": 2.0, "grade_point": 4.1, "score": 86, "status": "passed"},
        {"course_name": "体育1", "credit": 1.0, "grade_point": 4.3, "score": 89, "status": "passed"},
        {"course_name": "大学计算机基础", "credit": 3.2, "grade_point": 4.0, "score": 85, "status": "passed"},
    ],
    "2022-2023春学期": [
        {"course_name": "工程数学", "credit": 3.0, "grade_point": 3.4, "score": 79, "status": "passed"},
        {"course_name": "Web前端技术基础", "credit": 2.5, "grade_point": 4.2, "score": 88, "status": "passed"},
        {"course_name": "Python程序设计", "credit": 3.0, "grade_point": 4.0, "score": 85, "status": "passed"},
        {"course_name": "大学生心理健康教育", "credit": 2.0, "grade_point": 4.3, "score": 89, "status": "passed"},
        {"course_name": "信息检索与利用", "credit": 1.5, "grade_point": 4.1, "score": 86, "status": "passed"},
        {"course_name": "工程训练", "credit": 2.0, "grade_point": 3.7, "score": 82, "status": "passed"},
        {"course_name": "大学物理实验", "credit": 1.0, "grade_point": 3.9, "score": 84, "status": "passed"},
        {"course_name": "劳动教育", "credit": 1.0, "grade_point": 4.5, "score": 90, "status": "passed"},
        {"course_name": "职业生涯规划", "credit": 1.2, "grade_point": 4.0, "score": 85, "status": "passed"},
        {"course_name": "工程伦理", "credit": 1.5, "grade_point": 3.8, "score": 84, "status": "passed"},
        {"course_name": "公共艺术鉴赏", "credit": 1.4, "grade_point": 4.2, "score": 88, "status": "passed"},
        {"course_name": "志愿服务实践", "credit": 1.0, "grade_point": 4.0, "score": 85, "status": "passed"},
    ],
    "2022-2023秋学期": [
        {"course_name": "大学语文", "credit": 2.0, "grade_point": 4.2, "score": 88, "status": "passed"},
        {"course_name": "形势与政策1", "credit": 0.3, "grade_point": 4.5, "score": 90, "status": "passed"},
        {"course_name": "大学英语写作", "credit": 1.5, "grade_point": 3.7, "score": 82, "status": "passed"},
        {"course_name": "马克思主义基本原理", "credit": 3.0, "grade_point": 3.6, "score": 81, "status": "passed"},
        {"course_name": "新生研讨课", "credit": 1.0, "grade_point": 4.1, "score": 86, "status": "passed"},
        {"course_name": "信息素养训练", "credit": 1.0, "grade_point": 4.0, "score": 85, "status": "passed"},
        {"course_name": "校史与大学文化", "credit": 1.0, "grade_point": 4.4, "score": 89, "status": "passed"},
        {"course_name": "大学生安全教育", "credit": 1.0, "grade_point": 4.5, "score": 90, "status": "passed"},
        {"course_name": "羽毛球基础", "credit": 1.0, "grade_point": 4.0, "score": 85, "status": "passed"},
        {"course_name": "普通话训练", "credit": 1.0, "grade_point": 4.2, "score": 88, "status": "passed"},
        {"course_name": "志愿服务导论", "credit": 1.0, "grade_point": 4.0, "score": 85, "status": "passed"},
        {"course_name": "社会实践基础", "credit": 0.0, "grade_point": 0.0, "score": 0, "status": "waived"},
    ],
}

SCHEDULE_TEMPLATES = [
    {
        "course_name": "软件项目管理",
        "weekday": 1,
        "section": 1,
        "section_span": 2,
        "location": "A4-606",
        "teacher": "李老师",
        "start_week": 1,
        "end_week": 16,
        "week_mode": "all",
    },
    {
        "course_name": "数据库系统原理",
        "weekday": 2,
        "section": 3,
        "section_span": 2,
        "location": "A2-208",
        "teacher": "王老师",
        "start_week": 1,
        "end_week": 16,
        "week_mode": "all",
    },
    {
        "course_name": "形势与政策7",
        "weekday": 2,
        "section": 7,
        "section_span": 2,
        "location": "A6-201",
        "teacher": "周老师",
        "start_week": 1,
        "end_week": 8,
        "week_mode": "all",
    },
    {
        "course_name": "人机交互与可视化技术",
        "weekday": 3,
        "section": 5,
        "section_span": 2,
        "location": "A1-407",
        "teacher": "刘老师",
        "start_week": 1,
        "end_week": 16,
        "week_mode": "all",
    },
    {
        "course_name": "软件测试",
        "weekday": 4,
        "section": 1,
        "section_span": 2,
        "location": "A1-307",
        "teacher": "赵老师",
        "start_week": 1,
        "end_week": 16,
        "week_mode": "all",
    },
    {
        "course_name": "实习实训",
        "weekday": 4,
        "section": 7,
        "section_span": 2,
        "location": "A4-305实验室",
        "teacher": "孙老师",
        "start_week": 9,
        "end_week": 16,
        "week_mode": "all",
    },
    {
        "course_name": "软件工程经济学",
        "weekday": 5,
        "section": 3,
        "section_span": 2,
        "location": "A5-203",
        "teacher": "陈老师",
        "start_week": 1,
        "end_week": 16,
        "week_mode": "all",
    },
    {
        "course_name": "学科前沿讲座",
        "weekday": 5,
        "section": 9,
        "section_span": 2,
        "location": "A1-101",
        "teacher": "学院报告厅",
        "start_week": 1,
        "end_week": 18,
        "week_mode": "odd",
    },
]

EXAM_ITEMS = [
    {
        "course_name": "软件项目管理",
        "exam_type": "第20周周末考试",
        "term": CURRENT_TERM,
        "exam_date": "2026-07-08",
        "exam_time": "10:00-11:30",
        "exam_location": "七一路校区A4座606教室",
        "exam_status": "upcoming",
    },
    {
        "course_name": "人机交互与可视化技术",
        "exam_type": "第20周周末考试",
        "term": CURRENT_TERM,
        "exam_date": "2026-07-09",
        "exam_time": "10:00-11:30",
        "exam_location": "七一路校区A1座407教室",
        "exam_status": "upcoming",
    },
    {
        "course_name": "软件测试",
        "exam_type": "课程考核",
        "term": CURRENT_TERM,
        "exam_date": "2026-07-10",
        "exam_time": "08:30-10:00",
        "exam_location": "七一路校区A1座307教室",
        "exam_status": "upcoming",
    },
    {
        "course_name": "软件测试实验",
        "exam_type": "实验考核",
        "term": CURRENT_TERM,
        "exam_date": "2026-06-28",
        "exam_time": "14:00-15:30",
        "exam_location": "七一路校区A4座305实验室",
        "exam_status": "finished",
    },
]

CLASSROOM_BLUEPRINT = {
    "七一路校区": {
        "A1座": [("101", 28, False), ("104", 24, False), ("203", 16, True), ("307", 18, True), ("407", 26, False)],
        "A2座": [("101", 22, False), ("103", 18, True), ("104", 25, False), ("201", 21, False), ("203", 12, True), ("208", 15, True)],
        "A3座": [("101", 34, False), ("202", 27, False), ("205", 20, True), ("301", 24, False)],
        "A4座": [("203", 12, True), ("301", 18, True), ("307", 20, True), ("310", 24, False), ("410", 33, False), ("603", 22, False), ("606", 16, True)],
        "A5座": [("102", 19, True), ("203", 20, True), ("306", 27, False), ("502", 29, False), ("603", 28, False)],
        "A6座": [("101", 26, False), ("201", 18, True), ("302", 23, False), ("406", 17, True)],
    },
    "五四路校区": {
        "第一教学楼": [("101", 27, False), ("105", 26, False), ("203", 19, True), ("305", 22, False)],
        "第七教学楼": [("101", 21, False), ("201", 18, True), ("303", 17, True), ("405", 28, False)],
        "第八教学楼": [("102", 19, True), ("205", 14, True), ("301", 23, False), ("403", 15, True)],
        "第九教学楼": [("103", 24, False), ("204", 31, False), ("302", 29, False), ("406", 18, True)],
        "综合教学楼": [("201", 20, True), ("304", 26, False), ("407", 24, False), ("504", 22, False)],
    },
    "裕华路校区": {
        "综合楼": [("103", 25, False), ("206", 24, False), ("305", 18, True), ("402", 20, True)],
        "医学教学楼": [("101", 22, False), ("202", 18, True), ("305", 17, True), ("406", 27, False)],
        "公共教学楼": [("102", 26, False), ("204", 23, False), ("301", 19, True), ("402", 27, False)],
        "基础实验楼": [("108", 35, False), ("203", 28, False), ("304", 21, False), ("408", 18, True)],
    },
}


def _expand_classrooms() -> dict[str, dict[str, list[dict]]]:
    expanded: dict[str, dict[str, list[dict]]] = {}
    for campus, buildings in CLASSROOM_BLUEPRINT.items():
        expanded[campus] = {}
        for building, rooms in buildings.items():
            expanded[campus][building] = [
                {
                    "building": building,
                    "room": room,
                    "idle_percent": idle_percent,
                    "campus": campus,
                    "recommended": recommended,
                }
                for room, idle_percent, recommended in rooms
            ]
    return expanded


FREE_CLASSROOMS = _expand_classrooms()

OVERVIEW = {
    "student_name": "赵毅",
    "student_id": "20222605045",
    "total_score": 167.6,
    "gpa": 3.35,
    "passed_courses": 46,
    "failed_courses": 0,
    "retake_courses": 0,
    "term": CURRENT_TERM,
    "available_terms": TERM_ORDER,
    "current_week": CURRENT_WEEK,
    "total_weeks": TOTAL_WEEKS,
    "campuses": list(FREE_CLASSROOMS.keys()),
}


def _calc_term_summary(items: list[dict]) -> dict:
    credits = round(sum(float(item.get("credit") or 0.0) for item in items), 1)
    weighted_points = sum(float(item.get("credit") or 0.0) * float(item.get("grade_point") or 0.0) for item in items)
    term_gpa = round(weighted_points / credits, 2) if credits > 0 else 0.0
    passed_count = sum(1 for item in items if str(item.get("status", "")).lower() == "passed")
    pending_count = len(items) - passed_count
    return {
        "term_credit": credits,
        "term_gpa": term_gpa,
        "passed_count": passed_count,
        "pending_count": pending_count,
    }


def _matches_week(template: dict, week_no: int) -> bool:
    start_week = int(template.get("start_week") or 1)
    end_week = int(template.get("end_week") or TOTAL_WEEKS)
    if week_no < start_week or week_no > end_week:
        return False
    week_mode = str(template.get("week_mode") or "all").lower()
    if week_mode == "odd":
        return week_no % 2 == 1
    if week_mode == "even":
        return week_no % 2 == 0
    return True


def _format_weeks_label(template: dict) -> str:
    start_week = int(template.get("start_week") or 1)
    end_week = int(template.get("end_week") or TOTAL_WEEKS)
    week_mode = str(template.get("week_mode") or "all").lower()
    suffix = ""
    if week_mode == "odd":
        suffix = "单周"
    elif week_mode == "even":
        suffix = "双周"
    return f"{start_week}-{end_week}周{suffix}"


def _schedule_items_for_week(week_no: int) -> list[dict]:
    items: list[dict] = []
    for template in SCHEDULE_TEMPLATES:
        if not _matches_week(template, week_no):
            continue
        item = deepcopy(template)
        item.pop("start_week", None)
        item.pop("end_week", None)
        item.pop("week_mode", None)
        item["weeks"] = _format_weeks_label(template)
        items.append(item)
    items.sort(key=lambda row: (int(row.get("weekday") or 0), int(row.get("section") or 0), str(row.get("location") or "")))
    return items


def _room_sort_key(room: dict) -> tuple[int, str]:
    room_no = str(room.get("room") or "")
    digits = "".join(ch for ch in room_no if ch.isdigit())
    return (int(digits or 0), room_no)


class EduService:
    def overview(self) -> dict:
        return deepcopy(OVERVIEW)

    def grades(self, term: str | None = None) -> dict:
        safe_term = term if term in TERM_GRADES else CURRENT_TERM
        items = deepcopy(TERM_GRADES[safe_term])
        return {
            "term": safe_term,
            "terms": deepcopy(TERM_ORDER),
            **_calc_term_summary(items),
            "items": items,
        }

    def exams(self) -> dict:
        return {"items": deepcopy(EXAM_ITEMS)}

    def schedule(self, week_no: int = CURRENT_WEEK) -> dict:
        safe_week = max(1, min(TOTAL_WEEKS, int(week_no or CURRENT_WEEK)))
        return {
            "term": CURRENT_TERM,
            "week_no": safe_week,
            "weeks": list(range(1, TOTAL_WEEKS + 1)),
            "items": _schedule_items_for_week(safe_week),
        }

    def free_classrooms(self, campus: str = DEFAULT_CAMPUS, building: str | None = None) -> dict:
        safe_campus = campus if campus in FREE_CLASSROOMS else DEFAULT_CAMPUS
        building_map = FREE_CLASSROOMS[safe_campus]
        buildings = list(building_map.keys())
        safe_building = building if building in building_map else ""
        selected_items = (
            deepcopy(building_map[safe_building])
            if safe_building
            else [deepcopy(item) for name in buildings for item in building_map[name]]
        )
        selected_items.sort(key=lambda row: (str(row.get("building") or ""), *_room_sort_key(row)))
        return {
            "campus": safe_campus,
            "campuses": list(FREE_CLASSROOMS.keys()),
            "building": safe_building,
            "buildings": deepcopy(buildings),
            "items": selected_items,
        }


edu_service = EduService()
