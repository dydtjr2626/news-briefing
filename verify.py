"""1차 자동 검증: 요약·쉬운 영어의 숫자와 단어장 예문이 원문에 실제로 있는지 대조한다.
사용: python -I verify.py <article.json> <source.txt>"""
import json, re, sys
from pathlib import Path

art = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
src = Path(sys.argv[2]).read_text(encoding="utf-8")
norm = lambda s: re.sub(r"\s+", " ", s.replace("’", "'").replace("“", '"').replace("”", '"')).lower()
src_n = norm(src)
src_nums = set(re.findall(r"\d[\d,\.]*\d|\d", src.replace("£", "")))
src_nums = {n.rstrip(".,") for n in src_nums}


def numbers(text):
    text = text.replace("£", "")
    found = set()
    # 한국어 '만' 단위(2,000만 = 20 million)는 원문의 'N million'과 비교
    for m in re.finditer(r"(\d[\d,]*)만", text):
        n = float(m.group(1).replace(",", "")) * 10000
        if f"{n / 1e6:g}" not in {f"{float(x):g}" for x in re.findall(r"(\d+(?:\.\d+)?) million", src)}:
            found.add(m.group(1) + "만")
    text = re.sub(r"\d[\d,]*만", " ", text)
    # '10월', '3년' 같은 월/년 표기는 영어 월 이름·'three years' 와 대조가 어려워 제외
    text = re.sub(r"\d+\s*(월|년)", " ", text)
    return found | {n.rstrip(".,") for n in re.findall(r"\d[\d,\.]*\d|\d", text)}


problems = []
checks = [("summary_ko[%d]" % i, b["text"]) for i, b in enumerate(art["summary_ko"])]
easy_en = " ".join(p["en"] for p in art["easy_en_pairs"])
checks.append(("easy_en", easy_en))
for i, p in enumerate(art["easy_en_pairs"]):
    checks.append((f"해석[{i}]", p["ko"]))
    if not p["ko"].strip():
        problems.append(f"해석[{i}]: 비어 있음")
for name, text in checks:
    for n in sorted(numbers(text) - src_nums):
        problems.append(f"{name}: 숫자 '{n}' 가 원문에 없음 (단위 변환 여부 수동 확인)")

for v in art["vocab"]:
    if norm(v["example"]) not in src_n:
        problems.append(f"vocab '{v['word']}': 예문이 원문에 그대로 없음 -> {v['example']}")

sents = [p["en"] for p in art["easy_en_pairs"]]
long_sents = [s for s in sents if len(s.split()) > 25]
words = len(easy_en.split())
print(f"쉬운 영어: {words}단어, {len(sents)}문장, 25단어 초과 문장 {len(long_sents)}개")
print(f"단어장 {len(art['vocab'])}개, 요약 {len(art['summary_ko'])}줄")
print("--- 문제 ---" if problems else "--- 문제 없음 ---")
for p in problems:
    print(p)
