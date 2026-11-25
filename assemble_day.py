"""하위 에이전트가 쓴 초안(drafts)과 선별 파일(selection)을 합쳐 하루치 JSON(data/out/<날짜>.json)을 만든다.
입력: data/work/selection-<날짜>.json, data/work/drafts/<날짜>/<기사id>.json, meta.json, (선택) comments.json
사용: python -I assemble_day.py <YYYY-MM-DD> [출력경로]"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).parent
day = sys.argv[1]
out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "data" / "out" / f"{day}.json"
W = ROOT / "data" / "work"
D = W / "drafts" / day
LABEL = {"economy": "경제", "politics": "정치", "ai": "AI 기술", "semiconductor": "반도체"}


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


sel = {s["id"]: s for s in load(W / f"selection-{day}.json")}
meta = load(D / "meta.json")
comments = load(D / "comments.json") if (D / "comments.json").exists() else {}

articles = []
for cat in LABEL:
    for i in meta["order"].get(cat, []):
        s, d = sel[i], load(D / f"{i}.json")
        sources = [{"id": "s1", "outlet": s["outlet"], "title": s["title"], "url": s["url"], "published": (s.get("published") or "")[:10]}]
        for n, x in enumerate(s.get("extra", []), 2):
            sources.append({"id": f"s{n}", "outlet": x["outlet"], "title": x["title"], "url": x["url"], "published": (x.get("published") or "")[:10]})
        a = {
            "id": i, "category": cat, "region": s["region"],
            "headline_en": s["title"] if s["region"] == "foreign" else None,
            "headline_ko": d["headline_ko"],
            "sources": sources,
            "summary_ko": d["summary_ko"],
            "confidence": "multi-source" if len(sources) > 1 else "single-source",
        }
        for k in ("why_it_matters_ko", "easy_en_pairs", "vocab", "questions"):
            if k in d:
                a[k] = d[k]
        if i in comments:
            a["comments"] = comments[i]
        articles.append(a)

out = {
    "date": day,
    "briefing": meta["briefing"],
    # 핫한 기사가 없는 분야도 항목은 남기고(article_ids=[]), 총평은 기본 문구로 채운다
    "categories": {c: {"label": LABEL[c],
                       "overview": meta.get("overview", {}).get(c) or {"text": "오늘은 이 분야에 핫한 기사가 없습니다.", "refs": []},
                       "article_ids": meta["order"].get(c, [])} for c in LABEL},
    "articles": articles,
}
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"조립 완료: {out_path} | 기사 {len(articles)}건")
