"""data/out/*.json 을 모두 읽어 하나의 HTML(site/index.html)로 만든다. 더블클릭으로 열린다(서버 불필요).
화면 구성: 한 페이지를 스크롤로 읽고, 위에 고정된 분야 메뉴(요약·경제·정치·AI·반도체·단어장)로 바로 이동한다."""
import json
from pathlib import Path

ROOT = Path(__file__).parent
days = {}
for p in sorted((ROOT / "data" / "out").glob("*.json")):
    days[p.stem] = json.loads(p.read_text(encoding="utf-8"))
payload = json.dumps(days, ensure_ascii=False).replace("</", "<\\/")

TEMPLATE = r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>오늘의 뉴스 브리핑</title>
<style>
:root{
  --bg:#faf8f3; --card:#faf8f3; --ink:#1d1c1a; --body:#2a2926; --muted:#6b6962; --line:#d9d5c9; --rule:#1d1c1a;
  --accent:#8a2b1f; --accent-ink:#ffffff; --accent-soft:#f1ebe0; --mark:#f6e9b8; --mark-line:#c9a227;
  --serif:"Noto Serif KR","Source Han Serif K","Nanum Myeongjo","Batang","AppleMyungjo",Georgia,serif;
  --sans:"Pretendard","Malgun Gothic","Apple SD Gothic Neo","Noto Sans KR",system-ui,sans-serif;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#16150f; --card:#16150f; --ink:#f0eee6; --body:#dedbd0; --muted:#a09d92; --line:#36342c; --rule:#cfcbbd;
    --accent:#e58a78; --accent-ink:#1a0d09; --accent-soft:#221f17; --mark:#3d3516; --mark-line:#b8932a;
  }
}
:root[data-theme="dark"]{
  --bg:#16150f; --card:#16150f; --ink:#f0eee6; --body:#dedbd0; --muted:#a09d92; --line:#36342c; --rule:#cfcbbd;
  --accent:#e58a78; --accent-ink:#1a0d09; --accent-soft:#221f17; --mark:#3d3516; --mark-line:#b8932a;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--body);font:17.5px/1.75 var(--sans);letter-spacing:-.01em;word-break:keep-all;overflow-wrap:break-word}
a{color:var(--accent);text-underline-offset:3px}
button{font:inherit;color:inherit;cursor:pointer;letter-spacing:inherit;word-break:keep-all}
.wrap{max-width:700px;margin:0 auto;padding:0 20px 96px}
header.top{padding:28px 0 12px;border-bottom:3px double var(--rule);text-align:center}
header.top h1{margin:0;font:700 30px/1.25 var(--serif);letter-spacing:-.02em;color:var(--ink)}
.datebar{display:flex;align-items:center;justify-content:center;gap:12px;margin-top:10px;flex-wrap:wrap}
.datebar .date{font-size:15px;color:var(--muted);font-variant-numeric:tabular-nums}
.btn{border:1px solid var(--line);background:transparent;border-radius:2px;padding:6px 14px;font-size:15px}
.btn:hover:not(:disabled){border-color:var(--ink)}
.btn:disabled{opacity:.35;cursor:default}
.btn.primary{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.searchbar{margin-top:14px}
.searchbar input{width:100%;font:inherit;font-size:16px;color:var(--ink);background:transparent;border:0;border-bottom:1px solid var(--line);border-radius:0;padding:8px 2px;outline:none}
.searchbar input:focus{border-bottom-color:var(--ink)}
mark.hit{background:var(--mark);color:inherit;padding:0 1px}
.res{display:block;width:100%;text-align:left;background:transparent;border:0;border-top:1px solid var(--line);border-radius:0;padding:14px 0;margin:0}
.res:hover .rt{text-decoration:underline}
.res .rm{display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:13.5px;color:var(--muted)}
.res .rt{display:block;font:700 18px/1.45 var(--serif);color:var(--ink);margin:3px 0 2px}
.res .rs{display:block;font-size:15.5px;color:var(--muted);line-height:1.65}
.res .rq{display:block;font-size:16px;line-height:1.65;border-left:2px solid var(--line);padding-left:12px;margin-top:4px}
.sresh{font-size:14px;font-weight:700;margin:28px 0 6px;color:var(--accent);letter-spacing:.02em}
.stick{position:sticky;top:0;z-index:20;background:var(--bg);border-bottom:1px solid var(--line);margin-bottom:6px}
.nav{display:flex;gap:22px;overflow-x:auto;padding:10px 0 0;scrollbar-width:none;justify-content:center}
.nav::-webkit-scrollbar,.subnav::-webkit-scrollbar{display:none}
.nav button{white-space:nowrap;border:0;border-bottom:2px solid transparent;background:transparent;padding:6px 2px 8px;font-size:16px;color:var(--muted);border-radius:0}
.nav button .n{font-size:12.5px;margin-left:4px;opacity:.8}
.nav button:hover{color:var(--ink)}
.nav button[aria-current="true"]{color:var(--ink);border-bottom-color:var(--accent);font-weight:700}
.subnav{display:flex;gap:18px;overflow-x:auto;padding:0 0 9px;scrollbar-width:none;justify-content:center}
.subnav[hidden]{display:none}
.subnav button{white-space:nowrap;border:0;background:transparent;padding:2px 0;font-size:14.5px;color:var(--muted)}
.subnav button .n{font-size:12px;margin-left:3px;opacity:.8}
.subnav button[aria-current="true"]{color:var(--accent);font-weight:700}
.subnav button:hover{color:var(--ink)}
section.sec{scroll-margin-top:112px;padding-top:6px}
.enter{display:grid;grid-template-columns:1fr 1fr;gap:0;margin:8px 0 4px;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.enter button{text-align:left;border:0;background:transparent;padding:18px 18px 16px 0;border-radius:0}
.enter button+button{border-left:1px solid var(--line);padding-left:20px}
.enter button:hover .t{text-decoration:underline}
.enter .t{font:700 21px/1.3 var(--serif);color:var(--ink);display:block}
.enter .c{display:block;margin-top:2px;color:var(--accent);font-size:15px}
.enter .d{display:block;margin-top:6px;font-size:14.5px;color:var(--muted);line-height:1.6}
.enter .go{display:block;margin-top:10px;font-size:14.5px;color:var(--accent)}
.toolbar{display:flex;align-items:center;gap:12px;margin:14px 0 0;flex-wrap:wrap}
.toolbar .note{flex:1;font-size:14.5px;color:var(--muted);min-width:200px}
@media (max-width:520px){ .enter{grid-template-columns:1fr} .enter button+button{border-left:0;border-top:1px solid var(--line);padding-left:0} }
h2.cat-h{font:700 22px/1.3 var(--serif);color:var(--ink);margin:44px 0 14px;padding:10px 0 0;border-top:2px solid var(--rule);display:flex;align-items:baseline;gap:10px}
h2.cat-h .count{font:400 14px var(--sans);color:var(--muted)}
.card{background:transparent;border:0;border-top:1px solid var(--line);border-radius:0;padding:26px 0 8px;margin:0 0 18px;scroll-margin-top:120px}
section.sec .card:first-of-type{border-top:0;padding-top:6px}
.brief{border-top:0;padding-top:8px}
.brief h2{font:700 22px/1.3 var(--serif);color:var(--ink);margin:0 0 6px}
.brief ol{margin:0;padding-left:0;list-style:none;counter-reset:b}
.brief li{counter-increment:b;display:grid;grid-template-columns:26px 1fr;gap:6px;padding:14px 0;border-top:1px solid var(--line)}
.brief li:first-child{border-top:0;padding-top:6px}
.brief li::before{content:counter(b);font:700 20px/1.5 var(--serif);color:var(--accent)}
.chips{display:flex;flex-wrap:wrap;gap:4px 14px;margin-top:4px}
.chip{border:0;background:transparent;padding:0;font-size:14px;color:var(--muted);text-decoration:underline;text-decoration-color:var(--line);text-underline-offset:3px}
.chip:hover{color:var(--accent);text-decoration-color:var(--accent)}
.overview{border-top:1px solid var(--line);padding:18px 0 4px;margin:0}
.overview h3{margin:0 0 4px;font:700 17px/1.4 var(--serif);color:var(--accent)}
.overview p{margin:0}
.meta{display:flex;flex-wrap:wrap;gap:4px 10px;align-items:center;font-size:13.5px;color:var(--muted);margin-bottom:8px}
.badge{padding:0;font-weight:700;font-size:13px;color:var(--accent);letter-spacing:.04em}
.badge.domestic{color:var(--muted)}
.card h3.hl{margin:0 0 4px;font:700 26px/1.38 var(--serif);letter-spacing:-.025em;color:var(--ink)}
.en-title{margin:0 0 12px;color:var(--muted);font:italic 15.5px/1.5 Georgia,serif}
ul.sum{margin:14px 0 0;padding-left:20px}
ul.sum li{margin:0 0 12px;padding-left:2px}
ul.sum li::marker{color:var(--muted)}
a.cite{font-size:12px;text-decoration:none;border:0;padding:0 2px;margin-left:2px;white-space:nowrap;vertical-align:super;line-height:1}
.why{margin:16px 0 0;padding:2px 0 2px 16px;border-left:2px solid var(--accent);font-size:16.5px;color:var(--ink)}
.src{margin-top:16px;font-size:14px;line-height:1.65;color:var(--muted);word-break:break-all}
.reactions{margin-top:22px;padding-top:14px;border-top:1px solid var(--line)}
.reactions .rh{font:700 17px var(--serif);color:var(--ink)}
.reactions .rnote{margin:2px 0 12px;font-size:14px;color:var(--muted)}
blockquote.cm{margin:0 0 16px;padding:2px 0 2px 16px;border-left:2px solid var(--line)}
blockquote.cm p{margin:0;font-size:16.5px;line-height:1.7;white-space:pre-wrap;word-break:keep-all;overflow-wrap:break-word}
blockquote.cm footer{margin-top:6px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;font-size:13.5px;color:var(--muted)}
blockquote.cm .pt{font-weight:700;font-size:13px;color:var(--muted)}
blockquote.cm .from{flex-basis:100%;order:3;font-size:13px;line-height:1.5}
.replies{margin:12px 0 2px 0;padding-left:14px;border-left:1px solid var(--line)}
.rpl-h{font-size:13px;color:var(--muted);margin-bottom:8px;line-height:1.6}
.rp{border-top:1px solid var(--line);padding:8px 0;margin:0}
.rp.none{display:flex;gap:10px;align-items:baseline;color:var(--muted);font-size:14.5px}
.rp-h{display:flex;flex-wrap:wrap;gap:2px 10px;align-items:baseline;font-size:14.5px}
.sd{font-weight:700;font-size:13px;color:var(--accent);white-space:nowrap}
.dt{color:var(--muted);margin-left:auto;font-size:13px}
.rp-t{margin:4px 0 2px;font-size:16px;line-height:1.7}
.rp-s{font-size:13.5px;color:var(--muted);line-height:1.6;word-break:break-all}
.rp-s a{color:var(--muted)}
details.study{margin-top:18px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:12px 0 14px}
details.study>summary{cursor:pointer;font-weight:700;color:var(--ink);list-style:none;padding:2px 0;font-size:16px}
details.study>summary::-webkit-details-marker{display:none}
details.study>summary::before{content:"▸ ";color:var(--accent)}
details.study[open]>summary::before{content:"▾ "}
.en-read{font-size:19px;line-height:1.85;font-family:Georgia,"Times New Roman",var(--serif);color:var(--ink);margin:12px 0 8px;word-break:normal;letter-spacing:0}
.vw{background:linear-gradient(transparent 62%,var(--mark) 62%);cursor:help;position:relative}
.vw:hover::after,.vw:focus::after{content:attr(data-tip);position:absolute;left:0;top:100%;margin-top:6px;z-index:10;width:max-content;max-width:min(280px,80vw);background:var(--ink);color:var(--bg);font:14px/1.5 var(--sans);padding:6px 10px;border-radius:2px;word-break:keep-all}
.tr-btn{margin:6px 0 4px}
.tr{margin:8px 0 0;padding:0;list-style:none;counter-reset:s}
.tr li{counter-increment:s;padding:10px 0 10px 32px;border-top:1px solid var(--line);position:relative}
.tr li::before{content:counter(s);position:absolute;left:0;top:11px;font-size:14px;color:var(--muted);font-variant-numeric:tabular-nums}
.tr .en{display:block;color:var(--muted);font:15.5px/1.7 Georgia,serif;word-break:normal;letter-spacing:0}
.tr .ko{display:block;margin-top:2px}
.vocab{display:grid;gap:0;margin-top:4px}
.vitem{display:grid;grid-template-columns:1fr auto;gap:2px 10px;padding:12px 0;border:0;border-top:1px solid var(--line)}
.vitem .w{font-weight:700;font-size:17.5px;color:var(--ink)}
.vitem .pos{color:var(--muted);font-size:13.5px;margin-left:8px;font-weight:400}
.vitem .k{grid-column:1}
.vitem .ex{grid-column:1/-1;font:italic 15px/1.65 Georgia,serif;color:var(--muted);word-break:normal;letter-spacing:0}
.star{grid-row:1/3;grid-column:2;align-self:start;border:0;background:transparent;width:40px;height:40px;font-size:20px;color:var(--line)}
.star:hover{color:var(--muted)}
.star[aria-pressed="true"]{color:var(--accent)}
.qa{margin-top:6px}
.qa details{border:0;border-top:1px solid var(--line);padding:10px 0;margin:0}
.qa summary{cursor:pointer;font-family:Georgia,serif;font-size:17px;letter-spacing:0;word-break:normal}
.qa .ans{margin:6px 0 0;color:var(--accent);font-family:Georgia,serif;letter-spacing:0;word-break:normal}
.sub{font:700 15px var(--sans);color:var(--ink);margin:20px 0 4px;letter-spacing:.01em}
.empty{color:var(--muted);text-align:center;padding:30px 0}
.flash{text-align:center;padding:28px 16px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin:0 0 14px}
.flash .big{font:700 26px/1.4 var(--serif);color:var(--ink);margin:8px 0}
.flash .small{color:var(--muted);font-size:15px}
.row{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:14px}
.totop{position:fixed;right:14px;bottom:16px;z-index:25;width:42px;height:42px;border-radius:50%;border:1px solid var(--line);background:var(--bg);font-size:18px;display:none}
.totop.show{display:block}
footer{margin-top:44px;padding-top:14px;border-top:1px solid var(--line);color:var(--muted);font-size:13.5px;line-height:1.7}
@media (max-width:520px){
  body{font-size:17px}
  .wrap{padding:0 18px 80px}
  header.top h1{font-size:25px}
  .card h3.hl{font-size:23px}
  .en-read{font-size:18px}
  .nav{gap:16px;justify-content:flex-start}
  .subnav{justify-content:flex-start}
}

</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <h1>오늘의 뉴스 브리핑</h1>
    <div class="datebar">
      <button class="btn" id="prev" aria-label="이전 날짜">←</button>
      <span class="date" id="date"></span>
      <button class="btn" id="next" aria-label="다음 날짜">→</button>
    </div>
    <div class="searchbar">
      <input type="search" id="q" placeholder="검색 (예: 수능, inflation)" aria-label="검색" autocomplete="off" spellcheck="false">
    </div>
  </header>
  <div class="stick">
    <nav class="nav" id="nav" aria-label="보기 선택"></nav>
    <nav class="subnav" id="subnav" aria-label="분야 바로가기" hidden></nav>
  </div>
  <main id="main"></main>
  <footer>요약은 원문 본문만 근거로 작성했고, 숫자와 단어장 예문은 원문과 자동 대조했습니다. 중요한 내용은 각 [1] 링크의 원문에서 한 번 더 확인하세요.</footer>
</div>
<button class="totop" id="totop" type="button" aria-label="맨 위로" title="맨 위로">↑</button>
<script type="application/json" id="data">__DATA__</script>
<script>
(function(){
"use strict";
var DATA = JSON.parse(document.getElementById("data").textContent);
var dates = Object.keys(DATA).sort();
var state = {date: dates[dates.length-1], view: "home", query: "", prevView: "home"};

/* ---------- 저장소 (막혀 있어도 동작) ---------- */
var mem = {};
function load(){ try{ var s = localStorage.getItem("np.words"); return s ? JSON.parse(s) : {}; }catch(e){ return mem; } }
function save(o){ mem = o; try{ localStorage.setItem("np.words", JSON.stringify(o)); }catch(e){} }

/* ---------- DOM 헬퍼 ---------- */
function el(tag, attrs){
  var n = document.createElement(tag);
  if(attrs) for(var k in attrs){
    if(k === "class") n.className = attrs[k];
    else if(k === "text") n.textContent = attrs[k];
    else if(k.slice(0,2) === "on") n.addEventListener(k.slice(2), attrs[k]);
    else if(attrs[k] !== null && attrs[k] !== undefined) n.setAttribute(k, attrs[k]);
  }
  (function add(list){
    for(var i=0;i<list.length;i++){
      var c = list[i];
      if(c === null || c === undefined || c === false) continue;
      if(Array.isArray(c)){ add(c); continue; }
      n.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    }
  })([].slice.call(arguments, 2));
  return n;
}
function esc(s){ return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }
function byId(day, id){ return day.articles.filter(function(a){ return a.id === id; })[0]; }

/* ---------- 단어 하이라이트 ---------- */
function vocabRegex(word){
  var body = word.split(/\s+/).map(esc).join("\\s+");
  return new RegExp("(^|[^A-Za-z])(" + body + "[A-Za-z]{0,3})(?![A-Za-z])", "i");
}
function highlight(text, vocab){
  var spans = [];
  vocab.forEach(function(v){
    var m = vocabRegex(v.word).exec(text);
    if(m){ var start = m.index + m[1].length; spans.push({s:start, e:start + m[2].length, v:v}); }
  });
  spans.sort(function(a,b){ return a.s - b.s; });
  var frag = document.createDocumentFragment(), pos = 0;
  spans.forEach(function(sp){
    if(sp.s < pos) return;
    frag.appendChild(document.createTextNode(text.slice(pos, sp.s)));
    frag.appendChild(el("span", {class:"vw", tabindex:"0", "data-tip": sp.v.word + " · " + sp.v.pos + " · " + sp.v.ko}, text.slice(sp.s, sp.e)));
    pos = sp.e;
  });
  frag.appendChild(document.createTextNode(text.slice(pos)));
  return frag;
}

/* ---------- 기사 카드 ---------- */
function citeLinks(art, ids){
  var out = [];
  (ids||[]).forEach(function(id){
    var s = art.sources.filter(function(x){ return x.id === id; })[0];
    if(s) out.push(el("a", {class:"cite", href:s.url, target:"_blank", rel:"noopener noreferrer", title:s.outlet + ": " + s.title}, "[" + (art.sources.indexOf(s)+1) + "]"));
  });
  return out;
}
function vocabItem(art, v){
  var key = v.word.toLowerCase();
  var btn = el("button", {class:"star", type:"button", "aria-pressed": load()[key] ? "true" : "false", title:"내 단어장에 저장", "aria-label": v.word + " 저장"}, "★");
  btn.addEventListener("click", function(){
    var w = load();
    if(w[key]){ delete w[key]; btn.setAttribute("aria-pressed","false"); }
    else { w[key] = {word:v.word, pos:v.pos, ko:v.ko, example:v.example, from:art.headline_en || art.headline_ko, date:state.date}; btn.setAttribute("aria-pressed","true"); }
    save(w); refreshWords();
  });
  return el("div", {class:"vitem"},
    el("div", {class:"w"}, v.word, el("span", {class:"pos"}, v.pos)),
    btn,
    el("div", {class:"k"}, v.ko),
    el("div", {class:"ex"}, "“" + v.example + "”"));
}
function studyBlock(art){
  var pairs = art.easy_en_pairs;
  var para = el("p", {class:"en-read"});
  pairs.forEach(function(p, i){
    para.appendChild(highlight(p.en, art.vocab));
    if(i < pairs.length-1) para.appendChild(document.createTextNode(" "));
  });
  var tr = el("ol", {class:"tr", hidden:""});
  pairs.forEach(function(p){ tr.appendChild(el("li", null, el("span", {class:"en"}, p.en), el("span", {class:"ko"}, p.ko))); });
  var trBtn = el("button", {class:"btn tr-btn", type:"button", "aria-expanded":"false"}, "해석 보기 (문장별)");
  trBtn.addEventListener("click", function(){
    var open = tr.hasAttribute("hidden");
    if(open) tr.removeAttribute("hidden"); else tr.setAttribute("hidden","");
    trBtn.setAttribute("aria-expanded", open ? "true" : "false");
    trBtn.textContent = open ? "해석 숨기기" : "해석 보기 (문장별)";
  });
  var vocab = el("div", {class:"vocab"});
  art.vocab.forEach(function(v){ vocab.appendChild(vocabItem(art, v)); });
  var qa = el("div", {class:"qa"});
  art.questions.forEach(function(q){ qa.appendChild(el("details", null, el("summary", null, q.q), el("p", {class:"ans"}, q.a))); });
  return el("details", {class:"study", open:""},
    el("summary", null, "영어로 읽기 · 단어 · 질문 (TOEIC 700 수준)"),
    el("p", {style:"margin:8px 0 0;font-size:14.5px;line-height:1.65;color:var(--muted)"}, "먼저 영어를 읽고 직접 해석해 본 뒤, 아래 버튼으로 맞춰 보세요. 노란 표시는 마우스를 올리거나 탭하면 뜻이 나옵니다."),
    para, trBtn, tr,
    el("div", {class:"sub"}, "핵심 단어 (★ 눌러 저장)"), vocab,
    el("div", {class:"sub"}, "이해 확인"), qa);
}
var SIDE = {ruling:["여당","ruling"], opposition:["야당","opposition"], government:["정부","government"]};
function repliesBlock(reps){
  var box = el("div", {class:"replies"}, el("div", {class:"rpl-h"}, "정치권 입장 · 이 쟁점에 대한 공개 발언입니다 (이 댓글에 직접 답한 것은 아닙니다)"));
  reps.forEach(function(r){
    var sd = SIDE[r.side];
    if(r.none){
      box.appendChild(el("div", {class:"rp none"}, el("span", {class:"sd " + sd[1]}, sd[0]), el("span", null, r.summary)));
      return;
    }
    box.appendChild(el("div", {class:"rp"},
      el("div", {class:"rp-h"}, el("span", {class:"sd " + sd[1]}, sd[0]), el("b", null, r.party), el("span", null, r.who), el("span", {class:"dt"}, r.date)),
      el("p", {class:"rp-t"}, r.summary),
      el("div", {class:"rp-s"}, "원문 표현: ‘" + r.evidence + "’ · ", el("a", {href:r.source_url, target:"_blank", rel:"noopener noreferrer"}, r.source_title))));
  });
  return box;
}
function articleCard(art){
  var src = art.sources[0];
  var card = el("article", {class:"card", id:"art-" + art.id},
    el("div", {class:"meta"},
      el("span", {class:"badge " + art.region}, art.region === "foreign" ? "해외" : "국내"),
      el("span", null, src.outlet),
      el("span", null, "· " + (art.confidence === "single-source" ? "단일 출처" : "복수 출처 확인"))),
    el("h3", {class:"hl"}, art.headline_ko),
    art.headline_en ? el("p", {class:"en-title"}, art.headline_en) : null);
  var ul = el("ul", {class:"sum"});
  art.summary_ko.forEach(function(b){
    var li = el("li", null, b.text);
    citeLinks(art, b.source_ids).forEach(function(c){ li.appendChild(c); });
    ul.appendChild(li);
  });
  if(art.region === "foreign"){
    // 영어 공부가 목적이므로 해외 기사는 영어 읽기를 먼저, 한국어 요약은 그 아래에 둔다
    card.appendChild(studyBlock(art));
    card.appendChild(el("div", {class:"sub"}, "한국어 요약"));
  }
  card.appendChild(ul);
  if(art.why_it_matters_ko) card.appendChild(el("p", {class:"why"}, art.why_it_matters_ko));
  if(art.comments && art.comments.items && art.comments.items.length){
    var rx = el("div", {class:"reactions"},
      el("div", {class:"rh"}, "독자 반응 · 포털 베스트 댓글"),
      el("p", {class:"rnote"}, art.comments.note || ""));
    art.comments.items.forEach(function(c){
      var bq = el("blockquote", {class:"cm"},
        el("p", null, c.text),
        el("footer", null,
          el("span", {class:"pt " + c.portal}, c.portal === "naver" ? "네이버" : "다음"),
          el("span", null, "공감 " + (c.likes === null || c.likes === undefined ? "-" : c.likes)),
          c.article ? el("span", {class:"from"}, "「" + c.article + "」 기사") : null,
          c.url ? el("a", {href:c.url, target:"_blank", rel:"noopener noreferrer"}, "댓글창 보기") : null));
      if(c.replies && c.replies.length) bq.appendChild(repliesBlock(c.replies));
      rx.appendChild(bq);
    });
    card.appendChild(rx);
  }
  if(art.sources.length === 1){
    card.appendChild(el("div", {class:"src"}, "원문: ", el("a", {href:src.url, target:"_blank", rel:"noopener noreferrer"}, src.title), " · " + src.published));
  } else {
    var box = el("div", {class:"src"}, "출처 " + art.sources.length + "건");
    art.sources.forEach(function(s, n){
      box.appendChild(el("div", {style:"margin-top:3px"}, "[" + (n+1) + "] " + s.outlet + " · ",
        el("a", {href:s.url, target:"_blank", rel:"noopener noreferrer"}, s.title), " · " + s.published));
    });
    card.appendChild(box);
  }
  return card;
}

/* ---------- 보기 전환 ---------- */
var REGIONS = {domestic:"국내 기사", foreign:"해외 기사"};
var CATS = [["economy","경제"],["politics","정치"],["ai","AI 기술"],["semiconductor","반도체"]];
var CATS_OLD = [["economy","경제"],["politics","정치"],["ai","AI 기술"],["engineering","공학 기술"]];
var CATS_NEW = CATS;
function articlesOf(day, region, cat){
  if(!day.categories[cat]) return [];
  return day.categories[cat].article_ids.map(function(id){ return byId(day, id); }).filter(function(a){ return a && a.region === region; });
}
function countOf(day, region){
  var n = 0; CATS.forEach(function(c){ n += articlesOf(day, region, c[0]).length; }); return n;
}
function setView(v){
  state.view = v; state.query = "";
  var qi = document.getElementById("q"); if(qi) qi.value = "";
  render(); window.scrollTo(0,0);
}
function goArticle(id){
  var day = DATA[state.date], a = byId(day, id); if(!a) return;
  if(state.view !== a.region){ state.view = a.region; render(); }
  var t = document.getElementById("art-" + id);
  if(t) t.scrollIntoView({behavior:"smooth", block:"start"});
}
function jumpTo(cat){
  var t = document.getElementById("sec-" + cat);
  if(t) t.scrollIntoView({behavior:"smooth", block:"start"});
}
function refChips(day, refs){
  var box = el("div", {class:"chips"});
  refs.forEach(function(id){
    var a = byId(day, id); if(!a) return;
    box.appendChild(el("button", {class:"chip", type:"button", onclick:function(){ goArticle(id); }}, a.sources[0].outlet));
  });
  return box;
}

/* ---------- 요약(처음 화면) ---------- */
function homeView(day){
  var wrap = el("div");
  var ol = el("ol");
  day.briefing.forEach(function(b){ ol.appendChild(el("li", null, el("div", null, b.text, refChips(day, b.refs)))); });
  wrap.appendChild(el("div", {class:"card brief"}, el("h2", null, "오늘의 5줄 브리핑"), ol));
  function entry(region, desc){
    var parts = CATS.map(function(c){ return c[1] + " " + articlesOf(day, region, c[0]).length; }).join(" · ");
    return el("button", {type:"button", onclick:function(){ setView(region); }},
      el("span", {class:"t"}, REGIONS[region]),
      el("span", {class:"c"}, countOf(day, region) + "건"),
      el("span", {class:"d"}, parts),
      el("span", {class:"d"}, desc),
      el("span", {class:"go"}, "들어가기 →"));
  }
  wrap.appendChild(el("h2", {class:"cat-h"}, "기사 보러 가기"));
  wrap.appendChild(el("div", {class:"enter"},
    entry("domestic", "한국어 요약 · 출처 링크"),
    entry("foreign", "영어 읽기 · 문장별 해석 · 단어장 · 질문")));
  wrap.appendChild(el("h2", {class:"cat-h"}, "분야별 총평"));
  CATS.forEach(function(c){
    var cat = day.categories[c[0]]; if(!cat) return;
    wrap.appendChild(el("div", {class:"card overview"}, el("h3", null, cat.label), el("p", null, cat.overview.text), refChips(day, cat.overview.refs)));
  });
  return wrap;
}

/* ---------- 국내 기사 / 해외 기사 ---------- */
var studyOpen = true;
function regionView(day, region){
  var wrap = el("div");
  wrap.appendChild(el("h2", {class:"cat-h", style:"margin-top:24px"}, REGIONS[region] + " · " + countOf(day, region) + "건"));
  if(region === "foreign"){
    var tb = el("button", {class:"btn", type:"button"}, studyOpen ? "영어 학습 블록 접기" : "영어 학습 블록 펼치기");
    tb.addEventListener("click", function(){
      studyOpen = !studyOpen;
      [].forEach.call(document.querySelectorAll("details.study"), function(d){ d.open = studyOpen; });
      tb.textContent = studyOpen ? "영어 학습 블록 접기" : "영어 학습 블록 펼치기";
    });
    wrap.appendChild(el("div", {class:"toolbar"}, el("span", {class:"note"}, "영어 읽기 → 해석 확인 → 단어 저장 순서로 보세요."), tb));
  }
  CATS.forEach(function(c){
    var arts = articlesOf(day, region, c[0]);
    var sec = el("section", {class:"sec", id:"sec-" + c[0]},
      el("h2", {class:"cat-h"}, c[1], el("span", {class:"count"}, arts.length + "건")));
    if(!arts.length) sec.appendChild(el("div", {class:"empty", style:"padding:14px 0;text-align:left"}, "오늘은 핫한 " + (region === "foreign" ? "해외" : "국내") + " 기사가 없습니다."));
    arts.forEach(function(a){ sec.appendChild(articleCard(a)); });
    wrap.appendChild(sec);
  });
  return wrap;
}

/* ---------- 단어장 ---------- */
var flash = {queue:[], shown:false};
function refreshWords(){
  var body = document.getElementById("words-body"); if(!body) return;
  body.textContent = "";
  var w = load(), keys = Object.keys(w);
  if(!keys.length){
    body.appendChild(el("div", {class:"empty"}, "아직 저장한 단어가 없어요. 해외 기사의 ‘영어로 읽기’에서 ★를 눌러 저장하세요."));
    return;
  }
  body.appendChild(el("div", {class:"row", style:"justify-content:flex-start;margin:0 0 12px"},
    el("span", {style:"align-self:center;color:var(--muted)"}, "저장한 단어 " + keys.length + "개"),
    el("button", {class:"btn primary", type:"button", onclick:function(){ flash.queue = keys.slice().sort(function(){ return Math.random()-.5; }); flash.shown = false; refreshWords(); }}, "복습 시작")));
  if(flash.queue.length){
    var v = w[flash.queue[0]];
    if(!v){ flash.queue.shift(); return refreshWords(); }
    var card = el("div", {class:"card flash"},
      el("div", {class:"small"}, "남은 카드 " + flash.queue.length + "장 · 뜻을 보고 영어 단어를 떠올려 보세요"),
      el("div", {class:"big"}, v.ko + "  (" + v.pos + ")"));
    if(flash.shown){
      card.appendChild(el("div", {class:"big", style:"color:var(--accent)"}, v.word));
      card.appendChild(el("div", {class:"small", style:"font-family:Georgia,serif;font-style:italic"}, "“" + v.example + "”"));
      card.appendChild(el("div", {class:"row"},
        el("button", {class:"btn primary", type:"button", onclick:function(){ flash.queue.shift(); flash.shown = false; refreshWords(); }}, "알아요"),
        el("button", {class:"btn", type:"button", onclick:function(){ flash.queue.push(flash.queue.shift()); flash.shown = false; refreshWords(); }}, "다시 볼래요")));
    } else {
      card.appendChild(el("div", {class:"row"}, el("button", {class:"btn primary", type:"button", onclick:function(){ flash.shown = true; refreshWords(); }}, "정답 보기")));
    }
    body.appendChild(card);
  }
  keys.sort().forEach(function(k){
    var v = w[k];
    var rm = el("button", {class:"star", type:"button", "aria-pressed":"true", title:"삭제", onclick:function(){ var x = load(); delete x[k]; save(x); refreshWords(); }}, "★");
    body.appendChild(el("div", {class:"vitem", style:"margin-bottom:0"},
      el("div", {class:"w"}, v.word, el("span", {class:"pos"}, v.pos)), rm,
      el("div", {class:"k"}, v.ko),
      el("div", {class:"ex"}, "“" + v.example + "”  · " + v.date)));
  });
}
function wordsView(){
  return el("section", {class:"sec"}, el("h2", {class:"cat-h", style:"margin-top:16px"}, "내 단어장"), el("div", {id:"words-body"}));
}

/* ---------- 검색 ---------- */
var CATLABEL = {economy:"경제", politics:"정치", ai:"AI 기술", engineering:"공학 기술", semiconductor:"반도체"};
function termsOf(q){ return q.toLowerCase().split(/\s+/).filter(Boolean); }
function hasAll(text, terms){ var t = (text || "").toLowerCase(); return terms.every(function(x){ return t.indexOf(x) >= 0; }); }
function hl(text, terms){
  var frag = document.createDocumentFragment(), lower = text.toLowerCase(), pos = 0;
  while(pos < text.length){
    var best = -1, bl = 0;
    terms.forEach(function(t){
      var i = lower.indexOf(t, pos);
      if(i >= 0 && (best < 0 || i < best || (i === best && t.length > bl))){ best = i; bl = t.length; }
    });
    if(best < 0) break;
    frag.appendChild(document.createTextNode(text.slice(pos, best)));
    frag.appendChild(el("mark", {class:"hit"}, text.slice(best, best + bl)));
    pos = best + bl;
  }
  frag.appendChild(document.createTextNode(text.slice(pos)));
  return frag;
}
function around(text, terms, radius){
  var lower = text.toLowerCase(), at = -1;
  terms.forEach(function(t){ var i = lower.indexOf(t); if(i >= 0 && (at < 0 || i < at)) at = i; });
  if(at < 0) return text.slice(0, radius * 2);
  var s = Math.max(0, at - radius), e = Math.min(text.length, at + radius);
  return (s > 0 ? "…" : "") + text.slice(s, e) + (e < text.length ? "…" : "");
}
function runSearch(q){
  var terms = termsOf(q), out = {articles:[], words:[], comments:[], positions:[]};
  dates.slice().reverse().forEach(function(d){
    DATA[d].articles.forEach(function(a){
      var parts = [a.headline_ko, a.headline_en || "", a.why_it_matters_ko || ""];
      a.summary_ko.forEach(function(b){ parts.push(b.text); });
      (a.easy_en_pairs || []).forEach(function(p){ parts.push(p.en); parts.push(p.ko); });
      if(hasAll(parts.join("\n"), terms)){
        var inTitle = hasAll(a.headline_ko + " " + (a.headline_en || ""), terms), pick = null;
        for(var i = 0; i < parts.length && !pick; i++){
          if(parts[i] && terms.some(function(t){ return parts[i].toLowerCase().indexOf(t) >= 0; })) pick = parts[i];
        }
        out.articles.push({d:d, a:a, score: inTitle ? 2 : 1, snip: around(pick || a.headline_ko, terms, 60)});
      }
      (a.vocab || []).forEach(function(v){
        if(hasAll(v.word + " " + v.ko + " " + v.example, terms)) out.words.push({d:d, a:a, v:v});
      });
      if(a.comments && a.comments.items) a.comments.items.forEach(function(c){
        if(hasAll(c.text, terms)) out.comments.push({d:d, a:a, c:c});
        (c.replies || []).forEach(function(r){
          if(!r.none && hasAll([r.party, r.who, r.summary].join(" "), terms)) out.positions.push({d:d, a:a, c:c, r:r});
        });
      });
    });
  });
  out.articles.sort(function(x, y){ return y.score - x.score; });
  return out;
}
function openArticle(d, id){
  var art = byId(DATA[d], id);
  state.date = d; state.query = ""; state.view = art.region;
  var qi = document.getElementById("q"); if(qi) qi.value = "";
  render();
  var t = document.getElementById("art-" + id);
  if(t) t.scrollIntoView({block:"start"});
}
function metaOf(d, a){
  var cat = CATLABEL[a.category] || a.category;
  return [el("span", {class:"badge " + a.region}, a.region === "foreign" ? "해외" : "국내"), el("span", null, d + " · " + cat + " · " + a.sources[0].outlet)];
}
function searchView(){
  var q = state.query, terms = termsOf(q), r = runSearch(q);
  var total = r.articles.length + r.words.length + r.comments.length + r.positions.length;
  var wrap = el("div");
  wrap.appendChild(el("h2", {class:"cat-h", style:"margin-top:24px;font-size:20px"}, "‘" + q + "’ 검색 결과 " + total + "건"));
  if(!total){
    wrap.appendChild(el("div", {class:"empty"}, "결과가 없어요. 다른 단어로 찾아보세요. (여러 단어는 띄어 쓰면 모두 포함된 것을 찾습니다)"));
    return wrap;
  }
  if(r.articles.length){
    wrap.appendChild(el("div", {class:"sresh"}, "기사 " + r.articles.length + "건"));
    r.articles.forEach(function(x){
      wrap.appendChild(el("button", {class:"res", type:"button", onclick:function(){ openArticle(x.d, x.a.id); }},
        el("span", {class:"rm"}, metaOf(x.d, x.a)),
        el("span", {class:"rt"}, hl(x.a.headline_ko, terms)),
        el("span", {class:"rs"}, hl(x.snip, terms))));
    });
  }
  if(r.words.length){
    wrap.appendChild(el("div", {class:"sresh"}, "단어 " + r.words.length + "개"));
    r.words.forEach(function(x){
      wrap.appendChild(el("button", {class:"res", type:"button", onclick:function(){ openArticle(x.d, x.a.id); }},
        el("span", {class:"rm"}, metaOf(x.d, x.a)),
        el("span", {class:"rt"}, hl(x.v.word, terms), el("span", {style:"font-weight:400;color:var(--muted);font-size:13px;margin-left:6px"}, x.v.pos)),
        el("span", {class:"rs"}, hl(x.v.ko, terms)),
        el("span", {class:"rs", style:"font-family:Georgia,serif;font-style:italic"}, hl("“" + x.v.example + "”", terms))));
    });
  }
  if(r.comments.length){
    wrap.appendChild(el("div", {class:"sresh"}, "독자 반응 " + r.comments.length + "건"));
    r.comments.forEach(function(x){
      wrap.appendChild(el("button", {class:"res", type:"button", onclick:function(){ openArticle(x.d, x.a.id); }},
        el("span", {class:"rm"}, metaOf(x.d, x.a), el("span", null, "공감 " + x.c.likes)),
        el("span", {class:"rq"}, hl(x.c.text, terms)),
        el("span", {class:"rs"}, x.a.headline_ko)));
    });
  }
  if(r.positions.length){
    wrap.appendChild(el("div", {class:"sresh"}, "정치권 입장 " + r.positions.length + "건"));
    r.positions.forEach(function(x){
      var sd = SIDE[x.r.side];
      wrap.appendChild(el("button", {class:"res", type:"button", onclick:function(){ openArticle(x.d, x.a.id); }},
        el("span", {class:"rm"}, metaOf(x.d, x.a), el("span", {class:"sd " + sd[1]}, sd[0])),
        el("span", {class:"rt"}, hl(x.r.party + " " + x.r.who, terms)),
        el("span", {class:"rs"}, hl(x.r.summary, terms)),
        el("span", {class:"rs", style:"font-size:12.5px"}, "댓글: " + x.c.text.slice(0, 60))));
    });
  }
  return wrap;
}
var searchTimer = null;
function onSearchInput(){
  var v = this.value.trim();
  clearTimeout(searchTimer);
  searchTimer = setTimeout(function(){
    if(v){
      if(state.view !== "search") state.prevView = state.view;
      state.view = "search"; state.query = v; render(); window.scrollTo(0, 0);
    } else if(state.view === "search"){
      state.query = ""; state.view = state.prevView || "home"; render();
    }
  }, 180);
}

/* ---------- 메뉴 ---------- */
function buildNav(day){
  var nav = document.getElementById("nav"); nav.textContent = "";
  [["home","요약",null],["domestic","국내 기사",countOf(day,"domestic")],["foreign","해외 기사",countOf(day,"foreign")],["words","내 단어장",null]].forEach(function(s){
    var b = el("button", {type:"button", onclick:function(){ setView(s[0]); }}, s[1], s[2] ? el("span", {class:"n"}, String(s[2])) : null);
    if(state.view === s[0]) b.setAttribute("aria-current","true");
    nav.appendChild(b);
  });
  var sub = document.getElementById("subnav"); sub.textContent = "";
  if(state.view === "domestic" || state.view === "foreign"){
    sub.removeAttribute("hidden");
    CATS.forEach(function(c){
      var n = articlesOf(day, state.view, c[0]).length;
      sub.appendChild(el("button", {type:"button", "data-cat":c[0], onclick:function(){ jumpTo(c[0]); }}, c[1], el("span", {class:"n"}, String(n))));
    });
  } else sub.setAttribute("hidden","");
}
function updateSpy(){
  document.getElementById("totop").classList.toggle("show", window.scrollY > 600);
  if(state.view !== "domestic" && state.view !== "foreign") return;
  var current = null;
  CATS.forEach(function(c){
    var sec = document.getElementById("sec-" + c[0]);
    if(sec && (current === null || sec.getBoundingClientRect().top <= 150)) current = c[0];
  });
  if(window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4){
    CATS.forEach(function(c){ if(document.getElementById("sec-" + c[0])) current = c[0]; });
  }
  [].forEach.call(document.querySelectorAll("#subnav button"), function(b){
    if(b.getAttribute("data-cat") === current){
      b.setAttribute("aria-current","true");
      var sub = document.getElementById("subnav");
      if(sub.scrollWidth > sub.clientWidth) sub.scrollLeft = b.offsetLeft - 16;
    } else b.removeAttribute("aria-current");
  });
}
function render(){
  var day = DATA[state.date];
  CATS = (day.categories.engineering && !day.categories.semiconductor) ? CATS_OLD : CATS_NEW;
  document.getElementById("date").textContent = state.date;
  var i = dates.indexOf(state.date);
  document.getElementById("prev").disabled = i <= 0;
  document.getElementById("next").disabled = i >= dates.length-1;
  buildNav(day);
  var main = document.getElementById("main"); main.textContent = "";
  if(state.view === "search") main.appendChild(searchView());
  else if(state.view === "home") main.appendChild(homeView(day));
  else if(state.view === "words") main.appendChild(wordsView());
  else main.appendChild(regionView(day, state.view));
  refreshWords();
  updateSpy();
}
document.getElementById("prev").addEventListener("click", function(){ var i = dates.indexOf(state.date); if(i>0){ state.date = dates[i-1]; render(); window.scrollTo(0,0); } });
document.getElementById("next").addEventListener("click", function(){ var i = dates.indexOf(state.date); if(i<dates.length-1){ state.date = dates[i+1]; render(); window.scrollTo(0,0); } });
document.getElementById("totop").addEventListener("click", function(){ window.scrollTo({top:0, behavior:"smooth"}); });
var ticking = false;
window.addEventListener("scroll", function(){ if(!ticking){ ticking = true; requestAnimationFrame(function(){ updateSpy(); ticking = false; }); } }, {passive:true});
window.addEventListener("resize", updateSpy);
var qi = document.getElementById("q");
qi.addEventListener("input", onSearchInput);
qi.addEventListener("keydown", function(e){ if(e.key === "Escape"){ this.value = ""; onSearchInput.call(this); this.blur(); } });
document.addEventListener("keydown", function(e){
  var tag = document.activeElement ? document.activeElement.tagName : "";
  if(e.key === "/" && !/INPUT|TEXTAREA/.test(tag)){ e.preventDefault(); qi.focus(); }
});
render();
})();
</script>
</body>
</html>
"""

out = ROOT / "site" / "index.html"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(TEMPLATE.replace("__DATA__", payload), encoding="utf-8")
print("생성:", out, f"({out.stat().st_size // 1024} KB, {len(days)}일치)")
