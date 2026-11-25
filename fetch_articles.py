"""선별된 기사의 본문을 가져와 data/work/articles/<id>.txt 로 저장한다.
사용: python -I fetch_articles.py <YYYY-MM-DD>   (data/work/selection-<날짜>.json 필요)"""
import json, re, sys, html
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
UA = {"User-Agent": "Mozilla/5.0 (newspaper-personal-reader)", "Accept-Language": "en,ko;q=0.8"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        raw = r.read()
        enc = r.headers.get_content_charset() or "utf-8"
    return raw.decode(enc, errors="replace")


def clean(t):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t))).strip()


def extract(page):
    page = re.sub(r"<(script|style|noscript|svg|figure|aside|nav|footer|header)\b.*?</\1>", " ", page, flags=re.S | re.I)
    # 페이지에 <article>이 여러 개(광고·추천 포함)일 수 있어, 글자 수가 가장 많은 블록을 본문으로 본다
    blocks = re.findall(r"<article\b.*?</article>", page, flags=re.S | re.I)
    body = max(blocks, key=lambda b: len(re.sub(r"<[^>]+>", "", b))) if blocks else page
    if len(re.sub(r"<[^>]+>", "", body).split()) < 120 and len(page) > len(body):
        body = page
    paras = []
    for p in re.findall(r"<p\b[^>]*>(.*?)</p>", body, flags=re.S | re.I):
        t = clean(p)
        if t.startswith("BBC Homepage"):  # BBC: 내비게이션 문구가 첫 문단에 붙어 있음
            mm = re.search(r"Published\d{1,2} \w+ \d{4}(.*)", t)
            t = mm.group(1).strip() if mm else ""
        paras.append(t)
    korean = sum(len(re.findall(r"[가-힣]", p)) for p in paras) > 200
    min_len = 30 if korean else 8
    keep = []
    for t in paras:
        n = len(t) if korean else len(t.split())
        junk = ("Get in touch", "Copyright", "All Rights Reserved", "IE+", "Black Friday", "inbox",
                "Renews at", "Regular price", "Access expert insights", "Subscribe", "Sign up")
        if n >= min_len and not any(j in t for j in junk) and "무단" not in t[:40]:
            keep.append(t)
    return keep


def main():
    day = sys.argv[1]
    sel = json.loads((ROOT / "data" / "work" / f"selection-{day}.json").read_text(encoding="utf-8"))
    outdir = ROOT / "data" / "work" / "articles" / day
    outdir.mkdir(parents=True, exist_ok=True)
    for a in sel:
        # 복수 출처 기사: 첫 출처(s1) 뒤에 extra 출처(s2, s3...)를 이어 붙인다
        urls = [a["url"]] + [x["url"] for x in a.get("extra", [])]
        chunks = []
        for n, u in enumerate(urls, 1):
            try:
                chunk = "\n".join(extract(get(u)))
            except Exception as e:
                chunk = ""
                print(f"[실패] {a['id']} s{n}: {e}")
            if len(urls) > 1:
                (outdir / f"{a['id']}__s{n}.txt").write_text(chunk, encoding="utf-8")
                chunk = f"[s{n}]\n" + chunk
            chunks.append(chunk)
        paras = [c for c in chunks if c.strip()]
        text = "\n".join(paras)
        (outdir / f"{a['id']}.txt").write_text(text, encoding="utf-8")
        words = len(text.split())
        flag = "" if words >= 120 else "  <-- 본문 부족(RSS 요약 사용 필요)"
        print(f"{a['id']:<18} 문단 {len(paras):>2}, {words:>4}단어  {a['title'][:40]}{flag}")


if __name__ == "__main__":
    main()
