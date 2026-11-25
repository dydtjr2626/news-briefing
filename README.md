# news-briefing

매일 분야별(경제·정치·AI·반도체)로 가장 핫한 뉴스를 골라 요약하고, 해외 기사는 영어 학습 자료(쉬운 영어·해석·단어장)로 만들어 한 장짜리 웹페이지로 보여 주는 개인용 도구입니다. 이 저장소에는 **코드와 작성 지침만** 있고, 기사 원문·요약·결과 페이지는 들어 있지 않습니다.

## 흐름

1. 수집: `collect.py`가 `sources.json`의 RSS에서 기사 목록을 모읍니다.
2. 화제 확인: `trending.py`, `buzz.py`, `shortlist.py`로 핫한 기사를 추립니다.
3. 선별: 분야마다 가장 핫한 기사 최대 2건을 `selection-<날짜>.json`으로 저장합니다.
4. 본문 확보: `fetch_articles.py`가 본문을 받습니다.
5. 작성: 하위 에이전트가 지침(`writer-domestic.md`, `writer-foreign.md`)대로 초안을 씁니다.
6. 조립·검증: `assemble_day.py`로 하루치 JSON을 만들고 `verify_day.py`로 숫자·예문·출처를 원문과 대조합니다.
7. 화면: `build_html.py`가 `site/index.html`을 만듭니다.

## 사용 방법

[Claude Code](https://claude.com/claude-code)에서 이 폴더를 열고 새 대화에서 실행합니다.

```
/daily-brief            # 오늘 날짜
/daily-brief 2026-11-25 # 날짜 지정
```

전체 절차와 설정(분야당 기사 수, 핫함 기준, 검수 강도)은 [`.claude/skills/daily-brief/SKILL.md`](.claude/skills/daily-brief/SKILL.md)에 있습니다. 하위 에이전트 역할 분담은 [`teams/README.md`](teams/README.md)를 보세요.

필요한 것: Python 3(표준 라이브러리만 사용), Claude Code.

## 구성

| 경로 | 설명 |
|---|---|
| `sources.json` | 분야별 RSS 출처와 키워드 필터 |
| `collect.py`, `trending.py`, `buzz.py`, `shortlist.py` | 수집·화제·후보 추리기 |
| `fetch_articles.py` | 기사 본문 받기 |
| `assemble_day.py`, `verify_day.py`, `verify.py` | 하루치 조립과 검증 |
| `build_html.py` | 웹페이지 생성 |
| `desktop_widget/brief_widget.py` | 윈도우 바탕화면 헤드라인 위젯(tkinter) |
| `.claude/skills/daily-brief/` | 브리핑 스킬과 작성 지침 |
| `teams/README.md` | 역할별 지시서 |

## 참고

- 위젯의 데이터 경로(`C:\Users\User\Desktop\kim\newspaper\data\out`)는 본인 환경에 맞게 고쳐 쓰세요.
- 기사 원문과 결과물은 저작권 때문에 저장소에서 제외했습니다(`.gitignore`의 `data/`, `site/`).
- 요약은 AI가 쓰므로 자동 검증과 검수를 거쳐도 오류가 있을 수 있습니다. 중요한 내용은 원문을 확인하세요.
