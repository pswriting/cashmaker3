import streamlit as st
import google.generativeai as genai
import re
import json
import io
from datetime import datetime
from pathlib import Path

# ==========================================
# 🧠 CASHMAKER 천재 작가 페르소나 & 프롬프트 정의
# ==========================================
GENIUS_PERSONA = """# Role Definition
당신은 대한민국 상위 1% 전자책 매출을 기록하는 '초고수익 전자책 기획자'이자 '심리 설계자'입니다.
당신의 문장은 읽는 순간 독자의 뇌리에 박히며, 밤을 새워서라도 다음 내용을 읽게 만드는 마력이 있습니다.

# Writing Principles (천재 작가의 5원칙)
1. **[통찰의 재해석]**: 뻔한 이야기를 하지 않습니다. 현상을 비틀어 충격적인 진실을 드러냅니다.
2. **[리듬감 부여]**: 짧은 문장으로 때리고(Impact), 긴 문장으로 설득(Logic)합니다.
3. **[구체성의 마법]**: "열심히" 대신 "새벽 4시 기상"이라고 씁니다. 추상적인 형용사를 혐오합니다.
4. **[차가운 공감]**: 무조건적인 위로 대신, 독자의 게으름과 실패를 날카롭게 지적하고 해결책을 줍니다.
5. **[어려운 말 금지]**: 중학생도 이해 못 할 전문 용어는 쓰레기통에 버립니다. 쉬운 비유를 듭니다.

# Final Rule
답변의 맨 마지막에는 반드시 구분선(---)을 긋고, **'🗣️ 작가의 한마디'**를 덧붙여 사용자의 실행을 독려하거나 핵심을 요약해주십시오.
"""

# (원본 템플릿들은 유지 — 실제로는 generate_outline / generate_subtopic_content에서 더 강하게 쓰고 있음)
TOC_PROMPT_TEMPLATE = """# Task
사용자가 입력한 [주제], [타겟], [고통]을 바탕으로, 즉시 결제를 유도하는 '살인적인 전자책 목차'를 기획하십시오.
"""

CONTENT_PROMPT_TEMPLATE = """# Task
당신은 '설명충'이 아니라 '스토리텔러'입니다.
"""

# ==========================================
# 🔐 API 키 저장/불러오기 (로컬 파일)
# ==========================================
def get_config_path() -> Path:
    home = Path.home()
    return home / ".ebook_app_config.json"

def load_saved_api_key() -> str:
    config_path = get_config_path()
    try:
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("api_key", "")
    except Exception:
        pass
    return ""

def save_api_key(api_key: str) -> bool:
    config_path = get_config_path()
    try:
        config = {}
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        config["api_key"] = api_key
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

# ==========================================
# 🎨 CSS (원본 CSS가 길어 채팅 제한 가능 — 필요 시 여기 문자열을 원본 그대로 교체)
# ==========================================
PREMIUM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

* {
    font-family: 'Inter', -apple-system, sans-serif;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    letter-spacing: -0.01em;
}
.stApp { background: #000000; }
.main .block-container {
    background: rgba(10, 10, 15, 0.7);
    backdrop-filter: blur(40px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 32px;
    padding: 3rem 3.5rem;
    max-width: 1280px;
}
[data-testid="stSidebar"] {
    background: rgba(5, 5, 10, 0.95);
    border-right: 1px solid rgba(255, 215, 0, 0.15);
}
.stButton > button {
    width: 100%;
    border-radius: 14px;
    font-weight: 700;
    background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%) !important;
    color: #000 !important;
    border: none !important;
    padding: 16px 36px;
    font-size: 15px;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%) !important;
    color: #fff !important;
}
.stDeployButton {display:none;}
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}
</style>
"""

st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

# ==========================================
# 🔑 비밀번호 설정
# ==========================================
CORRECT_PASSWORD = "cashmaker2024"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown(
        """
        <div style="max-width:460px;margin:120px auto;padding:70px 50px;background:rgba(10,10,15,0.8);
        border:1px solid rgba(255,215,0,0.3);border-radius:32px;text-align:center;">
            <div style="font-size:48px;font-weight:900;font-family:'Space Grotesk',sans-serif;color:#FFD700;">
                CASHMAKER
            </div>
            <div style="font-size:16px;color:rgba(255,255,255,0.5);margin-top:6px;">
                전자책 작성 프로그램
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        password_input = st.text_input("비밀번호를 입력하세요", type="password", placeholder="비밀번호")
        if st.button("입장하기"):
            if password_input == CORRECT_PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다")
    st.stop()

# ==========================================
# 🧾 세션 초기화
# ==========================================
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
    "outline_mode": "ai",
    "full_outline": "",
    "auto_save_trigger": False,
}
for k, v in default_states.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==========================================
# 🧰 헬퍼 함수들
# ==========================================
def get_api_key() -> str:
    return st.session_state.get("api_key", "")

def calculate_char_count(text: str) -> int:
    if not text:
        return 0
    return len(text.replace("\n", "").replace(" ", ""))

def sync_full_outline():
    if not st.session_state.get("outline"):
        st.session_state["full_outline"] = ""
        return
    new_full_outline = ""
    for ch in st.session_state["outline"]:
        new_full_outline += f"## {ch}\n"
        if ch in st.session_state.get("chapters", {}):
            for st_name in st.session_state["chapters"][ch].get("subtopics", []):
                new_full_outline += f"- {st_name}\n"
        new_full_outline += "\n"
    st.session_state["full_outline"] = new_full_outline.strip()

def trigger_auto_save():
    sync_full_outline()
    st.session_state["auto_save_trigger"] = True

def get_all_content_text() -> str:
    pure_content = ""
    for ch in st.session_state.get("outline", []):
        ch_data = st.session_state.get("chapters", {}).get(ch, {})
        subtopic_data = ch_data.get("subtopic_data", {})
        for st_name, st_data in subtopic_data.items():
            if st_data.get("content"):
                pure_content += st_data["content"].strip() + "\n\n"
    return pure_content.strip()

def escape_rtf_unicode(text: str) -> str:
    """RTF 유니코드 안전 처리"""
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

# ==========================================
# 🤖 AI 기본 함수 (페르소나 적용, system_instruction 적용)
# ==========================================
def ask_ai(system_role: str, prompt: str, temperature: float = 0.7) -> str:
    api_key = get_api_key()
    if not api_key:
        return "⚠️ API 키를 먼저 입력해주세요."
    try:
        genai.configure(api_key=api_key)

        final_system_instruction = GENIUS_PERSONA + "\n\n" + f"현재 당신의 구체적인 역할: {system_role}"

        model = genai.GenerativeModel(
            model_name="models/gemini-2.0-flash",
            system_instruction=final_system_instruction,
        )

        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=4000,
        )

        resp = model.generate_content(prompt, generation_config=generation_config)
        return resp.text or ""
    except Exception as e:
        return f"오류 발생: {str(e)}"

# ==========================================
# 🔥 AI 기능들 (원본 기능 유지 + 버그 수정)
# ==========================================
def analyze_topic_score(topic: str) -> str:
    prompt = f"""'{topic}' 주제의 전자책 적합도를 분석해주세요.
다음 5가지 항목을 각각 0~100점으로 채점하고, 종합 점수와 판정을 내려주세요.
채점 항목:
1. 시장성 (수요가 있는가?)
2. 수익성 (돈을 지불할 의향이 있는 주제인가?)
3. 차별화 가능성 (경쟁에서 이길 수 있는가?)
4. 작성 난이도 (전자책으로 만들기 쉬운가?)
5. 지속성 (오래 팔릴 수 있는가?)

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
}}
"""
    return ask_ai("전자책 시장 분석가", prompt, temperature=0.3)

def generate_titles_advanced(topic: str, persona: str, pain_points: str) -> str:
    prompt = f"""당신은 자청(역행자), 엠제이 드마코(부의 추월차선), 김승호(돈의 속성)급 베스트셀러 작가입니다.

[분석 대상]
주제: {topic}
타겟: {persona}
타겟의 속마음: {pain_points}

[베스트셀러 제목의 핵심 원칙]
1. "읽는 순간 뒤통수를 맞은 느낌" - 기존 상식을 정면으로 뒤집어라
2. "이건 나만 몰랐던 거 아냐?" - 소외감과 긴급함을 동시에 자극
3. "구체적 숫자는 신뢰를 만든다" - 모호함 제거
4. "짧을수록 강하다" - 7자 이내 메인 타이틀

[절대 금지]
- "비법", "노하우", "성공", "방법", "전략", "가이드"
- "~하는 법", "~하기", "완벽한", "쉬운"
- 평범한 질문형 물음표 제목

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
(5개)
"""
    return ask_ai("카피라이터", prompt, temperature=0.9)

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

나쁜 예: "돈 관리의 중요성"
좋은 예: "통장 쪼개기가 당신을 가난하게 만든다"

[원칙 2] 소제목 = 호기심 폭발
- "이게 뭐야?" 싶은 궁금증 유발
- 구체적 숫자, 비유, 반전 활용
- 뻔한 조언 대신 날카로운 통찰

나쁜 예: "시간 관리 팁"
좋은 예: "하루 2시간으로 연봉 2배 만든 공식"

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
- **굵은글씨**, 번호(1.1), 들여쓰기, 부연설명

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

'{subtopic_title}' 소제목의 핵심 내용을 끌어낼 수 있는 인터뷰 질문 3개를 만들어주세요.

형식:
Q1: [질문]
Q2: [질문]
Q3: [질문]
"""
    return ask_ai("베스트셀러 고스트라이터", prompt, temperature=0.7)

def regenerate_single_subtopic(chapter_title: str, subtopic_num: int, topic: str, current_subtopics: list[str]) -> str:
    prompt = f"""주제 '{topic}'의 챕터 '{chapter_title}'에서 소제목 {subtopic_num}번을 새롭게 작성해주세요.

현재 소제목들:
{chr(10).join([f"- {s}" for s in current_subtopics])}

{subtopic_num}번 소제목만 새롭게 작성하되, 다른 소제목들과 중복되지 않게 해주세요.

[소제목 원칙]
- "이게 뭐야?" 싶은 궁금증 유발
- 구체적 숫자 활용 (97%, 3개월 등)
- 뻔한 표현 완전 배제 ("~의 중요성", "~하는 방법" 금지)
- 상식을 뒤집는 반전

출력: 새 소제목 한 줄만 (번호나 기호 없이)
"""
    result = ask_ai("카피라이터", prompt, temperature=0.85).strip()
    first_line = result.split("\n")[0].strip()
    return first_line.lstrip("- ").lstrip("0123456789.").strip()

def regenerate_chapter_outline(chapter_num: int, topic: str, persona: str, current_outline: list[str]) -> str:
    prompt = f"""주제 '{topic}'의 전자책에서 챕터 {chapter_num}을 새롭게 작성해주세요.

현재 목차:
{chr(10).join(current_outline)}

챕터 {chapter_num}만 새롭게 작성하되, 다른 챕터들과 중복되지 않고 자연스럽게 이어지도록 해주세요.

[챕터 제목 원칙]
- 상식을 정면으로 부정
- "~의 중요성", "~하는 방법" 절대 금지
- 읽는 순간 "어?" 하게 만들기

[소제목 원칙]
- "이게 뭐야?" 싶은 호기심
- 구체적 숫자, 비유, 반전 활용

출력 형식:
## [새로운 챕터 제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]
"""
    return ask_ai("베스트셀러 편집자", prompt, temperature=0.85)

def generate_subtopic_content(
    subtopic_title: str,
    chapter_title: str,
    questions: list[str],
    answers: list[str],
    topic: str,
    persona: str,
) -> str:
    # ✅ 원본의 치명적 버그 수정: qa_pairs 생성 루프 밖에서 prompt 생성해야 함
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
[법칙 2] 짧은 문장, 강한 임팩트
[법칙 3] 문단 구성 = 리듬감 (한 문단 3~5문장, 문단 사이 빈 줄 1개)
[법칙 4] 스토리 > 설명 (Before→깨달음→After)
[법칙 5] 숫자로 증명하라
[법칙 6] 감정을 건드려라 (과잉 금지)
[법칙 7] 대화체 활용
[법칙 8] 반복과 강조 (표현 바꿔 2~3번)
[법칙 9] 구체적 장면 묘사 (시간/장소/상황)
[법칙 10] 독자 = 친구 (딱딱한 설명 금지)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 문체 규칙 (합쇼체 100%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
모든 문장 끝:
✓ ~입니다 / ~습니다 / ~했습니다 / ~됩니다
✓ ~죠 / ~거죠 / ~셨죠 / ~네요
✓ ~세요 / ~하세요

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚫 AI 티 나는 표현 절대 금지
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
다음 표현 사용 시 0점 처리:
- "실수 1:", "실수 2:", "해결책:" (나열 금지)
- "첫째,", "둘째,", "셋째," (번호 금지)
- "중요합니다", "핵심입니다", "필수적입니다" (반복 금지)
- "따라서", "그러므로", "결론적으로"
- "~라고 할 수 있습니다"
- "많은 분들이", "대부분의 사람들이"
- "~하는 것이 좋습니다"
- **굵은글씨**, *기울임*, 1. 2. 3. 번호
- "저는," (주어 뒤 쉼표 금지)
- "포기하지 마세요", "도전해보세요"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📏 분량: 1500~2000자 (공백 포함)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
반드시 1500자 이상 작성하세요.
독자가 "이 부분만 읽어도 돈값 한다"고 느끼게 깊이 있게 쓰세요.
"""
    return ask_ai("베스트셀러 작가", prompt, temperature=0.8)

def refine_content(content: str, style: str = "친근한") -> str:
    style_guide = {
        "친근한": "친근한 스타일 - 합니다체, 자신감 있는 단정, 구체적 숫자와 팩트",
        "전문적": "전문가 스타일 - 합니다체, 데이터와 출처 강조, 논리적 전개",
        "직설적": "직설 스타일 - 합니다체, 핵심만 간결하게, 군더더기 제로",
        "스토리텔링": "스토리 스타일 - 합니다체, 구체적 장면 묘사, 대화체 활용",
    }
    prompt = f"""다음 글을 다듬어주세요.

[원본]
{content}

[수정 사항]
1. 반드시 "합니다체(존댓말)"로 통일
2. 한 문단은 3~5문장으로 구성
3. AI 티 나는 표현 모두 제거 ("따라서", "중요합니다" 반복 등)
4. 마크다운 제거 (**굵게**, *기울임*, 번호 매기기)

[목표 스타일]
{style_guide.get(style, style_guide["친근한"])}

다듬어진 글만 출력하세요.
"""
    return ask_ai("에디터", prompt, temperature=0.7)

def check_quality(content: str) -> str:
    prompt = f"""다음 글이 베스트셀러 수준인지 평가해주세요.

[평가할 글]
{content[:4000]}

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

# ==========================================
# 🧭 사이드바
# ==========================================
with st.sidebar:
    # Progress
    st.markdown("### Progress")
    progress_items = [
        bool(st.session_state.get("topic")),
        bool(st.session_state.get("target_persona")),
        bool(st.session_state.get("outline")),
        len(st.session_state.get("chapters", {})) > 0,
        bool(get_all_content_text()),
    ]
    progress = sum(progress_items) / len(progress_items) * 100
    st.progress(progress / 100)
    st.caption(f"{progress:.0f}% 완료")
    st.markdown("---")

    # Info
    st.markdown("### Info")
    if st.session_state.get("topic"):
        st.caption(f"주제: {st.session_state['topic']}")
    if st.session_state.get("book_title"):
        st.caption(f"제목: {st.session_state['book_title']}")
    if st.session_state.get("outline"):
        st.caption(f"목차: {len(st.session_state['outline'])}개")
    completed_chapters = 0
    for ch, ch_data in st.session_state.get("chapters", {}).items():
        for st_name, st_data in ch_data.get("subtopic_data", {}).items():
            if st_data.get("content"):
                completed_chapters += 1
    if completed_chapters:
        st.caption(f"완성: {completed_chapters}개")
    st.markdown("---")

    # Save / Load
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
    }
    save_json = json.dumps(save_data, ensure_ascii=False, indent=2)

    file_name = st.session_state.get("book_title", "전자책") or "전자책"
    file_name = re.sub(r"[^\w\s가-힣-]", "", file_name)[:20]
    st.download_button(
        "📥 작업 저장하기",
        save_json,
        file_name=f"{file_name}_{datetime.now().strftime('%m%d_%H%M')}.json",
        mime="application/json",
        use_container_width=True,
    )

    uploaded_file = st.file_uploader("📤 작업 불러오기", type=["json"], label_visibility="collapsed")
    if uploaded_file is not None:
        try:
            loaded_data = json.loads(uploaded_file.read().decode("utf-8"))
            if st.button("불러오기 적용", use_container_width=True):
                for key in [
                    "topic",
                    "target_persona",
                    "pain_points",
                    "one_line_concept",
                    "outline",
                    "chapters",
                    "book_title",
                    "subtitle",
                    "market_analysis",
                    "topic_score",
                    "topic_verdict",
                    "score_details",
                    "generated_titles",
                ]:
                    if key in loaded_data:
                        st.session_state[key] = loaded_data[key]
                sync_full_outline()
                st.success("불러오기 완료!")
                st.rerun()
        except Exception as e:
            st.error(f"파일 오류: {e}")

    st.markdown("---")

    # API 설정
    st.markdown("### API 설정")
    if "api_key" not in st.session_state:
        st.session_state["api_key"] = load_saved_api_key()

    api_key_input = st.text_input(
        "Gemini API 키",
        value=st.session_state.get("api_key", ""),
        type="password",
        placeholder="AIza...",
        help="Google AI Studio에서 발급받은 API 키를 입력하세요",
    )

    if api_key_input != st.session_state.get("api_key", ""):
        st.session_state["api_key"] = api_key_input
        if save_api_key(api_key_input):
            st.toast("✅ API 키가 저장되었습니다!", icon="💾")

    with st.expander("API 키 발급 방법 (무료)"):
        st.markdown(
            """**2분이면 끝!**

1. Google AI Studio 접속
2. Google 계정으로 로그인
3. "API 키 만들기" 클릭
4. 생성된 키 복사
5. 위 입력창에 붙여넣기

✅ 무료로 시작 가능 (정책은 Google 측 변경 가능)
"""
        )

    if not st.session_state.get("api_key"):
        st.caption("⚠️ API 키를 입력하세요")
    else:
        col_status, col_del = st.columns([3, 1])
        with col_status:
            st.caption("✅ API 키 입력됨 (자동 저장)")
        with col_del:
            if st.button("🗑️", key="del_api_key", help="API 키 삭제"):
                st.session_state["api_key"] = ""
                save_api_key("")
                st.rerun()

# ==========================================
# 🖥️ 메인 UI
# ==========================================
st.markdown(
    """
    <div style="text-align:center;padding:60px 20px;margin-bottom:20px;">
        <div style="font-size:12px;font-weight:800;font-family:'JetBrains Mono', monospace;color:rgba(255,215,0,0.7);letter-spacing:0.3em;">
            CASHMAKER
        </div>
        <div style="font-size:64px;font-weight:900;font-family:'Space Grotesk',sans-serif;color:#FFD700;margin-top:12px;">
            전자책 작성 프로그램
        </div>
        <div style="font-size:20px;color:rgba(255,255,255,0.5);margin-top:10px;">
            쉽고, 빠른 전자책 수익화
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tabs = st.tabs(["① 주제 선정", "② 타겟 & 컨셉", "③ 목차 설계", "④ 본문 작성", "⑤ 문체 다듬기", "⑥ 최종 출력"])

# === TAB 1: 주제 선정 ===
with tabs[0]:
    st.markdown("## 주제 선정 & 적합도 분석")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### 주제 입력")
        topic_input = st.text_input(
            "어떤 주제로 전자책을 쓰고 싶으세요?",
            value=st.session_state["topic"],
            placeholder="예: 크몽으로 월 500만원 벌기",
        )
        if topic_input != st.session_state["topic"]:
            st.session_state["topic"] = topic_input
            st.session_state["topic_score"] = None
            st.session_state["score_details"] = None

        if st.button("📊 적합도 분석하기 (선택)", key="analyze_btn"):
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
                    except Exception:
                        st.error("분석 결과 파싱 오류. 다시 시도해주세요.")

    with col2:
        st.markdown("### 분석 결과")
        if st.session_state["topic_score"] is not None:
            details = st.session_state.get("score_details") or {}
            st.metric("종합 점수", st.session_state["topic_score"])
            st.write(f"판정: {st.session_state.get('topic_verdict')}")
            if details:
                st.markdown("#### 세부 점수")
                for name, key in [
                    ("시장성", "market"),
                    ("수익성", "profit"),
                    ("차별화", "differentiation"),
                    ("작성 난이도", "difficulty"),
                    ("지속성", "sustainability"),
                ]:
                    sv = details.get(key, {}).get("score", 0)
                    rs = details.get(key, {}).get("reason", "")
                    st.write(f"- {name}: {sv}점")
                    if rs:
                        st.caption(rs)
                if details.get("summary"):
                    st.info(details["summary"])
        else:
            st.info("분석은 선택사항입니다. 주제만 입력해도 다음 단계로 진행 가능합니다.")

# === TAB 2: 타겟 & 컨셉 ===
with tabs[1]:
    st.markdown("## 타겟 설정 & 제목 생성")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### 타겟 정의")
        persona = st.text_area(
            "누가 이 책을 읽나요?",
            value=st.session_state["target_persona"],
            placeholder="예: 30대 직장인, 퇴근 후 부업으로 월 100만원 추가 수입을 원하는 사람",
            height=120,
        )
        st.session_state["target_persona"] = persona

        pain_points = st.text_area(
            "타겟의 가장 큰 고민은?",
            value=st.session_state["pain_points"],
            placeholder="예: 시간이 없다, 뭘 해야 할지 모르겠다, 시작이 두렵다",
            height=120,
        )
        st.session_state["pain_points"] = pain_points

        st.markdown("---")
        st.markdown("### 한 줄 컨셉")
        if st.button("컨셉 생성하기", key="concept_btn"):
            if not st.session_state["topic"] or not st.session_state["target_persona"]:
                st.error("주제와 타겟을 먼저 입력해주세요.")
            else:
                with st.spinner("생성 중..."):
                    st.session_state["one_line_concept"] = generate_concept(
                        st.session_state["topic"],
                        st.session_state["target_persona"],
                        st.session_state["pain_points"],
                    )
        if st.session_state.get("one_line_concept"):
            st.text(st.session_state["one_line_concept"])

    with col2:
        st.markdown("### 제목 생성")
        if st.button("제목 생성하기", key="title_btn"):
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

        if st.session_state.get("generated_titles") and "titles" in st.session_state["generated_titles"]:
            for i, t in enumerate(st.session_state["generated_titles"]["titles"], 1):
                st.markdown(f"#### TITLE {i:02d}")
                st.write(f"제목: {t.get('title','')}")
                st.caption(f"부제: {t.get('subtitle','')}")
                st.write(t.get("why_works", ""))
                st.markdown("---")

        st.markdown("### 최종 선택")
        st.session_state["book_title"] = st.text_input("제목", value=st.session_state["book_title"], placeholder="최종 제목")
        st.session_state["subtitle"] = st.text_input("부제", value=st.session_state["subtitle"], placeholder="부제")

# === TAB 3: 목차 설계 ===
with tabs[2]:
    st.markdown("## 목차 설계")

    outline_mode = st.radio(
        "목차를 어떻게 만드시겠어요?",
        ["🤖 자동으로 목차 생성", "✍️ 내가 직접 입력"],
        horizontal=True,
        key="outline_mode_radio",
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        if outline_mode == "🤖 자동으로 목차 생성":
            st.markdown("### 목차 자동 설계")
            if st.button("🚀 목차 생성하기", key="outline_btn"):
                if not st.session_state["topic"]:
                    st.error("주제를 먼저 입력해주세요.")
                else:
                    with st.spinner("설계 중..."):
                        outline_text = generate_outline(
                            st.session_state["topic"],
                            st.session_state["target_persona"],
                            st.session_state["pain_points"],
                        )
                        lines = outline_text.split("\n")

                        chapters = []
                        current_chapter = None
                        chapter_subtopics = {}

                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue

                            if line.startswith("##") or "PART" in line.upper():
                                chapter_name = line.lstrip("#").strip()
                                chapter_name = re.sub(r"\*\*(.+?)\*\*", r"\1", chapter_name)
                                if chapter_name and "PART" in chapter_name.upper():
                                    current_chapter = chapter_name
                                    chapters.append(current_chapter)
                                    chapter_subtopics[current_chapter] = []
                            elif current_chapter and line.startswith("-"):
                                subtopic = line.lstrip("- ").strip()
                                subtopic = re.sub(r"\*\*(.+?)\*\*", r"\1", subtopic)
                                subtopic = re.sub(r"^\d+\.\d+\s*", "", subtopic)
                                subtopic = re.sub(r"^\d+\.\s*", "", subtopic)
                                if subtopic and len(subtopic) > 2:
                                    chapter_subtopics[current_chapter].append(subtopic)

                        if chapters:
                            st.session_state["outline"] = chapters
                            st.session_state["chapters"] = {}
                            for ch in chapters:
                                subs = chapter_subtopics.get(ch, [])
                                st.session_state["chapters"][ch] = {
                                    "subtopics": subs,
                                    "subtopic_data": {s: {"questions": [], "answers": [], "content": ""} for s in subs},
                                }
                            sync_full_outline()
                            st.success(f"✅ {len(chapters)}개 챕터 생성 완료")
                            st.rerun()
                        else:
                            st.error("목차 생성 실패. 다시 시도해주세요.")

            if st.session_state.get("full_outline"):
                st.markdown("### 📋 현재 목차")
                st.code(st.session_state["full_outline"], language=None)

        else:
            st.markdown("### 목차 직접 입력")
            existing_outline = st.session_state.get("full_outline", "")
            manual_outline = st.text_area(
                "목차 입력",
                value=existing_outline,
                height=350,
                placeholder="## 챕터1: 제목\n- 소제목1\n- 소제목2\n\n## 챕터2: 제목\n- 소제목3",
                key="manual_outline_input",
            )
            if st.button("✅ 목차 저장하기", key="save_manual_outline"):
                if manual_outline.strip():
                    lines = manual_outline.strip().split("\n")
                    chapters = []
                    current_chapter = None
                    chapter_subtopics = {}

                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        if line.startswith("##") or any(line.lower().startswith(kw) for kw in ["챕터", "chapter"]):
                            chapter_name = line.lstrip("#").strip()
                            current_chapter = chapter_name
                            chapters.append(current_chapter)
                            chapter_subtopics[current_chapter] = []
                        elif current_chapter and line.startswith("-"):
                            subtopic = line.lstrip("- ").strip()
                            if subtopic:
                                chapter_subtopics[current_chapter].append(subtopic)

                    st.session_state["outline"] = chapters
                    st.session_state["chapters"] = {}
                    for ch in chapters:
                        subs = chapter_subtopics.get(ch, [])
                        st.session_state["chapters"][ch] = {
                            "subtopics": subs,
                            "subtopic_data": {s: {"questions": [], "answers": [], "content": ""} for s in subs},
                        }
                    sync_full_outline()
                    st.success("✅ 저장 완료!")
                    st.rerun()

    with col2:
        st.markdown("### 📋 목차 관리")
        if not st.session_state.get("outline"):
            st.info("왼쪽에서 목차를 생성하거나 직접 입력하세요.")
        else:
            for i, chapter in enumerate(st.session_state["outline"]):
                subtopic_count = len(st.session_state["chapters"].get(chapter, {}).get("subtopics", []))
                with st.expander(f"{chapter} ({subtopic_count}개 소제목)", expanded=False):
                    col_edit, col_actions = st.columns([3, 2])
                    with col_edit:
                        new_title = st.text_input("챕터 제목", value=chapter, key=f"edit_chapter_{i}", label_visibility="collapsed")
                    with col_actions:
                        col_regen, col_del = st.columns(2)
                        with col_regen:
                            if st.button("🔄", key=f"regen_chapter_{i}", help="재생성"):
                                with st.spinner("재생성 중..."):
                                    new_chapter_text = regenerate_chapter_outline(
                                        i + 1,
                                        st.session_state["topic"],
                                        st.session_state["target_persona"],
                                        st.session_state["outline"],
                                    )
                                    lines = new_chapter_text.split("\n")
                                    new_chapter_title = None
                                    new_subtopics = []
                                    for line in lines:
                                        line = line.strip()
                                        if line.startswith("##"):
                                            new_chapter_title = line.lstrip("#").strip()
                                        elif line.startswith("-"):
                                            st_name = line.lstrip("- ").strip()
                                            if st_name:
                                                new_subtopics.append(st_name)

                                    if new_chapter_title:
                                        old_chapter = st.session_state["outline"][i]
                                        st.session_state["outline"][i] = new_chapter_title
                                        if old_chapter in st.session_state["chapters"]:
                                            del st.session_state["chapters"][old_chapter]
                                        st.session_state["chapters"][new_chapter_title] = {
                                            "subtopics": new_subtopics,
                                            "subtopic_data": {s: {"questions": [], "answers": [], "content": ""} for s in new_subtopics},
                                        }
                                        trigger_auto_save()
                                        st.rerun()

                        with col_del:
                            if st.button("🗑️", key=f"del_chapter_{i}", help="삭제"):
                                old_chapter = st.session_state["outline"].pop(i)
                                if old_chapter in st.session_state["chapters"]:
                                    del st.session_state["chapters"][old_chapter]
                                trigger_auto_save()
                                st.rerun()

                    if new_title != chapter and new_title.strip():
                        if st.button("💾 제목 저장", key=f"save_chapter_title_{i}"):
                            st.session_state["outline"][i] = new_title
                            if chapter in st.session_state["chapters"]:
                                st.session_state["chapters"][new_title] = st.session_state["chapters"].pop(chapter)
                            trigger_auto_save()
                            st.rerun()

                    st.markdown("---")
                    st.markdown("**소제목**")
                    subtopics = st.session_state["chapters"].get(chapter, {}).get("subtopics", [])
                    for j, st_name in enumerate(subtopics):
                        col_st, col_st_actions = st.columns([3, 2])
                        with col_st:
                            new_st = st.text_input(
                                f"소제목 {j+1}",
                                value=st_name,
                                key=f"edit_st_{i}_{j}",
                                label_visibility="collapsed",
                            )
                        with col_st_actions:
                            col_st_regen, col_st_del = st.columns(2)
                            with col_st_regen:
                                if st.button("🔄", key=f"regen_st_{i}_{j}", help="재생성"):
                                    with st.spinner("재생성 중..."):
                                        new_st_title = regenerate_single_subtopic(
                                            chapter, j + 1, st.session_state["topic"], subtopics
                                        )
                                        if new_st_title:
                                            old_st = st.session_state["chapters"][chapter]["subtopics"][j]
                                            st.session_state["chapters"][chapter]["subtopics"][j] = new_st_title
                                            if old_st in st.session_state["chapters"][chapter]["subtopic_data"]:
                                                st.session_state["chapters"][chapter]["subtopic_data"][new_st_title] = st.session_state["chapters"][chapter]["subtopic_data"].pop(old_st)
                                            else:
                                                st.session_state["chapters"][chapter]["subtopic_data"][new_st_title] = {"questions": [], "answers": [], "content": ""}
                                            trigger_auto_save()
                                            st.rerun()
                            with col_st_del:
                                if st.button("🗑️", key=f"del_st_{i}_{j}", help="삭제"):
                                    removed_st = st.session_state["chapters"][chapter]["subtopics"].pop(j)
                                    if removed_st in st.session_state["chapters"][chapter]["subtopic_data"]:
                                        del st.session_state["chapters"][chapter]["subtopic_data"][removed_st]
                                    trigger_auto_save()
                                    st.rerun()

                        if new_st != st_name and new_st.strip():
                            if st.button("💾", key=f"save_st_{i}_{j}", help="저장"):
                                st.session_state["chapters"][chapter]["subtopics"][j] = new_st
                                if st_name in st.session_state["chapters"][chapter]["subtopic_data"]:
                                    st.session_state["chapters"][chapter]["subtopic_data"][new_st] = st.session_state["chapters"][chapter]["subtopic_data"].pop(st_name)
                                trigger_auto_save()
                                st.rerun()

            if st.button("➕ 새 챕터 추가", key="add_chapter"):
                new_ch_name = f"챕터{len(st.session_state['outline'])+1}: 새 챕터"
                st.session_state["outline"].append(new_ch_name)
                st.session_state["chapters"][new_ch_name] = {"subtopics": [], "subtopic_data": {}}
                trigger_auto_save()
                st.rerun()

# === TAB 4: 본문 작성 (원본이 끊긴 부분까지 포함해 '끝까지' 복구) ===
with tabs[3]:
    st.markdown("## 본문 작성")

    if not st.session_state.get("outline"):
        st.warning("⚠️ 먼저 '③ 목차 설계' 탭에서 목차를 작성해주세요.")
        st.stop()

    chapter_list = list(st.session_state["outline"])
    if not chapter_list:
        st.warning("⚠️ 챕터가 없습니다.")
        st.stop()

    selected_chapter = st.selectbox("📚 챕터 선택", chapter_list, key="chapter_select_main")

    if selected_chapter not in st.session_state["chapters"]:
        st.session_state["chapters"][selected_chapter] = {"subtopics": [], "subtopic_data": {}}

    chapter_data = st.session_state["chapters"][selected_chapter]
    chapter_data.setdefault("subtopics", [])
    chapter_data.setdefault("subtopic_data", {})

    # 소제목 리스트
    with st.expander(f"📋 '{selected_chapter}' 소제목 ({len(chapter_data['subtopics'])}개)", expanded=True):
        if chapter_data["subtopics"]:
            for j, st_name in enumerate(chapter_data["subtopics"]):
                has_content = bool(chapter_data["subtopic_data"].get(st_name, {}).get("content", "").strip())
                st.write(f"{'✅' if has_content else '⬜'} {j+1}. {st_name}")
        else:
            st.info("소제목이 없습니다. 아래에서 추가하거나 자동 생성하세요.")

        st.markdown("---")
        col_gen, col_add = st.columns(2)
        with col_gen:
            num_subtopics = st.number_input("생성할 개수", min_value=1, max_value=10, value=3, key="num_subtopics_gen_tab4")
            if st.button("✨ 소제목 자동 생성", key="gen_subtopics_tab4"):
                with st.spinner("생성 중..."):
                    subtopics_text = generate_subtopics(
                        selected_chapter,
                        st.session_state["topic"],
                        st.session_state["target_persona"],
                        int(num_subtopics),
                    )
                    new_subtopics = []
                    for line in subtopics_text.split("\n"):
                        line = line.strip()
                        if not line:
                            continue
                        if line[0].isdigit() or line.startswith("-"):
                            cleaned = re.sub(r"^[\d\.\-\s]+", "", line).strip()
                            if cleaned:
                                new_subtopics.append(cleaned)

                    if new_subtopics:
                        # 기존 유지 + 추가 형태가 더 안전
                        for s in new_subtopics[: int(num_subtopics)]:
                            if s not in chapter_data["subtopics"]:
                                chapter_data["subtopics"].append(s)
                                chapter_data["subtopic_data"][s] = {"questions": [], "answers": [], "content": ""}
                        trigger_auto_save()
                        st.success("✅ 소제목 생성/추가 완료!")
                        st.rerun()

        with col_add:
            new_subtopic = st.text_input("새 소제목 추가", placeholder="직접 입력...", key="add_new_subtopic_tab4")
            if st.button("➕ 추가", key="add_subtopic_btn_tab4"):
                if new_subtopic.strip() and new_subtopic not in chapter_data["subtopics"]:
                    chapter_data["subtopics"].append(new_subtopic.strip())
                    chapter_data["subtopic_data"][new_subtopic.strip()] = {"questions": [], "answers": [], "content": ""}
                    trigger_auto_save()
                    st.rerun()

    # 본문 작성 영역
    if not chapter_data["subtopics"]:
        st.warning("⚠️ 이 챕터에 소제목이 없습니다. 위에서 소제목을 추가/생성하세요.")
        st.stop()

    st.markdown("---")
    st.markdown("### ✍️ 본문 작성")

    selected_subtopic = st.selectbox(
        "작성할 소제목",
        chapter_data["subtopics"],
        key="subtopic_select_main",
        format_func=lambda x: f"{'✅' if chapter_data['subtopic_data'].get(x, {}).get('content') else '⬜'} {x}",
    )

    # 진행률
    completed = sum(1 for s in chapter_data["subtopics"] if chapter_data["subtopic_data"].get(s, {}).get("content"))
    total = len(chapter_data["subtopics"])
    st.progress(completed / total if total > 0 else 0)
    st.caption(f"진행: {completed}/{total} 완료")

    # 데이터 보장
    chapter_data["subtopic_data"].setdefault(selected_subtopic, {"questions": [], "answers": [], "content": ""})
    subtopic_data = chapter_data["subtopic_data"][selected_subtopic]

    colL, colR = st.columns([1, 1])

    with colL:
        st.markdown("### 🎤 인터뷰")
        if st.button("🎤 질문 생성하기", key="gen_questions_main"):
            with st.spinner("질문 생성 중..."):
                questions_text = generate_interview_questions(selected_subtopic, selected_chapter, st.session_state["topic"])
                questions = re.findall(r"Q\d+:\s*(.+)", questions_text)
                if not questions:
                    questions = [q.strip() for q in questions_text.split("\n") if q.strip()][:3]
                subtopic_data["questions"] = questions
                subtopic_data["answers"] = [""] * len(questions)
                trigger_auto_save()
                st.rerun()

        if subtopic_data.get("questions"):
            for i, q in enumerate(subtopic_data["questions"]):
                st.write(f"Q{i+1}. {q}")
                if i >= len(subtopic_data.get("answers", [])):
                    subtopic_data["answers"].append("")
                subtopic_data["answers"][i] = st.text_area(
                    f"A{i+1}",
                    value=subtopic_data["answers"][i],
                    key=f"answer_{selected_chapter}_{selected_subtopic}_{i}",
                    height=80,
                    label_visibility="collapsed",
                )
        else:
            st.info("👆 '질문 생성하기'를 눌러 인터뷰 질문을 만든 뒤 답변하세요.")

    with colR:
        st.markdown("### 📝 본문")
        has_answers = subtopic_data.get("questions") and any(a.strip() for a in subtopic_data.get("answers", []))
        if has_answers:
            if st.button("✨ 본문 생성하기", key="gen_content_main"):
                with st.spinner("집필 중..."):
                    content = generate_subtopic_content(
                        selected_subtopic,
                        selected_chapter,
                        subtopic_data["questions"],
                        subtopic_data["answers"],
                        st.session_state["topic"],
                        st.session_state["target_persona"],
                    )
                    subtopic_data["content"] = content
                    trigger_auto_save()
                    st.rerun()
        else:
            st.info("👈 먼저 인터뷰 질문에 답변해야 본문 생성이 가능합니다.")

        # 편집 가능한 본문
        content_key = f"content_{selected_chapter}_{selected_subtopic}"
        if content_key not in st.session_state:
            st.session_state[content_key] = subtopic_data.get("content", "")

        edited = st.text_area("본문 내용", height=420, key=content_key, label_visibility="collapsed")
        subtopic_data["content"] = edited
        trigger_auto_save()

        if subtopic_data.get("content"):
            st.caption(f"📊 {calculate_char_count(subtopic_data['content']):,}자")
            st.success(f"✅ '{selected_subtopic}' 본문 작성 완료!")

# === TAB 5: 문체 다듬기 ===
with tabs[4]:
    st.markdown("## 문체 다듬기")

    content_all = get_all_content_text()
    if not content_all:
        st.info("아직 작성된 본문이 없습니다. '④ 본문 작성'에서 내용을 먼저 생성하세요.")
        st.stop()

    style = st.selectbox("목표 스타일", ["친근한", "전문적", "직설적", "스토리텔링"], index=0)
    st.markdown("---")

    st.markdown("### 현재 전체 본문 (요약 미리보기)")
    st.text_area("미리보기", value=content_all[:6000], height=300)

    colA, colB = st.columns([1, 1])
    with colA:
        if st.button("🪄 전체 본문 다듬기", key="refine_all"):
            with st.spinner("다듬는 중..."):
                refined = refine_content(content_all, style=style)
                st.session_state["refined_all_content"] = refined

    with colB:
        if st.button("🧪 퀄리티 평가", key="quality_check"):
            with st.spinner("평가 중..."):
                st.session_state["quality_report"] = check_quality(content_all)

    if st.session_state.get("refined_all_content"):
        st.markdown("---")
        st.markdown("### 다듬어진 결과")
        st.text_area("결과", value=st.session_state["refined_all_content"], height=420)

    if st.session_state.get("quality_report"):
        st.markdown("---")
        st.markdown("### 편집자 평가")
        st.write(st.session_state["quality_report"])

# === TAB 6: 최종 출력 ===
with tabs[5]:
    st.markdown("## 최종 출력")

    if not st.session_state.get("outline"):
        st.info("목차가 없습니다. 먼저 목차를 생성하세요.")
        st.stop()

    # 최종 텍스트 구성
    title = st.session_state.get("book_title") or "전자책"
    subtitle = st.session_state.get("subtitle") or ""

    full_text = []
    full_text.append(title)
    if subtitle:
        full_text.append(subtitle)
    full_text.append("")
    full_text.append("")

    for ch in st.session_state["outline"]:
        full_text.append(f"[{ch}]")
        full_text.append("")
        ch_data = st.session_state["chapters"].get(ch, {})
        subs = ch_data.get("subtopics", [])
        sub_data = ch_data.get("subtopic_data", {})
        for st_name in subs:
            st_block = sub_data.get(st_name, {})
            content = (st_block.get("content") or "").strip()
            if content:
                full_text.append(f"- {st_name}")
                full_text.append(content)
                full_text.append("")
        full_text.append("")

    final_export_text = "\n".join(full_text).strip()

    st.markdown("### 최종 원고")
    st.text_area("최종 원고", value=final_export_text, height=520)

    st.markdown("---")
    st.markdown("### 다운로드")

    # TXT 다운로드
    st.download_button(
        "📄 TXT 다운로드",
        data=final_export_text.encode("utf-8"),
        file_name=f"{re.sub(r'[^\w\s가-힣-]', '', title)[:30] or 'ebook'}.txt",
        mime="text/plain",
        use_container_width=True,
    )

    # RTF 다운로드 (한글 대응)
    rtf_header = r"{\rtf1\ansi\deff0{\fonttbl{\f0\fnil\fcharset129 Malgun Gothic;}}\f0\fs24 "
    rtf_body = escape_rtf_unicode(final_export_text)
    rtf = (rtf_header + rtf_body + "}").encode("utf-8", errors="ignore")

    st.download_button(
        "📝 RTF 다운로드(워드 호환)",
        data=rtf,
        file_name=f"{re.sub(r'[^\w\s가-힣-]', '', title)[:30] or 'ebook'}.rtf",
        mime="application/rtf",
        use_container_width=True,
    )
