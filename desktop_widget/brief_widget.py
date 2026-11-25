"""바탕화면 브리핑 위젯: 가장 최근 날짜의 분야별 헤드라인을 둥근 반투명 패널로 보여 준다.
데이터: data/out/<날짜>.json (읽기만 함). 60초마다 다시 읽는다.
조작: 마우스로 끌어서 이동 / 오른쪽 클릭 → 새로고침·글자 크게·작게·닫기."""
import json, sys, ctypes, webbrowser
import tkinter as tk
from pathlib import Path

DATA_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\Users\User\Desktop\kim\newspaper\data\out")
KEY = "#010101"  # 이 색은 투명 처리된다(둥근 모서리 바깥)
state = {"size": 12, "alpha": 0.90, "theme": "dark", "top": True}
hits = {}  # 캔버스 글자 id -> 기사 주소
THEMES = {
    "dark": dict(bg="#1E1F22", label="#8A8D94", date="#6E7178", title="#F2F2F0", text="#E4E4E1", line="#2A2B2F",
                 dots=dict(economy="#D9A85B", politics="#E0807A", ai="#9B8AE0", semiconductor="#6FCBB0", engineering="#9A9DA3")),
    "light": dict(bg="#FAFAF8", label="#8C8F96", date="#A0A3AA", title="#1D1D1F", text="#2E2E31", line="#ECECE8",
                 dots=dict(economy="#C99235", politics="#D9675F", ai="#7E6BD0", semiconductor="#3FAE90", engineering="#8A8D93")),
}
FONT = "맑은 고딕"


def headlines():
    files = sorted(DATA_DIR.glob("*.json"))
    if not files:
        return "브리핑 없음", [("", "", [("data/out 폴더에 날짜 파일이 없습니다.", None)])]
    d = f = None
    for f in reversed(files):  # 최신 파일이 깨졌으면 그 전 날짜로 대체
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(d, dict):
                break
        except Exception:
            pass
        d = None
    if d is None:
        return "브리핑 없음", [("", "", [("날짜 파일을 읽을 수 없습니다.", None)])]
    files = [f]
    by = {a.get("id"): a for a in d.get("articles", []) if isinstance(a, dict)}
    groups = []  # [(분야 이름, [헤드라인...])] 분야별로 나눠서 보여 준다
    cats = d.get("categories", {})
    order = [c for c in ("economy", "politics", "ai", "semiconductor", "engineering") if c in cats]
    for c in order + [c for c in cats if c not in order]:
        info = cats[c] if isinstance(cats[c], dict) else {}
        heads = []
        for i in info.get("article_ids", []):
            a = by.get(i) or {}
            h = a.get("headline_ko")
            srcs = a.get("sources") or [{}]
            url = srcs[0].get("url") if isinstance(srcs[0], dict) else None  # 클릭하면 첫 출처 기사로 이동
            if h and h not in [x[0] for x in heads]:
                heads.append((h if len(h) <= 80 else h[:79] + "…", url))
        groups.append((info.get("label", c), c, heads[:2] or [("오늘은 핫한 기사가 없습니다.", None)]))
    return d.get("date", files[-1].stem), groups or [("", "", [("오늘은 핫한 기사가 없습니다.", None)])]


root = tk.Tk()
root.overrideredirect(True)
root.configure(bg=KEY)
root.attributes("-transparentcolor", KEY)
root.attributes("-alpha", state["alpha"])
canvas = tk.Canvas(root, bg=KEY, highlightthickness=0)
canvas.pack()


def round_rect(x0, y0, x1, y1, r, **kw):
    pts = [x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r, x1, y1 - r, x1, y1, x1 - r, y1,
           x0 + r, y1, x0, y1, x0, y1 - r, x0, y0 + r, x0, y0]
    return canvas.create_polygon(pts, smooth=True, **kw)


def draw():
    canvas.delete("all")
    hits.clear()
    c = THEMES[state["theme"]]
    date, groups = headlines()
    s, w, pad, R = state["size"], 460, 26, 22
    panel = round_rect(0, 0, w, 10, R, fill=c["bg"], outline="")
    # 헤더: 단정한 제목 + 작고 연한 날짜
    t = canvas.create_text(pad, pad - 2, text="오늘의 뉴스", anchor="nw", font=(FONT, s + 4), fill=c["title"])
    canvas.create_text(w - pad, canvas.bbox(t)[3] - 3, text=str(date), anchor="se", font=(FONT, s - 3), fill=c["date"])
    y = canvas.bbox(t)[3] + 20
    tx = pad + 14
    tw = w - tx - pad
    for label, key, hs in groups:
        dot = c["dots"].get(key, c["label"])
        if label:  # 분야: 색 점 + 작고 연한 라벨
            t = canvas.create_text(pad + 14, y, text=label, anchor="nw", font=(FONT, s - 3), fill=c["label"])
            b = canvas.bbox(t)
            cy = (b[1] + b[3]) / 2
            canvas.create_oval(pad, cy - 3, pad + 7, cy + 4, fill=dot, outline="")
            y = b[3] + 7
        for h, url in hs:
            t = canvas.create_text(tx, y, text=h, anchor="nw", font=(FONT, s), fill=c["text"], width=tw)
            if url:
                hits[t] = url
            y = canvas.bbox(t)[3] + 9
        y += 11
    h_total = y + pad - 18
    canvas.delete(panel)
    panel = round_rect(0, 0, w, h_total, R, fill=c["bg"], outline="")
    canvas.tag_lower(panel)
    canvas.config(width=w, height=h_total + 1)


def refresh():
    try:
        draw()
    except Exception as e:
        canvas.delete("all")
        canvas.create_text(6, 6, text=f"읽기 실패: {e}", anchor="nw", fill="white")
    root.after(60000, refresh)


def to_bottom():  # 다른 창 뒤, 바탕화면 바로 위에 둔다
    try:
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id()) or root.winfo_id()
        ctypes.windll.user32.SetWindowPos(hwnd, 1, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010)  # HWND_BOTTOM, NOSIZE|NOMOVE|NOACTIVATE
    except Exception:
        pass


drag = {}
def on_press(e):
    drag.update(x=e.x, y=e.y, moved=False)


def on_motion(e):
    if abs(e.x - drag["x"]) + abs(e.y - drag["y"]) > 4:
        drag["moved"] = True
    if drag["moved"]:
        root.geometry(f"+{root.winfo_x() + e.x - drag['x']}+{root.winfo_y() + e.y - drag['y']}")


def on_release(e):
    if not drag.get("moved"):  # 끌지 않고 눌렀다 뗐으면 클릭: 헤드라인이면 기사 열기
        for i in canvas.find_overlapping(e.x, e.y, e.x, e.y):
            if i in hits:
                webbrowser.open(hits[i])
                break
    elif not state["top"]:
        to_bottom()


def on_hover(e):
    over = any(i in hits for i in canvas.find_overlapping(e.x, e.y, e.x, e.y))
    canvas.config(cursor="hand2" if over else "")


canvas.bind("<ButtonPress-1>", on_press)
canvas.bind("<B1-Motion>", on_motion)
canvas.bind("<ButtonRelease-1>", on_release)
canvas.bind("<Motion>", on_hover)

menu = tk.Menu(root, tearoff=0)
def set_alpha(d):
    state["alpha"] = min(1.0, max(0.4, state["alpha"] + d))
    root.attributes("-alpha", state["alpha"])


def safe_draw():
    try:
        draw()
    except Exception as e:
        canvas.delete("all")
        canvas.create_text(6, 6, text=f"읽기 실패: {e}", anchor="nw", fill="white")


def toggle_theme():
    state["theme"] = "light" if state["theme"] == "dark" else "dark"
    safe_draw()


menu.add_command(label="새로고침", command=safe_draw)
menu.add_command(label="글자 크게", command=lambda: (state.update(size=min(state["size"] + 1, 24)), safe_draw()))
menu.add_command(label="글자 작게", command=lambda: (state.update(size=max(state["size"] - 1, 9)), safe_draw()))
menu.add_command(label="배경 진하게", command=lambda: set_alpha(0.06))
menu.add_command(label="배경 연하게", command=lambda: set_alpha(-0.06))
menu.add_command(label="다크/라이트 전환", command=toggle_theme)


def apply_top():
    root.attributes("-topmost", state["top"])
    if not state["top"]:
        to_bottom()


def toggle_top():
    state["top"] = not state["top"]
    apply_top()


menu.add_command(label="항상 위에 표시 켜기/끄기(끄면 바탕화면에 붙음)", command=toggle_top)
menu.add_separator()
menu.add_command(label="닫기", command=root.destroy)
canvas.bind("<Button-3>", lambda e: menu.tk_popup(e.x_root, e.y_root))

root.update_idletasks()
root.geometry(f"+{root.winfo_screenwidth() - 500}+60")  # 오른쪽 위
refresh()
apply_top()
root.mainloop()
