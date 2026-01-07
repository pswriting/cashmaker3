import time
import textwrap
import uuid
from datetime import datetime
import streamlit as st

# =========================================================
# 0) Page config (MUST be first Streamlit call)
# =========================================================
st.set_page_config(
    page_title="Ebook Studio • Ultra Artist Console",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# 1) Ultra UI (CSS + JS)
# =========================================================
def inject_ultra_ui():
    st.markdown(
        r"""
<style>
/* =========================================================
   ULTRA ARTIST CONSOLE — Production-grade Streamlit skin
   ========================================================= */
:root{
  --bg0:#05060a;
  --bg1:#070917;
  --bg2:#0b1026;

  --card: rgba(255,255,255,.07);
  --card2: rgba(255,255,255,.10);

  --stroke: rgba(255,255,255,.14);
  --stroke2: rgba(255,255,255,.20);

  --text: rgba(255,255,255,.92);
  --muted: rgba(255,255,255,.64);
  --muted2: rgba(255,255,255,.50);

  --a1:#7c3aed;  /* violet */
  --a2:#22d3ee;  /* cyan */
  --a3:#fb7185;  /* rose */
  --a4:#f59e0b;  /* amber */
  --good:#34d399;
  --bad:#fb7185;

  --radius: 22px;
  --r2: 18px;
  --shadow: 0 22px 90px rgba(0,0,0,.55);
}

html, body, [data-testid="stAppViewContainer"]{
  background:
      radial-gradient(1100px 700px at 12% 10%, rgba(124,58,237,.26), transparent 55%),
      radial-gradient(900px 650px at 86% 22%, rgba(34,211,238,.20), transparent 52%),
      radial-gradient(1000px 700px at 45% 92%, rgba(251,113,133,.10), transparent 60%),
      linear-gradient(180deg, var(--bg0), var(--bg1) 45%, var(--bg2));
  color: var(--text);
}

/* Kill Streamlit chrome */
header, footer { visibility: hidden; height: 0px; }
.block-container{ padding-top: 2.1rem; padding-bottom: 4rem; max-width: 1220px; }
[data-testid="stSidebar"], [data-testid="collapsedControl"]{ display:none !important; }

/* Layer stack */
[data-testid="stAppViewContainer"] > .main { position: relative; z-index: 10; }

/* =========================================================
   Ambient layers
   ========================================================= */
.aurora{
  position: fixed; inset:-35vh -35vw;
  pointer-events:none; z-index:0;
  filter: blur(70px); opacity:.78;
}
.aurora:before, .aurora:after{
  content:""; position:absolute; border-radius:50%;
  width: 60vw; height: 60vw;
  background: conic-gradient(from 180deg,
    rgba(124,58,237,.55),
    rgba(34,211,238,.45),
    rgba(251,113,133,.30),
    rgba(245,158,11,.22),
    rgba(124,58,237,.55)
  );
  mix-blend-mode: screen;
  animation: aurFloat1 18s ease-in-out infinite;
}
.aurora:after{
  width: 44vw; height: 44vw;
  right: 12%; top: 18%;
  opacity:.70;
  animation: aurFloat2 22s ease-in-out infinite;
}
@keyframes aurFloat1{
  0%{ transform: translate(6%, 2%) rotate(0deg) scale(1.0); }
  50%{ transform: translate(-9%, 11%) rotate(150deg) scale(1.14); }
  100%{ transform: translate(6%, 2%) rotate(290deg) scale(1.0); }
}
@keyframes aurFloat2{
  0%{ transform: translate(-4%, -4%) rotate(0deg) scale(1.0); }
  50%{ transform: translate(13%, -7%) rotate(-120deg) scale(1.18); }
  100%{ transform: translate(-4%, -4%) rotate(-240deg) scale(1.0); }
}

/* Grid drift + mask */
.grid{
  position: fixed; inset: 0;
  z-index:1; pointer-events:none;
  background-image:
    linear-gradient(rgba(255,255,255,.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.05) 1px, transparent 1px);
  background-size: 64px 64px;
  mask-image: radial-gradient(520px 420px at 50% 22%, black 35%, transparent 74%);
  opacity:.28;
  transform: translateZ(0);
  animation: gridDrift 12s linear infinite;
}
@keyframes gridDrift{
  0%{ background-position: 0 0, 0 0; }
  100%{ background-position: 64px 64px, 64px 64px; }
}

/* Scanlines + grain */
.scanlines{
  position: fixed; inset:0;
  z-index:2; pointer-events:none;
  background: repeating-linear-gradient(
    to bottom,
    rgba(255,255,255,.03),
    rgba(255,255,255,.03) 1px,
    transparent 1px,
    transparent 3px
  );
  opacity:.10;
  mix-blend-mode: overlay;
}
.grain{
  position: fixed; inset:0;
  z-index:3; pointer-events:none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='240' height='240'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='240' height='240' filter='url(%23n)' opacity='.30'/%3E%3C/svg%3E");
  opacity:.10;
  mix-blend-mode: overlay;
  animation: grainMove 6s steps(8) infinite;
}
@keyframes grainMove{
  0%{ transform: translate(0,0); }
  25%{ transform: translate(-2%, 1%); }
  50%{ transform: translate(2%, -1%); }
  75%{ transform: translate(-1%, -2%); }
  100%{ transform: translate(0,0); }
}

/* Cursor glow (moved by JS) */
#cursorGlow{
  position: fixed;
  width: 520px; height: 520px;
  left: -9999px; top: -9999px;
  border-radius: 50%;
  pointer-events:none; z-index:4;
  background: radial-gradient(circle at 35% 35%,
    rgba(34,211,238,.22),
    rgba(124,58,237,.18),
    rgba(251,113,133,.10),
    transparent 60%
  );
  filter: blur(10px);
  mix-blend-mode: screen;
  transition: transform .06s linear;
}

/* =========================================================
   Hero
   ========================================================= */
.hero{
  position: relative;
  border-radius: var(--radius);
  padding: 30px 28px 22px;
  border: 1px solid var(--stroke);
  background: linear-gradient(135deg, rgba(255,255,255,.10), rgba(255,255,255,.05));
  box-shadow: var(--shadow);
  overflow:hidden;
  transform: translateZ(0);
  animation: rise .95s ease-out both;
}
@keyframes rise{
  from{ opacity:0; transform: translateY(12px) scale(.99); }
  to{ opacity:1; transform: translateY(0) scale(1); }
}
.hero .flare{
  position:absolute; inset: -30%;
  background:
    radial-gradient(circle at 20% 25%, rgba(124,58,237,.30), transparent 42%),
    radial-gradient(circle at 78% 18%, rgba(34,211,238,.22), transparent 45%),
    radial-gradient(circle at 55% 88%, rgba(245,158,11,.14), transparent 50%);
  filter: blur(14px);
  animation: flarePulse 7.5s ease-in-out infinite;
}
@keyframes flarePulse{
  0%,100%{ transform: scale(1); opacity:.90; }
  50%{ transform: scale(1.06); opacity:1; }
}
.hero .badgeRow{
  display:flex; gap:10px; align-items:center; flex-wrap: wrap;
  margin-bottom: 12px;
}
.pill{
  font-size: 12px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,.16);
  background: rgba(255,255,255,.06);
  color: rgba(255,255,255,.80);
  letter-spacing: .08em;
  text-transform: uppercase;
}
.hero h1{
  margin: 8px 0 10px;
  font-size: 52px;
  line-height: 1.03;
  letter-spacing: -0.03em;
}
.hero .sub{
  font-size: 16px;
  color: var(--muted);
  max-width: 78ch;
}
.hero .divider{
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,.22), transparent);
  margin: 16px 0 12px;
}
.hero .meta{
  display:flex; gap:14px; flex-wrap:wrap;
  color: var(--muted2);
  font-size: 13px;
}

/* =========================================================
   Cards + Reveal
   ========================================================= */
.card{
  border: 1px solid var(--stroke);
  border-radius: var(--r2);
  padding: 18px 18px 16px;
  background: linear-gradient(180deg, rgba(255,255,255,.09), rgba(255,255,255,.05));
  box-shadow: 0 16px 70px rgba(0,0,0,.48);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  overflow:hidden;
  transform: translateZ(0);
  opacity: 0;
  transform: translateY(14px);
}
.card.revealed{
  opacity: 1;
  transform: translateY(0px);
  transition: opacity .7s ease, transform .7s ease;
}
.cardTop{
  display:flex; align-items:center; justify-content:space-between; gap:12px;
  margin-bottom: 10px;
}
.cardTitle{
  font-size: 18px; font-weight: 850; letter-spacing: -0.01em;
}
.tag{
  font-size: 12px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,.16);
  background: rgba(255,255,255,.06);
  color: rgba(255,255,255,.78);
}
.hr{
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,.16), transparent);
  margin: 12px 0 14px;
}
.small{
  font-size: 12.5px;
  color: var(--muted);
  line-height: 1.55;
}

/* 3D Tilt target */
.tilt{
  transform-style: preserve-3d;
  will-change: transform;
}

/* =========================================================
   Inputs / Buttons
   ========================================================= */
label, .stTextInput label, .stTextArea label, .stSelectbox label{
  color: rgba(255,255,255,.82) !important;
}

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea{
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,.18) !important;
  background: rgba(10,12,20,.55) !important;
  color: rgba(255,255,255,.92) !important;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,.04);
  transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus{
  border-color: rgba(34,211,238,.55) !important;
  box-shadow: 0 0 0 7px rgba(34,211,238,.12) !important;
  transform: translateY(-1px);
}

/* Make selectboxes match */
div[data-testid="stSelectbox"] > div{
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,.18) !important;
  background: rgba(10,12,20,.55) !important;
  color: rgba(255,255,255,.92) !important;
}
div[data-testid="stSelectbox"] svg{ color: rgba(255,255,255,.70) !important; }

.stButton button{
  width: 100%;
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,.18);
  background: linear-gradient(135deg, rgba(124,58,237,.90), rgba(34,211,238,.58));
  color: white;
  font-weight: 850;
  letter-spacing: .02em;
  padding: 12px 14px;
  box-shadow: 0 18px 72px rgba(0,0,0,.50);
  transition: transform .15s ease, filter .15s ease, box-shadow .15s ease;
  position: relative;
  overflow: hidden;
}
.stButton button:before{
  content:"";
  position:absolute; inset:-60%;
  background: radial-gradient(circle at 30% 30%,
    rgba(255,255,255,.28), transparent 55%);
  transform: translateX(-30%) translateY(10%) rotate(12deg);
  opacity:0;
  transition: opacity .25s ease;
}
.stButton button:hover{
  transform: translateY(-2px);
  filter: brightness(1.06);
  box-shadow: 0 24px 92px rgba(0,0,0,.62);
}
.stButton button:hover:before{ opacity:.95; }
.stButton button:active{ transform: translateY(0px) scale(.99); }

/* Secondary buttons (we'll add a class via wrapper) */
.secondaryBtn button{
  background: rgba(255,255,255,.08) !important;
  border: 1px solid rgba(255,255,255,.16) !important;
}
.secondaryBtn button:hover{
  filter: brightness(1.12);
}

/* =========================================================
   Output panel
   ========================================================= */
.outputShell{
  border-radius: var(--r2);
  border: 1px solid rgba(255,255,255,.14);
  background: rgba(0,0,0,.20);
  padding: 14px 14px;
  overflow:auto;
  max-height: 560px;
}
.outputShell .mono{
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 13.5px;
  line-height: 1.65;
  color: rgba(255,255,255,.88);
  white-space: pre-wrap;
}

/* =========================================================
   Cinematic Loader
   ========================================================= */
.loaderWrap{
  border-radius: var(--r2);
  border: 1px solid rgba(255,255,255,.14);
  background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(0,0,0,.15));
  padding: 16px;
  box-shadow: 0 16px 70px rgba(0,0,0,.42);
}
.loaderTop{
  display:flex; justify-content:space-between; align-items:center; gap:12px;
  margin-bottom: 10px;
}
.loaderTitle{
  font-weight: 900; letter-spacing:-0.01em;
}
.loaderPct{
  font-family: ui-monospace, Menlo, Monaco, Consolas, monospace;
  color: rgba(255,255,255,.74);
}
.progressBar{
  height: 10px;
  border-radius: 999px;
  background: rgba(255,255,255,.08);
  border: 1px solid rgba(255,255,255,.12);
  overflow:hidden;
}
.progressFill{
  height: 100%;
  width: 0%;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(34,211,238,.75), rgba(124,58,237,.75), rgba(251,113,133,.60));
  box-shadow: 0 0 18px rgba(34,211,238,.25);
  transition: width .18s ease;
}
.loaderLine{
  margin-top: 10px;
  color: rgba(255,255,255,.66);
  font-size: 13px;
}

/* =========================================================
   Responsive
   ========================================================= */
@media (max-width: 980px){
  .hero h1{ font-size: 40px; }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce){
  .aurora:before, .aurora:after, .grid, .grain { animation: none !important; }
}
</style>

<div class="aurora"></div>
<div class="grid"></div>
<div class="scanlines"></div>
<div class="grain"></div>
<div id="cursorGlow"></div>

<script>
(function(){
  // Cursor glow tracking
  const glow = document.getElementById("cursorGlow");
  let x = -9999, y = -9999;
  let tx = x, ty = y;

  window.addEventListener("mousemove", (e) => {
    x = e.clientX - 260;
    y = e.clientY - 260;
  });

  function glowAnim(){
    tx += (x - tx) * 0.12;
    ty += (y - ty) * 0.12;
    glow.style.left = tx + "px";
    glow.style.top  = ty + "px";
    requestAnimationFrame(glowAnim);
  }
  glowAnim();

  // Reveal cards on view
  const reveal = () => {
    const cards = document.querySelectorAll(".card");
    const vh = window.innerHeight || 800;
    cards.forEach(c => {
      const r = c.getBoundingClientRect();
      if(r.top < vh * 0.92) c.classList.add("revealed");
    });
  };
  window.addEventListener("scroll", reveal);
  window.addEventListener("load", reveal);
  setTimeout(reveal, 200);

  // 3D Tilt
  const tiltEls = document.querySelectorAll(".tilt");
  const clamp = (v, min, max) => Math.min(Math.max(v, min), max);
  tiltEls.forEach(el => {
    el.addEventListener("mousemove", (e) => {
      const rect = el.getBoundingClientRect();
      const px = (e.clientX - rect.left) / rect.width;
      const py = (e.clientY - rect.top) / rect.height;
      const rx = clamp((0.5 - py) * 10, -8, 8);
      const ry = clamp((px - 0.5) * 12, -10, 10);
      el.style.transform = `perspective(900px) rotateX(${rx}deg) rotateY(${ry}deg) translateY(-1px)`;
    });
    el.addEventListener("mouseleave", () => {
      el.style.transform = "perspective(900px) rotateX(0deg) rotateY(0deg) translateY(0px)";
    });
  });

  // Parallax grid subtle
  window.addEventListener("mousemove", (e) => {
    const gx = (e.clientX / window.innerWidth - 0.5) * 6;
    const gy = (e.clientY / window.innerHeight - 0.5) * 6;
    const grid = document.querySelector(".grid");
    if(grid) grid.style.transform = `translate(${gx}px, ${gy}px) translateZ(0)`;
  });

})();
</script>
        """,
        unsafe_allow_html=True,
    )

def hero(title: str, subtitle: str, pills=None, meta=None):
    pills = pills or ["EBOOK STUDIO", "ARTIST CONSOLE", "PRODUCTION"]
    meta = meta or ["Aurora Motion", "3D Tilt Cards", "Cinematic Loader", "Typewriter", "Clipboard + Export"]

    pills_html = "".join([f"<div class='pill'>{p}</div>" for p in pills])
    meta_html = " · ".join(meta)

    st.markdown(
        f"""
<div class="hero tilt">
  <div class="flare"></div>
  <div class="badgeRow">{pills_html}</div>
  <h1>{title}</h1>
  <div class="sub">{subtitle}</div>
  <div class="divider"></div>
  <div class="meta">{meta_html}</div>
</div>
        """,
        unsafe_allow_html=True,
    )

def card_open(title: str, tag: str = "", tilt: bool = True):
    tag_html = f"<div class='tag'>{tag}</div>" if tag else ""
    tilt_class = "tilt" if tilt else ""
    st.markdown(
        f"""
<div class="card {tilt_class}">
  <div class="cardTop">
    <div class="cardTitle">{title}</div>
    {tag_html}
  </div>
  <div class="hr"></div>
        """,
        unsafe_allow_html=True,
    )

def card_close():
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 2) Production-friendly generation plumbing (Gemini plug-in)
# =========================================================
DEFAULT_PROMPT_TEMPLATE = """너는 전자책 집필을 위한 '편집장 + 퍼포먼스 마케터'다.
아래 조건을 만족하는 전자책 초안을 만들어라.

[주제]
{topic}

[독자]
{reader}

[톤/스타일]
{tone}

[목차(초안)]
{outline}

[요구사항]
- 문장을 짧게, 바로 이해되게 쓴다.
- 전문용어는 최소화하되, 필요한 경우 1문장 정의를 붙인다.
- 각 장마다 '체크리스트'와 '즉시 실행 과제'를 넣는다.
- 마지막에는 전체 요약 + 다음 7일 실행 플랜을 제시한다.

[추가 지시]
{extra}
"""

def build_prompt(topic: str, reader: str, tone: str, outline: str, extra: str) -> str:
    outline = outline.strip() if outline.strip() else "- (목차 미입력)"
    extra = extra.strip() if extra.strip() else "- (추가 지시 없음)"
    return DEFAULT_PROMPT_TEMPLATE.format(
        topic=topic.strip(),
        reader=reader.strip(),
        tone=tone.strip(),
        outline=outline,
        extra=extra,
    )

def generate_with_model(prompt: str, api_key: str | None = None) -> str:
    """
    프로덕션에서는 여기를 실제 Gemini 호출로 교체하세요.
    현재는 '더미'로 동작하지만, UX/아트 연출은 최종 수준으로 유지됩니다.

    예) Google Gemini를 쓰는 경우:
      - st.secrets["GEMINI_API_KEY"] 사용 권장
      - 네트워크/의존성/SDK는 사용 환경에 맞춰 추가
    """
    # --- ARTISTIC stub: convincing "real" output ---
    # (당신의 실제 모델 결과 string을 그대로 반환하도록 교체하면 됨)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    demo = f"""
# {extract_topic_from_prompt(prompt)}

> 생성 시각: {now}  
> 목적: “읽는 즉시 실행되는 전자책” — 설명이 아니라 **작동하는 설계**.

---

## 0) 한 문장 정의
이 전자책은 독자가 **오늘 당장 결과를 바꿀 수 있는 설정과 실행 루틴**을 손에 쥐게 만드는 안내서다.

## 1) 전체 지도 (왜 이 순서인가)
- **정의 → 측정 → 세팅 → 실험 → 스케일 → 디버깅**
- 이유는 단순하다. “세팅”은 감이 아니라 **검증 가능한 구조**여야 한다.

## 2) 핵심 원리 3가지
1. **변수는 한 번에 하나만 바꾼다.**  
2. **지표는 먼저 고정한다.** (무엇이 성공인지부터)  
3. **오퍼(제안)가 약하면 최적화는 의미가 없다.**

## 3) 1장 — 준비: 실패가 안 남도록 ‘기록’부터 만든다
### 체크리스트
- [ ] 목표 지표: CTR / CVR / CPA / ROAS 중 무엇인가
- [ ] 실험 단위: 소재 1개, 랜딩 1개, 오퍼 1개
- [ ] 중단 기준: ‘며칠/얼마’에서 끊을지

### 즉시 실행 과제 (10분)
- 오늘부터 “실험 노트”를 만들고, 실험 이름 규칙을 정해라.  
  예: `240107_AUD1_CRT2_OFR1_LP1`

## 4) 2장 — 세팅: ‘좋은 세팅’의 정의는 한 가지다
좋은 세팅이란 **다음 실험이 더 빨라지는 세팅**이다.

### 체크리스트
- [ ] 이벤트/전환 추적이 단절되지 않는다
- [ ] 랜딩의 첫 화면에서 오퍼가 한 문장으로 끝난다
- [ ] 폼/문의/결제 동선이 3클릭 이내다

### 즉시 실행 과제 (20분)
- 랜딩 첫 화면을 한 문장으로 바꿔라.  
  “누구를, 어떤 결과로, 얼마나 빨리”를 한 줄에 넣어라.

## 5) 3장 — 실험: ‘느낌’을 버리고 ‘샷’을 쏜다
- 실험은 예술이 아니라 **사격**이다.  
- 한 발의 총알은 한 개의 가설만 담아야 한다.

### 체크리스트
- [ ] 가설이 한 문장이다
- [ ] 관찰 기간이 정해져 있다
- [ ] 실패 시 수정 포인트가 미리 정해져 있다

### 즉시 실행 과제 (30분)
- 소재 3개를 만들고, ‘한 줄 오퍼’를 전부 다르게 써라.

## 6) 4장 — 스케일: 올리는 게 아니라 ‘부서지지 않게’ 키운다
- 스케일은 “예산 증가”가 아니라 **시스템의 내구성**이다.

### 체크리스트
- [ ] 리드 품질이 떨어지는 구간을 알고 있다
- [ ] 문의 응대 속도가 병목이 되지 않는다
- [ ] 전환 후 후속 메시지가 자동화되어 있다

### 즉시 실행 과제 (30분)
- 문의 후 5분 내 자동 메시지를 세팅해라.  
  “확인 → 기대 → 다음 행동” 순서로 3문장.

## 7) 디버깅: 흔한 실패 7가지와 바로잡는 법
1) CTR만 좋고 전환이 없다 → 오퍼/랜딩 정렬 문제  
2) 전환은 있는데 수익이 없다 → 가격/업셀 구조 문제  
3) 데이터가 들쭉날쭉 → 실험 단위가 너무 큼  
4) 클릭은 있는데 이탈 → 첫 화면이 약함  
5) 문의가 오는데 결제가 없음 → 신뢰/보증/증거 부족  
6) 성과가 잠깐만 좋음 → 타겟 과포화 또는 소재 소진  
7) ROAS가 좋은데 성장 안 됨 → 공급(인력/재고/응대) 병목

## 8) 요약
- 정의 → 측정 → 세팅 → 실험 → 스케일 → 디버깅  
- “한 번에 하나”가 이 책의 규율이다.

## 9) 다음 7일 실행 플랜
- Day1: 목표 지표 확정 + 실험 노트 템플릿 만들기  
- Day2: 랜딩 첫 화면 오퍼 1문장으로 교체  
- Day3: 소재 3개 제작 + 가설 3개 작성  
- Day4: 실험 1개 실행(변수 1개)  
- Day5: 결과 기록 + 다음 수정 포인트 확정  
- Day6: 문의 후 자동 메시지 3문장 세팅  
- Day7: 가장 잘 된 오퍼를 기반으로 소재 확장

---

### 마지막 문장
지금 필요한 것은 ‘더 많은 아이디어’가 아니라 **더 적은 변수**다.
"""
    return textwrap.dedent(demo).strip()

def extract_topic_from_prompt(prompt: str) -> str:
    # Very small helper to make demo outputs feel "real".
    for line in prompt.splitlines():
        if line.strip() and ("[주제]" in line):
            # next non-empty line
            continue
    # fallback: find first non-empty
    for line in prompt.splitlines():
        t = line.strip()
        if t and not t.startswith("[") and len(t) < 80:
            return t
    return "Ebook Draft"

# =========================================================
# 3) UX Effects: typewriter + cinematic loader + clipboard
# =========================================================
def cinematic_loader(steps: list[str], duration_s: float = 2.2):
    """
    Cinematic loader that updates on the page.
    Uses Streamlit placeholders; no external dependencies.
    """
    box = st.empty()

    start = time.time()
    n = len(steps)
    for i, msg in enumerate(steps, start=1):
        # progress from 0..100
        pct = int((i / n) * 100)
        box.markdown(
            f"""
<div class="loaderWrap">
  <div class="loaderTop">
    <div class="loaderTitle">RENDERING</div>
    <div class="loaderPct">{pct}%</div>
  </div>
  <div class="progressBar"><div class="progressFill" style="width:{pct}%"></div></div>
  <div class="loaderLine">{msg}</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        # pace
        time.sleep(max(duration_s / n, 0.08))

    # tiny cinematic pause
    while time.time() - start < duration_s:
        time.sleep(0.02)
    box.empty()

def typewriter_markdown(md: str, speed: float = 0.0035):
    ph = st.empty()
    acc = ""
    for ch in md:
        acc += ch
        ph.markdown(acc)
        time.sleep(speed)
    return ph

def copy_button(html_id: str, text: str, label: str = "COPY TO CLIPBOARD"):
    safe_text = text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    st.markdown(
        f"""
<div class="secondaryBtn">
  <button id="{html_id}" style="
    width:100%;
    border-radius:14px;
    border:1px solid rgba(255,255,255,.16);
    background:rgba(255,255,255,.08);
    padding:12px 14px;
    font-weight:850;
    letter-spacing:.02em;
    color:white;
    cursor:pointer;
  ">{label}</button>
</div>

<script>
(function(){{
  const btn = document.getElementById("{html_id}");
  if(!btn) return;
  const payload = `{safe_text}`;
  btn.addEventListener("click", async () => {{
    try {{
      await navigator.clipboard.writeText(payload);
      const prev = btn.innerText;
      btn.innerText = "COPIED";
      btn.style.filter = "brightness(1.14)";
      setTimeout(() => {{
        btn.innerText = prev;
        btn.style.filter = "none";
      }}, 900);
    }} catch (e) {{
      const prev = btn.innerText;
      btn.innerText = "COPY FAILED";
      setTimeout(() => btn.innerText = prev, 1200);
    }}
  }});
}})();
</script>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# 4) State
# =========================================================
if "unlocked" not in st.session_state:
    st.session_state.unlocked = False

if "history" not in st.session_state:
    # each item: dict(id, ts, topic, result)
    st.session_state.history = []

if "result" not in st.session_state:
    st.session_state.result = ""

if "last_meta" not in st.session_state:
    st.session_state.last_meta = {}

# =========================================================
# 5) Header
# =========================================================
inject_ultra_ui()

hero(
    title="Write like a gallery.\nShip like a product.",
    subtitle="이 콘솔은 ‘내용 생성기’가 아니라, 결과가 더 잘 팔리도록 설계된 ‘연출 엔진’입니다.",
    pills=["Funnel Hacker", "Ebook Studio", "Ultra Artist UI", "Production Build"],
    meta=["Aurora + Grid Parallax", "3D Tilt + Reveal", "Cinematic Loader", "Clipboard + Export", "History Vault"],
)

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

# =========================================================
# 6) Layout
# =========================================================
left, right = st.columns([1, 1], gap="large")

# -----------------------------
# Left: Access + Templates + History
# -----------------------------
with left:
    card_open("ACCESS GATE", tag="SECURE", tilt=True)

    # Passphrase: either st.secrets["PASSPHRASE"] or fallback.
    secret_pass = None
    try:
        secret_pass = st.secrets.get("PASSPHRASE", None)
    except Exception:
        secret_pass = None

    passphrase = st.text_input("비밀번호", type="password", placeholder="Enter passphrase")
    st.caption("Public repo면 비밀번호/API Key는 st.secrets(.streamlit/secrets.toml)로 분리하세요.")

    colA, colB = st.columns(2)
    with colA:
        unlock = st.button("UNLOCK CONSOLE")
    with colB:
        lock = st.button("LOCK")

    if unlock:
        # Fallback passphrase if not provided in secrets
        expected = secret_pass or "funnelhacker"
        if passphrase.strip() == expected:
            st.session_state.unlocked = True
            st.success("Unlocked.")
        else:
            st.session_state.unlocked = False
            st.error("Wrong passphrase.")

    if lock:
        st.session_state.unlocked = False
        st.info("Locked.")

    st.markdown(
        "<div class='small'>권장: <b>.streamlit/secrets.toml</b>에 PASSPHRASE, GEMINI_API_KEY 저장.</div>",
        unsafe_allow_html=True,
    )
    card_close()

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    card_open("PROMPT PRESETS", tag="EDITOR", tilt=True)
    preset = st.selectbox(
        "프리셋",
        [
            "전자책 (실행형 가이드)",
            "세일즈 레터 (구매 욕구 증폭)",
            "랜딩페이지 (히어로+증거+CTA)",
            "광고 소재 (후킹 20개)",
            "릴스 스크립트 (30초)",
        ],
        index=0,
    )

    preset_hint = {
        "전자책 (실행형 가이드)": "각 장: 체크리스트 + 즉시 실행 과제 + 7일 플랜.",
        "세일즈 레터 (구매 욕구 증폭)": "오퍼 구조/리스크 리버설/증거/FAQ 중심.",
        "랜딩페이지 (히어로+증거+CTA)": "Above-the-fold 한 문장 + 섹션 설계.",
        "광고 소재 (후킹 20개)": "후킹 → 문제 → 해결 → CTA의 짧은 포맷.",
        "릴스 스크립트 (30초)": "0~2초 훅 → 3포인트 → 결론 CTA.",
    }
    st.markdown(f"<div class='small'>{preset_hint[preset]}</div>", unsafe_allow_html=True)
    card_close()

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    card_open("HISTORY VAULT", tag="ARCHIVE", tilt=True)
    if st.session_state.history:
        options = [f"{item['ts']} · {item['topic']}" for item in st.session_state.history[::-1]]
        pick = st.selectbox("불러오기", options, index=0)
        if st.button("LOAD SELECTED"):
            idx = options.index(pick)
            item = st.session_state.history[::-1][idx]
            st.session_state.result = item["result"]
            st.success("Loaded from history.")
    else:
        st.markdown("<div class='small'>아직 히스토리가 없습니다. 생성 후 자동 저장됩니다.</div>", unsafe_allow_html=True)

    if st.session_state.history and st.button("CLEAR HISTORY"):
        st.session_state.history = []
        st.session_state.result = ""
        st.info("History cleared.")
    card_close()

# -----------------------------
# Right: Generator
# -----------------------------
with right:
    card_open("GENERATION CONSOLE", tag="MODEL", tilt=True)

    # Prefer secrets for API key
    secret_key = None
    try:
        secret_key = st.secrets.get("GEMINI_API_KEY", None)
    except Exception:
        secret_key = None

    api_key = st.text_input(
        "Gemini API Key (선택)",
        type="password",
        placeholder="권장: secrets.toml에 GEMINI_API_KEY 저장",
        value="" if not secret_key else "• stored in secrets •",
    )
    # if secrets exists, we will use it; otherwise use input (if user pasted).
    resolved_key = secret_key or (api_key.strip() if api_key and "stored" not in api_key else None)

    topic = st.text_input("주제", placeholder="예: 메타 광고 최적화 설정으로 ROAS 올리는 법")
    reader = st.text_input("독자", placeholder="예: 병원 원장 / 1인 사업자 / 크몽 지식서비스 판매자")
    tone = st.selectbox("톤", ["프리미엄", "직관적", "세일즈 중심", "브랜드 에세이", "하드 데이터"], index=0)

    outline = st.text_area(
        "목차(초안)",
        height=140,
        placeholder="예)\n1장 세팅의 철학\n2장 타겟/소재 매칭\n3장 이벤트/전환 최적화\n4장 스케일링\n5장 실패 디버깅"
    )

    extra = st.text_area(
        "추가 지시(금지어/예시/분량/말투/포맷)",
        height=140,
        placeholder="예) 전문용어 최소화, 체크리스트 위주, 30분 안에 실행 가능하게, 사례 2개 포함"
    )

    col1, col2 = st.columns(2)
    with col1:
        temperature = st.slider("크리에이티브 강도", 0.0, 1.0, 0.7, 0.05)
    with col2:
        tw_speed = st.slider("타이핑 연출 속도(초/글자)", 0.0, 0.02, 0.0035, 0.0005)

    can_generate = st.session_state.unlocked and bool(topic.strip())

    if st.button("CREATE FINAL DRAFT"):
        if not st.session_state.unlocked:
            st.warning("먼저 UNLOCK 하세요.")
        elif not topic.strip():
            st.warning("주제를 입력하세요.")
        else:
            # Build prompt based on preset (light adaptation)
            prompt = build_prompt(topic, reader or "일반 독자", tone, outline, extra)
            # preset-specific flavor
            if "세일즈 레터" in preset:
                prompt += "\n\n[추가] 세일즈 레터 구조(훅→문제→해결→증거→오퍼→FAQ→CTA)로 작성해라."
            elif "랜딩페이지" in preset:
                prompt += "\n\n[추가] 랜딩 구조(히어로/증거/사회적증명/FAQ/CTA)를 섹션으로 출력해라."
            elif "광고 소재" in preset:
                prompt += "\n\n[추가] 광고 후킹 20개를 번호로 출력하고, 각 후킹마다 2문장 바디+CTA를 붙여라."
            elif "릴스" in preset:
                prompt += "\n\n[추가] 30초 릴스 스크립트: 0~2초 훅 / 3포인트 / 1문장 CTA로 구성해라."

            # Cinematic loader
            steps = [
                "Aligning intent and reader psychology…",
                "Locking measurement and execution scaffolds…",
                "Forging narrative rhythm and conversion triggers…",
                "Rendering chapters, checklists, and 7-day plan…",
                "Polishing tone, clarity, and momentum…",
            ]
            cinematic_loader(steps, duration_s=2.4)

            # Generate
            result = generate_with_model(prompt, api_key=resolved_key)

            # Save state + history
            st.session_state.result = result
            st.session_state.last_meta = {
                "id": str(uuid.uuid4())[:8],
                "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "topic": topic.strip(),
                "preset": preset,
                "tone": tone,
                "temp": temperature,
            }
            st.session_state.history.append(
                {
                    "id": st.session_state.last_meta["id"],
                    "ts": st.session_state.last_meta["ts"],
                    "topic": topic.strip(),
                    "result": result,
                }
            )
            st.success("Final draft generated and saved to History.")

    st.markdown(
        "<div class='small'>현재는 ‘더미 모델’로도 프로덕션 UX를 체감할 수 있게 설계되어 있습니다. "
        "실제 Gemini 호출을 붙이면 결과 퀄리티까지 완전한 프로덕션이 됩니다.</div>",
        unsafe_allow_html=True,
    )
    card_close()

# =========================================================
# 7) Output
# =========================================================
st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

card_open("OUTPUT STAGE", tag="LIVE", tilt=True)

if st.session_state.result:
    meta = st.session_state.last_meta or {}
    meta_line = " · ".join(
        [f"{k}:{v}" for k, v in [
            ("id", meta.get("id", "")),
            ("ts", meta.get("ts", "")),
            ("preset", meta.get("preset", "")),
            ("tone", meta.get("tone", "")),
        ] if v]
    )
    if meta_line:
        st.markdown(f"<div class='small'>{meta_line}</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1], gap="small")

    with c1:
        if st.button("PLAY TYPEWRITER"):
            typewriter_markdown(st.session_state.result, speed=tw_speed)

    with c2:
        # copy (HTML button)
        copy_button(f"copy_{meta.get('id','x')}", st.session_state.result, label="COPY MARKDOWN")

    with c3:
        # download md
        file_name = f"draft_{meta.get('id','draft')}.md"
        st.download_button(
            "DOWNLOAD .MD",
            data=st.session_state.result.encode("utf-8"),
            file_name=file_name,
            mime="text/markdown",
            use_container_width=True,
        )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # default view
    st.markdown(st.session_state.result)

else:
    st.markdown(
        """
<div class="outputShell">
  <div class="mono">
  아직 결과가 없습니다.
  오른쪽 GENERATION CONSOLE에서 주제/독자/목차를 입력하고 CREATE FINAL DRAFT를 누르세요.
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

card_close()

# =========================================================
# 8) Footer note (safe secrets guidance)
# =========================================================
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
st.caption(
    "데모 기본 비밀번호: funnelhacker. "
    "프로덕션에서는 .streamlit/secrets.toml에 PASSPHRASE, GEMINI_API_KEY를 넣고 코드에서 입력란을 숨기는 것을 권장합니다."
)
