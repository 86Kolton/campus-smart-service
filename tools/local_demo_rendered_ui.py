from __future__ import annotations

import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont


LOGICAL_WIDTH = 1450
LOGICAL_HEIGHT = 860
UI_ZOOM = 1.09
WIDTH = int(LOGICAL_WIDTH * UI_ZOOM)
HEIGHT = int(LOGICAL_HEIGHT * UI_ZOOM)
SCALE = 2

PALETTE = {
    "bg": "#f7fbff",
    "titlebar": "#fbfdff",
    "ink": "#071832",
    "muted": "#687a99",
    "subtle": "#93a6c2",
    "line": "#dbe9fb",
    "line2": "#edf5ff",
    "primary": "#1769ff",
    "primary2": "#2f8cff",
    "blue": "#2369f4",
    "green": "#0aa86e",
    "green_soft": "#ddf7ec",
    "purple": "#7c3aed",
    "warn": "#b75a00",
    "warn_soft": "#fff3d9",
    "danger": "#b42318",
    "danger_soft": "#ffe7e2",
    "white": "#ffffff",
}


def _font_path(*names: str) -> str | None:
    font_dir = Path(r"C:\Windows\Fonts")
    for name in names:
        path = font_dir / name
        if path.exists():
            return str(path)
    return None


FONT_REGULAR = _font_path("msyh.ttc", "segoeui.ttf")
FONT_BOLD = _font_path("msyhbd.ttc", "seguisb.ttf", "msyh.ttc")
FONT_UI = _font_path("segoeui.ttf", "msyh.ttc")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if bold else FONT_REGULAR
    if path:
        return ImageFont.truetype(path, size * SCALE)
    return ImageFont.load_default(size * SCALE)


def ui_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if bold else FONT_UI
    if path:
        return ImageFont.truetype(path, size * SCALE)
    return ImageFont.load_default(size * SCALE)


def sc_rect(rect: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return tuple(int(v * SCALE) for v in rect)  # type: ignore[return-value]


def sc_xy(x: int, y: int) -> tuple[int, int]:
    return x * SCALE, y * SCALE


def text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, size: int, fill: str, bold: bool = False, anchor: str = "la") -> None:
    draw.text(sc_xy(*xy), value, font=font(size, bold), fill=fill, anchor=anchor)


def rounded(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], radius: int, fill: str, outline: str | None = None, width: int = 1) -> None:
    draw.rounded_rectangle(sc_rect(rect), radius=radius * SCALE, fill=fill, outline=outline, width=width * SCALE)


def shadowed(base: Image.Image, rect: tuple[int, int, int, int], radius: int, fill: str, outline: str = "#dbe9fb", blur: int = 10, offset: tuple[int, int] = (0, 5)) -> ImageDraw.ImageDraw:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    ox, oy = offset
    sd.rounded_rectangle(sc_rect((rect[0] + ox, rect[1] + oy, rect[2] + ox, rect[3] + oy)), radius=radius * SCALE, fill=(185, 205, 230, 70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur * SCALE))
    base.alpha_composite(shadow)
    draw = ImageDraw.Draw(base)
    rounded(draw, rect, radius, fill, outline, 1)
    return draw


def circle(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, fill: str, outline: str | None = None, width: int = 1) -> None:
    draw.ellipse(sc_rect((cx - r, cy - r, cx + r, cy + r)), fill=fill, outline=outline, width=width * SCALE)


def line(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], fill: str, width: int = 1) -> None:
    draw.line([(x * SCALE, y * SCALE) for x, y in points], fill=fill, width=width * SCALE, joint="curve")


def polygon(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], fill: str, outline: str | None = None) -> None:
    draw.polygon([(x * SCALE, y * SCALE) for x, y in points], fill=fill, outline=outline)


def draw_logo(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int = 16) -> None:
    circle(draw, cx, cy, r, PALETTE["primary"], "#0f55df")
    polygon(draw, [(cx - 8, cy + 10), (cx + 5, cy - 12), (cx + 13, cy - 16), (cx + 8, cy - 5), (cx - 4, cy + 9)], PALETTE["white"])
    circle(draw, cx + 4, cy - 7, 3, "#dcecff")
    polygon(draw, [(cx - 5, cy + 8), (cx - 13, cy + 13), (cx - 9, cy + 2)], "#cfe1ff")


def draw_shield(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int, accent: str = "#2369f4") -> None:
    pts = [(cx, cy - size), (cx + size, cy - size // 2), (cx + size - 5, cy + size // 2), (cx, cy + size), (cx - size + 5, cy + size // 2), (cx - size, cy - size // 2)]
    polygon(draw, pts, "#dcecff", accent)
    line(draw, [(cx - 8, cy + 1), (cx - 1, cy + 10), (cx + 12, cy - 10)], accent, 3)


def draw_users(draw: ImageDraw.ImageDraw, cx: int, cy: int, accent: str) -> None:
    circle(draw, cx - 10, cy - 9, 7, accent)
    circle(draw, cx + 8, cy - 9, 7, accent)
    draw.ellipse(sc_rect((cx - 25, cy, cx + 3, cy + 22)), fill=accent)
    draw.ellipse(sc_rect((cx - 5, cy, cx + 25, cy + 22)), fill=accent)


def draw_server(draw: ImageDraw.ImageDraw, cx: int, cy: int, accent: str) -> None:
    for yy in (cy - 17, cy + 4):
        rounded(draw, (cx - 28, yy, cx + 28, yy + 16), 4, accent)
        circle(draw, cx - 19, yy + 8, 3, "#dff7ee")
        line(draw, [(cx - 5, yy + 8), (cx + 18, yy + 8)], "#dff7ee", 2)


def draw_doc(draw: ImageDraw.ImageDraw, cx: int, cy: int, accent: str) -> None:
    rounded(draw, (cx - 13, cy - 20, cx + 13, cy + 20), 3, accent)
    line(draw, [(cx - 5, cy - 8), (cx + 6, cy - 8)], PALETTE["white"], 2)
    line(draw, [(cx - 5, cy + 1), (cx + 7, cy + 1)], PALETTE["white"], 2)


def draw_monitor(draw: ImageDraw.ImageDraw, cx: int, cy: int, accent: str) -> None:
    rounded(draw, (cx - 30, cy - 24, cx + 30, cy + 20), 5, accent)
    rounded(draw, (cx - 20, cy - 13, cx + 20, cy + 9), 2, PALETTE["white"])
    draw.rectangle(sc_rect((cx - 7, cy + 20, cx + 7, cy + 34)), fill=accent)
    rounded(draw, (cx - 23, cy + 34, cx + 23, cy + 40), 2, accent)


def draw_database(draw: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    accent = "#059669"
    draw.ellipse(sc_rect((cx - 30, cy - 30, cx + 30, cy - 8)), fill="#8cf0bc", outline=accent, width=2 * SCALE)
    draw.rectangle(sc_rect((cx - 30, cy - 19, cx + 30, cy + 28)), fill="#b9f6d1", outline=accent, width=2 * SCALE)
    draw.ellipse(sc_rect((cx - 30, cy + 15, cx + 30, cy + 38)), fill="#8cf0bc", outline=accent, width=2 * SCALE)
    draw.arc(sc_rect((cx - 30, cy - 2, cx + 30, cy + 22)), 0, 180, fill=accent, width=2 * SCALE)


def draw_python(draw: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    draw.ellipse(sc_rect((cx - 34, cy - 34, cx + 8, cy + 8)), fill="#2369f4")
    draw.ellipse(sc_rect((cx - 8, cy - 8, cx + 34, cy + 34)), fill="#facc15")
    rounded(draw, (cx - 17, cy - 17, cx + 18, cy + 18), 3, PALETTE["white"])


def draw_rocket(draw: ImageDraw.ImageDraw, cx: int, cy: int, accent: str) -> None:
    polygon(draw, [(cx - 15, cy + 27), (cx + 11, cy - 24), (cx + 31, cy - 34), (cx + 22, cy - 9), (cx - 4, cy + 21)], accent)
    circle(draw, cx + 8, cy - 16, 6, "#dcecff")
    polygon(draw, [(cx - 12, cy + 22), (cx - 34, cy + 34), (cx - 22, cy + 9)], "#dcecff")


def status_style(snapshot: dict[str, bool], key: str) -> tuple[bool, str, str]:
    if key == "backend":
        ok = bool(snapshot.get("backend"))
        return ok, "正常" if ok else "未启动", "服务已就绪，监听端口 8000" if ok else "等待启动"
    if key == "frontend":
        ok = bool(snapshot.get("frontend"))
        return ok, "正常" if ok else "未启动", "页面已就绪，访问 localhost:5173" if ok else "等待启动"
    if key == "db":
        ok = bool(snapshot.get("db"))
        return ok, "已就绪" if ok else "缺失", "本地数据库连接正常" if ok else "请检查 campus.db"
    ok = bool(snapshot.get("python"))
    return ok, "已就绪" if ok else "缺失", "Python 环境可用" if ok else "请检查 .venv"


def draw_pill_status(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], ok: bool, label: str) -> None:
    fill = PALETTE["green_soft"] if ok else PALETTE["warn_soft"]
    fg = PALETTE["green"] if ok else PALETTE["warn"]
    rounded(draw, rect, 18, fill)
    circle(draw, rect[0] + 18, (rect[1] + rect[3]) // 2, 4, fg)
    text(draw, (rect[0] + 32, rect[1] + 7), label, 14, fg, True)


def draw_top_pill(base: Image.Image, rect: tuple[int, int, int, int], icon: str, label: str, accent: str) -> None:
    draw = shadowed(base, rect, 12, PALETTE["white"], PALETTE["line"], 6, (0, 4))
    cx = rect[0] + 45
    cy = (rect[1] + rect[3]) // 2
    circle(draw, cx, cy, 19, "#eaf3ff")
    if icon == "shield":
        draw_shield(draw, cx, cy, 16, accent)
    elif icon == "users":
        draw_users(draw, cx, cy, accent)
    elif icon == "server":
        draw_server(draw, cx, cy, accent)
    else:
        draw_doc(draw, cx, cy, accent)
    text(draw, (rect[0] + 78, rect[1] + 23), label, 16, PALETTE["ink"], True)


def draw_hero_art(base: Image.Image) -> None:
    draw = ImageDraw.Draw(base)
    draw.ellipse(sc_rect((1048, 238, 1384, 318)), fill="#dcecff", outline="#c7daf8", width=2 * SCALE)
    draw.ellipse(sc_rect((1094, 210, 1320, 292)), fill="#eaf4ff")
    shadowed(base, (1154, 92, 1332, 224), 18, "#f4f9ff", "#bfd6fa", 10, (0, 5))
    rounded(draw, (1180, 122, 1302, 186), 11, "#5aa0ff", "#2d74e8", 2)
    rounded(draw, (1192, 134, 1290, 174), 4, "#4d8ff0")
    line(draw, [(1199, 162), (1216, 146), (1232, 174), (1252, 151), (1278, 156)], PALETTE["white"], 4)
    draw.rectangle(sc_rect((1234, 187, 1256, 224)), fill="#8bbfff")
    rounded(draw, (1207, 224, 1282, 234), 3, "#c9dfff")
    polygon(draw, [(1114, 166), (1158, 145), (1202, 166), (1190, 220), (1158, 244), (1126, 220)], "#d9eaff", "#6aa6ff")
    line(draw, [(1142, 197), (1155, 210), (1182, 177)], "#1f66e5", 6)
    circle(draw, 1076, 178, 8, "#dceaff")
    circle(draw, 1368, 180, 8, "#dceaff")
    polygon(draw, [(1096, 130), (1115, 140), (1096, 150)], "#c9ddff")


def render_ui(
    snapshot: dict[str, bool] | None = None,
    busy: bool = False,
    busy_message: str = "",
    output_size: tuple[int, int] | None = None,
) -> Image.Image:
    snapshot = snapshot or {}
    img = Image.new("RGBA", (LOGICAL_WIDTH * SCALE, LOGICAL_HEIGHT * SCALE), PALETTE["bg"])
    draw = ImageDraw.Draw(img)

    draw.ellipse(sc_rect((820, 28, 1520, 365)), fill="#edf6ff")
    draw.ellipse(sc_rect((1015, 124, 1320, 330)), fill="#e7f2ff")
    draw.ellipse(sc_rect((-230, 645, 520, 980)), fill="#ffffff")
    polygon(draw, [(900, 54), (LOGICAL_WIDTH, 54), (LOGICAL_WIDTH, 315), (1282, 438), (1020, 304)], "#f8fbff")
    draw.rectangle(sc_rect((0, 0, LOGICAL_WIDTH - 1, LOGICAL_HEIGHT - 1)), outline="#cbd9ee", width=SCALE)

    text(draw, (78, 112), "校园助手 · 本地演示控制台", 36, PALETTE["ink"], True)
    text(draw, (78, 168), "答辩兜底专用：无需黑框启动、状态可视化、异常可追踪", 18, PALETTE["muted"])
    draw_hero_art(img)

    draw_top_pill(img, (78, 218, 316, 286), "shield", "本地离线兜底", PALETTE["blue"])
    draw_top_pill(img, (344, 218, 580, 286), "users", "用户端  5173", PALETTE["primary"])
    draw_top_pill(img, (602, 218, 820, 286), "server", "后端  8000", PALETTE["green"])
    draw_top_pill(img, (838, 218, 1034, 286), "doc", "日志可追踪", PALETTE["purple"])

    shadowed(img, (56, 316, 1376, 540), 16, "#fbfdff", PALETTE["line"], 9, (0, 6))
    draw.rectangle(sc_rect((86, 344, 92, 362)), fill=PALETTE["primary"])
    text(draw, (112, 339), "运行状态", 18, PALETTE["ink"], True)

    cards = [
        ("backend", (80, 388, 385, 522), "后端服务", "server", PALETTE["blue"]),
        ("frontend", (405, 388, 710, 522), "用户端页面", "monitor", PALETTE["primary"]),
        ("db", (733, 388, 1032, 522), "本地数据库", "database", PALETTE["green"]),
        ("python", (1052, 388, 1355, 522), "Python 环境", "python", "#facc15"),
    ]
    for key, rect, title, icon, accent in cards:
        shadowed(img, rect, 13, PALETTE["white"], PALETTE["line"], 7, (0, 5))
        cx = rect[0] + 72
        cy = rect[1] + 67
        circle(draw, cx, cy, 47, "#edf5ff")
        circle(draw, cx, cy, 37, "#f5f9ff")
        if icon == "server":
            draw_server(draw, cx, cy, accent)
        elif icon == "monitor":
            draw_monitor(draw, cx, cy, accent)
        elif icon == "database":
            draw_database(draw, cx, cy)
        else:
            draw_python(draw, cx, cy)
        ok, label, _detail = status_style(snapshot, key)
        text(draw, (rect[0] + 150, rect[1] + 43), title, 18, PALETTE["ink"], True)
        draw_pill_status(draw, (rect[0] + 148, rect[1] + 82, rect[0] + 248, rect[1] + 120), ok and not busy, "检查中" if busy else label)

    actions = [
        ((60, 568, 446, 694), "rocket", "启动并打开用户端", "自动拉起服务并打开用户端", True),
        ((462, 568, 749, 694), "window", "打开后台管理", "进入后台管理系统", False),
        ((767, 568, 1050, 694), "play", "仅启动服务", "静默启动本地服务", False),
        ((1087, 568, 1380, 694), "refresh", "重启服务", "重启本地服务组件", False),
    ]
    for rect, icon, title, sub, primary in actions:
        if primary:
            shadowed(img, rect, 13, PALETTE["primary"], "#0f55df", 10, (0, 7))
            draw.rounded_rectangle(sc_rect((rect[0] + 1, rect[1] + 1, rect[2] - 1, rect[1] + 68)), radius=13 * SCALE, fill="#237cff")
            fg = PALETTE["white"]
            sub_fg = "#cfe1ff"
            icon_fg = PALETTE["white"]
        else:
            shadowed(img, rect, 13, PALETTE["white"], PALETTE["line"], 7, (0, 5))
            fg = PALETTE["ink"]
            sub_fg = PALETTE["muted"]
            icon_fg = PALETTE["primary"]
        cx = rect[0] + 88
        cy = rect[1] + 63
        circle(draw, cx, cy, 43, "#edf5ff")
        if icon == "rocket":
            draw_rocket(draw, cx, cy, icon_fg)
        elif icon == "window":
            rounded(draw, (cx - 24, cy - 24, cx + 24, cy + 24), 5, icon_fg)
            rounded(draw, (cx - 15, cy - 9, cx + 15, cy + 13), 2, PALETTE["white"])
            circle(draw, cx - 13, cy - 16, 3, PALETTE["white"])
        elif icon == "play":
            circle(draw, cx, cy, 29, icon_fg)
            polygon(draw, [(cx - 7, cy - 14), (cx - 7, cy + 14), (cx + 17, cy)], PALETTE["white"])
        else:
            draw.arc(sc_rect((cx - 28, cy - 28, cx + 28, cy + 28)), 32, 315, fill=icon_fg, width=5 * SCALE)
            polygon(draw, [(cx + 22, cy - 22), (cx + 34, cy - 20), (cx + 27, cy - 8)], icon_fg)
        text(draw, (rect[0] + 175, rect[1] + 44), title, 18, fg, True)
        text(draw, (rect[0] + 175, rect[1] + 76), sub, 12, sub_fg)
        if primary:
            text(draw, (rect[2] - 34, rect[1] + 44), "›", 30, "#dbeafe", True)

    shadowed(img, (56, 720, 1376, 842), 14, PALETTE["white"], PALETTE["line"], 8, (0, 5))
    text(draw, (94, 746), "系统日志（最近）", 16, PALETTE["ink"], True)
    text(draw, (910, 746), "查看全部日志  >", 13, PALETTE["primary"], True)
    draw.line([sc_xy(1044, 740), sc_xy(1044, 822)], fill=PALETTE["line"], width=SCALE)
    text(draw, (1082, 746), "当前环境", 16, PALETTE["ink"], True)

    now_logs = [
        ("后端服务已就绪，监听端口 8000" if snapshot.get("backend") else "后端服务尚未启动", snapshot.get("backend")),
        ("用户端页面已就绪，访问地址 http://localhost:5173" if snapshot.get("frontend") else "用户端页面尚未启动", snapshot.get("frontend")),
        ("本地数据库连接正常" if snapshot.get("db") else "本地数据库缺失", snapshot.get("db")),
    ]
    if busy:
        now_logs = [(busy_message or "正在处理，请稍等...", False), ("服务启动通常需要 5-15 秒", False), ("关闭控制台会自动停止本地服务", True)]
    for index, (value, ok) in enumerate(now_logs):
        y = 786 + index * 25
        circle(draw, 98, y + 2, 4, PALETTE["green"] if ok else PALETTE["warn"])
        text(draw, (122, y - 8), time_like(index), 12, PALETTE["subtle"])
        text(draw, (226, y - 8), value, 12, PALETTE["muted"])

    env_ok = snapshot.get("backend") and snapshot.get("frontend") and snapshot.get("db") and snapshot.get("python") and not busy
    env_wait = snapshot.get("db") and snapshot.get("python") and not env_ok
    env_color = PALETTE["green"] if env_ok else PALETTE["warn"] if env_wait or busy else PALETTE["danger"]
    env_label = "一切正常" if env_ok else "正在处理" if busy else "等待启动" if env_wait else "依赖缺失"
    env_desc = "系统运行良好，请放心使用" if env_ok else (busy_message or "如未启动，点击左侧蓝色主按钮即可自动拉起服务")
    circle(draw, 1104, 793, 18, env_color)
    line(draw, [(1094, 793), (1101, 801), (1115, 783)], PALETTE["white"], 4)
    text(draw, (1138, 775), env_label, 18, env_color, True)
    text(draw, (1082, 820), env_desc, 13, PALETTE["muted"])

    return img.resize(output_size or (WIDTH, HEIGHT), Image.Resampling.LANCZOS).convert("RGB")


def time_like(index: int) -> str:
    return time.strftime("%H:%M:%S", time.localtime(time.time() - index * 2))
