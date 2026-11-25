"""RSS 수집기: 최근 N시간 기사를 모아 data/raw/YYYY-MM-DD.json 로 저장한다. (표준 라이브러리만 사용)"""
import json, re, sys, html
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).parent
KST = timezone(timedelta(hours=9))
UA = {"User-Agent": "Mozilla/5.0 (newspaper-personal-reader)"}


def strip_html(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def parse_date(s):
    if not s:
        return None
    try:
        d = parsedate_to_datetime(s)
    except Exception:
        try:
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def text_of(el, *names):
    for n in names:
        found = el.find(n)
        if found is not None and (found.text or "").strip():
            return found.text.strip()
    return ""


def fetch_feed(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        data = r.read()
    root = ET.fromstring(data)
    atom = "{http://www.w3.org/2005/Atom}"
    items = []
    for it in root.iter("item"):
        items.append({
            "title": strip_html(text_of(it, "title")),
            "url": text_of(it, "link"),
            "summary": strip_html(text_of(it, "description"))[:600],
            "published": text_of(it, "pubDate", "{http://purl.org/dc/elements/1.1/}date"),
        })
    for it in root.iter(atom + "entry"):
        link = it.find(atom + "link")
        items.append({
            "title": strip_html(text_of(it, atom + "title")),
            "url": link.get("href") if link is not None else "",
            "summary": strip_html(text_of(it, atom + "summary", atom + "content"))[:600],
            "published": text_of(it, atom + "updated", atom + "published"),
        })
    return items


def main():
    cfg = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=cfg["window_hours"])
    out = {"collected_at": now.astimezone(KST).isoformat(), "categories": {}}
    for cat, c in cfg["categories"].items():
        out["categories"][cat] = {"label": c["label"], "foreign": [], "domestic": []}
        for region in ("foreign", "domestic"):
            seen = set()
            for src in c[region]:
                try:
                    items = fetch_feed(src["url"])
                except Exception as e:
                    print(f"[실패] {src['outlet']}: {e}", file=sys.stderr)
                    continue
                kept = 0
                for it in items:
                    d = parse_date(it["published"])
                    if not it["title"] or not it["url"] or it["url"] in seen:
                        continue
                    src_cutoff = now - timedelta(hours=src["window_hours"]) if src.get("window_hours") else cutoff
                    if d is not None and d < src_cutoff:
                        continue
                    kws = src.get("keywords")
                    if kws and not any(k.lower() in (it["title"] + " " + it["summary"]).lower() for k in kws):
                        continue
                    seen.add(it["url"])
                    it["outlet"] = src["outlet"]
                    it["published_iso"] = d.astimezone(KST).isoformat() if d else None
                    out["categories"][cat][region].append(it)
                    kept += 1
                print(f"{cat}/{region} {src['outlet']}: {kept}건")
    day = datetime.now(KST).strftime("%Y-%m-%d")
    path = ROOT / "data" / "raw" / f"{day}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("저장:", path)


if __name__ == "__main__":
    main()
