# =========================================================
# Project    : DailyFlow+ — Habit & Mood Tracker (GUI)
# Author     : Chen Zhang
# Unit       : COMP9001 Final Project
# Version    : 1.0
# Date       : 2024-06-01
# Description:
#     A simple habit & mood tracker with a Tkinter GUI.
#     Uses only Python's standard library (tkinter, json, datetime, etc.).
#     Data is saved to `habits.json` in the same folder.
#
# Ed:
#     ⚠️ Ed's online environment cannot display GUI windows.
#     Please run locally:
#         python3 main.py
# =========================================================

# Unified date format
DATE_FMT = "%d-%m-%Y"

import tkinter as tk                    # 导入 Tkinter（标准库 GUI）
from tkinter import ttk                 # 引入 ttk，自定义按钮样式（便于改背景色）
import os                               # 文件与路径操作
import json                             # 读写 JSON
import random                           # 随机选择一句鼓励语
from datetime import date, timedelta, datetime    # 日期、时间间隔、时间戳
from tkinter import messagebox          # 弹出提示/确认
from tkinter import font as tkfont      # 字体选择
import calendar

# -----------------------------
# Colors (keep original palette)
# -----------------------------
COLORS = {
    "sidebar_bg":   "#FADADD",   # left pink area
    "main_bg":      "#FFF5F7",   # right pale pink
    "card_bg":      "#FFF0F3",   # card pale pink/white
    "card_border":  "#F2D4DC",
    "btn_card_bg":  "#E6F2E8",   # green button (cards)
    "btn_card_fg":  "#244A34",
    "btn_card_bg_active":"#D7ECD9",
    "btn_toolbar_bg":"#A8D5BA",  # green button (toolbar)
    "btn_toolbar_fg":"#2E3A34",
    "btn_toolbar_bg_active":"#B8E0C8",
    "title_fg":     "#1F1F1F",
    "border":       "#EAD5DD",
    "hint_fg":      "#525252",
    "dot_empty": "#D9D9D9",
    "dot_outline": "#2E7D32",
}

# -----------------------------
# Mood options
# -----------------------------
MOOD_OPTIONS = [
    ("happy",    "😊"),
    ("neutral",  "😐"),
    ("tired",    "😪"),
    ("stressed", "😰"),
]
MOOD_ICON = {}
for k, v in MOOD_OPTIONS:
    MOOD_ICON[k] = v

# Unified Morandi mood colors for dots, trend, and calendar
MOOD_COLOR = {
    "happy":    COLORS["btn_card_bg"],  # soft green (theme)
    "neutral":  "#B7C0C7",              # blue-grey (muted)
    "tired":    "#D9C3A3",              # warm sand
    "stressed": "#CFA2B5",              # dusty mauve
    None:        COLORS["dot_empty"],    # empty grey
}
MOOD_OUTLINE = {
    "happy":    "#6CCB7E",   # darker green
    "neutral":  "#7E8A93",   # darker blue-grey
    "tired":    "#B48C5A",   # darker warm sand
    "stressed": "#A76A86",   # darker dusty mauve
    None:        "#BFBFBF",   # darker empty grey
}

BI_MOTIVATIONS = [
    "Consistency builds habits ✨",
    "You’re doing amazing today 💕",
    "Small steps every day 🌱",
    "You’re growing beautifully 🌸",
    "Keep it up — future you will thank you 🌿",
    "Progress, not perfection ⭐️",
    "Show up for yourself today ☀️",
    "One step at a time 🚶",
    "Tiny wins add up 📈",
    "Your effort matters, always 💫",
    "Breathe, do, smile 🙂",
    "Trust the process 🔄",
    "Today is a fresh start 🌅",
    "You’re building a better you 🧩",
    "Momentum starts now 🚀",
    "Proud of you for trying 🙌",
    "Discipline is self‑love 💚",
    "Do it for future you 🧭",
    "Keep going — you’ve got this 💪",
    "Focus on the next small action 🎯",
]

# -----------------------------
# Data persistence
# -----------------------------
DATA_FILE = "habits.json"
DATA = {"habits": {}, "recent": []}       # + recent log: list of {dt, habit, mood}
SELECTED = {"habit": None}  # currently selected habit name

def load_data():
    """Load data from JSON file."""
    if not os.path.exists(DATA_FILE):
        return {"habits": {}, "recent": []}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
            if isinstance(d, dict):
                if "habits" not in d or not isinstance(d["habits"], dict):
                    d["habits"] = {}
                if "recent" not in d or not isinstance(d["recent"], list):
                    d["recent"] = []
                # 兼容旧数据：为所有习惯补上 done 字段
                for h in d.get("habits", {}).values():
                    if isinstance(h, dict):
                        h.setdefault("done", {})
                return d
    except Exception as e:
        print(f"[Warning] Failed to load habits.json: {e}")
    return {"habits": {}, "recent": []}

def save_data():
    """Save data to JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(DATA, f, ensure_ascii=False, indent=2)

def today_str():
    """Return today's date in YYYY-MM-DD."""
    return date.today().isoformat()

def parse_date(s):
    """Parse 'YYYY-MM-DD' or 'DD-MM-YYYY' (trims spaces). Return date or None."""
    try:
        s = (s or "").strip()
        parts = s.split("-")
        if len(parts) != 3:
            return None
        a, b, c = (p.strip() for p in parts)
        # try YYYY-MM-DD first
        if len(a) == 4 and a.isdigit() and b.isdigit() and c.isdigit():
            y, m, d = int(a), int(b), int(c)
        else:
            # try DD-MM-YYYY
            if not (a.isdigit() and b.isdigit() and c.isdigit() and len(c) == 4):
                return None
            d, m, y = int(a), int(b), int(c)
        return date(y, m, d)
    except Exception:
        return None

def fmt_date_obj(d):
    """Format a date object as DD-MM-YYYY for display."""
    try:
        return d.strftime(DATE_FMT)
    except Exception:
        return "--"

def fmt_date_iso(iso_s):
    """Format an ISO date string YYYY-MM-DD as DD-MM-YYYY for display."""
    d = parse_date(iso_s)
    return d.strftime(DATE_FMT) if d else iso_s

def daterange(d1, d2):
    """Return list of days [d1..d2]."""
    out = []
    cur = d1
    while cur <= d2:
        out.append(cur)
        cur += timedelta(days=1)
    return out

def ensure_habit(name):
    """Create habit shell if not exists."""
    if name not in DATA["habits"]:
        DATA["habits"][name] = {"history": {}, "last": None, "done": {}}
    else:
        # 兼容旧数据：没有 done 字段就补一个
        DATA["habits"][name].setdefault("done", {})

def list_habits():
    return list(DATA["habits"].keys())

def get_habit(name):
    return DATA["habits"].get(name)

def is_done(h, ds):
    """今天是否完成？优先看 done[ds]；没有则兼容旧数据：history 里有 mood 也算完成。"""
    if not h:
        return False
    if h.get("done", {}).get(ds):
        return True
    return ds in h.get("history", {})

def compute_streak(name):
    """Count consecutive days from today backwards (based on 'done')."""
    h = get_habit(name)
    if not h:
        return 0
    s = 0
    cur = date.today()
    while is_done(h, cur.isoformat()):
        s += 1
        cur -= timedelta(days=1)
    return s

# --- Recent log helpers ---
def push_recent(habit, mood):
    """Append a newest action to recent list, keep at most 50, and drop removed habits."""
    DATA.setdefault("recent", [])
    DATA["recent"].insert(0, {
        "dt": datetime.now().isoformat(timespec="seconds"),
        "habit": habit,
        "mood": mood,
    })
    # remove entries whose habit was deleted, then cap length to 50
    DATA["recent"] = [r for r in DATA["recent"] if r.get("habit") in DATA["habits"]][:50]

# ===================== GUI =====================

# 创建主窗口

root = tk.Tk()
root.title("DailyFlow+ – Habit & Mood Tracker")
root.configure(bg=COLORS["main_bg"])
root.geometry("1260x700")

# ----- Rounded fonts (pick available family) -----
def _pick_family(candidates):
    # 依次选择第一个系统存在的字体
    have = set(tkfont.families())
    for fam in candidates:
        if fam in have:
            return fam
    return "Helvetica"

_EN_ROUNDED = ("Avenir Next Rounded", "SF Pro Rounded", "Arial Rounded MT Bold")
_CN_ROUNDED = ("PingFang SC", "Hiragino Sans GB", "Microsoft YaHei UI")

FONT_TITLE = tkfont.Font(family=_pick_family(_EN_ROUNDED + _CN_ROUNDED), size=20, weight="bold")

_EN_CUTE = (
    "Avenir Next Rounded",
    "SF Pro Rounded",
    "Arial Rounded MT Bold",
)
_ZH_CUTE = (
    "PingFang SC",
    "Hiragino Sans GB",
    "Microsoft YaHei UI",
)

 # English line uses a slightly larger, bold rounded font
FONT_ENC_EN = tkfont.Font(family=_pick_family(_EN_CUTE), size=18, weight="bold")
# Chinese line keeps the cute rounded CJK font
FONT_ENC_ZH = tkfont.Font(family=_pick_family(_ZH_CUTE), size=16)
# Section title stays bold
FONT_ENC_B  = tkfont.Font(family=_pick_family(_ZH_CUTE + _EN_CUTE), size=14, weight="bold")
# Right column encouragement title font
FONT_ENC_TITLE = tkfont.Font(family=_pick_family(_ZH_CUTE + _EN_CUTE), size=20, weight="bold")

# Title
title = tk.Label(
    root,
    text="DailyFlow+  Habit & Mood Tracker 🌿",
    bg=COLORS["main_bg"],
    fg=COLORS["title_fg"],
    font=FONT_TITLE
)
title.pack(pady=(10, 8))

# Toolbar (green buttons)
toolbar = tk.Frame(root, bg=COLORS["main_bg"])
toolbar.pack(pady=(0, 6))

# Use ttk with 'clam' theme so background colors apply on macOS
# --- ttk styles for green buttons (macOS-friendly) ---
style = ttk.Style()
try:
    # 'clam' allows background color changes; native Aqua often ignores bg
    style.theme_use('clam')
except Exception:
    pass

# toolbar buttons (soft green)
style.configure(
    "Green.TButton",
    background=COLORS["btn_toolbar_bg"],
    foreground=COLORS["btn_toolbar_fg"],
    padding=(12, 6)
)
style.map(
    "Green.TButton",
    background=[("active", COLORS["btn_toolbar_bg_active"]), ("pressed", COLORS["btn_toolbar_bg_active"])],
    relief=[("pressed", "sunken")]
)

# small variant for compact actions (e.g., Shuffle on the right panel)
style.configure(
    "SmallGreen.TButton",
    background=COLORS["btn_toolbar_bg"],
    foreground=COLORS["btn_toolbar_fg"],
    padding=(8, 3),
    font=("Arial", 10)
)
style.map(
    "SmallGreen.TButton",
    background=[("active", COLORS["btn_toolbar_bg_active"]), ("pressed", COLORS["btn_toolbar_bg_active"])],
    relief=[("pressed", "sunken")]
)


# card buttons (even lighter green)
style.configure(
    "CardGreen.TButton",
    background=COLORS["btn_card_bg"],
    foreground=COLORS["btn_card_fg"],
    padding=(14, 6)
)
style.map(
    "CardGreen.TButton",
    background=[("active", COLORS["btn_card_bg_active"]), ("pressed", COLORS["btn_card_bg_active"])],
    relief=[("pressed", "sunken")]
)

# danger buttons (for destructive actions)
style.configure(
    "Danger.TButton",
    background="#F4B1B8",
    foreground="#5A1E24",
    padding=(14, 6)
)
style.map(
    "Danger.TButton",
    background=[("active", "#F7C2C7"), ("pressed", "#F7C2C7")],
    relief=[("pressed", "sunken")]
)
# -----------------------------------------------------


def make_toolbar_btn(parent, text, command_func):
    # Use ttk.Button + custom style so the light green shows correctly on macOS
    btn = ttk.Button(parent, text=text, style="Green.TButton", command=command_func)
    btn.pack(side="left", padx=10)
    return btn


# Main body: left cards + right side
body = tk.Frame(root, bg=COLORS["main_bg"])
body.pack(fill="both", expand=True, padx=8, pady=(0, 8))

left_wrap = tk.Frame(body, bg=COLORS["sidebar_bg"])
left_wrap.pack(side="left", fill="both", expand=True, padx=(4, 8), pady=4)

right = tk.Frame(body, bg=COLORS["main_bg"], width=240)
right.pack(side="right", fill="y", padx=(0, 6), pady=4)
right.pack_propagate(False)

# Right header: two lines, left/right aligned
enc_header = tk.Frame(right, bg=COLORS["main_bg"])
enc_header.pack(fill="x", padx=0, pady=(4, 4))

lbl_today = tk.Label(
    enc_header,
    text="Today's",
    bg=COLORS["main_bg"],
    fg=COLORS["title_fg"],
    font=FONT_ENC_TITLE,
    anchor="w",  # left align
    justify="left"
)
lbl_today.pack(fill="x")

lbl_enc = tk.Label(
    enc_header,
    text="Encouragement 💖",
    bg=COLORS["main_bg"],
    fg=COLORS["title_fg"],
    font=FONT_ENC_TITLE,
    anchor="e",  # right align
    justify="right"
)
lbl_enc.pack(fill="x")

# Current date label (right aligned under title)
today_label = tk.Label(
    enc_header,
    text=fmt_date_obj(date.today()),
    bg=COLORS["main_bg"],
    fg=COLORS["hint_fg"],
    font=("Arial", 11)
)
today_label.pack(anchor="e", pady=(0, 4))

 # English line only
en0 = BI_MOTIVATIONS[0]
enc_msg_en = tk.Label(
    right,
    text=f"✨ {en0}",
    bg=COLORS["main_bg"],
    fg=COLORS["title_fg"],
    wraplength=210,
    justify="left",
    font=FONT_ENC_EN
)
enc_msg_en.pack(anchor="nw", pady=(8, 4))

# Helper: pick a random encouragement and update the English label
def set_random_tip():
    # pick one sentence and update the English line
    en = random.choice(BI_MOTIVATIONS)
    enc_msg_en.config(text=f"✨ {en}")

set_random_tip()  # show a random encouragement on startup

# Shuffle button (right aligned under encouragement text)
shuffle_btn = ttk.Button(
    right, text="↻ Shuffle", style="SmallGreen.TButton",
    command=set_random_tip
)
shuffle_btn.pack(anchor="e", pady=(0, 6))

# Section containers on the right
right_sep1 = tk.Frame(right, bg=COLORS["border"], height=1)
right_sep1.pack(fill="x", padx=2, pady=(2, 8))

right_summary = tk.Frame(right, bg=COLORS["main_bg"])
right_summary.pack(fill="x", padx=2, pady=(0, 10))

right_sep2 = tk.Frame(right, bg=COLORS["border"], height=1)
right_sep2.pack(fill="x", padx=2, pady=(2, 8))

right_activity = tk.Frame(right, bg=COLORS["main_bg"])
right_activity.pack(fill="x", padx=2, pady=(0, 10))

right_sep3 = tk.Frame(right, bg=COLORS["border"], height=1)
right_sep3.pack(fill="x", padx=2, pady=(2, 8))

right_selected = tk.Frame(right, bg=COLORS["main_bg"])
right_selected.pack(fill="x", padx=2, pady=(0, 10))


# --------- Right panel helper functions ---------
def _clear_children(frame):
    for w in frame.winfo_children():
        w.destroy()

def _mini_progress(done, total):
    # Build a 10-cell mini bar string
    fill = int(round((done / total) * 10)) if total else 0
    return "■" * fill + "·" * (10 - fill)

def refresh_right_panel():
    # --- Today Summary ---
    _clear_children(right_summary)
    tk.Label(
        right_summary, text="🌿 Today Summary",
        bg=COLORS["main_bg"], fg=COLORS["title_fg"], font=("Arial", 12, "bold")
    ).pack(anchor="w")

    names = list_habits()
    today = today_str()
    done = 0
    for n in names:
        h = get_habit(n)
        if h and is_done(h, today):
            done += 1
    total = len(names)
    bar = _mini_progress(done, total)
    tk.Label(
        right_summary,
        text=f"{bar}  {done}/{total} habits",
        bg=COLORS["main_bg"], fg=COLORS["hint_fg"], font=("Arial", 11)
    ).pack(anchor="w", pady=(2, 0))

    # --- Recent Activity (last 5) ---
    _clear_children(right_activity)
    tk.Label(
        right_activity, text="📅 Recent Activity",
        bg=COLORS["main_bg"], fg=COLORS["title_fg"], font=("Arial", 12, "bold")
    ).pack(anchor="w")

    # gather last 5 marks using the recent log (already newest-first)
    events = []
    for r in DATA.get("recent", []):
        nm = r.get("habit")
        if nm in DATA.get("habits", {}):
            events.append((r.get("dt", ""), nm, r.get("mood")))
    shown = 0
    for dt_str, n, mood in events[:5]:
        # 显示 DD-MM
        d = parse_date(dt_str[:10]) if dt_str else None
        day_txt = d.strftime('%d-%m') if d else "--"

        # Show a friendly label for a clear action; otherwise show the mood emoji
        if mood == "cleared":
            emoji = "🧽"
            tail  = "clear"
        else:
            emoji = MOOD_ICON.get(mood, "—")
            tail  = ""

        txt = f"{day_txt}  {n}  {emoji}"
        if tail:
            txt += f" {tail}"

        tk.Label(
            right_activity,
            text=txt,
            bg=COLORS["main_bg"], fg=COLORS["hint_fg"], font=("Arial", 11)
        ).pack(anchor="w")
        shown += 1
    if shown == 0:
        tk.Label(
            right_activity, text="(no recent activity)",
            bg=COLORS["main_bg"], fg=COLORS["hint_fg"], font=("Arial", 10)
        ).pack(anchor="w")

    # --- Selected Habit · Last 7 days ---
    _clear_children(right_selected)
    sel = SELECTED.get("habit")
    # Right panel section title uses the new name
    title_text = f"📊 7-Day Mood Dots — {sel}" if sel else "📊 7-Day Mood Dots"
    tk.Label(
        right_selected, text=title_text,
        bg=COLORS["main_bg"], fg=COLORS["title_fg"], font=("Arial", 12, "bold")
    ).pack(anchor="w")

    if not sel:
        tk.Label(
            right_selected, text="(tap a card on the left to select)",
            bg=COLORS["main_bg"], fg=COLORS["hint_fg"], font=("Arial", 10)
        ).pack(anchor="w")
        return

    h = get_habit(sel)
    if not h:
        return
    e = date.today()
    s = e - timedelta(days=6)
    days = daterange(s, e)
    by = h["history"]


    # small canvas for 7-day dots
    cv = tk.Canvas(right_selected, width=220, height=52, bg=COLORS["main_bg"],
                   highlightthickness=0)
    cv.pack(anchor="w", pady=(2, 0))

    x0 = 14
    step = 30
    y0 = 20
    done7 = 0
    for i, d in enumerate(days):
        ds = d.isoformat()
        m = by.get(ds)
        if is_done(h, ds):
            done7 += 1
        x = x0 + i * step
        r = 6
        fill = MOOD_COLOR.get(m, COLORS["dot_empty"])
        outline = MOOD_OUTLINE.get(m, MOOD_OUTLINE[None])
        cv.create_oval(x - r, y0 - r, x + r, y0 + r, fill=fill, outline=outline, width=1)
        # put emoji under the dot (small)
        cv.create_text(x, y0 + 16, text=MOOD_ICON.get(m, "—"), font=("Arial", 10))

    tk.Label(
        right_selected, text=f"({done7}/7 days complete)",
        bg=COLORS["main_bg"], fg=COLORS["hint_fg"], font=("Arial", 10)
    ).pack(anchor="w", pady=(2, 0))


# Cards area (scrollable)
cards_outer = tk.Frame(left_wrap, bg=COLORS["sidebar_bg"])
cards_outer.pack(fill="both", expand=True, padx=4, pady=4)

cards_canvas = tk.Canvas(cards_outer, bg=COLORS["sidebar_bg"], highlightthickness=0)
cards_canvas.pack(side="left", fill="both", expand=True)

cards_scroll = tk.Scrollbar(cards_outer, orient="vertical", command=cards_canvas.yview)
cards_scroll.pack(side="right", fill="y")
cards_canvas.configure(yscrollcommand=cards_scroll.set)

cards_frame = tk.Frame(cards_canvas, bg=COLORS["sidebar_bg"])
canvas_window = cards_canvas.create_window((0, 0), window=cards_frame, anchor="nw")

def _update_scrollregion(_=None):
    """Refresh scroll region."""
    cards_canvas.configure(scrollregion=cards_canvas.bbox("all"))

# 绑定内部 Frame 大小变化，更新滚动范围
cards_frame.bind("<Configure>", _update_scrollregion)

# Keep inner frame width equal to canvas width, so cards stretch full row
def _sync_inner_width(_=None):
    cards_canvas.itemconfig(canvas_window, width=cards_canvas.winfo_width())
cards_canvas.bind("<Configure>", _sync_inner_width)


# Center a popup at the center of the parent window, keeping above parent (not globally topmost)
def center_on_parent(win, parent, y_bias=0):
    """
    Place dialog at the center of the given parent frame (not screen center).
    The dialog stays above its parent window. `y_bias` lets us shift upward
    (use a negative value like -60 to move a bit higher).
    """
    try:
        win.withdraw()              # hide to avoid initial flash
        parent.update_idletasks()
        win.update_idletasks()

        # parent geometry (absolute screen coordinates)
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        if pw <= 1 or ph <= 1:
            parent.update_idletasks()
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()

        ww = win.winfo_reqwidth()
        wh = win.winfo_reqheight()

        # true center inside the parent area; allow negative offset if child wider
        x = px + (pw - ww) // 2 - 40
        y = py + (ph - wh) // 2 + y_bias
        # keep within parent's vertical bounds
        y = max(py, min(y, py + max(0, ph - wh)))

        win.geometry(f"+{x}+{y}")
        win.deiconify()
        win.lift(parent)
        try:
            win.attributes("-topmost", False)
        except Exception:
            pass
    except Exception:
        win.deiconify()

# Themed confirm dialog replacing messagebox.askyesno
def confirm_delete_dialog(habit_name):
    # Themed confirm dialog replacing messagebox.askyesno
    top = tk.Toplevel(root)
    top.title("Confirm")
    top.configure(bg=COLORS["main_bg"])
    top.resizable(False, False)
    top.transient(root)
    center_on_parent(top, left_wrap, y_bias=-60)

    card = tk.Frame(
        top, bg=COLORS["card_bg"],
        highlightthickness=1, highlightbackground=COLORS["card_border"]
    )
    card.pack(padx=18, pady=18)

    # header icon + title
    icon = tk.Label(card, text="🗑️", bg=COLORS["card_bg"], font=("Arial", 28))
    icon.grid(row=0, column=0, columnspan=2, pady=(6, 2))
    tk.Label(
        card, text="Delete this habit?", bg=COLORS["card_bg"],
        fg=COLORS["title_fg"], font=("Arial", 14, "bold")
    ).grid(row=1, column=0, columnspan=2, pady=(0, 6))

    # message line
    tk.Label(
        card,
        text=f"‘{habit_name}’ will be removed permanently.",
        bg=COLORS["card_bg"], fg=COLORS["hint_fg"]
    ).grid(row=2, column=0, columnspan=2, padx=14, pady=(0, 10))

    result = {"ok": False}

    def do_cancel():
        result["ok"] = False
        top.destroy()

    def do_delete():
        result["ok"] = True
        top.destroy()

    # Keyboard bindings
    top.bind("<Return>", lambda e=None: do_delete())
    top.bind("<Escape>", lambda e=None: do_cancel())

    # buttons
    btns = tk.Frame(card, bg=COLORS["card_bg"])
    btns.grid(row=3, column=0, columnspan=2, sticky="e", padx=10, pady=(2, 10))

    ttk.Button(btns, text="Cancel", style="CardGreen.TButton", command=do_cancel)\
        .pack(side="left", padx=(0, 8))
    ttk.Button(btns, text="Delete", style="Danger.TButton", command=do_delete)\
        .pack(side="left")

    top.grab_set()
    root.wait_window(top)
    return result["ok"]


# ---- Themed alert helpers (pretty dialogs) ----
def notify_dialog(title_text, message_text, icon="✅"):
    top = tk.Toplevel(root)
    top.title(title_text)
    top.configure(bg=COLORS["main_bg"])
    top.resizable(False, False)
    top.transient(root)
    center_on_parent(top, left_wrap, y_bias=-60)

    card = tk.Frame(top, bg=COLORS["card_bg"],
                    highlightthickness=1, highlightbackground=COLORS["card_border"])
    card.pack(padx=18, pady=18)

    # Icon and title
    tk.Label(card, text=icon, bg=COLORS["card_bg"], font=("Arial", 28)).pack(pady=(6, 2))
    tk.Label(card, text=title_text, bg=COLORS["card_bg"], fg=COLORS["title_fg"],
             font=("Arial", 14, "bold")).pack(pady=(0, 4))

    # Message (wrap; monospace if it looks like a filename)
    lab = tk.Label(card, text=message_text, bg=COLORS["card_bg"], fg=COLORS["hint_fg"],
                   font=("Menlo", 11), wraplength=380, justify="center")
    lab.pack(padx=12, pady=(2, 10))

    ttk.Button(card, text="OK", style="CardGreen.TButton", command=top.destroy).pack(pady=(0, 8))

    top.grab_set()
    root.wait_window(top)

def error_dialog(title_text, message_text):
    notify_dialog(title_text, message_text, icon="⚠️")

# Themed warning dialog (light tip)
def warn_dialog(message_text, title_text="Tip"):
    # 统一风格的浅色提示弹窗
    notify_dialog(title_text, message_text, icon="💡")

# ------------- Dialogs -------------

def pick_mood_dialog(default=None, title_text="Update Mood"):
    """Return selected mood string or None (if 'Clear today' is chosen)."""
    # 弹出选择心情的子窗口
    top = tk.Toplevel(root)
    top.title(title_text)
    top.configure(bg=COLORS["main_bg"])
    top.resizable(False, False)
    top.transient(root)           # keep above the main window
    center_on_parent(top, left_wrap, y_bias=-60)   # place dialog in the center

    card = tk.Frame(top, bg=COLORS["card_bg"],
                    highlightthickness=1, highlightbackground=COLORS["card_border"])
    card.pack(padx=16, pady=16)

    tk.Label(card, text=title_text, bg=COLORS["card_bg"], fg=COLORS["title_fg"],
             font=("Arial", 13, "bold")).pack(anchor="w", padx=10, pady=(10, 6))

    row = tk.Frame(card, bg=COLORS["card_bg"])
    row.pack(anchor="w", padx=6, pady=(0, 6))

    mood_var = tk.StringVar(value=default or "")
    btns = []

    def sync_ui():
        """Refresh selected preview and button color."""
        code = mood_var.get() or None
        emoji = MOOD_ICON.get(code, "—")
        preview.config(text=f"Selected: {emoji} {code or ''}".strip())
        for c, b in btns:
            b.configure(bg=COLORS["btn_card_bg_active"] if c == code else COLORS["btn_card_bg"])

    for code, emoji in MOOD_OPTIONS:
        b = tk.Radiobutton(
            row, text=f"{emoji} {code}", value=code, variable=mood_var,
            indicatoron=False, padx=12, pady=6, bd=0, relief="flat",
            bg=COLORS["btn_card_bg"], fg=COLORS["btn_card_fg"],
            activebackground=COLORS["btn_card_bg_active"],
            command=sync_ui
        )
        b.pack(side="left", padx=6, pady=2)
        btns.append((code, b))

    preview = tk.Label(card, text="Selected: —", bg=COLORS["card_bg"], fg="#555")
    preview.pack(anchor="w", padx=10, pady=(0, 8))
    sync_ui()

    result = {"mood": None}
    def ok():
        if not mood_var.get():
            warn_dialog("Please select a mood.")
            return
        result["mood"] = mood_var.get()
        top.destroy()
    def cancel():
        top.destroy()
    def clear_today():
        result["mood"] = None
        top.destroy()

    # Keyboard bindings
    top.bind("<Return>", lambda e=None: ok())
    top.bind("<Escape>", lambda e=None: cancel())

    bar = tk.Frame(card, bg=COLORS["card_bg"])
    bar.pack(padx=10, pady=(0, 10), anchor="e")
    tk.Button(bar, text="OK", bg=COLORS["btn_toolbar_bg"], fg=COLORS["btn_toolbar_fg"],
              command=ok).pack(side="left", padx=6)
    tk.Button(bar, text="Cancel", command=cancel).pack(side="left", padx=6)
    tk.Button(bar, text="Clear today", command=clear_today).pack(side="left", padx=6)

    top.grab_set()
    root.wait_window(top)
    # If user clicked "Clear today", return None
    return result["mood"]

def add_habit_dialog():
    """Create a new habit with Day-1 mood."""
    # 添加习惯的弹窗
    top = tk.Toplevel(root)
    top.title("Add Habit")
    top.configure(bg=COLORS["main_bg"])
    top.resizable(False, False)
    top.transient(root)
    center_on_parent(top, left_wrap, y_bias=-100)

    card = tk.Frame(top, bg=COLORS["card_bg"],
                    highlightthickness=1, highlightbackground=COLORS["card_border"])
    card.pack(padx=16, pady=16)

    tk.Label(card, text="Add Habit", bg=COLORS["card_bg"], fg=COLORS["title_fg"],
             font=("Arial", 13, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 6))

    tk.Label(card, text="Habit name:", bg=COLORS["card_bg"]).grid(row=1, column=0, sticky="w", padx=10)
    name_var = tk.StringVar()
    ent = tk.Entry(card, textvariable=name_var, width=30)
    ent.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 8))
    ent.focus_set()

    tk.Label(card, text="Mood today:", bg=COLORS["card_bg"]).grid(row=3, column=0, sticky="w", padx=10, pady=(6, 0))
    mood_var = tk.StringVar(value="happy")
    row = tk.Frame(card, bg=COLORS["card_bg"])
    row.grid(row=4, column=0, columnspan=2, sticky="w", padx=6, pady=(2, 6))

    btns = []
    def sync_ui():
        code = mood_var.get()
        emoji = MOOD_ICON.get(code, "—")
        preview.config(text=f"Selected: {emoji} {code}")
        for c, b in btns:
            b.configure(bg=COLORS["btn_card_bg_active"] if c == code else COLORS["btn_card_bg"])

    for code, emoji in MOOD_OPTIONS:
        b = tk.Radiobutton(row, text=f"{emoji} {code}", value=code, variable=mood_var,
                           indicatoron=False, padx=12, pady=6, bd=0, relief="flat",
                           bg=COLORS["btn_card_bg"], fg=COLORS["btn_card_fg"],
                           activebackground=COLORS["btn_card_bg_active"], command=sync_ui)
        b.pack(side="left", padx=6, pady=2)
        btns.append((code, b))

    preview = tk.Label(card, text="Selected: 😊 happy", bg=COLORS["card_bg"], fg="#555")
    preview.grid(row=5, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 8))
    sync_ui()

    def ok():
        name = name_var.get().strip()
        if not name:
            warn_dialog("Please enter a habit name.")
            return
        names_lower = {n.lower() for n in DATA["habits"]}
        if name.lower() in names_lower:
            warn_dialog("This habit already exists.")
            return
        mood = mood_var.get()
        ensure_habit(name)
        DATA["habits"][name]["history"][today_str()] = mood
        DATA["habits"][name]["last"] = mood
        DATA["habits"][name].setdefault("done", {})[today_str()] = True
        save_data()
        top.destroy()
        render_cards()

    def cancel():
        top.destroy()

    # Keyboard bindings
    top.bind("<Return>", lambda e=None: ok())
    top.bind("<Escape>", lambda e=None: cancel())

    bar = tk.Frame(card, bg=COLORS["card_bg"])
    bar.grid(row=6, column=0, columnspan=2, sticky="e", padx=10, pady=(0, 10))
    tk.Button(bar, text="OK", bg=COLORS["btn_toolbar_bg"], fg=COLORS["btn_toolbar_fg"], command=ok).pack(side="left", padx=6)
    tk.Button(bar, text="Cancel", command=cancel).pack(side="left", padx=6)

def range_dialog(title_text, default_days, allow_last=True, limit_days=None):
    """Return (habit, start, end) or (None, None, None)."""
    # 统一的时间范围弹窗；可限制最大天数，并禁选未来日期
    top = tk.Toplevel(root)
    top.title(title_text)
    top.configure(bg=COLORS["main_bg"])
    top.resizable(False, False)
    top.transient(root)
    center_on_parent(top, left_wrap, y_bias=-60)

    card = tk.Frame(top, bg=COLORS["card_bg"],
                    highlightthickness=1, highlightbackground=COLORS["card_border"])
    card.pack(padx=16, pady=16)

    tk.Label(card, text=title_text, bg=COLORS["card_bg"], fg=COLORS["title_fg"],
             font=("Arial", 13, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 6))

    tk.Label(card, text="Habit:", bg=COLORS["card_bg"]).grid(row=1, column=0, sticky="e", padx=8)
    names = list_habits()
    if not names:
        notify_dialog(title_text, "No habits yet.", icon="💬")
        top.destroy()
        return None, None, None
    habit_var = tk.StringVar(value=SELECTED["habit"] or names[0])
    tk.OptionMenu(card, habit_var, *names).grid(row=1, column=1, sticky="w", padx=8, pady=2)

    tk.Label(card, text="Range:", bg=COLORS["card_bg"]).grid(row=2, column=0, sticky="e", padx=8)
    range_var = tk.StringVar(value="last")
    if allow_last:
        tk.Radiobutton(card, text=f"Last {default_days} days (incl. today)", variable=range_var, value="last",
                       bg=COLORS["card_bg"]).grid(row=2, column=1, sticky="w")
    tk.Radiobutton(card, text=f"Custom ({DATE_FMT})", variable=range_var, value="custom",
                   bg=COLORS["card_bg"]).grid(row=3, column=1, sticky="w")

    today_d = date.today()
    def_start = today_d - timedelta(days=default_days - 1)

    tk.Label(card, text="Start date:", bg=COLORS["card_bg"]).grid(row=4, column=0, sticky="e", padx=8, pady=(6, 0))
    tk.Label(card, text="End date:",   bg=COLORS["card_bg"]).grid(row=5, column=0, sticky="e", padx=8)

    ent_s = tk.Entry(card, width=18)
    ent_e = tk.Entry(card, width=18)
    ent_s.insert(0, fmt_date_obj(def_start))
    ent_e.insert(0, fmt_date_obj(today_d))
    ent_s.grid(row=4, column=1, sticky="w", padx=8, pady=(6, 0))
    ent_e.grid(row=5, column=1, sticky="w", padx=8)

    result = {"ok": False, "habit": None, "start": None, "end": None}

    def ok():
        h = habit_var.get().strip()
        if range_var.get() == "last":
            s, e = def_start, today_d
        else:
            s = parse_date(ent_s.get().strip())
            e = parse_date(ent_e.get().strip())
            if (s is None) or (e is None):
                error_dialog("Invalid", "Please enter valid dates.")
                return
            if s > e:
                error_dialog("Invalid", "Start date cannot be after end date.")
                return
            if s > date.today() or e > date.today():
                error_dialog("Invalid", "Dates cannot be in the future.")
                return
            if limit_days is not None and (e - s).days + 1 > limit_days:
                error_dialog("Invalid", f"Range too long (max {limit_days} days).")
                return
        result["ok"] = True
        result["habit"] = h
        result["start"] = s
        result["end"] = e
        top.destroy()

    def cancel():
        top.destroy()

    # Keyboard bindings
    top.bind("<Return>", lambda e=None: ok())
    top.bind("<Escape>", lambda e=None: cancel())

    bar = tk.Frame(card, bg=COLORS["card_bg"])
    bar.grid(row=6, column=0, columnspan=2, sticky="e", padx=10, pady=(8, 10))
    tk.Button(bar, text="Show", bg=COLORS["btn_toolbar_bg"], fg=COLORS["btn_toolbar_fg"], command=ok).pack(side="left", padx=6)
    tk.Button(bar, text="Cancel", command=cancel).pack(side="left", padx=6)

    top.grab_set()
    root.wait_window(top)
    if result["ok"]:
        return result["habit"], result["start"], result["end"]
    return None, None, None

# ------------- Actions -------------

def do_report():
    """Open a report window with in-place Export button."""
    habit, s, e = range_dialog("Report", default_days=7, allow_last=True, limit_days=None)
    if not habit:
        return
    h = get_habit(habit)
    by = h["history"]

    # Build report text (same content as before)
    lines = []
    lines.append(f"Report — {habit}")
    lines.append(f"Range  — {fmt_date_obj(s)} to {fmt_date_obj(e)}")
    lines.append("-" * 40)
    done_cnt = 0
    counts = {"happy": 0, "neutral": 0, "tired": 0, "stressed": 0}
    for d in daterange(s, e):
        ds = d.isoformat()
        m = by.get(ds)
        icon = MOOD_ICON.get(m, "—")
        stamp = "✓" if is_done(h, ds) else "—"
        lines.append(f"{fmt_date_iso(ds)}: {stamp}  {icon} {m or '—'}")
        if is_done(h, ds):
            done_cnt += 1
        if m in counts:
            counts[m] += 1
    lines.append("-" * 40)
    total = len(daterange(s, e))
    fill = int(round((done_cnt / total) * 10)) if total else 0
    bar = "█" * fill + "░" * (10 - fill)
    lines.append(f"Completion: [{bar}] {done_cnt}/{total} days")
    lines.append(f"😊 {counts['happy']}  😐 {counts['neutral']}  😪 {counts['tired']}  😰 {counts['stressed']}")
    report_text = "\n".join(lines)

    # Custom window with Export + Close
    win = tk.Toplevel(root)
    win.title("Report")
    win.configure(bg=COLORS["main_bg"])
    win.resizable(False, False)
    win.transient(root)
    center_on_parent(win, left_wrap, y_bias=-80)

    # Title
    tk.Label(
        win, text=f"Report — {habit}",
        bg=COLORS["main_bg"], fg=COLORS["title_fg"],
        font=("Arial", 13, "bold")
    ).pack(anchor="w", padx=12, pady=(10, 4))
    tk.Label(
        win, text=f"{fmt_date_obj(s)} to {fmt_date_obj(e)}",
        bg=COLORS["main_bg"], fg=COLORS["hint_fg"]
    ).pack(anchor="w", padx=12, pady=(0, 6))

    # Scrollable text area
    wrap = tk.Frame(win, bg=COLORS["main_bg"])
    wrap.pack(fill="both", expand=True, padx=12, pady=(0, 10))

    scroll = tk.Scrollbar(wrap, orient="vertical")
    txt = tk.Text(
        wrap, width=60, height=22, wrap="word",
        bg=COLORS["card_bg"], fg=COLORS["title_fg"],
        highlightthickness=1, highlightbackground=COLORS["border"],
        font=("Menlo", 12)  # monospaced for neat layout
    )
    scroll.config(command=txt.yview)
    txt.config(yscrollcommand=scroll.set)
    txt.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    txt.insert("1.0", report_text)
    txt.config(state="disabled")

    # Button bar (Export + Close)
    barf = tk.Frame(win, bg=COLORS["main_bg"])
    barf.pack(padx=12, pady=(0, 12), anchor="e")

    def do_export_now():
        # export to a TXT file with an auto name in the current folder
        fname = f"report_{habit.replace(' ', '_')}_{fmt_date_obj(s)}_to_{fmt_date_obj(e)}.txt"
        try:
            with open(fname, "w", encoding="utf-8") as f:
                f.write(report_text + "\n")
            notify_dialog("Exported", f"{fname}", icon="📄")
        except Exception as ex:
            error_dialog("Export failed", f"{ex}")

    tk.Button(
        barf, text="Export", bg=COLORS["btn_toolbar_bg"], fg=COLORS["btn_toolbar_fg"],
        command=do_export_now
    ).pack(side="left", padx=6)
    tk.Button(
        barf, text="Close", command=win.destroy
    ).pack(side="left", padx=6)

    # Ensure proper centering after layout
    win.update_idletasks()
    center_on_parent(win, left_wrap, y_bias=-80)

def do_trend():
    """Show emoji trend (<=60 days) with horizontal scroll."""
    habit, s, e = range_dialog("Trend", default_days=14, allow_last=True, limit_days=60)
    if not habit:
        return
    h = get_habit(habit)
    by = h["history"]

    # 趋势弹窗（横向滚动）
    win = tk.Toplevel(root)
    win.title(f"Trend — {habit}")
    win.configure(bg=COLORS["main_bg"])
    win.resizable(False, False)
    win.transient(root); center_on_parent(win, left_wrap, y_bias=-80)

    tk.Label(win, text=f"Mood Trend — {habit}  ({fmt_date_obj(s)} → {fmt_date_obj(e)})",
             bg=COLORS["main_bg"], fg=COLORS["title_fg"], font=("Arial", 13, "bold")).pack(pady=(10, 6))

    days = daterange(s, e)
    n = len(days)
    step = 30
    pad = 24
    width = pad * 2 + max(0, n - 1) * step + 60

    wrap = tk.Frame(win, bg=COLORS["main_bg"])
    wrap.pack(padx=12, pady=10, fill="x")

    cv = tk.Canvas(wrap, width=min(960, width), height=130, bg=COLORS["card_bg"],
                   highlightthickness=1, highlightbackground=COLORS["border"])
    cv.pack(side="top", fill="x")

    xbar = tk.Scrollbar(wrap, orient="horizontal", command=cv.xview)
    xbar.pack(side="top", fill="x")
    cv.configure(xscrollcommand=xbar.set, scrollregion=(0, 0, width, 130))

    x0 = pad
    y0 = 60
    done = 0
    stats = {"happy": 0, "neutral": 0, "tired": 0, "stressed": 0}

    for i, d in enumerate(days):
        ds = d.isoformat()
        m = by.get(ds)
        if m:
            done += 1
        if m in stats:
            stats[m] += 1
        x = x0 + i * step
        r = 8  # keep slightly larger radius
        fill = MOOD_COLOR.get(m, MOOD_COLOR[None])
        outline = MOOD_OUTLINE.get(m, MOOD_OUTLINE[None])
        cv.create_oval(x - r, y0 - r, x + r, y0 + r, fill=fill, outline=outline, width=1)
        cv.create_text(x, y0 + 22, text=MOOD_ICON.get(m, "—"), font=("Arial", 12))

    total = len(days)
    pct = int(round((done / total) * 100)) if total else 0
    tk.Label(win, text=f"Completion: {done}/{total} days ({pct}%)",
             bg=COLORS["main_bg"]).pack(anchor="w", padx=12)
    tk.Label(win, text=f"😊 {stats['happy']}  😐 {stats['neutral']}  😪 {stats['tired']}  😰 {stats['stressed']}",
             bg=COLORS["main_bg"]).pack(anchor="w", padx=12, pady=(0, 10))
    tk.Button(win, text="Close", bg=COLORS["btn_toolbar_bg"], fg=COLORS["btn_toolbar_fg"], command=win.destroy)\
        .pack(pady=(0, 10))

    # Ensure proper centering after layout
    win.update_idletasks()
    center_on_parent(win, left_wrap, y_bias=-80)


# -------- Calendar Month View --------
def do_calendar():
    """Show a month calendar view for a habit, color by mood (Morandi palette)."""
    names = list_habits()
    if not names:
        notify_dialog("Calendar", "No habits yet.", icon="💬")
        return

    # Default selection
    habit = SELECTED.get("habit") or names[0]
    today_d = date.today()
    cur_y, cur_m = today_d.year, today_d.month


    win = tk.Toplevel(root)
    win.title(f"Calendar — {habit}")
    win.configure(bg=COLORS["main_bg"])
    win.resizable(False, False)
    win.transient(root)
    # keep hidden first to avoid initial flash; we center after layout
    win.withdraw()

    header = tk.Frame(win, bg=COLORS["main_bg"])
    header.pack(fill="x", pady=(10, 6), padx=12)

    tk.Label(header, text="Habit:", bg=COLORS["main_bg"]).pack(side="left")
    habit_var = tk.StringVar(value=habit)
    tk.OptionMenu(header, habit_var, *names).pack(side="left", padx=(4, 10))
    def _on_habit_change(*_):
        # 当下拉选择的习惯改变时，更新全局选择并重绘日历
        SELECTED["habit"] = habit_var.get()
        redraw()
    habit_var.trace_add("write", _on_habit_change)

    month_lbl = tk.Label(header, text="", bg=COLORS["main_bg"], fg=COLORS["title_fg"], font=("Arial", 13, "bold"))
    month_lbl.pack(side="left", padx=10)

    def prev_month():
        nonlocal cur_y, cur_m
        if cur_m == 1:
            cur_y -= 1; cur_m = 12
        else:
            cur_m -= 1
        redraw()

    def next_month():
        nonlocal cur_y, cur_m
        if cur_m == 12:
            cur_y += 1; cur_m = 1
        else:
            cur_m += 1
        redraw()

    def open_trend_for_current():
        # 将当前选择的习惯设为选中，再打开 Trend 自定义范围
        SELECTED["habit"] = habit_var.get()
        do_trend()

    btn_trend = ttk.Button(header, text="Trend…", style="SmallGreen.TButton", command=open_trend_for_current)
    btn_trend.pack(side="right", padx=(0, 8))

    btn_next = tk.Button(header, text="▶", command=next_month,
                         bg=COLORS["btn_toolbar_bg"], fg=COLORS["btn_toolbar_fg"])
    btn_next.pack(side="right")

    btn_prev = tk.Button(header, text="◀", command=prev_month,
                         bg=COLORS["btn_toolbar_bg"], fg=COLORS["btn_toolbar_fg"])
    btn_prev.pack(side="right")

    body = tk.Frame(win, bg=COLORS["main_bg"])
    body.pack(padx=12, pady=(0, 10))

    cv_w, cv_h = 700, 460
    cv = tk.Canvas(body, width=cv_w, height=cv_h, bg=COLORS["card_bg"],
                   highlightthickness=1, highlightbackground=COLORS["border"])
    cv.pack()

    # weekday headers
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    def draw_headers():
        x0, y0 = 20, 20
        cell_w = (cv_w - 40) // 7
        for i, wd in enumerate(weekdays):
            x = x0 + i * cell_w + cell_w // 2
            cv.create_text(x, y0, text=wd, font=("Arial", 10, "bold"), fill=COLORS["title_fg"])

    def redraw():
        cv.delete("all")
        # use the current value from the dropdown for both title and data source
        current_habit_name = habit_var.get()
        win.title(f"Calendar — {current_habit_name}")
        mon_name = calendar.month_name[cur_m]
        month_lbl.config(text=f"{mon_name} {cur_y}")

        draw_headers()
        x0, y0 = 20, 40
        cell_w = (cv_w - 40) // 7
        cell_h = (cv_h - 70) // 6

        sel_habit = get_habit(current_habit_name)
        by = sel_habit["history"] if sel_habit else {}

        first_wd, days_in_month = calendar.monthrange(cur_y, cur_m)  # first_wd: Mon=0
        # Convert to our grid where Mon=0..Sun=6 already matches
        day = 1
        row = 0
        col = first_wd
        while day <= days_in_month:
            d = date(cur_y, cur_m, day)
            ds = d.isoformat()
            mood = by.get(ds)

            left = x0 + col * cell_w
            top  = y0 + row * cell_h
            right = left + cell_w - 6
            bottom = top + cell_h - 6

            # cell background by mood
            fill = MOOD_COLOR.get(mood, MOOD_COLOR[None])
            cv.create_rectangle(left, top, right, bottom, fill=fill, outline=COLORS["border"], width=1)

            # day number
            cv.create_text(left + 10, top + 12, text=str(day), anchor="w", font=("Arial", 10, "bold"), fill=COLORS["title_fg"])
            # emoji centered
            cv.create_text((left+right)//2, (top+bottom)//2 + 6, text=MOOD_ICON.get(mood, "—"), font=("Arial", 14))

            # advance grid
            col += 1
            if col == 7:
                col = 0
                row += 1
            day += 1

        # legend
        lx, ly = 24, cv_h - 18
        items = [("happy", "😊"), ("neutral", "😐"), ("tired", "😪"), ("stressed", "😰"), (None, "—")]
        off = 0
        for code, em in items:
            cv.create_rectangle(lx + off, ly - 10, lx + off + 14, ly + 4, fill=MOOD_COLOR.get(code, MOOD_COLOR[None]), outline=COLORS["border"])
            cv.create_text(lx + off + 22, ly - 3, text=f"{em} {code or 'none'}", anchor="w", font=("Arial", 9), fill=COLORS["hint_fg"])
            off += 120

    redraw()
    # Ensure proper centering after layout
    win.update_idletasks()
    center_on_parent(win, left_wrap, y_bias=-40)

def do_export():
    """Export a text report file."""
    habit, s, e = range_dialog("Export", default_days=7, allow_last=True, limit_days=None)
    if not habit:
        return
    h = get_habit(habit)
    by = h["history"]
    fname = f"report_{habit.replace(' ', '_')}_{fmt_date_obj(s)}_to_{fmt_date_obj(e)}.txt"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(f"DailyFlow+ Report\nHabit: {habit}\nRange: {fmt_date_obj(s)} to {fmt_date_obj(e)}\n")
        f.write("-" * 40 + "\n")
        for d in daterange(s, e):
            ds = d.isoformat()
            m = by.get(ds)
            f.write(f"{fmt_date_iso(ds)}: {MOOD_ICON.get(m, '—')} {m or '—'}\n")
    notify_dialog("Exported", f"{fname}", icon="📄")

def delete_habit(name):
    """Delete a habit entry."""
    if confirm_delete_dialog(name):
        DATA["habits"].pop(name, None)
        # 清理与该习惯相关的 recent 记录
        if "recent" in DATA:
            DATA["recent"] = [r for r in DATA["recent"] if r.get("habit") != name]
        save_data()
        if SELECTED["habit"] == name:
            SELECTED["habit"] = None
        render_cards()
        refresh_right_panel()

def mark_habit(name):
    """Set or clear today's mood for a habit.
    - If pick_mood_dialog returns a mood code: mark complete for today and log to recent.
    - If it returns None (Clear today): clear today's record, unset completion, and remove today's recent log for this habit.
    """
    h = get_habit(name)
    if not h:
        return
    mood = pick_mood_dialog(default=h.get("last"), title_text=f"Update Mood — {name}")

    t = today_str()

    # If user chose "Clear today": remove today's record and completion, log a "clear" event to recent
    if mood is None:
        # 删除今天的心情
        if t in h.get("history", {}):
            try:
                del h["history"][t]
            except Exception:
                h["history"].pop(t, None)  # 兜底
        # 取消今日完成标记
        if "done" in h and t in h["done"]:
            h["done"].pop(t, None)
        # 重新估算 last：用最近一次（早于今天）的记录，否则置空
        prev_keys = [ds for ds in h.get("history", {}).keys() if ds < t]
        if prev_keys:
            prev_day = max(prev_keys)  # 字符串 ISO 日期可直接比较
            h["last"] = h["history"].get(prev_day)
        else:
            h["last"] = None
        # 从 recent 里移除“今天此习惯”的原有记录，并新增一条“Clear”记录
        DATA.setdefault("recent", [])
        DATA["recent"] = [
            r for r in DATA["recent"]
            if not (r.get("habit") == name and r.get("dt", "")[:10] == t)
        ]
        DATA["recent"].insert(0, {
            "dt": datetime.now().isoformat(timespec="seconds"),
            "habit": name,
            "mood": "cleared"
        })
        save_data()
        render_cards()
        refresh_right_panel()
        return

    # 用户正常选择了心情：记录 + 完成 + recent
    h.setdefault("history", {})[t] = mood
    h["last"] = mood
    h.setdefault("done", {})[t] = True   # 今日完成
    push_recent(name, mood)  # 记录这一条最新行为（带时间）
    save_data()
    set_random_tip()  # 打卡后随机更换一条鼓励语
    render_cards()
    refresh_right_panel()

# ------------- Cards rendering -------------

def render_cards():
    """Render habit cards."""
    for w in cards_frame.winfo_children():
        w.destroy()

    names = list_habits()
    if not names:
        tk.Label(cards_frame, text="(no habits yet)", bg=COLORS["sidebar_bg"]).pack(pady=8)
        refresh_right_panel()
        return

    for name in names:
        h = get_habit(name)
        today_iso = today_str()
        today_mood = h["history"].get(today_iso) if h else None
        show_mood = today_mood if (h and is_done(h, today_iso)) else None
        emoji = MOOD_ICON.get(show_mood, "—")
        streak = compute_streak(name)

        # row container
        row = tk.Frame(cards_frame, bg=COLORS["sidebar_bg"])
        row.pack(fill="x", padx=22, pady=10, anchor="nw")

        # the card panel
        card = tk.Frame(
            row,
            bg=COLORS["card_bg"],
            highlightthickness=1, highlightbackground=COLORS["card_border"]
        )
        card.pack(fill="x", expand=True, ipadx=10, ipady=8)

        # Hover effect
        def on_hover_in(event):
            current = event.widget.cget("bg")
            if current != "#FFF8FA":  # avoid redundant updates
                event.widget.config(bg="#FFF8FA")

        def on_hover_out(event):
            event.widget.config(bg=COLORS["card_bg"])

        card.bind("<Enter>", on_hover_in)
        card.bind("<Leave>", on_hover_out)

        # Make left info column stretch so the button column sticks to the right edge
        card.grid_columnconfigure(0, weight=1)

        # left info area
        info = tk.Frame(card, bg=COLORS["card_bg"])
        info.grid(row=0, column=0, sticky="w", padx=12, pady=6)

        tk.Label(info, text=name, bg=COLORS["card_bg"], fg="#262626",
                 font=("Arial", 16, "bold")).pack(anchor="w")
        tk.Label(info, text=f"Streak: {streak} day{'s' if streak != 1 else ''}",
                 bg=COLORS["card_bg"], fg="#333", pady=2).pack(anchor="w")
        tk.Label(info, text=f"Current Mood: {emoji} {show_mood or '—'}",
                 bg=COLORS["card_bg"], fg="#333", pady=2).pack(anchor="w")

        # right buttons (inline)
        btn_area = tk.Frame(card, bg=COLORS["card_bg"])
        btn_area.grid(row=0, column=1, sticky="e", padx=12, pady=10)

        def on_mark(n=name):
            # call mark for this habit
            mark_habit(n)

        def on_delete(n=name):
            # delete this habit
            delete_habit(n)

        ttk.Button(
            btn_area, text="Mark", style="CardGreen.TButton",
            command=on_mark
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            btn_area, text="🗑 Delete", style="CardGreen.TButton",
            command=on_delete
        ).pack(side="left")

        # select highlight
        def select_me(_=None, nm=name, cd=card):
            SELECTED["habit"] = nm
            for wrap in cards_frame.winfo_children():
                if not wrap.winfo_children():
                    continue
                c = wrap.winfo_children()[0]
                c.configure(highlightthickness=1)
            cd.configure(highlightthickness=2)
            refresh_right_panel()

        card.bind("<Button-1>", select_me)
        info.bind("<Button-1>", select_me)

    if SELECTED["habit"] is None and names:
        SELECTED["habit"] = names[0]
        first_wrap = cards_frame.winfo_children()[0]
        c = first_wrap.winfo_children()[0]
        c.configure(highlightthickness=2)
    refresh_right_panel()

# ------------- Toolbar wiring -------------

def on_add_habit():
    add_habit_dialog()

def on_trend():
    do_trend()

def on_report():
    do_report()

def on_export():
    do_export()


def on_calendar():
    do_calendar()

make_toolbar_btn(toolbar, "Add Habit", on_add_habit)
# make_toolbar_btn(toolbar, "View Mood Trend", on_trend)  # Removed per instructions
make_toolbar_btn(toolbar, "Month View", on_calendar)
make_toolbar_btn(toolbar, "Report", on_report)
make_toolbar_btn(toolbar, "Export", on_export)

# ------------- Boot -------------

DATA = load_data()

def first_select_default():
    names = list_habits()
    if names and SELECTED["habit"] is None:
        SELECTED["habit"] = names[0]

def refresh_all():
    first_select_default()
    render_cards()
    refresh_right_panel()

refresh_all()
root.mainloop()     # 启动事件循环（显示窗口并响应交互）
