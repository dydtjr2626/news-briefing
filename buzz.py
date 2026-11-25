"""화제 수집기: Google 뉴스(한국·미국)의 주요뉴스·분야별 순위를 가져와, 우리가 수집한 기사 풀과 연결한다.
Google 뉴스는 '순위 신호'로만 쓰고(링크는 매체로 바로 연결되지 않음), 본문은 우리 RSS 풀의 기사에서 가져온다.
결과: data/work/buzz-<날짜>.json 과 터미널 요약.
사용: python -I buzz.py <YYYY-MM-DD>"""
import json, re, sys, html
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).parent
day = sys.argv[1]
raw = json.loads((ROOT / "data/raw" / f"{day}.json").read_text(encoding="utf-8"))["categories"]

FEEDS = {
    "domestic": [
        ("주요", "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"),
        ("정치·사회", "https://news.google.com/rss/headlines/section/topic/NATION?hl=ko&gl=KR&ceid=KR:ko"),
        ("경제", "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ko&gl=KR&ceid=KR:ko"),
        ("기술", "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=ko&gl=KR&ceid=KR:ko"),
        ("과학", "https://news.google.com/rss/headlines/section/topic/SCIENCE?hl=ko&gl=KR&ceid=KR:ko"),
    ],
    "foreign": [
        ("주요", "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"),
        ("정치·세계", "https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-US&gl=US&ceid=US:en"),
        ("경제", "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en"),
        ("기술", "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-US&gl=US&ceid=US:en"),
    ],
}
STOP_KO = set("연합뉴스 속보 종합 사진 포토 게시판 오늘 내일 어제 기자 단독 영상 대한 위해 통해 관련 이후 이번 지난 올해 내년 가운데".split())
STOP_EN = set("the and for with that this from are was has have will its not but you your how why what who new says say more after over into than about just out can could would".split())
SUFFIX = ("에서", "에게", "으로", "까지", "부터", "하는", "했다", "한다", "에는", "이다", "에도", "의", "을", "를", "은", "는", "이", "가", "도", "에", "로", "와", "과")


def toks(title, korean):
    if korean:
        out = set()
        for w in re.findall(r"[가-힣]{2,}|[A-Za-z]{2,}|\d{2,}", title):
            if re.match(r"[A-Za-z0-9]", w):
                out.add(w.lower()); continue
            for s in SUFFIX:
                if len(w) > len(s) + 1 and w.endswith(s):
                    w = w[:-len(s)]; break
            if w not in STOP_KO:
                out.add(w)
        return out
    return {w.lower() for w in re.findall(r"[A-Za-z][A-Za-z\-']{2,}", title) if w.lower() not in STOP_EN}


def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=25).read()


pool = {}
for cat, v in raw.items():
    for region in ("domestic", "foreign"):
        for a in v[region]:
            pool.setdefault(region, {})[a["url"]] = {**a, "pool_cat": cat}

result = {}
for region, feeds in FEEDS.items():
    korean = region == "domestic"
    stories, seen = [], set()
    for section, url in feeds:
        try:
            items = list(ET.fromstring(get(url)).iter("item"))
        except Exception as e:
            print(f"[실패] {region}/{section}: {e}", file=sys.stderr); continue
        for rank, it in enumerate(items[:15], 1):
            title = re.sub(r"\s+-\s+[^-]+$", "", it.findtext("title") or "").strip()
            if title in seen:
                continue
            seen.add(title)
            desc = it.findtext("description") or ""
            related = re.findall(r"<a [^>]*>(.*?)</a>&nbsp;&nbsp;<font[^>]*>(.*?)</font>", desc)
            outlets = {html.unescape(o) for _, o in related}
            tk = toks(title, korean)
            matched = []
            for url_, a in pool.get(region, {}).items():
                common = tk & toks(a["title"], korean)
                need = 2 if len(tk) >= 3 else 1
                if len(common) >= need:
                    matched.append((len(common), a))
            matched.sort(key=lambda x: -x[0])
            stories.append({
                "section": section, "rank": rank, "title": title, "related_outlets": len(outlets),
                "matched": [{"outlet": a["outlet"], "title": a["title"], "url": a["url"], "pool_cat": a["pool_cat"]} for _, a in matched[:6]],
            })
    result[region] = stories

(ROOT / "data/work" / f"buzz-{day}.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
for region in ("domestic", "foreign"):
    print(f"\n===== {'국내' if region == 'domestic' else '해외'} 화제 (Google 뉴스 순위 · 우리 풀에서 찾은 기사 수) =====")
    for s in result[region]:
        if not s["matched"]:
            continue  # 풀에 없는 화제는 선별에 못 쓰므로 출력하지 않는다(토큰 절약). 전체는 buzz-<날짜>.json 에 있음
        print(f"[{s['section']} {s['rank']:>2}위] 풀매칭 {len(s['matched'])}건 | {s['title'][:62]}")
