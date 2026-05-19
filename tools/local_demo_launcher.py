import os
import queue
import socket
import subprocess
import sys
import threading
import time
import traceback
import urllib.request
import webbrowser
import ctypes
from pathlib import Path
from tkinter import Canvas, Tk, messagebox

from PIL import Image, ImageTk

try:
    from tools.local_demo_rendered_ui import HEIGHT as UI_HEIGHT
    from tools.local_demo_rendered_ui import LOGICAL_HEIGHT as UI_LOGICAL_HEIGHT
    from tools.local_demo_rendered_ui import LOGICAL_WIDTH as UI_LOGICAL_WIDTH
    from tools.local_demo_rendered_ui import WIDTH as UI_WIDTH
    from tools.local_demo_rendered_ui import render_ui
except ModuleNotFoundError:
    from local_demo_rendered_ui import HEIGHT as UI_HEIGHT
    from local_demo_rendered_ui import LOGICAL_HEIGHT as UI_LOGICAL_HEIGHT
    from local_demo_rendered_ui import LOGICAL_WIDTH as UI_LOGICAL_WIDTH
    from local_demo_rendered_ui import WIDTH as UI_WIDTH
    from local_demo_rendered_ui import render_ui


def enable_dpi_awareness() -> None:
    # Keep Tk in Windows logical pixels. If we force DPI awareness here,
    # maximized windows on 200% scaled displays report physical pixels
    # (for example 2880x1659), which makes the rendered dashboard overscale.
    return


enable_dpi_awareness()


def set_app_user_model_id() -> None:
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("CampusAssistant.LocalDemo")
    except Exception:
        pass


set_app_user_model_id()


def force_taskbar_entry(root: Tk) -> None:
    if sys.platform != "win32":
        return
    try:
        root.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id()) or root.winfo_id()
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = (style | WS_EX_APPWINDOW) & ~WS_EX_TOOLWINDOW
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        ctypes.windll.user32.SetWindowPos(
            hwnd,
            0,
            0,
            0,
            0,
            0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE | SWP_FRAMECHANGED,
        )
        root.deiconify()
        root.lift()
    except Exception:
        pass


BACKEND_PORT = 8000
FRONTEND_PORT = 5173
USER_URL = f"http://127.0.0.1:{FRONTEND_PORT}/index.html"
ADMIN_URL = f"http://127.0.0.1:{BACKEND_PORT}/studio/"
HEALTH_URL = f"http://127.0.0.1:{BACKEND_PORT}/healthz"

CREATE_NO_WINDOW = 0x08000000
GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010
SWP_FRAMECHANGED = 0x0020

COLORS = {
    "bg": "#f7fbff",
    "bg2": "#eef6ff",
    "titlebar": "#fbfdff",
    "panel": "#ffffff",
    "panel_soft": "#fbfdff",
    "ink": "#0a1833",
    "muted": "#6b7c99",
    "subtle": "#9aacbf",
    "line": "#d8e7fb",
    "line_soft": "#edf5ff",
    "shadow": "#dce9fb",
    "shadow_deep": "#cfe0f6",
    "primary": "#1769ff",
    "primary_hover": "#0f55df",
    "primary_soft": "#eaf3ff",
    "blue": "#2369f4",
    "blue_soft": "#edf5ff",
    "green": "#10b981",
    "green_soft": "#e6f8f0",
    "purple": "#7c3aed",
    "purple_soft": "#f0ebff",
    "success": "#059669",
    "success_bg": "#dff7eb",
    "warn": "#b45309",
    "warn_bg": "#fff4dc",
    "danger": "#b42318",
    "danger_bg": "#ffe7e2",
    "white": "#ffffff",
}

FONT = "Microsoft YaHei UI"


def exe_stem() -> str:
    return Path(sys.executable if getattr(sys, "frozen", False) else __file__).stem.lower()


def find_project_root() -> Path:
    base = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve()
    for candidate in [base.parent, *base.parents]:
        if (candidate / "backend" / "campus.db").exists() and (candidate / "app.js").exists():
            return candidate
    return base.parent


ROOT = find_project_root()
BACKEND_DIR = ROOT / "backend"
LOG_DIR = ROOT / "local-demo-logs"
PYTHONW = ROOT / ".venv" / "Scripts" / "pythonw.exe"
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"


def resource_path(relative_path: str) -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    return ROOT / relative_path


ICON_PATH = resource_path("tools/local_demo_icon.ico")


def launcher_log(message: str) -> None:
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_DIR / "launcher.runtime.log", "a", encoding="utf-8") as file:
            file.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass


def ensure_log_dir() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def http_ok(url: str, timeout: float = 2.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return 200 <= int(resp.status) < 500
    except Exception:
        return False


def health_ok() -> bool:
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=2.0) as resp:
            body = resp.read().decode("utf-8", "ignore")
            return resp.status == 200 and "ok" in body.lower()
    except Exception:
        return False


def runtime_snapshot() -> dict[str, bool]:
    return {
        "backend": health_ok(),
        "frontend": http_ok(USER_URL),
        "db": (BACKEND_DIR / "campus.db").exists(),
        "python": PYTHONW.exists() or PYTHON.exists(),
        "backend_port": port_open(BACKEND_PORT),
        "frontend_port": port_open(FRONTEND_PORT),
    }


def run_hidden(args, cwd: Path | None = None, stdout_path: Path | None = None, stderr_path: Path | None = None):
    stdout_handle = open(stdout_path, "ab") if stdout_path else subprocess.DEVNULL
    stderr_handle = open(stderr_path, "ab") if stderr_path else subprocess.DEVNULL
    try:
        return subprocess.Popen(
            args,
            cwd=str(cwd) if cwd else None,
            stdout=stdout_handle,
            stderr=stderr_handle,
            stdin=subprocess.DEVNULL,
            creationflags=CREATE_NO_WINDOW,
            close_fds=False,
        )
    finally:
        if stdout_path:
            stdout_handle.close()
        if stderr_path:
            stderr_handle.close()


def powershell_stop_ports() -> None:
    command = (
        "$ErrorActionPreference='SilentlyContinue';"
        f"$ports=@({BACKEND_PORT},{FRONTEND_PORT});"
        "foreach($port in $ports){"
        "$items=Get-NetTCPConnection -State Listen -LocalPort $port;"
        "foreach($procId in ($items|Select-Object -ExpandProperty OwningProcess -Unique)){"
        "Stop-Process -Id $procId -Force"
        "}}"
        "$self=$PID;"
        "$processes=Get-CimInstance Win32_Process | Where-Object {"
        "$cmd=$_.CommandLine;$name=$_.Name;"
        "$_.ProcessId -ne $self -and $cmd -and $name -match '^pythonw?\\.exe$' -and ("
        "($cmd -like '*-m uvicorn app.main:app*--host 127.0.0.1*--port 8000*') -or "
        "($cmd -like '*-m http.server 5173*--bind 127.0.0.1*')"
        ")"
        "};"
        "foreach($process in $processes){Stop-Process -Id $process.ProcessId -Force}"
    )
    subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-WindowStyle",
            "Hidden",
            "-Command",
            command,
        ],
        creationflags=CREATE_NO_WINDOW,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=20,
        check=False,
    )


def wait_for_ports_closed(timeout: float = 8.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not port_open(BACKEND_PORT) and not port_open(FRONTEND_PORT):
            return True
        time.sleep(0.35)
    return not port_open(BACKEND_PORT) and not port_open(FRONTEND_PORT)


def validate_runtime() -> None:
    if not BACKEND_DIR.exists():
        raise RuntimeError(f"找不到后端目录：{BACKEND_DIR}")
    if not PYTHONW.exists() and not PYTHON.exists():
        raise RuntimeError(f"找不到项目虚拟环境 Python：{ROOT / '.venv' / 'Scripts'}")
    if not (BACKEND_DIR / "campus.db").exists():
        raise RuntimeError(f"找不到本地数据库：{BACKEND_DIR / 'campus.db'}")


def start_services(restart: bool = False) -> None:
    validate_runtime()
    ensure_log_dir()
    if restart:
        powershell_stop_ports()
        time.sleep(1)

    python_exe = PYTHONW if PYTHONW.exists() else PYTHON
    if not health_ok():
        run_hidden(
            [str(python_exe), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(BACKEND_PORT)],
            cwd=BACKEND_DIR,
            stdout_path=LOG_DIR / "backend.stdout.log",
            stderr_path=LOG_DIR / "backend.stderr.log",
        )

    if not port_open(FRONTEND_PORT):
        run_hidden(
            [str(python_exe), "-m", "http.server", str(FRONTEND_PORT), "--bind", "127.0.0.1"],
            cwd=ROOT,
            stdout_path=LOG_DIR / "frontend.stdout.log",
            stderr_path=LOG_DIR / "frontend.stderr.log",
        )

    deadline = time.time() + 35
    while time.time() < deadline:
        if health_ok() and http_ok(USER_URL):
            return
        time.sleep(0.5)
    raise RuntimeError(build_failure_message())


def build_failure_message() -> str:
    err_log = LOG_DIR / "backend.stderr.log"
    tail = ""
    if err_log.exists():
        text = err_log.read_text(encoding="utf-8", errors="ignore").splitlines()
        tail = "\n".join(text[-8:])
    return (
        "本地演示服务启动超时。\n\n"
        f"项目目录：{ROOT}\n"
        f"后端日志：{LOG_DIR / 'backend.stderr.log'}\n"
        f"前端日志：{LOG_DIR / 'frontend.stderr.log'}\n\n"
        "建议先点击“打开日志目录”查看最新日志；如端口被占用，可点击“重启服务”。\n\n"
        f"{tail}"
    ).strip()


def stop_services(show_message: bool = True) -> None:
    powershell_stop_ports()
    if not wait_for_ports_closed():
        powershell_stop_ports()
        wait_for_ports_closed(5.0)
    if show_message:
        messagebox.showinfo("校园助手本地演示", "本地演示服务已停止。")


def open_user() -> None:
    webbrowser.open(USER_URL)


def open_admin() -> None:
    webbrowser.open(ADMIN_URL)


def center_window(root: Tk, width: int, height: int) -> None:
    root.update_idletasks()
    x = max((root.winfo_screenwidth() - width) // 2, 0)
    y = max((root.winfo_screenheight() - height) // 2, 0)
    root.geometry(f"{width}x{height}+{x}+{y}")


class LauncherApp:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.title("校园助手本地演示控制台")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(True, True)
        if ICON_PATH.exists():
            try:
                self.root.iconbitmap(str(ICON_PATH))
                self.window_icon = ImageTk.PhotoImage(Image.open(ICON_PATH))
                self.root.iconphoto(True, self.window_icon)
            except Exception as exc:
                launcher_log(f"window icon load failed: {exc}")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        fit_scale = min(
            1.0,
            max(screen_width - 28, 980) / UI_WIDTH,
            max(screen_height - 28, 700) / UI_HEIGHT,
        )
        self.width = int(round(UI_WIDTH * fit_scale))
        self.height = int(round(UI_HEIGHT * fit_scale))
        self.display_width = self.width
        self.display_height = self.height
        self.offset_x = 0
        self.offset_y = 0
        self.scale_x = self.display_width / UI_LOGICAL_WIDTH
        self.scale_y = self.display_height / UI_LOGICAL_HEIGHT
        self.resize_job = None
        center_window(self.root, self.width, self.height)
        self.root.minsize(1040, 735)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.bind("<Alt-F4>", lambda _event: self.on_close())
        self.root.bind("<Map>", self.restore_override)

        self.busy = False
        self.closing = False
        self.refreshing = False
        self.drag_x = 0
        self.drag_y = 0
        self.dragging_window = False
        self.current_snapshot = runtime_snapshot()
        self.ui_image = None
        self.image_item = 0
        self.click_regions: list[tuple[str, tuple[int, int, int, int]]] = []
        self.ui_queue: queue.Queue = queue.Queue()
        self.worker_threads: list[threading.Thread] = []
        self.badges: dict[str, dict[str, int]] = {}
        self.log_items: list[int] = []
        self.status_item = 0
        self.env_item = 0
        self.detail_item = 0
        self.env_icon_items: list[int] = []

        self.canvas = Canvas(self.root, width=self.width, height=self.height, bg=COLORS["bg"], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.update_display_metrics(self.width, self.height)
        self.build_ui()
        self.root.after(80, self.drain_ui_queue)
        self.root.after(100, lambda: force_taskbar_entry(self.root))
        self.root.after(120, self.bring_to_front)
        self.refresh_status_async()
        self.root.after(3500, self.schedule_refresh)

    def build_ui(self) -> None:
        c = self.canvas
        self.draw_background()
        self.draw_titlebar()

        c.create_text(62, 128, text="校园助手 · 本地演示控制台", anchor="w", font=(FONT, 34, "bold"), fill=COLORS["ink"])
        c.create_text(63, 178, text="答辩兜底专用：无需黑框启动、状态可视化、异常可追踪", anchor="w", font=(FONT, 13), fill=COLORS["muted"])
        self.draw_hero_art(848, 88)

        pill_y = 222
        self.make_top_pill(62, pill_y, 194, "shield", "本地离线兜底", COLORS["blue"])
        self.make_top_pill(278, pill_y, 192, "users", f"用户端  {FRONTEND_PORT}", COLORS["primary"])
        self.make_top_pill(492, pill_y, 192, "server", f"后端  {BACKEND_PORT}", COLORS["green"])
        self.make_top_pill(706, pill_y, 170, "log", "日志可追踪", COLORS["purple"])

        self.shadowed_round_rect(46, 330, 1114, 548, 18, fill=COLORS["panel_soft"], outline=COLORS["line"], width=1, shadow=COLORS["shadow"])
        c.create_rectangle(70, 358, 75, 375, fill=COLORS["primary"], outline="")
        c.create_text(92, 367, text="运行状态", anchor="w", font=(FONT, 16, "bold"), fill=COLORS["ink"])

        status_cards = [
            ("backend", 66, "server", "后端服务", COLORS["blue"]),
            ("frontend", 323, "monitor", "用户端页面", COLORS["primary"]),
            ("db", 580, "database", "本地数据库", COLORS["green"]),
            ("python", 837, "python", "Python 环境", "#f7c316"),
        ]
        for key, x, icon, title, accent in status_cards:
            self.make_status_card(x, 402, key, icon, title, accent)

        self.make_action_card(48, 572, 310, 120, "start_user", "rocket", "启动并打开用户端", "启动服务并在浏览器中打开用户端", self.start_and_open_user, primary=True)
        self.make_action_card(374, 572, 230, 120, "admin", "window", "打开后台管理", "打开后台管理系统", self.start_and_open_admin)
        self.make_action_card(620, 572, 230, 120, "start", "play", "仅启动服务", "后台静默启动所有服务", self.start_only)
        self.make_action_card(866, 572, 248, 120, "restart", "refresh", "重启服务", "重启所有服务组件", self.restart_services)

        self.shadowed_round_rect(48, 724, 1114, 845, 14, fill=COLORS["panel"], outline=COLORS["line"], width=1, shadow="#e7f0fb")
        c.create_text(76, 750, text="系统日志（最近）", anchor="w", font=(FONT, 12, "bold"), fill=COLORS["ink"])
        link_tag = "open_logs_link"
        c.create_text(730, 750, text="查看全部日志  >", anchor="w", font=(FONT, 10, "bold"), fill=COLORS["primary"], tags=(link_tag,))
        self.bind_tag(link_tag, self.open_logs)
        for y in [782, 810, 838]:
            item = c.create_text(76, y, text="●  正在读取状态...", anchor="w", font=(FONT, 10), fill=COLORS["muted"])
            self.log_items.append(item)

        c.create_line(835, 748, 835, 830, fill=COLORS["line"], width=1)
        c.create_text(865, 750, text="当前环境", anchor="w", font=(FONT, 12, "bold"), fill=COLORS["ink"])
        self.env_icon_items = self.draw_check_icon(884, 792, COLORS["success"])
        self.status_item = c.create_text(922, 790, text="正在检查", anchor="w", font=(FONT, 12, "bold"), fill=COLORS["success"])
        self.env_item = c.create_text(865, 825, text="正在检查当前环境...", anchor="w", font=(FONT, 10), fill=COLORS["muted"])
        self.detail_item = c.create_text(48, 858, text="", anchor="w", font=(FONT, 8), fill=COLORS["subtle"], width=1065)

    def draw_background(self) -> None:
        c = self.canvas
        c.create_rectangle(0, 0, self.width, self.height, fill=COLORS["bg"], outline="")
        c.create_rectangle(0, 0, self.width, 54, fill=COLORS["titlebar"], outline="")
        c.create_line(0, 54, self.width, 54, fill="#dfe9f7", width=1)
        c.create_oval(690, 20, 1290, 410, fill="#edf6ff", outline="")
        c.create_oval(880, 120, 1130, 335, fill="#e7f2ff", outline="")
        c.create_oval(-210, 650, 430, 1040, fill="#ffffff", outline="")
        c.create_polygon(900, 54, 1160, 54, 1160, 275, 1070, 360, 930, 260, fill="#f8fbff", outline="")
        c.create_line(0, self.height - 1, self.width, self.height - 1, fill="#cbd9ee")
        c.create_line(0, 0, self.width, 0, fill="#cbd9ee")
        c.create_line(0, 0, 0, self.height, fill="#cbd9ee")
        c.create_line(self.width - 1, 0, self.width - 1, self.height, fill="#cbd9ee")

    def draw_titlebar(self) -> None:
        c = self.canvas
        bar_tag = "titlebar_drag"
        c.create_rectangle(0, 0, self.width, 54, fill=COLORS["titlebar"], outline="", tags=(bar_tag,))
        self.draw_window_logo(30, 27, bar_tag)
        c.create_text(58, 27, text="校园助手 · 本地演示控制台", anchor="w", font=(FONT, 12, "bold"), fill=COLORS["ink"], tags=(bar_tag,))
        self.bind_drag_tag(bar_tag)
        self.make_window_button(self.width - 142, 27, "−", "min_window", self.minimize_window)
        self.make_window_button(self.width - 86, 27, "□", "max_window", self.bring_to_front)
        self.make_window_button(self.width - 31, 27, "×", "close_window", self.on_close, danger=True)

    def draw_window_logo(self, cx: int, cy: int, tag: str) -> None:
        c = self.canvas
        c.create_oval(cx - 13, cy - 13, cx + 13, cy + 13, fill="#1769ff", outline="#0f55df", width=1, tags=(tag,))
        c.create_polygon(cx - 6, cy + 8, cx + 4, cy - 10, cx + 11, cy - 13, cx + 8, cy - 5, cx - 2, cy + 7, fill="#ffffff", outline="", tags=(tag,))
        c.create_oval(cx + 1, cy - 7, cx + 6, cy - 2, fill="#dbeafe", outline="", tags=(tag,))
        c.create_polygon(cx - 4, cy + 7, cx - 12, cy + 12, cx - 8, cy + 2, fill="#cfe1ff", outline="", tags=(tag,))

    def make_window_button(self, cx: int, cy: int, label: str, tag: str, command, danger: bool = False) -> None:
        self.canvas.create_rectangle(cx - 22, cy - 18, cx + 22, cy + 18, fill=COLORS["titlebar"], outline="", tags=(tag,))
        self.canvas.create_text(cx, cy, text=label, anchor="center", font=("Segoe UI", 15), fill="#1f2f46" if not danger else "#1f2f46", tags=(tag,))
        self.canvas.tag_bind(tag, "<Button-1>", lambda _event: command())
        self.canvas.tag_bind(tag, "<Enter>", lambda _event: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind(tag, "<Leave>", lambda _event: self.canvas.config(cursor="watch" if self.busy else ""))

    def bind_drag_tag(self, tag: str) -> None:
        self.canvas.tag_bind(tag, "<ButtonPress-1>", self.start_move)
        self.canvas.tag_bind(tag, "<B1-Motion>", self.do_move)

    def start_move(self, event) -> None:
        self.drag_x = event.x
        self.drag_y = event.y

    def do_move(self, event) -> None:
        if self.closing:
            return
        x = event.x_root - self.drag_x
        y = event.y_root - self.drag_y
        self.root.geometry(f"+{x}+{y}")

    def minimize_window(self) -> None:
        self.root.iconify()

    def restore_override(self, _event=None) -> None:
        if not self.closing:
            self.root.after(80, self.restore_borderless_window)

    def restore_borderless_window(self) -> None:
        if self.closing:
            return
        force_taskbar_entry(self.root)

    def rounded_rect(self, x1: int, y1: int, x2: int, y2: int, r: int, **kwargs) -> int:
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def shadowed_round_rect(self, x1: int, y1: int, x2: int, y2: int, r: int, shadow: str | None = None, **kwargs) -> int:
        shadow_color = shadow or COLORS["shadow"]
        self.rounded_rect(x1 + 4, y1 + 7, x2 + 4, y2 + 7, r, fill=shadow_color, outline="")
        self.rounded_rect(x1 + 2, y1 + 3, x2 + 2, y2 + 3, r, fill="#edf5ff", outline="")
        return self.rounded_rect(x1, y1, x2, y2, r, **kwargs)

    def bind_tag(self, tag: str, command) -> None:
        self.canvas.tag_bind(tag, "<Button-1>", lambda _event: self.run_async(command))
        self.canvas.tag_bind(tag, "<Enter>", lambda _event: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind(tag, "<Leave>", lambda _event: self.canvas.config(cursor="watch" if self.busy else ""))

    def make_top_pill(self, x: int, y: int, w: int, icon: str, title: str, accent: str) -> None:
        self.rounded_rect(x + 3, y + 6, x + w + 3, y + 70, 12, fill="#e8f1fb", outline="")
        self.rounded_rect(x, y, x + w, y + 66, 12, fill=COLORS["panel"], outline=COLORS["line_soft"], width=1)
        self.canvas.create_oval(x + 20, y + 19, x + 48, y + 47, fill=COLORS["primary_soft"], outline="")
        self.draw_tiny_icon(x + 34, y + 33, icon, accent)
        self.canvas.create_text(x + 66, y + 33, text=title, anchor="w", font=(FONT, 12, "bold"), fill=COLORS["ink"])

    def draw_hero_art(self, ox: int, oy: int) -> None:
        c = self.canvas
        c.create_oval(ox + 15, oy + 144, ox + 298, oy + 214, fill="#dcecff", outline="#c8dcf8", width=2)
        c.create_oval(ox + 54, oy + 126, ox + 257, oy + 190, fill="#eaf4ff", outline="")
        c.create_oval(ox + 82, oy + 110, ox + 232, oy + 168, fill="#dcecff", outline="")
        self.shadowed_round_rect(ox + 94, oy + 18, ox + 238, oy + 150, 18, fill="#f3f8ff", outline="#bfd5f8", width=1, shadow="#d8e8fb")
        self.rounded_rect(ox + 125, oy + 48, ox + 219, oy + 106, 10, fill="#5ba2ff", outline="#2f74e8", width=2)
        c.create_rectangle(ox + 137, oy + 59, ox + 207, oy + 95, fill="#4d8ff0", outline="")
        c.create_line(ox + 140, oy + 80, ox + 154, oy + 66, ox + 168, oy + 94, ox + 187, oy + 72, ox + 207, oy + 76, fill="#ffffff", width=4, smooth=True)
        c.create_rectangle(ox + 165, oy + 107, ox + 181, oy + 135, fill="#8abfff", outline="")
        c.create_rectangle(ox + 141, oy + 135, ox + 205, oy + 145, fill="#c9dfff", outline="")
        c.create_polygon(ox + 54, oy + 92, ox + 90, oy + 74, ox + 126, oy + 92, ox + 116, oy + 138, ox + 90, oy + 158, ox + 64, oy + 138, fill="#d9eaff", outline="#6aa6ff", width=2)
        c.create_line(ox + 77, oy + 119, ox + 88, oy + 130, ox + 111, oy + 102, fill="#1f66e5", width=6)
        c.create_oval(ox + 18, oy + 62, ox + 34, oy + 78, fill="#dceaff", outline="")
        c.create_polygon(ox + 48, oy + 30, ox + 66, oy + 39, ox + 48, oy + 49, fill="#c9ddff", outline="")
        c.create_oval(ox + 250, oy + 85, ox + 264, oy + 99, fill="#dceaff", outline="")

    def make_status_card(self, x: int, y: int, key: str, icon: str, title: str, accent: str) -> None:
        self.shadowed_round_rect(x, y, x + 244, y + 134, 13, fill=COLORS["panel"], outline=COLORS["line"], width=1, shadow="#e8f1fb")
        self.draw_status_icon(x + 66, y + 67, icon, accent)
        self.canvas.create_text(x + 127, y + 51, text=title, anchor="w", font=(FONT, 14, "bold"), fill=COLORS["ink"])
        pill = self.rounded_rect(x + 126, y + 82, x + 205, y + 116, 17, fill=COLORS["warn_bg"], outline="")
        dot = self.canvas.create_oval(x + 141, y + 95, x + 149, y + 103, fill=COLORS["warn"], outline="")
        text = self.canvas.create_text(x + 158, y + 99, text="检查中", anchor="w", font=(FONT, 10, "bold"), fill=COLORS["warn"])
        self.badges[key] = {"pill": pill, "dot": dot, "text": text}

    def draw_status_icon(self, cx: int, cy: int, kind: str, accent: str) -> None:
        c = self.canvas
        c.create_oval(cx - 43, cy - 43, cx + 43, cy + 43, fill=COLORS["blue_soft"], outline="")
        c.create_oval(cx - 34, cy - 34, cx + 34, cy + 34, fill="#f5f9ff", outline="")
        if kind == "server":
            for y in [cy - 18, cy + 8]:
                self.rounded_rect(cx - 26, y, cx + 26, y + 17, 4, fill=accent, outline="")
                c.create_oval(cx - 18, y + 5, cx - 11, y + 12, fill="#dbeafe", outline="")
                c.create_line(cx + 3, y + 8, cx + 18, y + 8, fill="#dbeafe", width=2)
        elif kind == "monitor":
            self.rounded_rect(cx - 26, cy - 21, cx + 26, cy + 18, 5, fill=accent, outline="")
            self.rounded_rect(cx - 17, cy - 12, cx + 17, cy + 7, 2, fill=COLORS["white"], outline="")
            c.create_rectangle(cx - 6, cy + 18, cx + 6, cy + 31, fill=accent, outline="")
            c.create_rectangle(cx - 19, cy + 31, cx + 19, cy + 36, fill=accent, outline="")
        elif kind == "database":
            c.create_oval(cx - 25, cy - 26, cx + 25, cy - 7, fill="#86efac", outline="#059669", width=2)
            c.create_rectangle(cx - 25, cy - 16, cx + 25, cy + 25, fill="#bbf7d0", outline="#059669", width=2)
            c.create_oval(cx - 25, cy + 12, cx + 25, cy + 32, fill="#86efac", outline="#059669", width=2)
            c.create_arc(cx - 25, cy - 2, cx + 25, cy + 19, start=180, extent=180, style="arc", outline="#059669", width=2)
        else:
            c.create_oval(cx - 28, cy - 27, cx + 5, cy + 6, fill="#2369f4", outline="")
            c.create_oval(cx - 4, cy - 3, cx + 29, cy + 30, fill="#facc15", outline="")
            c.create_rectangle(cx - 13, cy - 13, cx + 16, cy + 16, fill=COLORS["white"], outline="")

    def make_action_card(self, x: int, y: int, w: int, h: int, tag: str, icon: str, title: str, subtitle: str, command, primary: bool = False) -> None:
        fill = COLORS["primary"] if primary else COLORS["panel"]
        outline = "#0f55df" if primary else COLORS["line"]
        title_fill = COLORS["white"] if primary else COLORS["ink"]
        sub_fill = "#cfe1ff" if primary else COLORS["muted"]
        self.rounded_rect(x + 4, y + 7, x + w + 4, y + h + 7, 13, fill="#dfeaf8", outline="", tags=(tag,))
        self.rounded_rect(x + 1, y + 3, x + w + 1, y + h + 3, 13, fill="#edf5ff", outline="", tags=(tag,))
        self.rounded_rect(x, y, x + w, y + h, 13, fill=fill, outline=outline, width=1, tags=(tag,))
        if primary:
            self.rounded_rect(x + 1, y + 1, x + w - 1, y + h // 2, 12, fill="#2378ff", outline="", tags=(tag,))
        self.draw_action_icon(x + 72, y + 60, icon, COLORS["white"] if primary else COLORS["primary"], tag, primary=primary)
        c = self.canvas
        c.create_text(x + 142, y + 48, text=title, anchor="w", font=(FONT, 13, "bold"), fill=title_fill, tags=(tag,))
        c.create_text(x + 142, y + 78, text=subtitle, anchor="w", font=(FONT, 9), fill=sub_fill, tags=(tag,))
        if primary:
            c.create_text(x + w - 28, y + 60, text="›", anchor="center", font=("Segoe UI", 24, "bold"), fill="#dbeafe", tags=(tag,))
        self.bind_tag(tag, command)

    def draw_action_icon(self, cx: int, cy: int, kind: str, accent: str, tag: str, primary: bool = False) -> None:
        c = self.canvas
        c.create_oval(cx - 36, cy - 36, cx + 36, cy + 36, fill="#edf5ff" if not primary else "#eaf3ff", outline="", tags=(tag,))
        if kind == "rocket":
            c.create_polygon(cx - 14, cy + 24, cx + 10, cy - 20, cx + 26, cy - 28, cx + 19, cy - 8, cx - 5, cy + 18, fill=accent, outline="", tags=(tag,))
            c.create_oval(cx + 5, cy - 15, cx + 16, cy - 4, fill=COLORS["primary"], outline="", tags=(tag,))
            c.create_polygon(cx - 10, cy + 18, cx - 28, cy + 28, cx - 19, cy + 8, fill="#cfe1ff", outline="", tags=(tag,))
        elif kind == "window":
            self.rounded_rect(cx - 20, cy - 20, cx + 20, cy + 20, 4, fill=accent, outline="", tags=(tag,))
            self.rounded_rect(cx - 12, cy - 8, cx + 12, cy + 11, 2, fill=COLORS["white"], outline="", tags=(tag,))
            c.create_oval(cx - 11, cy - 14, cx - 7, cy - 10, fill=COLORS["white"], outline="", tags=(tag,))
        elif kind == "play":
            c.create_oval(cx - 23, cy - 23, cx + 23, cy + 23, fill=accent, outline="", tags=(tag,))
            c.create_polygon(cx - 5, cy - 12, cx - 5, cy + 12, cx + 15, cy, fill=COLORS["white"], outline="", tags=(tag,))
        else:
            c.create_arc(cx - 21, cy - 21, cx + 21, cy + 21, start=30, extent=275, style="arc", outline=accent, width=4, tags=(tag,))
            c.create_polygon(cx + 16, cy - 16, cx + 27, cy - 15, cx + 21, cy - 5, fill=accent, outline="", tags=(tag,))

    def draw_tiny_icon(self, cx: int, cy: int, kind: str, accent: str) -> None:
        c = self.canvas
        if kind == "shield":
            c.create_polygon(cx - 13, cy - 15, cx, cy - 22, cx + 13, cy - 15, cx + 10, cy + 12, cx, cy + 21, cx - 10, cy + 12, fill="#dbeafe", outline=accent, width=2)
            c.create_line(cx - 7, cy, cx - 1, cy + 7, cx + 9, cy - 8, fill=accent, width=3)
        elif kind == "users":
            c.create_oval(cx - 12, cy - 17, cx, cy - 5, fill=accent, outline="")
            c.create_oval(cx + 3, cy - 16, cx + 15, cy - 4, fill=accent, outline="")
            c.create_oval(cx - 17, cy - 1, cx + 6, cy + 17, fill=accent, outline="")
            c.create_oval(cx - 1, cy, cx + 19, cy + 17, fill=accent, outline="")
        elif kind == "server":
            for y in [cy - 16, cy + 2]:
                c.create_rectangle(cx - 17, y, cx + 17, y + 12, fill=accent, outline="")
                c.create_oval(cx - 11, y + 4, cx - 7, y + 8, fill=COLORS["white"], outline="")
        else:
            c.create_rectangle(cx - 12, cy - 18, cx + 13, cy + 18, fill=accent, outline="")
            c.create_line(cx - 5, cy - 8, cx + 6, cy - 8, fill=COLORS["white"], width=2)
            c.create_line(cx - 5, cy, cx + 7, cy, fill=COLORS["white"], width=2)

    def draw_check_icon(self, cx: int, cy: int, accent: str) -> list[int]:
        circle = self.canvas.create_oval(cx - 14, cy - 14, cx + 14, cy + 14, fill=accent, outline="")
        check = self.canvas.create_line(cx - 7, cy, cx - 1, cy + 7, cx + 9, cy - 8, fill=COLORS["white"], width=4)
        return [circle, check]

    def scale_rect(self, rect: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
        x1, y1, x2, y2 = rect
        return (
            self.offset_x + int(round(x1 * self.scale_x)),
            self.offset_y + int(round(y1 * self.scale_y)),
            self.offset_x + int(round(x2 * self.scale_x)),
            self.offset_y + int(round(y2 * self.scale_y)),
        )

    def update_display_metrics(self, width: int, height: int) -> None:
        self.width = max(int(width), 1)
        self.height = max(int(height), 1)
        scale = min(self.width / UI_LOGICAL_WIDTH, self.height / UI_LOGICAL_HEIGHT)
        self.display_width = max(int(round(UI_LOGICAL_WIDTH * scale)), 1)
        self.display_height = max(int(round(UI_LOGICAL_HEIGHT * scale)), 1)
        self.offset_x = max((self.width - self.display_width) // 2, 0)
        self.offset_y = max((self.height - self.display_height) // 2, 0)
        self.scale_x = self.display_width / UI_LOGICAL_WIDTH
        self.scale_y = self.display_height / UI_LOGICAL_HEIGHT
        self.rebuild_click_regions()

    def rebuild_click_regions(self) -> None:
        self.click_regions = [
            ("start_user", self.scale_rect((60, 568, 446, 694))),
            ("admin", self.scale_rect((462, 568, 749, 694))),
            ("start", self.scale_rect((767, 568, 1050, 694))),
            ("restart", self.scale_rect((1087, 568, 1380, 694))),
            ("logs", self.scale_rect((890, 720, 1042, 770))),
        ]

    def on_canvas_configure(self, event) -> None:
        if self.closing:
            return
        if event.width == self.width and event.height == self.height:
            return
        self.update_display_metrics(event.width, event.height)
        if self.resize_job:
            self.root.after_cancel(self.resize_job)
        self.resize_job = self.root.after(80, self.finish_resize)

    def finish_resize(self) -> None:
        self.resize_job = None
        if not self.closing:
            self.render_current_ui()

    def post_ui(self, callback) -> None:
        if not self.closing:
            self.ui_queue.put(callback)

    def drain_ui_queue(self) -> None:
        while True:
            try:
                callback = self.ui_queue.get_nowait()
            except queue.Empty:
                break
            if self.closing:
                continue
            try:
                callback()
            except Exception as exc:
                messagebox.showerror("校园助手本地演示", str(exc))
        if not self.closing:
            self.root.after(80, self.drain_ui_queue)

    def build_ui(self) -> None:
        self.rebuild_click_regions()
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        self.render_current_ui()

    def render_current_ui(self, busy: bool | None = None, message: str = "") -> None:
        img = render_ui(
            self.current_snapshot,
            self.busy if busy is None else busy,
            message,
            output_size=(self.display_width, self.display_height),
        )
        self.ui_image = ImageTk.PhotoImage(img)
        if self.image_item:
            self.canvas.itemconfigure(self.image_item, image=self.ui_image)
            self.canvas.coords(self.image_item, self.offset_x, self.offset_y)
        else:
            self.image_item = self.canvas.create_image(self.offset_x, self.offset_y, image=self.ui_image, anchor="nw")

    def find_click_action(self, x: int, y: int) -> str | None:
        for action, (x1, y1, x2, y2) in self.click_regions:
            if x1 <= x <= x2 and y1 <= y <= y2:
                return action
        return None

    def on_canvas_motion(self, event) -> None:
        action = self.find_click_action(event.x, event.y)
        self.canvas.config(cursor="hand2" if action else "watch" if self.busy else "")

    def on_canvas_press(self, event) -> None:
        self.drag_x = event.x
        self.drag_y = event.y
        self.dragging_window = False

    def on_canvas_drag(self, event) -> None:
        return

    def on_canvas_release(self, event) -> None:
        was_dragging = self.dragging_window
        self.dragging_window = False
        if was_dragging:
            return
        action = self.find_click_action(event.x, event.y)
        if action == "start_user":
            self.run_async(self.start_and_open_user)
        elif action == "admin":
            self.run_async(self.start_and_open_admin)
        elif action == "start":
            self.run_async(self.start_only)
        elif action == "restart":
            self.run_async(self.restart_services)
        elif action == "logs":
            self.run_async(self.open_logs)

    def set_busy(self, busy: bool, message: str | None = None) -> None:
        self.busy = busy
        self.canvas.config(cursor="watch" if busy else "")
        if message:
            self.render_current_ui(True, message)
        elif not busy and not self.closing:
            self.render_current_ui(False)

    def bring_to_front(self) -> None:
        try:
            force_taskbar_entry(self.root)
            self.root.deiconify()
            self.root.lift()
            self.root.attributes("-topmost", True)
            self.root.focus_force()
            self.root.after(900, lambda: self.root.attributes("-topmost", False))
        except Exception:
            pass

    def set_badge(self, key: str, ok: bool, ok_text: str, bad_text: str) -> None:
        badge = self.badges[key]
        bg = COLORS["success_bg"] if ok else COLORS["warn_bg"]
        fg = COLORS["success"] if ok else COLORS["warn"]
        self.canvas.itemconfigure(badge["pill"], fill=bg)
        self.canvas.itemconfigure(badge["dot"], fill=fg)
        self.canvas.itemconfigure(badge["text"], text=ok_text if ok else bad_text, fill=fg)

    def apply_snapshot(self, snapshot: dict[str, bool]) -> None:
        self.current_snapshot = snapshot
        self.render_current_ui(False)

    def refresh_status_async(self) -> None:
        if self.refreshing or self.closing:
            return
        self.refreshing = True

        def worker():
            snapshot = runtime_snapshot()
            if not self.closing:
                self.post_ui(lambda snapshot=snapshot: self.finish_refresh(snapshot))

        threading.Thread(target=worker, daemon=True).start()

    def finish_refresh(self, snapshot: dict[str, bool]) -> None:
        self.refreshing = False
        if not self.busy:
            self.apply_snapshot(snapshot)

    def schedule_refresh(self) -> None:
        if self.closing:
            return
        if not self.busy:
            self.refresh_status_async()
        self.root.after(3500, self.schedule_refresh)

    def run_async(self, func) -> None:
        if self.busy or self.closing:
            return

        def worker():
            try:
                func()
            except Exception as exc:
                if not self.closing:
                    self.post_ui(lambda exc=exc: messagebox.showerror("校园助手本地演示", str(exc)))
            finally:
                if not self.closing:
                    self.post_ui(lambda: self.set_busy(False))
                    self.post_ui(self.refresh_status_async)

        self.set_busy(True, "正在处理，请稍等，服务启动通常需要 5-15 秒...")
        thread = threading.Thread(target=worker, daemon=True)
        self.worker_threads.append(thread)
        thread.start()

    def start_only(self) -> None:
        start_services(False)
        if not self.closing:
            self.post_ui(lambda: messagebox.showinfo("校园助手本地演示", "本地演示服务已启动。"))

    def restart_services(self) -> None:
        start_services(True)
        if not self.closing:
            self.post_ui(lambda: messagebox.showinfo("校园助手本地演示", "本地演示服务已重启。"))

    def restart_and_open_user(self) -> None:
        start_services(True)
        open_user()

    def start_and_open_user(self) -> None:
        start_services(False)
        open_user()

    def start_and_open_admin(self) -> None:
        start_services(False)
        open_admin()

    def stop_only(self) -> None:
        stop_services(False)
        if not self.closing:
            self.post_ui(lambda: messagebox.showinfo("校园助手本地演示", "本地演示服务已停止。"))

    def open_logs(self) -> None:
        ensure_log_dir()
        os.startfile(str(LOG_DIR))

    def on_close(self) -> None:
        if self.closing:
            return
        self.closing = True
        self.busy = True
        self.canvas.config(cursor="watch")
        self.render_current_ui(True, "正在停止本地演示服务，请稍等...")
        self.root.update_idletasks()

        # If a start/restart action is still running, let it settle before
        # killing ports; otherwise it could relaunch a service after cleanup.
        deadline = time.time() + 42
        for thread in list(self.worker_threads):
            remaining = deadline - time.time()
            if remaining <= 0:
                break
            if thread.is_alive():
                thread.join(timeout=min(remaining, 2))

        stop_services(False)
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def show_error(exc: Exception) -> None:
    root = Tk()
    root.withdraw()
    messagebox.showerror("校园助手本地演示", str(exc))
    root.destroy()


def main() -> int:
    mode = exe_stem()
    try:
        launcher_log(f"launcher start mode={mode} root={ROOT}")
        if "停止" in mode or "stop" in mode:
            stop_services(False)
            launcher_log("launcher stop mode finished")
            return 0
        app = LauncherApp()
        if "用户" in mode or "user" in mode:
            app.root.after(250, lambda: app.run_async(app.start_and_open_user))
        elif "后台" in mode or "admin" in mode:
            app.root.after(250, lambda: app.run_async(app.start_and_open_admin))
        elif "重启" in mode or "restart" in mode:
            app.root.after(250, lambda: app.run_async(app.restart_and_open_user))
        app.run()
        launcher_log("launcher exited normally")
        return 0
    except Exception as exc:
        launcher_log("launcher crashed:\n" + "".join(traceback.format_exception(exc)))
        show_error(exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
