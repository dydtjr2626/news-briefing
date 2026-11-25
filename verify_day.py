"""하루치 JSON 1차 자동 검증.
- 요약·쉬운 영어·해석·브리핑·총평의 숫자가 원문에 있는지(단위 환산 포함)
- 단어장 예문이 원문에 그대로 있는지
- 쉬운 영어 문장 길이(25단어 이하), 단어장 개수, 출처 누락
사용: python -I verify_day.py <YYYY-MM-DD>"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).parent
day = sys.argv[1]
data = json.loads((ROOT / "data/out" / f"{day}.json").read_text(encoding="utf-8"))
art_dir = ROOT / "data/work/articles" / day

MULT = {"trillion": 1e12, "tn": 1e12, "billion": 1e9, "bn": 1e9, "million": 1e6, "조": 1e12, "억": 1e8, "만": 1e4}
NUM = re.compile(r"(\d[\d,]*(?:\.\d+)?)\s*(trillion|tn|billion|bn|million|조|억|만)?", re.I)


def norm(s):
    return re.sub(r"\s+", " ", s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')).lower()


def values(text):
    out = set()
    for m in NUM.finditer(text.replace("£", "").replace("$", "")):
        raw = m.group(1).replace(",", "")
        try:
            v = float(raw)
        except ValueError:
            continue
        suf = (m.group(2) or "").lower()
        out.add(round(v * MULT.get(suf, 1), 4))
    return out


WORDNUM = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
           "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "first": 1, "second": 2, "third": 3, "fourth": 4}


def word_values(text):
    return {float(WORDNUM[w.lower()]) for w in re.findall(r"\b(" + "|".join(WORDNUM) + r")\b", text, re.I)}


def is_korean(t):
    return len(re.findall(r"[가-힣]", t)) > 100


problems, notes = [], []
src_text = {}
for a in data["articles"]:
    src_text[a["id"]] = (art_dir / f"{a['id']}.txt").read_text(encoding="utf-8")


def check_numbers(label, text, source_ids):
    src = "\n".join(src_text[i] for i in source_ids)
    foreign = not is_korean(src)
    t = text
    if foreign:  # 한국어 월/년 표기는 영어 월 이름·'three years' 와 대조가 어려워 제외
        t = re.sub(r"\d+\s*(월|년)", " ", t)
    miss = values(t) - values(src) - word_values(src)
    for v in sorted(miss):
        problems.append(f"{label}: 숫자 {v:g} 가 원문에 없음")


for a in data["articles"]:
    i = a["id"]
    if not a.get("summary_ko"):
        problems.append(f"{i}: 요약 없음")
    valid_sids = {s["id"] for s in a["sources"]}
    multi = (art_dir / f"{i}__s2.txt").exists()
    for k, b in enumerate(a["summary_ko"]):
        if not b.get("source_ids"):
            problems.append(f"{i} 요약[{k}]: 출처 없음")
        for sid in b.get("source_ids", []):
            if sid not in valid_sids:
                problems.append(f"{i} 요약[{k}]: 존재하지 않는 출처 {sid}")
        if multi:  # 복수 출처: 그 문장이 인용한 출처 본문하고만 대조(더 엄격)
            key = f"{i}#{k}"
            src_text[key] = "\n".join((art_dir / f"{i}__{sid}.txt").read_text(encoding="utf-8") for sid in b["source_ids"])
            check_numbers(f"{i} 요약[{k}]", b["text"], [key])
        else:
            check_numbers(f"{i} 요약[{k}]", b["text"], [i])
    if a["region"] == "foreign":
        pairs = a["easy_en_pairs"]
        en_all = " ".join(p["en"] for p in pairs)
        check_numbers(f"{i} 쉬운영어", en_all, [i])
        src_n = norm(src_text[i])
        for k, p in enumerate(pairs):
            check_numbers(f"{i} 해석[{k}]", p["ko"], [i])
            if not p["ko"].strip():
                problems.append(f"{i} 해석[{k}]: 비어 있음")
            n = len(p["en"].split())
            if n > 25:
                problems.append(f"{i} 쉬운영어[{k}]: {n}단어 (25 초과)")
        for v in a["vocab"]:
            if norm(v["example"]) not in src_n:
                problems.append(f"{i} 단어 '{v['word']}': 예문이 원문에 그대로 없음 -> {v['example']}")
        if not (8 <= len(a["vocab"]) <= 12):
            problems.append(f"{i}: 단어장 {len(a['vocab'])}개")
        notes.append(f"{i}: 쉬운 영어 {len(en_all.split())}단어/{len(pairs)}문장, 단어장 {len(a['vocab'])}개")

# 독자 반응(댓글): 원본 수집 기록(comments_raw/<id>.txt)에 그대로 있는지 대조하고, 작성자 정보·빈 값을 확인
for a in data["articles"]:
    cm = a.get("comments")
    if not cm:
        continue
    raw_file = ROOT / "data/work/comments_raw" / day / f"{a['id']}.txt"
    if not raw_file.exists():
        problems.append(f"{a['id']} 댓글: 원본 수집 기록 파일이 없음")
        continue
    # 원본 기록은 줄바꿈을 글자 '\n' 으로 기록하므로 공백으로 통일해 비교한다
    raw_n = re.sub(r"\s+", " ", raw_file.read_text(encoding="utf-8").replace("\\n", " "))
    for k, c in enumerate(cm["items"]):
        if not c.get("text", "").strip() or c.get("likes") is None:
            problems.append(f"{a['id']} 댓글[{k}]: 텍스트/공감 수 비어 있음")
        elif re.sub(r"\s+", " ", c["text"]) not in raw_n:
            problems.append(f"{a['id']} 댓글[{k}]: 원본 수집 기록에 그대로 없음 -> {c['text'][:30]}")
        if set(c) - {"portal", "text", "likes", "url", "article", "replies"}:
            problems.append(f"{a['id']} 댓글[{k}]: 허용되지 않은 필드 {set(c) - {'portal', 'text', 'likes', 'url', 'article', 'replies'}} (작성자 정보 등)")
    notes.append(f"{a['id']}: 독자 반응 댓글 {len(cm['items'])}개 (원본 대조 완료)")

# 정치권 입장 대댓글: 근거 문구가 실제 기사 본문에 있는지, 요약의 숫자가 그 기사에 있는지, 필드가 규칙에 맞는지 확인
st_index_path = ROOT / "data/work/statements" / day / "index.json"
st_index = json.loads(st_index_path.read_text(encoding="utf-8")) if st_index_path.exists() else {}
OK_FIELDS = {"side", "party", "who", "date", "summary", "source_title", "source_url", "evidence", "none"}
n_rep = n_none = 0
for a in data["articles"]:
    for ci, c in enumerate((a.get("comments") or {}).get("items", [])):
        for ri, r in enumerate(c.get("replies", [])):
            tag = f"{a['id']} 댓글[{ci}] 대댓글[{ri}]"
            if set(r) - OK_FIELDS:
                problems.append(f"{tag}: 허용되지 않은 필드 {set(r) - OK_FIELDS}")
            if r.get("side") not in ("ruling", "opposition", "government"):
                problems.append(f"{tag}: side 값 이상 {r.get('side')}")
            if not r.get("summary", "").strip():
                problems.append(f"{tag}: 요약 비어 있음")
            if r.get("none"):
                n_none += 1
                continue
            n_rep += 1
            for fld in ("party", "who", "date", "source_url", "source_title", "evidence"):
                if not r.get(fld):
                    problems.append(f"{tag}: {fld} 비어 있음")
            ent = st_index.get(r.get("source_url", ""))
            if not ent:
                problems.append(f"{tag}: 출처 주소가 출처 목록(index.json)에 없음")
                continue
            body = (ROOT / ent["file"]).read_text(encoding="utf-8")
            if re.sub(r"\s+", " ", r["evidence"]) not in re.sub(r"\s+", " ", body):
                problems.append(f"{tag}: 근거 문구가 기사 본문에 없음 -> {r['evidence']}")
            key = f"rep:{tag}"
            src_text[key] = body
            check_numbers(tag, r["summary"], [key])
notes.append(f"정치권 입장 대댓글 {n_rep}개(근거 문구 원문 대조 완료) + ‘발언 못 찾음’ 표시 {n_none}개")

for k, b in enumerate(data["briefing"]):
    check_numbers(f"브리핑[{k}]", b["text"], b["refs"])
for c, v in data["categories"].items():
    check_numbers(f"총평[{c}]", v["overview"]["text"], v["overview"]["refs"])
    for r in v["overview"]["refs"]:
        if r not in v["article_ids"]:
            problems.append(f"총평[{c}]: 참조 {r} 가 이 카테고리에 없음")

print("\n".join(notes))
print(f"기사 {len(data['articles'])}건")
print("--- 문제 없음 ---" if not problems else f"--- 문제 {len(problems)}건 ---")
for p in problems:
    print(p)
