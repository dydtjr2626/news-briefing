"""화제 주제 탐지: 수집된 기사 제목에서 여러 기사에 반복되는 단어를 세어 '지금 많이 다뤄지는 주제'를 찾는다.
선별 전에 먼저 실행해서, 기사가 많은 주제를 놓치지 않게 한다.
사용: python -I trending.py <YYYY-MM-DD> [상위 N=25]"""
import json, re, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
day = sys.argv[1]
top = int(sys.argv[2]) if len(sys.argv) > 2 else 25
raw = json.loads((ROOT / "data/raw" / f"{day}.json").read_text(encoding="utf-8"))["categories"]

STOP_KO = set("연합뉴스 속보 종합 사진 포토 게시판 오늘 내일 어제 이시각 헤드라인 기자 단독 영상 한국경제 전자신문 대한 위해 통해 관련 이후 이번 지난 올해 내년 대비 따라 가운데 오전 오후 현지시간".split())
STOP_EN = set("the and for with that this from are was has have will its not but you your how why what who new says say more after over into than about just out can could would".split())


def tokens(title, korean):
    if korean:
        ws = re.findall(r"[가-힣]{2,}|[A-Za-z]{2,}", title)
        out = set()
        for w in ws:
            if re.match(r"[A-Za-z]", w):
                out.add(w.lower())
                continue
            # 조사 제거(간단): 흔한 어미를 뗀 형태도 후보로
            for suf in ("에서", "에게", "으로", "까지", "부터", "하는", "했다", "한다", "에는", "이다", "에도", "이란", "이라", "의", "을", "를", "은", "는", "이", "가", "도", "에", "로", "와", "과"):
                if len(w) > len(suf) + 1 and w.endswith(suf):
                    w = w[: -len(suf)]
                    break
            if w not in STOP_KO and len(w) >= 2:
                out.add(w)
        return out
    return {w.lower() for w in re.findall(r"[A-Za-z][A-Za-z\-']{2,}", title) if w.lower() not in STOP_EN}


for region, korean in (("domestic", True), ("foreign", False)):
    docs = {}
    for cat, v in raw.items():
        for a in v[region]:
            docs[a["url"]] = (cat, a)
    df = defaultdict(set)
    for url, (cat, a) in docs.items():
        for t in tokens(a["title"], korean):
            df[t].add(url)
    ranked = sorted(df.items(), key=lambda kv: -len(kv[1]))[:top]
    print(f"\n===== {'국내' if korean else '해외'} 화제 단어 (기사 {len(docs)}건 중 해당 단어가 제목에 나온 기사 수) =====")
    for term, urls in ranked:
        if len(urls) < 3:
            continue
        sample = next(iter(urls))
        print(f"{len(urls):>3}건  {term:<14} 예: {docs[sample][1]['title'][:48]}")
