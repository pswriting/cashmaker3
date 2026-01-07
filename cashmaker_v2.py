# app.py
# -*- coding: utf-8 -*-
import streamlit as st
import google.generativeai as genai

import re
import json
from datetime import datetime
from pathlib import Path

# =========================================================
# Page Config
# =========================================================
st.set_page_config(
    page_title="CASHMAKER — 전자책 작성 프로그램",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# Premium (Apple-like) UI Theme
# =========================================================
PREMIUM_CSS = """
<style>
/* ---------------------------------------------------------
   Apple-like Premium Theme (Minimal + Luxury)
--------------------------------------------------------- */
:root{
  --bg0: #0B0D12;
  --bg1: #0E1117;
  --card: rgba(255,255,255,0.06);
  --card2: rgba(255,255,255,0.04);
  --stroke: rgba(255,255,255,0.10);
  --stroke2: rgba(255,255,255,0.16);
  --text: rgba(255,255,255,0.86);
  --muted: rgba(255,255,255,0.58);
  --muted2: rgba(255,255,255,0.38);

  --accent: #F5D76E;
  --accent2: #B794F4;
  --accent3: #6EE7F5;

  --shadow: 0 30px 80px rgba(0,0,0,0.55);
  --shadow2: 0 12px 40px rgba(0,0,0,0.45);
  --radius: 18px;
  --radius2: 28px;
}

html, body, [class*="stApp"] {
  background: radial-gradient(1100px 700px at 20% 15%, rgba(183,148,244,0.20), transparent 55%),
              radial-gradient(900px 600px at 80% 30%, rgba(110,231,245,0.14), transparent 55%),
              radial-gradient(900px 700px at 45% 80%, rgba(245,215,110,0.12), transparent 60%),
              linear-gradient(180deg, var(--bg0), var(--bg1));
  color: var(--text);
}

/* Hide Streamlit chrome */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none; }

/* Typography */
* { letter-spacing: -0.01em; }
h1, h2, h3, h4, h5, h6 {
  letter-spacing: -0.03em;
}
.stMarkdown, .stText, p, span, label, div {
  color: var(--text);
}

/* Main container */
.main .block-container{
  max-width: 1400px;
  padding-top: 2.2rem;
  padding-bottom: 3rem;
}

/* Sidebar */
[data-testid="stSidebar"]{
  background: rgba(8,10,14,0.82);
  backdrop-filter: blur(18px) saturate(140%);
  border-right: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div{
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  border-radius: 14px !important;
  color: var(--text) !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
}
.stTextInput input:focus, .stTextArea textarea:focus{
  border-color: rgba(245,215,110,0.55) !important;
  box-shadow: 0 0 0 3px rgba(245,215,110,0.10), inset 0 1px 0 rgba(255,255,255,0.05) !important;
}

/* Buttons */
.stButton button, .stDownloadButton button{
  border: 1px solid rgba(255,255,255,0.10) !important;
  border-radius: 14px !important;
  font-weight: 700 !important;
  padding: 0.85rem 1.0rem !important;
  background: linear-gradient(135deg, rgba(245,215,110,0.95), rgba(183,148,244,0.95)) !important;
  color: rgba(0,0,0,0.92) !important;
  box-shadow: 0 14px 35px rgba(0,0,0,0.35);
}
.stButton button:hover, .stDownloadButton button:hover{
  transform: translateY(-2px);
  box-shadow: 0 18px 45px rgba(0,0,0,0.45);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 6px;
}
.stTabs [data-baseweb="tab"]{
  border-radius: 12px;
  color: rgba(255,255,255,0.55);
  background: transparent;
  font-weight: 700;
}
.stTabs [aria-selected="true"]{
  background: rgba(255,255,255,0.08) !important;
  color: rgba(255,255,255,0.92) !important;
  border: 1px solid rgba(255,255,255,0.10);
}

/* Code blocks */
pre, code {
  border-radius: 14px !important;
  background: rgba(0,0,0,0.35) !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
}

/* Cards */
.p-card{
  background: var(--card);
  border: 1px solid var(--stroke);
  border-radius: var(--radius2);
  box-shadow: var(--shadow2);
  padding: 24px;
  position: relative;
  overflow: hidden;
}
.p-card::before{
  content:"";
  position:absolute;
  inset:-2px;
  background: radial-gradient(800px 250px at 20% 10%, rgba(245,215,110,0.14), transparent 60%),
              radial-gradient(700px 220px at 80% 20%, rgba(183,148,244,0.14), transparent 60%),
              radial-gradient(700px 260px at 45% 90%, rgba(110,231,245,0.10), transparent 60%);
  opacity: 0.9;
  pointer-events: none;
}
.p-card > * { position: relative; z-index: 1; }

.p-hero{
  margin: 10px 0 24px 0;
  padding: 32px 30px;
  border-radius: 28px;
  border: 1px solid rgba(255,255,255,0.10);
  background: linear-gradient(135deg, rgba(255,255,255,0.07), rgba(255,255,255,0.03));
  box-shadow: var(--shadow);
  overflow: hidden;
  position: relative;
}
.p-hero::after{
  content:"";
  position:absolute;
  width: 900px;
  height: 420px;
  left: -220px;
  top: -220px;
  background: radial-gradient(circle, rgba(245,215,110,0.24), transparent 60%);
  filter: blur(10px);
}
.p-hero h1{
  font-size: 44px;
  margin: 0 0 6px 0;
  line-height: 1.05;
  background: linear-gradient(135deg, rgba(245,215,110,1), rgba(183,148,244,1), rgba(110,231,245,1));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.p-hero p{
  margin: 0;
  color: var(--muted);
  font-size: 16px;
}

.p-pill{
  display:inline-block;
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.05);
  color: rgba(255,255,255,0.80);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

/* Alerts */
.stSuccess, .stWarning, .stError, .stInfo{
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  background: rgba(255,255,255,0.05) !important;
  backdrop-filter: blur(10px);
}
</style>
"""
st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

# =========================================================
# Persona & Prompts
# =========================================================
GENIUS_PERSONA = """# Role Definition
당신은 대한민국 상위 1% 전자책 매출을 기록하는 '초고수익 전자책 기획자'이자 '심리 설계자'입니다.
당신의 문장은 읽는 순간 독자의 뇌리에 박히며, 밤을 새워서라도 다음 내용을 읽게 만드는 마력이 있습니다.

# Writing Principles (천재 작가의 5원칙)
1. [통찰의 재해석]: 뻔한 이야기를 하지 않습니다. 현상을 비틀어 충격적인 진실을 드러냅니다.
2. [리듬감 부여]: 짧은 문장으로 때리고(Impact), 긴 문장으로 설득(Logic)합니다.
3. [구체성의 마법]: "열심히" 대신 "새벽 4시 기상"이라고 씁니다. 추상적인 형용사를 혐오합니다.
4. [차가운 공감]: 무조건적인 위로 대신, 독자의 게으름과 실패를 날카롭게 지적하고 해결책을 줍니다.
5. [어려운 말 금지]: 중학생도 이해 못 할 전문 용어는 쓰레기통에 버립니다. 쉬운 비유를 듭니다.

# Final Rule
답변의 맨 마지막에는 반드시 구분선(---)을 긋고, '🗣️ 작가의 한마디'를 덧붙여 사용자의 실행을 독려하거나 핵심을 요약해주십시오.
"""

# =========================================================
# Local Config (API Key) Storage
# =========================================================
def get_config_path() -> Path:
    return Path.home() / ".ebook_app_config.json"


def load_saved_api_key() -> str:
    config_path = get_config_path()
    try:
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            return cfg.get("api_key", "") or ""
    except Exception:
        return ""
    return ""


def save_api_key(api_key: str) -> bool:
    config_path = get_config_path()
    try:
        cfg = {}
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        cfg["api_key"] = api_key or ""
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


# =========================================================
# Utilities
# =========================================================
def sanitize_filename(name: str, max_len: int = 24) -> str:
    name = name or "전자책"
    name = re.sub(r"[^\w\s가-힣-]", "", name).strip()
    return (name[:max_len] or "전자책")


def calculate_char_count(text: str) -> int:
    # 공백 포함 (표기와 기능 일치)
    return len(text or "")


def escape_rtf_unicode(text: str) -> str:
    if not text:
        return ""
    result = []
    for char in text:
        code = ord(char)
        if code < 128:
            if char == "\\":
                result.append("\\\\")
            elif char == "{":
                result.append("\\{")
            elif char == "}":
                result.append("\\}")
            elif char == "\n":
                result.append("\\line ")
            elif char == "\r":
                continue
            else:
                result.append(char)
        else:
            signed_code = code - 65536 if code > 32767 else code
            result.append(f"\\u{signed_code}?")
    return "".join(result)


def clean_content_for_display(content: str, subtopic_title: str = None, chapter_title: str = None) -> str:
    if not content:
        return ""
    unicode_control_chars = [
        "\u200e", "\u200f", "\u202a", "\u202b", "\u202c", "\u202d", "\u202e",
        "\u2066", "\u2067", "\u2068", "\u2069", "\u200b", "\u200c", "\u200d",
        "\ufeff", "\u061c"
    ]
    for ch in unicode_control_chars:
        content = content.replace(ch, "")
    content = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", content)
    content = re.sub(r"<[^>]+>", "", content)
    content = (
        content.replace("&amp;", "&")
               .replace("&lt;", "<")
               .replace("&gt;", ">")
               .replace("&quot;", '"')
               .replace("&#39;", "'")
               .replace("&nbsp;", " ")
    )

    lines = content.split("\n")
    cleaned = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            if idx > 3 or cleaned:
                cleaned.append(line)
            continue

        if stripped.startswith("#"):
            continue

        if stripped.startswith("챕터") and ":" in stripped[:15]:
            continue

        if stripped.startswith("소제목") and ":" in stripped[:10]:
            continue

        if subtopic_title and idx < 5:
            clean_sub = subtopic_title.replace("**", "").strip()
            clean_line = stripped.replace("**", "").strip()
            if clean_line == clean_sub:
                continue
            if clean_sub in clean_line and len(clean_line) < len(clean_sub) + 20:
                continue

        if chapter_title and idx < 5:
            clean_ch = chapter_title.replace("**", "").strip()
            if clean_ch in stripped or stripped in clean_ch:
                continue

        cleaned.append(line)

    return "\n".join(cleaned).strip()


def ensure_subtopic_structure(chapters: dict, chapter: str, subtopic: str):
    if chapter not in chapters:
        chapters[chapter] = {"subtopics": [], "subtopic_data": {}}
    if "subtopics" not in chapters[chapter]:
        chapters[chapter]["subtopics"] = []
    if "subtopic_data" not in chapters[chapter]:
        chapters[chapter]["subtopic_data"] = {}
    if subtopic not in chapters[chapter]["subtopic_data"]:
        chapters[chapter]["subtopic_data"][subtopic] = {"questions": [], "answers": [], "content": ""}


def sync_full_outline():
    if not st.session_state.get("outline"):
        st.session_state["full_outline"] = ""
        return

    buf = []
    for ch in st.session_state["outline"]:
        buf.append(f"## {ch}")
        ch_data = st.session_state.get("chapters", {}).get(ch, {})
        for st_name in ch_data.get("subtopics", []):
            buf.append(f"- {st_name}")
        buf.append("")
    st.session_state["full_outline"] = "\n".join(buf).strip()


def trigger_auto_save():
    sync_full_outline()
    st.session_state["auto_save_trigger"] = True


def get_all_content_text() -> str:
    out = []
    for ch in st.session_state.get("outline", []):
        ch_data = st.session_state.get("chapters", {}).get(ch, {})
        subtopics = ch_data.get("subtopics", [])
        subtopic_data = ch_data.get("subtopic_data", {})
        for st_name in subtopics:
            st_data = subtopic_data.get(st_name, {})
            if st_data.get("content"):
                out.append(st_data["content"])
    return "".join(out)


# =========================================================
# AI Core
# =========================================================
def get_api_key() -> str:
    return st.session_state.get("api_key", "") or ""


def ask_ai(system_role: str, prompt: str, temperature: float = 0.7) -> str:
    api_key = get_api_key()
    if not api_key:
        return "⚠️ API 키를 먼저 입력해주세요."

    try:
        genai.configure(api_key=api_key)

        final_system_instruction = GENIUS_PERSONA + "\n\n" + f"현재 당신의 구체적인 역할: {system_role}"

        # NOTE: Gemini SDK마다 system_instruction 전달 방식이 다를 수 있습니다.
        # 가장 호환성이 좋은 방식으로 prompt에 시스템 지시를 포함시킵니다.
        composed_prompt = f"{final_system_instruction}\n\n---\n\n{prompt}"

        model_name = st.session_state.get("gemini_model_name", "models/gemini-2.0-flash")
        ai_model = genai.GenerativeModel(model_name)

        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=4000,
        )

        response = ai_model.generate_content(composed_prompt, generation_config=generation_config)
        text = getattr(response, "text", None)
        if text:
            return text
        # Fallback
        try:
            return response.candidates[0].content.parts[0].text
        except Exception:
            return "오류: 모델 응답을 읽을 수 없습니다."
    except Exception as e:
        return f"오류 발생: {str(e)}"


# =========================================================
# AI Features
# =========================================================
def analyze_topic_score(topic: str) -> str:
    prompt = f"""'{topic}' 주제의 전자책 적합도를 분석해주세요.
다음 5가지 항목을 각각 0~100점으로 채점하고, 종합 점수와 판정을 내려주세요.

채점 항목:
1. 시장성
2. 수익성
3. 차별화 가능성
4. 작성 난이도
5. 지속성

반드시 아래 JSON 형식으로만 답변하세요:
{{
  "market": {{"score": 85, "reason": "이유"}},
  "profit": {{"score": 80, "reason": "이유"}},
  "differentiation": {{"score": 75, "reason": "이유"}},
  "difficulty": {{"score": 90, "reason": "이유"}},
  "sustainability": {{"score": 70, "reason": "이유"}},
  "total_score": 80,
  "verdict": "적합" 또는 "보통" 또는 "부적합",
  "summary": "종합 의견 2~3문장"
}}"""
    return ask_ai("전자책 시장 분석가", prompt, temperature=0.3)


def generate_concept(topic: str, persona: str, pain_points: str) -> str:
    prompt = f"""주제: {topic}
타겟: {persona}
타겟의 고민: {pain_points}

"이 책 안 읽으면 손해"라는 느낌을 주는 한 줄 컨셉 5개를 만들어주세요.

좋은 컨셉의 조건:
- 상식을 정면으로 부정 ("~한다고? 틀렸다")
- 호기심 자극 ("진짜 이유는 따로 있다")
- 구체적 숫자 포함 ("3개월 만에", "상위 1%")

출력 형식:
1. [한 줄 컨셉]
   → 왜 끌리는가
(5개까지)
"""
    return ask_ai("카피라이터", prompt, temperature=0.9)


def generate_titles_advanced(topic: str, persona: str, pain_points: str) -> str:
    prompt = f"""당신은 자청(역행자), 엠제이 드마코(부의 추월차선), 김승호(돈의 속성)급 베스트셀러 작가입니다.

[분석 대상]
주제: {topic}
타겟: {persona}
타겟의 속마음: {pain_points}

[베스트셀러 제목의 핵심 원칙]
1. 읽는 순간 뒤통수를 맞은 느낌 (상식을 뒤집기)
2. 나만 몰랐던 거 아냐? (소외감+긴급함)
3. 구체적 숫자는 신뢰를 만든다
4. 짧을수록 강하다 (7자 이내 메인 타이틀)

[절대 금지]
- "비법", "노하우", "성공", "방법", "전략", "가이드"
- "~하는 법", "~하기", "완벽한", "쉬운"

형식 (JSON만 출력):
{{
  "titles": [
    {{
      "title": "7자 이내 임팩트 제목",
      "subtitle": "15자 이내 보조 설명",
      "concept": "이 제목의 핵심 컨셉",
      "why_works": "왜 사람들이 이 제목에 끌리는지"
    }}
  ]
}}
"""
    return ask_ai("베스트셀러 작가", prompt, temperature=0.9)


def generate_outline(topic: str, persona: str, pain_points: str) -> str:
    prompt = f"""당신은 "부의 추월차선", "역행자", "돈의 속성"을 기획한 편집자입니다.
목차만 봐도 "이거 사야겠다"라는 생각이 드는 전자책 목차를 만드세요.

[주제]: {topic}
[타겟]: {persona}
[타겟의 고민]: {pain_points}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 베스트셀러 목차의 비밀
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[원칙 1] 챕터 제목 = 뒤통수 한 방
- 상식을 정면으로 부정하라
- "~의 중요성", "~하는 방법" 절대 금지
- 읽는 순간 "어?" 하게 만들어라

[원칙 2] 소제목 = 호기심 폭발
- "이게 뭐야?" 싶은 궁금증 유발
- 구체적 숫자, 비유, 반전 활용
- 뻔한 조언 대신 날카로운 통찰

[원칙 3] 심리적 흐름 설계
1부: 충격과 공감
2부: 원인 폭로
3부: 해결책 공개
4부: 실행과 비전

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 출력 형식 (정확히 따르세요)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## PART 1. [충격적인 챕터 제목]
- [호기심 자극하는 소제목 1]
- [호기심 자극하는 소제목 2]
- [호기심 자극하는 소제목 3]

## PART 2. [반전 있는 챕터 제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]

## PART 3. [실행을 부르는 챕터 제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]

## PART 4. [비전을 보여주는 챕터 제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚫 절대 금지
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- "~의 중요성", "~의 필요성"
- "~하는 방법", "~하는 법", "~하기"
- "효과적인 ~", "성공적인 ~", "올바른 ~"
- "이해하기", "알아보기", "살펴보기"
- "기초", "기본", "입문", "개론"
- "팁", "노하우", "비법", "전략"
- 굵은글씨, 번호(1.1), 들여쓰기, 부연설명

목차만 출력하세요. 설명 없이.
"""
    return ask_ai("베스트셀러 편집자", prompt, temperature=0.85)


def generate_subtopics(chapter_title: str, topic: str, persona: str, count: int = 3) -> str:
    prompt = f"""당신은 "부의 추월차선", "역행자"를 기획한 편집자입니다.

[전자책 주제]: {topic}
[챕터 제목]: {chapter_title}
[타겟]: {persona}

이 챕터에 들어갈 소제목 {count}개를 만들어주세요.

[소제목 작성 원칙]
1. 읽는 순간 "이게 뭐야?" 궁금해지는 제목
2. 구체적 숫자 활용 (97%, 3개월, 하루 2시간 등)
3. 상식을 뒤집는 반전
4. 뻔한 표현 완전 배제

[금지 표현]
- "~의 중요성", "~하는 방법", "~하는 법"
- "효과적인", "성공적인", "올바른"
- "기초", "기본", "입문"

[출력 형식]
1. [소제목]
2. [소제목]
3. [소제목]

번호와 소제목만 출력하세요.
"""
    return ask_ai("베스트셀러 편집자", prompt, temperature=0.8)


def generate_interview_questions(subtopic_title: str, chapter_title: str, topic: str) -> str:
    prompt = f"""당신은 베스트셀러 작가의 고스트라이터입니다.
'{topic}' 전자책의 '{chapter_title}' 챕터 중 '{subtopic_title}' 소제목 부분을 쓰기 위해 작가를 인터뷰합니다.

[좋은 질문의 특징]
- 구체적 상황: 언제, 어디서, 어떻게
- 감정: 그때 기분이 어땠나요
- 실패: 처음에 뭘 잘못했나요
- 반전: 뭘 깨닫고 달라졌나요
- 디테일: 구체적으로 어떻게 했나요

'{subtopic_title}' 소제목의 핵심 내용을 끌어낼 수 있는 인터뷰 질문 3개를 만들어주세요.

형식:
Q1: [질문]
Q2: [질문]
Q3: [질문]
"""
    return ask_ai("베스트셀러 고스트라이터", prompt, temperature=0.7)


def generate_subtopic_content(subtopic_title: str, chapter_title: str, questions: list, answers: list, topic: str, persona: str) -> str:
    # ✅ 치명 버그 수정: qa_pairs 생성 루프와 prompt 생성 분리
    qa_pairs = ""
    for i, (q, a) in enumerate(zip(questions, answers), 1):
        if a and a.strip():
            qa_pairs += f"\n질문{i}: {q}\n답변{i}: {a}\n"

    prompt = f"""당신은 "역행자" 자청, "부의 추월차선" 엠제이 드마코 수준의 베스트셀러 작가입니다.
당신의 글은 첫 문장부터 독자를 사로잡고, 마지막 문장까지 손에서 책을 놓지 못하게 만듭니다.

[집필 정보]
주제: {topic}
챕터: {chapter_title}
현재 작성할 소제목: {subtopic_title}
타겟: {persona}

⚠️ 매우 중요: 오직 '{subtopic_title}'에 대한 본문만 작성하세요.
- 다른 챕터나 소제목 내용을 언급하지 마세요
- 소제목 제목을 본문에 다시 쓰지 마세요

[작가 인터뷰 - 이 내용만 바탕으로 작성]
{qa_pairs}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 자청 스타일 글쓰기 10가지 법칙
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[법칙 1] 첫 문장 = 뒤통수 한 방
- 첫 문장에서 상식을 뒤집거나 충격적인 사실로 시작
- "오늘은 ~에 대해" 금지

[법칙 2] 짧은 문장, 강한 임팩트
- 한 문장 15~25자
- 중요한 문장 10자 이하로 더 짧게

[법칙 3] 문단 리듬
- 한 문단 3~5문장
- 문단과 문단 사이 빈 줄 1개
- 한 문장마다 줄바꿈 금지

[법칙 4] 스토리 > 설명
- Before(실패) → 깨달음 → After(성공)

[법칙 5] 숫자로 증명
- 모호한 표현 금지
- 시간/금액/기간/횟수로 박아 넣기

[법칙 6] 감정은 차갑게, 선명하게
- 과잉 감정 금지
- 상황과 결과로 감정이 느껴지게

[법칙 7] 대화체 활용
- "이게 되겠어?" 같은 내면의 소리

[법칙 8] 반복과 강조
- 핵심 메시지를 표현을 바꿔 2~3번

[법칙 9] 장면 묘사
- 시간, 장소, 상황을 영화처럼

[법칙 10] 독자 = 옆자리 친구
- 합쇼체 유지
- 딱딱한 교과서 말투 금지

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 문체 규칙 (합쇼체 100%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
모든 문장 끝:
✓ ~입니다 / ~습니다 / ~했습니다 / ~됩니다
✓ ~죠 / ~거죠 / ~셨죠 / ~네요
✓ ~세요 / ~하세요

반말 금지:
✗ ~다 / ~했다 / ~이다 / ~였다 / ~된다

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚫 AI 티 나는 표현 절대 금지
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- "첫째/둘째/셋째" 금지
- "중요합니다/핵심입니다/필수적입니다" 남발 금지
- "따라서/그러므로/결론적으로" 금지
- "많은 분들이/대부분의 사람들이" 금지
- 굵은글씨/마크다운 번호 금지

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📏 분량: 공백 포함 1500~2000자
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
반드시 1500자 이상 작성하세요.
독자가 "이 부분만 읽어도 돈값 한다"고 느끼게 쓰세요.

[미션]
'{subtopic_title}'의 본문만 작성하세요.
첫 문장부터 뒤통수 치세요.
"""
    return ask_ai("베스트셀러 작가", prompt, temperature=0.8)


def refine_content(content: str, style: str = "친근한") -> str:
    style_guide = {
        "친근한": "친근한 스타일 - 합니다체, 자신감 있는 단정, 구체적 숫자와 팩트",
        "전문적": "전문가 스타일 - 합니다체, 논리적 전개, 데이터 기반",
        "직설적": "직설 스타일 - 합니다체, 핵심만 간결하게, 군더더기 제거",
        "스토리텔링": "스토리 스타일 - 합니다체, 장면 묘사 강화, 대화체 적절히",
    }
    prompt = f"""다음 글을 다듬어주세요.

[원본]
{content}

[수정 사항]
1. 반드시 합니다체(존댓말)로 통일
2. 한 문단은 3~5문장
3. AI 티 나는 표현 제거 ("따라서", "중요합니다" 반복 등)
4. 마크다운 제거 (**굵게**, *기울임*, 번호 매기기)

[목표 스타일]
{style_guide.get(style, style_guide["친근한"])}

다듬어진 글만 출력하세요.
"""
    return ask_ai("에디터", prompt, temperature=0.7)


def check_quality(content: str) -> str:
    prompt = f"""다음 글이 베스트셀러 수준인지 평가해주세요.

[평가할 글]
{(content or "")[:4000]}

[평가 기준]
1. 첫 문장 (10점)
2. 몰입도 (10점)
3. 공감력 (10점)
4. 구체성 (10점)
5. AI 티 (10점)

[출력 형식]
📊 종합 점수: __/50점
📌 각 항목 점수와 평가
✍️ 수정하면 좋을 문장 TOP 3
🎯 총평
"""
    return ask_ai("베스트셀러 편집자", prompt, temperature=0.6)


def regenerate_chapter_outline(chapter_num: int, topic: str, persona: str, current_outline: list) -> str:
    prompt = f"""주제 '{topic}' 전자책에서 챕터 {chapter_num}만 새롭게 작성해주세요.

현재 목차:
{chr(10).join(current_outline)}

[챕터 제목 원칙]
- 상식을 정면으로 부정
- "~의 중요성", "~하는 방법" 절대 금지
- 읽는 순간 "어?" 하게 만들기

[소제목 원칙]
- 호기심 폭발
- 숫자/비유/반전
- 뻔한 표현 금지

출력 형식:
## [새로운 챕터 제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]
"""
    return ask_ai("베스트셀러 편집자", prompt, temperature=0.85)


def regenerate_single_subtopic(chapter_title: str, subtopic_num: int, topic: str, current_subtopics: list) -> str:
    prompt = f"""주제 '{topic}'의 챕터 '{chapter_title}'에서 소제목 {subtopic_num}번만 새롭게 작성해주세요.

현재 소제목들:
{chr(10).join([f"- {s}" for s in current_subtopics])}

[소제목 원칙]
- "이게 뭐야?" 싶은 궁금증 유발
- 구체적 숫자 활용
- 뻔한 표현 금지 ("~의 중요성", "~하는 방법")
- 상식을 뒤집는 반전

출력:
새 소제목 한 줄만 (번호/기호 없이)
"""
    result = ask_ai("카피라이터", prompt, temperature=0.85).strip()
    first = result.split("\n")[0].strip()
    first = first.lstrip("- ").lstrip("0123456789.").strip()
    return first


def generate_marketing_copy(title: str, subtitle: str, topic: str, persona: str) -> str:
    prompt = f"""당신은 크몽에서 전자책을 수천 권 판매한 탑셀러입니다.

[상품 정보]
제목: {title}
부제: {subtitle}
주제: {topic}
타겟: {persona}

다음을 만들어주세요:
1) 크몽 상품 제목 (40자 이내, 검색 키워드 포함)
2) 상세페이지 헤드라인 3개
3) 구매 유도 문구(CTA) 3개 (긴급성 + FOMO)
4) 인스타그램 홍보 문구 (훅 + 스토리 + CTA + 해시태그 5개)
5) 블로그 포스팅 제목 3개
"""
    return ask_ai("크몽 탑셀러 마케터", prompt, temperature=0.85)


# =========================================================
# Authentication
# =========================================================
CORRECT_PASSWORD = "cashmaker2024"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown(
        """
        <div class="p-hero">
          <span class="p-pill">CASHMAKER</span>
          <h1>전자책 작성 프로그램</h1>
          <p>고급스러운 워크플로우. 빠른 생산성. 프리미엄 결과물.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="p-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.2, 1.6, 1.2])
    with c2:
        pw = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
        if st.button("입장하기", use_container_width=True):
            if pw == CORRECT_PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# =========================================================
# Session Defaults
# =========================================================
default_states = {
    "topic": "",
    "target_persona": "",
    "pain_points": "",
    "one_line_concept": "",
    "outline": [],
    "chapters": {},
    "market_analysis": "",
    "book_title": "",
    "subtitle": "",
    "topic_score": None,
    "topic_verdict": None,
    "score_details": None,
    "generated_titles": None,
    "full_outline": "",
    "auto_save_trigger": False,
    "refined_content": "",
    "quality_result": "",
    "marketing_copy": "",
    "gemini_model_name": "models/gemini-2.0-flash",
}
for k, v in default_states.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =========================================================
# Sidebar: Progress + Save/Load + API Settings
# =========================================================
with st.sidebar:
    st.markdown("### Progress")
    progress_items = [
        bool(st.session_state["topic"]),
        bool(st.session_state["target_persona"]),
        bool(st.session_state["outline"]),
        len(st.session_state["chapters"]) > 0,
        bool(get_all_content_text()),
    ]
    progress = (sum(progress_items) / len(progress_items)) * 100
    st.progress(progress / 100)
    st.caption(f"{progress:.0f}% 완료")

    st.markdown("---")
    st.markdown("### Info")
    if st.session_state["topic"]:
        st.caption(f"주제: {st.session_state['topic']}")
    if st.session_state["book_title"]:
        st.caption(f"제목: {st.session_state['book_title']}")
    if st.session_state["outline"]:
        st.caption(f"목차: {len(st.session_state['outline'])}개")

    completed_chapters = 0
    for ch_data in st.session_state.get("chapters", {}).values():
        for st_data in ch_data.get("subtopic_data", {}).values():
            if st_data.get("content"):
                completed_chapters += 1
    if completed_chapters:
        st.caption(f"완성: {completed_chapters}개")

    st.markdown("---")
    st.markdown("### 💾 저장/불러오기")

    save_data = {
        "topic": st.session_state.get("topic", ""),
        "target_persona": st.session_state.get("target_persona", ""),
        "pain_points": st.session_state.get("pain_points", ""),
        "one_line_concept": st.session_state.get("one_line_concept", ""),
        "outline": st.session_state.get("outline", []),
        "chapters": st.session_state.get("chapters", {}),
        "book_title": st.session_state.get("book_title", ""),
        "subtitle": st.session_state.get("subtitle", ""),
        "market_analysis": st.session_state.get("market_analysis", ""),
        "topic_score": st.session_state.get("topic_score"),
        "topic_verdict": st.session_state.get("topic_verdict"),
        "score_details": st.session_state.get("score_details"),
        "generated_titles": st.session_state.get("generated_titles"),
        "gemini_model_name": st.session_state.get("gemini_model_name"),
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    save_json = json.dumps(save_data, ensure_ascii=False, indent=2)
    file_title = sanitize_filename(st.session_state.get("book_title", "전자책"), 24)
    st.download_button(
        "📥 작업 저장하기",
        save_json,
        file_name=f"{file_title}_{datetime.now().strftime('%m%d_%H%M')}.json",
        mime="application/json",
        use_container_width=True,
    )

    uploaded = st.file_uploader("📤 작업 불러오기", type=["json"], label_visibility="collapsed")
    if uploaded is not None:
        try:
            loaded_data = json.loads(uploaded.read().decode("utf-8"))
            if st.button("불러오기 적용", use_container_width=True):
                for key in [
                    "topic", "target_persona", "pain_points", "one_line_concept",
                    "outline", "chapters", "book_title", "subtitle", "market_analysis",
                    "topic_score", "topic_verdict", "score_details", "generated_titles",
                    "gemini_model_name"
                ]:
                    if key in loaded_data:
                        st.session_state[key] = loaded_data[key]
                sync_full_outline()
                st.success("불러오기 완료!")
                st.rerun()
        except Exception as e:
            st.error(f"파일 오류: {e}")

    st.markdown("---")
    st.markdown("### API 설정")

    # ✅ api_key_input 스코프 버그 수정: 항상 렌더링
    saved_key = load_saved_api_key()
    if "api_key" not in st.session_state:
        st.session_state["api_key"] = saved_key

    api_key_input = st.text_input(
        "Gemini API 키",
        value=st.session_state.get("api_key", ""),
        type="password",
        placeholder="AIza...",
        help="Google AI Studio에서 발급받은 API 키를 입력하세요",
    )
    if api_key_input != st.session_state.get("api_key", ""):
        st.session_state["api_key"] = api_key_input
        save_api_key(api_key_input)

    st.text_input(
        "Gemini 모델",
        value=st.session_state.get("gemini_model_name", "models/gemini-2.0-flash"),
        key="gemini_model_name",
        help="기본값은 models/gemini-2.0-flash 입니다.",
    )

    with st.expander("API 키 발급 방법"):
        st.markdown(
            """1) Google AI Studio 접속  
2) 로그인  
3) API 키 만들기  
4) 키 복사 → 위 입력창에 붙여넣기"""
        )

    if not st.session_state.get("api_key"):
        st.caption("⚠️ API 키를 입력하세요")


# =========================================================
# Hero
# =========================================================
st.markdown(
    """
    <div class="p-hero">
      <span class="p-pill">CASHMAKER</span>
      <h1>전자책 작성 프로그램</h1>
      <p>예술가가 설계하고, 애플처럼 다듬은 흐름. 한 번에 프리미엄 결과물을 만드세요.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tabs = st.tabs(["① 주제 선정", "② 타겟 & 컨셉", "③ 목차 설계", "④ 본문 작성", "⑤ 문체 & 품질", "⑥ 최종 출력"])

# =========================================================
# TAB 1: Topic
# =========================================================
with tabs[0]:
    st.markdown('<div class="p-card">', unsafe_allow_html=True)
    st.subheader("주제 선정 & 적합도 분석")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.caption("Step 01")
        topic_input = st.text_input(
            "어떤 주제로 전자책을 쓰고 싶으세요?",
            value=st.session_state["topic"],
            placeholder="예: 크몽으로 월 500만원 벌기",
        )
        if topic_input != st.session_state["topic"]:
            st.session_state["topic"] = topic_input
            st.session_state["topic_score"] = None
            st.session_state["score_details"] = None

        st.markdown(
            """
            <div class="p-card" style="margin-top:12px;">
              <span class="p-pill">GUIDE</span>
              <p style="margin:10px 0 0 0; color: rgba(255,255,255,0.70);">
                • 내가 직접 경험하고 성과를 낸 것<br/>
                • 사람들이 돈 주고 배우고 싶어하는 것<br/>
                • 구체적인 결과를 약속할 수 있는 것
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("📊 적합도 분석하기", key="analyze_btn", use_container_width=True):
            if not st.session_state["topic"]:
                st.error("주제를 입력해주세요.")
            else:
                with st.spinner("분석 중..."):
                    result = analyze_topic_score(st.session_state["topic"])
                    try:
                        json_match = re.search(r"\{[\s\S]*\}", result)
                        if json_match:
                            score_data = json.loads(json_match.group())
                            st.session_state["topic_score"] = score_data.get("total_score", 0)
                            st.session_state["topic_verdict"] = score_data.get("verdict", "분석 실패")
                            st.session_state["score_details"] = score_data
                        else:
                            st.error("JSON 파싱 실패. 다시 시도해주세요.")
                    except Exception:
                        st.error("분석 결과 파싱 오류. 다시 시도해주세요.")

    with col2:
        st.caption("Step 02")
        st.markdown("#### 분석 결과")
        if st.session_state["topic_score"] is not None:
            score = st.session_state["topic_score"]
            verdict = st.session_state["topic_verdict"]
            details = st.session_state["score_details"] or {}

            st.markdown(
                f"""
                <div class="p-card" style="text-align:center;">
                  <div style="font-size:64px; font-weight:900; line-height:1; 
                              background: linear-gradient(135deg, rgba(245,215,110,1), rgba(183,148,244,1));
                              -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                    {score}
                  </div>
                  <div style="margin-top:10px; color: rgba(255,255,255,0.55); font-weight:700;">종합 점수</div>
                  <div style="margin-top:12px;">
                    <span class="p-pill">{verdict}</span>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if details:
                st.markdown("#### 세부 점수")
                for name, key in [
                    ("시장성", "market"),
                    ("수익성", "profit"),
                    ("차별화", "differentiation"),
                    ("작성 난이도", "difficulty"),
                    ("지속성", "sustainability"),
                ]:
                    s = details.get(key, {}).get("score", 0)
                    r = details.get(key, {}).get("reason", "")
                    st.markdown(f"- {name}: **{s}**")
                    if r:
                        st.caption(r)
                if details.get("summary"):
                    st.markdown("#### 종합 의견")
                    st.write(details["summary"])
        else:
            st.info("분석은 선택사항입니다. 주제만 입력해도 다음 단계로 진행 가능합니다.")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# TAB 2: Target & Concept
# =========================================================
with tabs[1]:
    st.markdown('<div class="p-card">', unsafe_allow_html=True)
    st.subheader("타겟 설정 & 제목/컨셉 생성")

    if not st.session_state["topic"]:
        st.info("주제를 먼저 입력하면 더 정밀한 결과가 나옵니다.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.caption("Step 01")
        if not st.session_state["topic"]:
            topic_here = st.text_input("주제 (여기서 입력 가능)", value="", key="topic_tab2")
            if topic_here:
                st.session_state["topic"] = topic_here

        persona = st.text_area(
            "누가 이 책을 읽나요?",
            value=st.session_state["target_persona"],
            placeholder="예: 30대 직장인, 퇴근 후 부업으로 월 100만원을 원하는 사람",
            height=100,
        )
        st.session_state["target_persona"] = persona

        pain = st.text_area(
            "타겟의 가장 큰 고민은?",
            value=st.session_state["pain_points"],
            placeholder="예: 시간이 없다, 뭘 해야 할지 모르겠다, 시작이 두렵다",
            height=100,
        )
        st.session_state["pain_points"] = pain

        st.markdown("---")
        st.caption("Step 02")
        if st.button("컨셉 생성하기", key="concept_btn", use_container_width=True):
            if not st.session_state["topic"] or not persona:
                st.error("주제와 타겟을 먼저 입력해주세요.")
            else:
                with st.spinner("생성 중..."):
                    concept = generate_concept(st.session_state["topic"], persona, pain)
                    st.session_state["one_line_concept"] = concept

        if st.session_state["one_line_concept"]:
            st.markdown('<div class="p-card">', unsafe_allow_html=True)
            st.write(st.session_state["one_line_concept"])
            st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.caption("Step 03")
        if st.button("제목 생성하기", key="title_btn", use_container_width=True):
            if not st.session_state["topic"]:
                st.error("주제를 먼저 입력해주세요.")
            else:
                with st.spinner("생성 중..."):
                    titles_result = generate_titles_advanced(
                        st.session_state["topic"],
                        st.session_state["target_persona"],
                        st.session_state["pain_points"],
                    )
                    try:
                        json_match = re.search(r"\{[\s\S]*\}", titles_result)
                        if json_match:
                            st.session_state["generated_titles"] = json.loads(json_match.group())
                        else:
                            st.session_state["generated_titles"] = None
                            st.write(titles_result)
                    except Exception:
                        st.session_state["generated_titles"] = None
                        st.write(titles_result)

        titles_data = st.session_state.get("generated_titles") or {}
        if titles_data.get("titles"):
            for i, t in enumerate(titles_data["titles"], 1):
                st.markdown(
                    f"""
                    <div class="p-card" style="margin-top:12px;">
                      <span class="p-pill">TITLE {i:02d}</span>
                      <div style="font-size:22px; font-weight:900; margin-top:10px;">{t.get("title","")}</div>
                      <div style="color: rgba(255,255,255,0.62); margin-top:6px;">{t.get("subtitle","")}</div>
                      <div style="margin-top:12px; color: rgba(255,255,255,0.70);">{t.get("why_works","")}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("---")
        st.caption("Step 04")
        st.session_state["book_title"] = st.text_input("제목", value=st.session_state["book_title"], placeholder="최종 제목")
        st.session_state["subtitle"] = st.text_input("부제", value=st.session_state["subtitle"], placeholder="부제")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# TAB 3: Outline
# =========================================================
with tabs[2]:
    st.markdown('<div class="p-card">', unsafe_allow_html=True)
    st.subheader("목차 설계")

    mode = st.radio(
        "목차를 어떻게 만드시겠어요?",
        ["🤖 자동으로 목차 생성", "✍️ 내가 직접 입력"],
        horizontal=True,
        key="outline_mode_radio",
    )
    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        if mode == "🤖 자동으로 목차 생성":
            st.caption("자동 목차 생성")
            if not st.session_state["topic"]:
                st.warning("주제를 먼저 입력해주세요.")
                topic_here = st.text_input("주제", value=st.session_state["topic"], key="topic_tab3")
                if topic_here:
                    st.session_state["topic"] = topic_here

            if st.button("🚀 목차 생성하기", key="outline_btn", use_container_width=True):
                if not st.session_state["topic"]:
                    st.error("주제를 먼저 입력해주세요.")
                else:
                    with st.spinner("설계 중..."):
                        outline_text = generate_outline(
                            st.session_state["topic"],
                            st.session_state["target_persona"],
                            st.session_state["pain_points"],
                        )

                        lines = [ln.strip() for ln in outline_text.split("\n") if ln.strip()]
                        chapters = []
                        chapter_subtopics = {}
                        current = None

                        # 더 엄격한 챕터 감지: "##"로 시작하는 라인만 챕터로 취급
                        for line in lines:
                            if line.startswith("##"):
                                chapter_name = line.lstrip("#").strip()
                                chapter_name = re.sub(r"\*\*(.+?)\*\*", r"\1", chapter_name)
                                current = chapter_name
                                chapters.append(current)
                                chapter_subtopics[current] = []
                            elif current and line.startswith("-"):
                                sub = line.lstrip("- ").strip()
                                sub = re.sub(r"\*\*(.+?)\*\*", r"\1", sub)
                                sub = re.sub(r"^\d+\.\d+\s*", "", sub)
                                sub = re.sub(r"^\d+\.\s*", "", sub)
                                if sub and len(sub) > 2:
                                    chapter_subtopics[current].append(sub)

                        if chapters:
                            st.session_state["outline"] = chapters
                            st.session_state["chapters"] = st.session_state.get("chapters", {})

                            for ch in chapters:
                                subs = chapter_subtopics.get(ch, [])
                                st.session_state["chapters"][ch] = {
                                    "subtopics": subs,
                                    "subtopic_data": {s: {"questions": [], "answers": [], "content": ""} for s in subs},
                                }

                            sync_full_outline()
                            total_subs = sum(len(chapter_subtopics.get(c, [])) for c in chapters)
                            st.success(f"✅ {len(chapters)}개 챕터, {total_subs}개 소제목 생성됨!")
                            st.rerun()
                        else:
                            st.error("목차 생성 실패. 다시 시도해주세요.")

            if st.session_state.get("full_outline"):
                st.markdown("#### 현재 목차")
                st.code(st.session_state["full_outline"], language=None)

        else:
            st.caption("직접 입력")
            st.markdown("아래 형식으로 입력하세요.")
            st.markdown(
                """
                <div class="p-card" style="margin-top:10px;">
                  <span class="p-pill">FORMAT</span>
                  <div style="margin-top:12px; color: rgba(255,255,255,0.70);">
                    ## 챕터1: 제목<br/>
                    - 소제목 1<br/>
                    - 소제목 2<br/><br/>
                    ## 챕터2: 제목<br/>
                    - 소제목 3
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            existing = ""
            if st.session_state["outline"]:
                for ch in st.session_state["outline"]:
                    existing += f"## {ch}\n"
                    ch_data = st.session_state["chapters"].get(ch, {})
                    for s in ch_data.get("subtopics", []):
                        existing += f"- {s}\n"
                    existing += "\n"

            manual = st.text_area("목차 입력", value=existing, height=360, key="manual_outline_input")

            if st.button("✅ 목차 저장하기", key="save_manual_outline", use_container_width=True):
                if not manual.strip():
                    st.error("목차를 입력해주세요.")
                else:
                    lines = [ln.strip() for ln in manual.split("\n") if ln.strip()]
                    chapters = []
                    chapter_subtopics = {}
                    current = None

                    for line in lines:
                        if line.startswith("##"):
                            current = line.lstrip("#").strip()
                            chapters.append(current)
                            chapter_subtopics[current] = []
                        elif current and line.startswith("-"):
                            chapter_subtopics[current].append(line.lstrip("- ").strip())

                    st.session_state["outline"] = chapters
                    st.session_state["chapters"] = {}

                    for ch in chapters:
                        subs = chapter_subtopics.get(ch, [])
                        st.session_state["chapters"][ch] = {
                            "subtopics": subs,
                            "subtopic_data": {s: {"questions": [], "answers": [], "content": ""} for s in subs},
                        }

                    sync_full_outline()
                    trigger_auto_save()
                    st.success(f"✅ {len(chapters)}개 챕터 저장 완료!")
                    st.rerun()

    with col2:
        st.caption("목차 관리")
        if not st.session_state["outline"]:
            st.info("왼쪽에서 목차를 생성하거나 직접 입력하세요.")
        else:
            for i, ch in enumerate(st.session_state["outline"]):
                ch_data = st.session_state["chapters"].get(ch, {})
                subs = ch_data.get("subtopics", [])
                with st.expander(f"{ch}  ({len(subs)}개 소제목)", expanded=False):
                    c_edit, c_actions = st.columns([3, 2])
                    with c_edit:
                        new_title = st.text_input("챕터 제목", value=ch, key=f"edit_ch_{i}", label_visibility="collapsed")

                    with c_actions:
                        a1, a2 = st.columns(2)
                        with a1:
                            if st.button("🔄", key=f"regen_ch_{i}", help="챕터 재생성"):
                                with st.spinner("재생성 중..."):
                                    txt = regenerate_chapter_outline(
                                        i + 1,
                                        st.session_state["topic"],
                                        st.session_state["target_persona"],
                                        st.session_state["outline"],
                                    )
                                    lines = [ln.strip() for ln in txt.split("\n") if ln.strip()]
                                    new_ch = None
                                    new_subs = []
                                    for ln in lines:
                                        if ln.startswith("##"):
                                            new_ch = ln.lstrip("#").strip()
                                        elif ln.startswith("-"):
                                            new_subs.append(ln.lstrip("- ").strip())
                                    if new_ch:
                                        old = st.session_state["outline"][i]
                                        st.session_state["outline"][i] = new_ch
                                        st.session_state["chapters"].pop(old, None)
                                        st.session_state["chapters"][new_ch] = {
                                            "subtopics": new_subs,
                                            "subtopic_data": {s: {"questions": [], "answers": [], "content": ""} for s in new_subs},
                                        }
                                        sync_full_outline()
                                        trigger_auto_save()
                                        st.rerun()

                        with a2:
                            if st.button("🗑️", key=f"del_ch_{i}", help="챕터 삭제"):
                                old = st.session_state["outline"].pop(i)
                                st.session_state["chapters"].pop(old, None)
                                sync_full_outline()
                                trigger_auto_save()
                                st.rerun()

                    if new_title.strip() and new_title != ch:
                        if st.button("💾 제목 저장", key=f"save_ch_title_{i}", use_container_width=True):
                            idx = st.session_state["outline"].index(ch)
                            st.session_state["outline"][idx] = new_title
                            st.session_state["chapters"][new_title] = st.session_state["chapters"].pop(ch)
                            sync_full_outline()
                            trigger_auto_save()
                            st.rerun()

                    st.markdown("---")
                    st.markdown("#### 소제목")
                    for j, s in enumerate(list(subs)):
                        row1, row2 = st.columns([3, 2])
                        with row1:
                            new_s = st.text_input("소제목", value=s, key=f"edit_st_{i}_{j}", label_visibility="collapsed")
                        with row2:
                            b1, b2 = st.columns(2)
                            with b1:
                                if st.button("🔄", key=f"regen_st_{i}_{j}", help="소제목 재생성"):
                                    with st.spinner("재생성 중..."):
                                        ns = regenerate_single_subtopic(ch, j + 1, st.session_state["topic"], subs)
                                        if ns:
                                            old_s = st.session_state["chapters"][ch]["subtopics"][j]
                                            st.session_state["chapters"][ch]["subtopics"][j] = ns
                                            # subtopic_data rename
                                            data = st.session_state["chapters"][ch]["subtopic_data"].pop(old_s, {"questions": [], "answers": [], "content": ""})
                                            st.session_state["chapters"][ch]["subtopic_data"][ns] = data
                                            sync_full_outline()
                                            trigger_auto_save()
                                            st.rerun()
                            with b2:
                                if st.button("🗑️", key=f"del_st_{i}_{j}", help="소제목 삭제"):
                                    removed = st.session_state["chapters"][ch]["subtopics"].pop(j)
                                    st.session_state["chapters"][ch]["subtopic_data"].pop(removed, None)
                                    sync_full_outline()
                                    trigger_auto_save()
                                    st.rerun()

                        if new_s.strip() and new_s != s:
                            if st.button("💾 저장", key=f"save_st_btn_{i}_{j}", help="소제목 저장"):
                                st.session_state["chapters"][ch]["subtopics"][j] = new_s
                                data = st.session_state["chapters"][ch]["subtopic_data"].pop(s, {"questions": [], "answers": [], "content": ""})
                                st.session_state["chapters"][ch]["subtopic_data"][new_s] = data
                                sync_full_outline()
                                trigger_auto_save()
                                st.rerun()

            st.markdown("---")
            if st.button("➕ 새 챕터 추가", use_container_width=True):
                new_ch = f"챕터{len(st.session_state['outline'])+1}: 새 챕터"
                st.session_state["outline"].append(new_ch)
                st.session_state["chapters"][new_ch] = {"subtopics": [], "subtopic_data": {}}
                sync_full_outline()
                trigger_auto_save()
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# TAB 4: Writing
# =========================================================
with tabs[3]:
    st.markdown('<div class="p-card">', unsafe_allow_html=True)
    st.subheader("본문 작성")

    if not st.session_state["outline"]:
        st.warning("먼저 '③ 목차 설계' 탭에서 목차를 작성해주세요.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        chapter_list = st.session_state["outline"][:]
        selected_chapter = st.selectbox("📚 챕터 선택", chapter_list, key="chapter_select_main")

        if selected_chapter not in st.session_state["chapters"]:
            st.session_state["chapters"][selected_chapter] = {"subtopics": [], "subtopic_data": {}}

        chapter_data = st.session_state["chapters"][selected_chapter]
        chapter_data.setdefault("subtopics", [])
        chapter_data.setdefault("subtopic_data", {})

        # Subtopics overview
        with st.expander(f"📋 '{selected_chapter}' 소제목 ({len(chapter_data['subtopics'])}개)", expanded=True):
            if chapter_data["subtopics"]:
                for j, st_name in enumerate(chapter_data["subtopics"]):
                    has_content = bool(chapter_data["subtopic_data"].get(st_name, {}).get("content", "").strip())
                    icon = "✅" if has_content else "⬜"
                    c1, c2, c3, c4 = st.columns([0.5, 6, 1, 1])
                    with c1:
                        st.write(icon)
                    with c2:
                        st.write(f"{j+1}. {st_name}")
                    with c3:
                        if st.button("✏️", key=f"edit_subtopic_quick_{j}", help="소제목 직접 수정"):
                            st.session_state[f"edit_mode_{selected_chapter}_{j}"] = True
                    with c4:
                        if st.button("🔄", key=f"regen_subtopic_quick_{j}", help="AI 재생성"):
                            with st.spinner("재생성 중..."):
                                ns = regenerate_single_subtopic(
                                    selected_chapter, j + 1, st.session_state["topic"], chapter_data["subtopics"]
                                )
                                if ns:
                                    old = chapter_data["subtopics"][j]
                                    chapter_data["subtopics"][j] = ns
                                    data = chapter_data["subtopic_data"].pop(old, {"questions": [], "answers": [], "content": ""})
                                    chapter_data["subtopic_data"][ns] = data
                                    sync_full_outline()
                                    trigger_auto_save()
                                    st.rerun()

                    if st.session_state.get(f"edit_mode_{selected_chapter}_{j}"):
                        new_title = st.text_input(
                            "소제목 수정",
                            value=st_name,
                            key=f"edit_input_{selected_chapter}_{j}",
                            label_visibility="collapsed",
                        )
                        a1, a2 = st.columns([1, 1])
                        with a1:
                            if st.button("💾 저장", key=f"save_edit_subtopic_{selected_chapter}_{j}", use_container_width=True):
                                new_title = new_title.strip()
                                if new_title and new_title != st_name:
                                    chapter_data["subtopics"][j] = new_title
                                    data = chapter_data["subtopic_data"].pop(st_name, {"questions": [], "answers": [], "content": ""})
                                    chapter_data["subtopic_data"][new_title] = data
                                st.session_state[f"edit_mode_{selected_chapter}_{j}"] = False
                                sync_full_outline()
                                trigger_auto_save()
                                st.rerun()
                        with a2:
                            if st.button("❌ 취소", key=f"cancel_edit_subtopic_{selected_chapter}_{j}", use_container_width=True):
                                st.session_state[f"edit_mode_{selected_chapter}_{j}"] = False
                                st.rerun()

                st.markdown("---")
                add1, add2 = st.columns([4, 1])
                with add1:
                    new_sub = st.text_input("새 소제목 추가", key=f"add_new_sub_{selected_chapter}", placeholder="직접 입력...", label_visibility="collapsed")
                with add2:
                    if st.button("➕ 추가", key=f"add_sub_btn_{selected_chapter}", use_container_width=True):
                        new_sub = (new_sub or "").strip()
                        if new_sub and new_sub not in chapter_data["subtopics"]:
                            chapter_data["subtopics"].append(new_sub)
                            chapter_data["subtopic_data"][new_sub] = {"questions": [], "answers": [], "content": ""}
                            sync_full_outline()
                            trigger_auto_save()
                            st.rerun()
            else:
                st.info("소제목이 없습니다. 아래에서 추가하거나 자동 생성하세요.")

            with st.expander("⚙️ 소제목 자동 생성", expanded=False):
                g1, g2 = st.columns([2, 1])
                with g1:
                    num = st.number_input("생성할 개수", min_value=1, max_value=10, value=3, key="gen_sub_count")
                with g2:
                    if st.button("✨ 생성", use_container_width=True):
                        with st.spinner("생성 중..."):
                            txt = generate_subtopics(selected_chapter, st.session_state["topic"], st.session_state["target_persona"], int(num))
                            new_list = []
                            for ln in txt.split("\n"):
                                ln = ln.strip()
                                if not ln:
                                    continue
                                if ln[0].isdigit() or ln.startswith("-"):
                                    cleaned = re.sub(r"^[\d\.\-\s]+", "", ln).strip()
                                    if cleaned:
                                        new_list.append(cleaned)
                            if new_list:
                                chapter_data["subtopics"] = new_list[: int(num)]
                                for s in chapter_data["subtopics"]:
                                    chapter_data["subtopic_data"].setdefault(s, {"questions": [], "answers": [], "content": ""})
                                sync_full_outline()
                                trigger_auto_save()
                                st.success(f"✅ {len(chapter_data['subtopics'])}개 생성됨!")
                                st.rerun()

        if chapter_data["subtopics"]:
            st.markdown("---")
            st.markdown("### ✍️ 본문 작성")

            def fmt_subtopic(x: str) -> str:
                has = bool(chapter_data["subtopic_data"].get(x, {}).get("content"))
                return f"{'✅' if has else '⬜'} {x}"

            selected_subtopic = st.selectbox("작성할 소제목", chapter_data["subtopics"], key="subtopic_select_main", format_func=fmt_subtopic)
            ensure_subtopic_structure(st.session_state["chapters"], selected_chapter, selected_subtopic)
            sub_data = st.session_state["chapters"][selected_chapter]["subtopic_data"][selected_subtopic]

            completed = sum(1 for s in chapter_data["subtopics"] if chapter_data["subtopic_data"].get(s, {}).get("content"))
            total = len(chapter_data["subtopics"])
            st.progress(completed / total if total else 0)
            st.caption(f"진행: {completed}/{total} 완료")

            st.markdown("---")
            cL, cR = st.columns([1, 1])

            with cL:
                st.caption("Step 01")
                st.markdown(f"#### 🎤 인터뷰")
                if st.button("🎤 질문 생성하기", key="gen_questions_main", use_container_width=True):
                    with st.spinner("질문 생성 중..."):
                        qt = generate_interview_questions(selected_subtopic, selected_chapter, st.session_state["topic"])
                        qs = re.findall(r"Q\d+:\s*(.+)", qt)
                        if not qs:
                            qs = [q.strip() for q in qt.split("\n") if q.strip() and "?" in q][:3]
                        sub_data["questions"] = qs
                        sub_data["answers"] = [""] * len(qs)
                        trigger_auto_save()
                        st.rerun()

                if sub_data.get("questions"):
                    for i, q in enumerate(sub_data["questions"]):
                        st.markdown(f"- Q{i+1}. {q}")
                        if i >= len(sub_data["answers"]):
                            sub_data["answers"].append("")
                        sub_data["answers"][i] = st.text_area(
                            f"A{i+1}",
                            value=sub_data["answers"][i],
                            key=f"ans_{selected_chapter}_{selected_subtopic}_{i}",
                            height=90,
                            label_visibility="collapsed",
                        )
                else:
                    st.info("질문 생성 후 답변을 채우면 본문을 더 정교하게 씁니다.")

            with cR:
                st.caption("Step 02")
                st.markdown("#### 📝 본문")
                has_answers = bool(sub_data.get("questions")) and any(a.strip() for a in sub_data.get("answers", []))

                if has_answers:
                    if st.button("✨ 본문 생성하기", key="gen_content_main", use_container_width=True):
                        with st.spinner("집필 중..."):
                            content = generate_subtopic_content(
                                selected_subtopic,
                                selected_chapter,
                                sub_data["questions"],
                                sub_data["answers"],
                                st.session_state["topic"],
                                st.session_state["target_persona"],
                            )
                            sub_data["content"] = content
                            trigger_auto_save()
                            st.rerun()
                else:
                    st.info("왼쪽 질문에 최소 1개라도 답변을 넣어주세요.")

                content_key = f"content_{selected_chapter}_{selected_subtopic}"
                if content_key not in st.session_state:
                    st.session_state[content_key] = sub_data.get("content", "")

                edited = st.text_area("본문 내용", height=420, key=content_key, label_visibility="collapsed")
                sub_data["content"] = edited

                if sub_data.get("content"):
                    cc = calculate_char_count(sub_data["content"])
                    st.caption(f"📊 공백 포함 {cc:,}자")
                    st.success("✅ 본문 저장됨")

            st.markdown("---")
            st.markdown("### 📖 작성된 본문 모아보기")
            pure = get_all_content_text()
            if pure:
                total_chars = calculate_char_count(pure)
                content_count = sum(
                    1
                    for ch_data in st.session_state["chapters"].values()
                    for st_d in ch_data.get("subtopic_data", {}).values()
                    if st_d.get("content")
                )
                st.success(f"✅ 총 {content_count}개 소제목 | {total_chars:,}자")

                with st.expander("전체 본문 펼쳐보기", expanded=False):
                    for ch in st.session_state["outline"]:
                        ch_d = st.session_state["chapters"].get(ch, {})
                        subtopics = ch_d.get("subtopics", [])
                        data = ch_d.get("subtopic_data", {})
                        any_content = any(data.get(s, {}).get("content") for s in subtopics)
                        if any_content:
                            st.markdown(f"#### {ch}")
                            for s in subtopics:
                                if data.get(s, {}).get("content"):
                                    st.markdown(f"- {s}")
                                    st.write(clean_content_for_display(data[s]["content"], s, ch))
                                    st.markdown("")
            else:
                st.info("아직 작성된 본문이 없습니다.")

        else:
            st.warning("이 챕터에 소제목이 없습니다. 소제목을 추가하거나 자동 생성하세요.")

        st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# TAB 5: Refine & Quality
# =========================================================
with tabs[4]:
    st.markdown('<div class="p-card">', unsafe_allow_html=True)
    st.subheader("문체 다듬기 & 품질 검사")

    # Build content options
    content_options = []
    for ch in st.session_state.get("outline", []):
        ch_data = st.session_state.get("chapters", {}).get(ch, {})
        for st_name, st_data in ch_data.get("subtopic_data", {}).items():
            if st_data.get("content"):
                content_options.append(f"{ch} > {st_name}")

    left, right = st.columns([1, 1])

    with left:
        st.caption("Style")
        selected_content = st.selectbox("다듬을 콘텐츠 선택", content_options if content_options else ["(직접 입력)"], key="refine_select")
        style = st.selectbox("목표 스타일", ["친근한", "전문적", "직설적", "스토리텔링"], key="style_select")

        direct_text = ""
        if not content_options or selected_content == "(직접 입력)":
            direct_text = st.text_area("다듬을 텍스트 직접 입력", height=260, placeholder="다듬고 싶은 텍스트를 여기에 붙여넣으세요...")

        if st.button("✨ 문체 다듬기", key="refine_btn", use_container_width=True):
            content_to_refine = ""
            if content_options and selected_content != "(직접 입력)":
                ch, s = selected_content.split(" > ", 1)
                content_to_refine = st.session_state["chapters"][ch]["subtopic_data"][s]["content"]
            else:
                content_to_refine = direct_text

            if content_to_refine.strip():
                with st.spinner("다듬는 중..."):
                    st.session_state["refined_content"] = refine_content(content_to_refine, style)
            else:
                st.error("다듬을 콘텐츠가 없습니다.")

        if st.session_state.get("refined_content"):
            st.text_area("다듬어진 본문", value=st.session_state["refined_content"], height=360)

            if content_options and selected_content != "(직접 입력)":
                if st.button("원본에 적용", key="apply_refined", use_container_width=True):
                    ch, s = selected_content.split(" > ", 1)
                    st.session_state["chapters"][ch]["subtopic_data"][s]["content"] = st.session_state["refined_content"]
                    trigger_auto_save()
                    st.success("적용됨!")
                    st.rerun()

    with right:
        st.caption("Quality")
        if st.button("🔍 베스트셀러 체크", key="quality_btn", use_container_width=True):
            content_to_check = ""
            if content_options and selected_content != "(직접 입력)":
                ch, s = selected_content.split(" > ", 1)
                content_to_check = st.session_state["chapters"][ch]["subtopic_data"][s]["content"]
            else:
                content_to_check = direct_text

            if content_to_check.strip():
                with st.spinner("분석 중..."):
                    st.session_state["quality_result"] = check_quality(content_to_check)
            else:
                st.error("검사할 콘텐츠가 없습니다.")

        if st.session_state.get("quality_result"):
            st.markdown('<div class="p-card">', unsafe_allow_html=True)
            st.write(st.session_state["quality_result"])
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# TAB 6: Export & Marketing
# =========================================================
with tabs[5]:
    st.markdown('<div class="p-card">', unsafe_allow_html=True)
    st.subheader("최종 출력 & 마케팅")

    left, right = st.columns([1.5, 1])

    with left:
        st.caption("Export")
        book_title = st.text_input("전자책 제목", value=st.session_state.get("book_title", ""), key="final_title")
        subtitle = st.text_input("부제", value=st.session_state.get("subtitle", ""), key="final_subtitle")
        st.session_state["book_title"] = book_title
        st.session_state["subtitle"] = subtitle

        # Build full book text/html
        full_txt = []
        full_html = []

        if book_title:
            full_txt.append(book_title)
            full_html.append(f"<h1>{book_title}</h1>")
        if subtitle:
            full_txt.append(subtitle)
            full_html.append(f"<p style='color:#777;'>{subtitle}</p>")

        full_txt.append("\n" + "=" * 50 + "\n")

        for ch in st.session_state.get("outline", []):
            ch_data = st.session_state.get("chapters", {}).get(ch, {})
            subs = ch_data.get("subtopics", [])
            data = ch_data.get("subtopic_data", {})
            chapter_has_content = any(data.get(s, {}).get("content") for s in subs)
            if not chapter_has_content:
                continue

            full_txt.append(f"\n{ch}\n" + "-" * 40 + "\n")
            full_html.append(f"<h2>{ch}</h2>")

            for s in subs:
                content = data.get(s, {}).get("content")
                if not content:
                    continue
                full_txt.append(f"\n{s}\n\n{content}\n")
                full_html.append(f"<h3>{s}</h3>")
                for para in content.split("\n\n"):
                    if para.strip():
                        full_html.append(f"<p>{para.strip()}</p>")

        full_txt_str = "\n".join(full_txt).strip()
        full_html_str = "\n".join(full_html)

        html_doc = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <title>{book_title or "전자책"}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Pretendard", "Segoe UI", Arial, sans-serif;
      max-width: 860px;
      margin: 0 auto;
      padding: 48px 20px;
      line-height: 1.85;
      color: #111;
    }}
    h1 {{ font-size: 34px; margin: 0 0 8px 0; }}
    h2 {{ font-size: 24px; margin-top: 44px; }}
    h3 {{ font-size: 18px; margin-top: 26px; }}
    p {{ font-size: 16px; margin: 14px 0; }}
    hr {{ border: none; border-top: 1px solid #eee; margin: 24px 0; }}
  </style>
</head>
<body>
{full_html_str}
</body>
</html>"""

        # Downloads
        c1, c2, c3 = st.columns(3)
        fname = sanitize_filename(book_title or "ebook", 24)
        with c1:
            st.download_button(
                "📄 TXT 다운로드",
                full_txt_str,
                file_name=f"{fname}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with c2:
            st.download_button(
                "🌐 HTML 다운로드",
                html_doc,
                file_name=f"{fname}_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True,
            )

        # RTF
        rtf = "{\\rtf1\\ansi\\ansicpg949\\deff0\n{\\fonttbl{\\f0\\fnil Malgun Gothic;}}\n\\f0\\fs24\n"
        rtf += escape_rtf_unicode(book_title or "") + "\\par\n"
        rtf += escape_rtf_unicode(subtitle or "") + "\\par\\par\n"
        for ch in st.session_state.get("outline", []):
            ch_data = st.session_state.get("chapters", {}).get(ch, {})
            subs = ch_data.get("subtopics", [])
            data = ch_data.get("subtopic_data", {})
            if not any(data.get(s, {}).get("content") for s in subs):
                continue
            rtf += "\\par\\b " + escape_rtf_unicode(ch) + "\\b0\\par\\par\n"
            for s in subs:
                content = data.get(s, {}).get("content")
                if not content:
                    continue
                rtf += "\\b " + escape_rtf_unicode(s) + "\\b0\\par\n"
                rtf += escape_rtf_unicode(content) + "\\par\\par\n"
        rtf += "}"

        with c3:
            st.download_button(
                "📗 RTF 다운로드",
                rtf.encode("utf-8"),
                file_name=f"{fname}_{datetime.now().strftime('%Y%m%d')}.rtf",
                mime="application/rtf",
                use_container_width=True,
            )

        st.markdown("---")
        pure = get_all_content_text()
        if pure:
            total_chars = calculate_char_count(pure)
            pages = max(1, total_chars // 500)
            st.success(f"✅ 총 {total_chars:,}자 | 약 {pages}페이지 (거칠게 환산)")
            with st.expander("📖 전체 본문 펼쳐보기", expanded=False):
                for ch in st.session_state.get("outline", []):
                    ch_data = st.session_state.get("chapters", {}).get(ch, {})
                    subs = ch_data.get("subtopics", [])
                    data = ch_data.get("subtopic_data", {})
                    if any(data.get(s, {}).get("content") for s in subs):
                        st.markdown(f"#### {ch}")
                        for s in subs:
                            if data.get(s, {}).get("content"):
                                st.markdown(f"- {s}")
                                st.write(clean_content_for_display(data[s]["content"], s, ch))
        else:
            st.info("아직 작성된 본문이 없습니다.")

    with right:
        st.caption("Marketing")
        if st.button("카피 생성하기", key="marketing_btn", use_container_width=True):
            with st.spinner("생성 중..."):
                marketing = generate_marketing_copy(
                    st.session_state.get("book_title", st.session_state.get("topic", "")),
                    st.session_state.get("subtitle", ""),
                    st.session_state.get("topic", ""),
                    st.session_state.get("target_persona", ""),
                )
                st.session_state["marketing_copy"] = marketing

        if st.session_state.get("marketing_copy"):
            st.markdown('<div class="p-card">', unsafe_allow_html=True)
            st.write(st.session_state["marketing_copy"])
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# Auto-save toast (lightweight)
# =========================================================
if st.session_state.get("auto_save_trigger"):
    st.session_state["auto_save_trigger"] = False
    st.toast("💾 자동 저장됨!")

# =========================================================
# Footer
# =========================================================
st.markdown(
    """
    <div style="text-align:center; margin-top: 26px; color: rgba(255,255,255,0.38);">
      CASHMAKER — <span style="color: rgba(245,215,110,0.95); font-weight: 800;">남현우 작가</span>
    </div>
    """,
    unsafe_allow_html=True,
)
