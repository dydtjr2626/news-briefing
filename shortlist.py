"""선별용 후보 목록(토큰 절약): 수집 풀 전체 제목 대신, 화제 기사만 짧게 보여 준다.
- 반도체 분야: 풀이 작으므로 전부 출력
- 나머지 분야: Google 뉴스 화제(buzz)와 매칭된 기사만 출력(화제 순위·매칭 건수 포함)
- 나머지 제목이 필요하면: python -I shortlist.py <날짜> --all <분야>   (분야: economy politics ai semiconductor)
사용: python -I shortlist.py <YYYY-MM-DD>"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).parent
day = sys.argv[1]
raw = json.loads((ROOT / "data/raw" / f"{day}.json").read_text(encoding="utf-8"))["categories"]
buzz_path = ROOT / "data/work" / f"buzz-{day}.json"
buzz = json.loads(buzz_path.read_text(encoding="utf-8")) if buzz_path.exists() else {}
show_all = sys.argv[sys.argv.index("--all") + 1] if "--all" in sys.argv else None
SMALL = {"semiconductor"}

hot = {}  # url -> [(구역, 순위)]
for region, stories in buzz.items():
    for s in stories:
        for m in s["matched"]:
            hot.setdefault(m["url"], []).append(f"{s['section']}{s['rank']}위")

for cat, v in raw.items():
    for region, tag in (("domestic", "국내"), ("foreign", "해외")):
        arts = v[region]
        if cat in SMALL or cat == show_all:
            pick = arts
        else:
            pick = [a for a in arts if a["url"] in hot]
        print(f"\n== {cat} / {tag}  (풀 {len(arts)}건 중 {len(pick)}건 표시) ==")
        for a in pick:
            mark = (" | 화제:" + ",".join(dict.fromkeys(hot[a["url"]]))) if a["url"] in hot else ""
            print(f"- {a['outlet']} | {a['title'][:70]} | {a['url']}{mark}")
