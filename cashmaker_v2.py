import streamlit as st
import google.generativeai as genai
import re
import json
import io
import os
from datetime import datetime
from pathlib import Path

# ==========================================
# 🧠 CASHMAKER 천재 작가 페르소나 & 프롬프트 정의
# ==========================================

GENIUS_PERSONA = """
# Role Definition
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

TOC_PROMPT_TEMPLATE = """
# Task
사용자가 입력한 [주제], [타겟], [고통]을 바탕으로, 즉시 결제를 유도하는 '살인적인 전자책 목차'를 기획하십시오.

# 목차 구성 가이드라인 (심리 설계)
## PART 1. 착각 붕괴 (The Shattering)
- 독자가 겪는 문제가 '노력 부족'이 아니라 '방법의 오류'임을 지적
- "이건 내 얘기잖아?"라고 소름 돋게 만들기 (부정 -> 반전)

## PART 2. 비밀 공개 (The Mechanism)
- 당신만의 유일한 해결책(치트키/공식)을 소개
- 원리를 설명하되, 어렵게 쓰지 말고 '도구'나 '공식'처럼 포장

## PART 3. 무조건적인 실행 (The Action)
- 당장 오늘부터 따라 할 수 있는 구체적 행동 지침 (Copy & Paste 수준)
- "이거 안 하면 손해"라는 느낌 부여

## PART 4. 확장과 유지 (The Scaling)
- 단순 해결을 넘어선, 경제적/시간적 자유의 비전 제시

# 절대 금지 (Banned Words)
- '서론', '본론', '결론', '이해', '개념', '정의', '기초' 사용 금지
- 평범한 표현 (~의 중요성, ~하는 방법) 금지
"""

CONTENT_PROMPT_TEMPLATE = """
# Task
당신은 '설명충'이 아니라 '스토리텔러'입니다. 
주제 '{topic}'의 챕터 '{chapter}' 중 소제목 '{subtopic}'에 해당하는 본문을 작성하십시오.
    
# Writing Rules (집필 수칙)
1. **[비유의 의무화]**: 추상적인 개념이 나오면 즉시 일상생활의 예시(음식, 연애, 게임 등)로 치환하십시오.
2. **[첫 문장 훅]**: 첫 문장은 무조건 독자의 뒤통수를 치거나 질문을 던지며 시작해야 합니다. "안녕하세요" 금지.
3. **[호흡 조절]**: 문장 길이를 다양하게 섞으십시오. 긴 설명 뒤엔 짧고 강렬한 한 마디를 던지십시오.
4. **[액션 플랜]**: 이론 설명 후에는 반드시 '지금 당장 할 수 있는 3가지 행동'을 리스트로 정리해주십시오.
5. **[톤앤매너]**: 옆에서 과외 선생님이 1:1로 가르쳐주듯 친절하지만, 딴짓은 못 하게 단호한 말투(합쇼체)를 유지하십시오.

# 분량
공백 포함 1500자 이상, 독자가 "이것만 읽어도 돈값 했다"고 느끼게 작성하십시오.
"""

# ==========================================
# API 키 저장/불러오기 (로컬 파일)
# ==========================================
def get_config_path():
    """설정 파일 경로 반환"""
    home = Path.home()
    return home / ".ebook_app_config.json"

def load_saved_api_key():
    """저장된 API 키 불러오기"""
    config_path = get_config_path()
    try:
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('api_key', '')
    except Exception:
        pass
    return ''

def save_api_key(api_key):
    """API 키 저장"""
    config_path = get_config_path()
    try:
        config = {}
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        config['api_key'] = api_key
        with open(config_path, 'w') as f:
            json.dump(config, f)
        return True
    except Exception:
        return False

# ==========================================
# 페이지 설정
# ==========================================
st.set_page_config(
    page_title="CASHMAKER - 전자책 작성 프로그램",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 페이지 스타일 (기존 CSS 유지) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    /* ==========================================
       🌌 BASE - 우주 같은 다크 베이스
    ========================================== */
    * { 
        font-family: 'Inter', -apple-system, sans-serif;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        letter-spacing: -0.01em;
    }
    
    /* 배경 - 움직이는 그라데이션 */
    .stApp { 
        background: #000000;
        position: relative;
        overflow-x: hidden;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: 
            radial-gradient(circle at 20% 30%, rgba(138, 43, 226, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, rgba(255, 215, 0, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 80%, rgba(0, 191, 255, 0.08) 0%, transparent 50%);
        animation: gradientShift 20s ease infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes gradientShift {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        50% { transform: translate(-10%, -10%) rotate(180deg); }
    }
    
    /* 메인 컨테이너 - 떠있는 유리판 */
    .main .block-container { 
        background: rgba(10, 10, 15, 0.7);
        backdrop-filter: blur(40px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 32px;
        padding: 3rem 3.5rem;
        max-width: 1280px;
        box-shadow: 
            0 0 0 1px rgba(255, 255, 255, 0.03),
            0 50px 100px -20px rgba(0, 0, 0, 0.5),
            0 0 200px rgba(138, 43, 226, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        position: relative;
        z-index: 1;
    }
    
    /* ... (나머지 CSS는 동일하게 유지) ... */
    
    /* 숨김 요소 */
    .stDeployButton {display:none;} 
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    [data-testid="collapsedControl"] { display: flex !important; visibility: visible !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 비밀번호 설정
# ==========================================
CORRECT_PASSWORD = "cashmaker2024"

# --- 비밀번호 확인 ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown("""
    <div class="login-container">
        <div class="login-title">CASHMAKER</div>
        <div class="login-subtitle">전자책 작성 프로그램</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        password_input = st.text_input("비밀번호를 입력하세요", type="password", placeholder="비밀번호")
        if st.button("입장하기"):
            if password_input == CORRECT_PASSWORD:
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다")
    st.stop()

# --- 세션 초기화 ---
default_states = {
    'topic': '', 
    'target_persona': '', 
    'pain_points': '', 
    'one_line_concept': '',
    'outline': [], 
    'chapters': {}, 
    'current_step': 1, 
    'market_analysis': '',
    'book_title': '', 
    'subtitle': '', 
    'topic_score': None, 
    'topic_verdict': None,
    'score_details': None, 
    'generated_titles': None, 
    'outline_mode': 'ai',
    'full_outline': '',
    'refined_content': '',
    'quality_result': '',
    'marketing_copy': '',
    'api_key': load_saved_api_key()
}

for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ==========================================
# 헬퍼 함수들
# ==========================================
def get_api_key():
    return st.session_state.get('api_key', '')

def get_auto_save_data():
    return {
        'topic': st.session_state.get('topic', ''), 
        'target_persona': st.session_state.get('target_persona', ''),
        'pain_points': st.session_state.get('pain_points', ''), 
        'one_line_concept': st.session_state.get('one_line_concept', ''),
        'outline': st.session_state.get('outline', []), 
        'chapters': st.session_state.get('chapters', {}),
        'book_title': st.session_state.get('book_title', ''), 
        'subtitle': st.session_state.get('subtitle', ''),
        'market_analysis': st.session_state.get('market_analysis', ''), 
        'topic_score': st.session_state.get('topic_score'),
        'topic_verdict': st.session_state.get('topic_verdict'), 
        'score_details': st.session_state.get('score_details'),
        'generated_titles': st.session_state.get('generated_titles'), 
        'saved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def sync_full_outline():
    if not st.session_state.get('outline'):
        return
    new_full_outline = ""
    for ch in st.session_state['outline']:
        new_full_outline += f"## {ch}\n"
        if ch in st.session_state.get('chapters', {}):
            for st_name in st.session_state['chapters'][ch].get('subtopics', []):
                new_full_outline += f"- {st_name}\n"
        new_full_outline += "\n"
    st.session_state['full_outline'] = new_full_outline.strip()

def trigger_auto_save():
    sync_full_outline()
    st.session_state['auto_save_trigger'] = True

def calculate_char_count(text):
    if not text:
        return 0
    return len(text.replace('\n', '').replace(' ', ''))

def get_all_content_text():
    pure_content = ""
    for ch in st.session_state.get('outline', []):
        if ch in st.session_state.get('chapters', {}):
            ch_data = st.session_state['chapters'][ch]
            if 'subtopic_data' in ch_data:
                subtopic_list = ch_data.get('subtopics', [])
                if not subtopic_list and ch in ch_data['subtopic_data']:
                    subtopic_list = [ch]
                for st_name in subtopic_list:
                    st_data = ch_data['subtopic_data'].get(st_name, {})
                    if st_data.get('content'):
                        pure_content += st_data['content']
    return pure_content

def clean_content_for_display(content, subtopic_title=None, chapter_title=None):
    if not content:
        return ""
    # Unicode 제어 문자 제거
    unicode_control_chars = ['\u200e', '\u200f', '\u202a', '\u202b', '\u202c', '\u202d', '\u202e', '\u2066', '\u2067', '\u2068', '\u2069', '\u200b', '\u200c', '\u200d', '\ufeff', '\u061c']
    for char in unicode_control_chars:
        content = content.replace(char, '')
    content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', content)
    content = re.sub(r'<[^>]+>', '', content)
    content = content.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
    
    lines = content.split('\n')
    cleaned_lines = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            if idx > 3 or len(cleaned_lines) > 0:
                cleaned_lines.append(line)
            continue
        if stripped.startswith('#'):
            continue
        if stripped.startswith('챕터') and ':' in stripped[:15]:
            continue
        if stripped.startswith('소제목') and ':' in stripped[:10]:
            continue
        if subtopic_title and idx < 5:
            clean_subtopic = subtopic_title.replace('**', '').strip()
            clean_stripped = stripped.replace('**', '').strip()
            if clean_stripped == clean_subtopic:
                continue
            if clean_subtopic in clean_stripped and len(clean_stripped) < len(clean_subtopic) + 20:
                continue
        if chapter_title and idx < 5:
            clean_chapter = chapter_title.replace('**', '').strip()
            if clean_chapter in stripped or stripped in clean_chapter:
                continue
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines).strip()

def escape_rtf_unicode(text):
    if not text:
        return ""
    result = []
    for char in text:
        code = ord(char)
        if code < 128:
            if char == '\\': result.append('\\\\')
            elif char == '{': result.append('\\{')
            elif char == '}': result.append('\\}')
            elif char == '\n': result.append('\\line ')
            elif char == '\r': continue
            else: result.append(char)
        else:
            signed_code = code - 65536 if code > 32767 else code
            result.append(f'\\u{signed_code}?')
    return ''.join(result)


# ==========================================
# AI 기본 함수 (수정됨: 페르소나 적용)
# ==========================================
def ask_ai(system_role, prompt, temperature=0.7):
    """Gemini API 호출 함수"""
    api_key = get_api_key()
    if not api_key:
        return "⚠️ API 키를 먼저 입력해주세요."
    
    try:
        genai.configure(api_key=api_key)
        
        # 시스템 프롬프트 결합
        final_prompt = f"""{GENIUS_PERSONA}

현재 역할: {system_role}

---

{prompt}"""
        
        # Gemini 모델 설정
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # 생성 설정
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=4000
        )
        
        # 콘텐츠 생성
        response = model.generate_content(
            final_prompt,
            generation_config=generation_config
        )
        
        return response.text
        
    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg.upper():
            return "⚠️ API 키가 유효하지 않습니다. 다시 확인해주세요."
        elif "QUOTA" in error_msg.upper():
            return "⚠️ API 사용량 한도를 초과했습니다."
        else:
            return f"❌ AI 요청 중 오류 발생: {error_msg}"

# ==========================================
# AI 함수들 (기존 코드 유지, ask_ai만 수정됨)
# ==========================================

def generate_outline(topic, persona, pain_points):
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

[원칙 3] 심리적 흐름 설계
1부: 충격과 공감 - "내 얘기잖아" + "뭔가 잘못됐구나"
2부: 원인 폭로 - "이래서 안 됐던 거구나"
3부: 해결책 공개 - "이렇게 하면 되는구나"  
4부: 실행과 비전 - "나도 할 수 있겠다"

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

목차만 출력하세요. 설명 없이."""
    return ask_ai("베스트셀러 편집자", prompt, temperature=0.85)


def generate_subtopics(chapter_title, topic, persona, count=3):
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

번호와 소제목만 출력하세요."""
    return ask_ai("베스트셀러 편집자", prompt, temperature=0.8)


def generate_subtopic_content(subtopic_title, chapter_title, questions, answers, topic, persona):
    qa_pairs = ""
    for i, (q, a) in enumerate(zip(questions, answers), 1):
        if a.strip():
            qa_pairs += f"\n질문{i}: {q}\n답변{i}: {a}\n"
    
    prompt = f"""당신은 "역행자" 자청, "부의 추월차선" 엠제이 드마코 수준의 베스트셀러 작가입니다.

[집필 정보]
주제: {topic}
챕터: {chapter_title}
현재 작성할 소제목: {subtopic_title}
타겟: {persona}

⚠️ 매우 중요: 오직 '{subtopic_title}'에 대한 본문만 작성하세요.

[작가 인터뷰]
{qa_pairs}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 자청 스타일 글쓰기 10가지 법칙
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[법칙 1] 첫 문장 = 뒤통수 한 방
- 좋은 예: "월급 230만원. 그게 제 전부였습니다."

[법칙 2] 짧은 문장, 강한 임팩트
- 한 문장 = 한 호흡 (15~25자)

[법칙 3] 문단 구성 = 리듬감
- 한 문단 = 3~5문장

[법칙 4] 스토리 > 설명
- Before(실패) → 깨달음 → After(성공)

[법칙 5] 숫자로 증명
- "열심히" → "새벽 4시에 일어났습니다"

[법칙 6] 감정을 건드려라

[법칙 7] 대화체 활용

[법칙 8] 반복과 강조

[법칙 9] 구체적 장면 묘사

[법칙 10] 독자 = 친구

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 문체 규칙: 합쇼체 100%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

모든 문장 끝: ~입니다 / ~습니다 / ~했습니다

절대 금지: ~다 / ~인 것이다

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📏 분량: 1500~2000자
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

'{subtopic_title}'의 본문만 작성하세요."""
    return ask_ai("베스트셀러 작가", prompt, temperature=0.8)


def analyze_topic_score(topic):
    prompt = f"""'{topic}' 주제의 전자책 적합도를 분석해주세요.

반드시 JSON 형식으로만 답변:
{{
    "market": {{"score": 85, "reason": "이유"}},
    "profit": {{"score": 80, "reason": "이유"}},
    "differentiation": {{"score": 75, "reason": "이유"}},
    "difficulty": {{"score": 90, "reason": "이유"}},
    "sustainability": {{"score": 70, "reason": "이유"}},
    "total_score": 80,
    "verdict": "적합",
    "summary": "종합 의견"
}}"""
    return ask_ai("전자책 시장 분석가", prompt, temperature=0.3)


def generate_titles_advanced(topic, persona, pain_points):
    prompt = f"""베스트셀러 제목 5개 생성.

주제: {topic}
타겟: {persona}

JSON 형식:
{{
    "titles": [
        {{
            "title": "7자 이내 제목",
            "subtitle": "15자 이내 부제",
            "concept": "컨셉",
            "why_works": "이유"
        }}
    ]
}}"""
    return ask_ai("베스트셀러 작가", prompt, temperature=0.9)


def generate_concept(topic, persona, pain_points):
    prompt = f"""주제: {topic}
타겟: {persona}
고민: {pain_points}

한 줄 컨셉 5개 만들기.

형식:
1. [컨셉]
→ 왜 끌리는가"""
    return ask_ai("카피라이터", prompt, temperature=0.9)


def generate_interview_questions(subtopic_title, chapter_title, topic):
    prompt = f"""'{subtopic_title}' 소제목의 핵심 내용을 끌어낼 인터뷰 질문 3개.

형식:
Q1: [질문]
Q2: [질문]
Q3: [질문]"""
    return ask_ai("베스트셀러 고스트라이터", prompt, temperature=0.7)


def refine_content(content, style="친근한"):
    prompt = f"""다음 글을 {style} 스타일로 다듬기.

[원본]
{content}

[수정 사항]
1. 합니다체 통일
2. 한 문단 3~5문장
3. AI 티 제거

다듬어진 글만 출력."""
    return ask_ai("에디터", prompt, temperature=0.7)


def check_quality(content):
    prompt = f"""베스트셀러 수준 평가.

[평가할 글]
{content[:4000]}

[출력]
📊 종합 점수: __/50점
📌 각 항목 점수
✍️ 수정할 문장 TOP 3
🎯 총평"""
    return ask_ai("베스트셀러 편집자", prompt, temperature=0.6)


def regenerate_chapter_outline(chapter_num, topic, persona, current_outline):
    prompt = f"""챕터 {chapter_num} 재생성.

현재 목차:
{chr(10).join(current_outline)}

출력:
## [새 챕터 제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]"""
    return ask_ai("베스트셀러 편집자", prompt, temperature=0.85)


def regenerate_single_subtopic(chapter_title, subtopic_num, topic, current_subtopics):
    prompt = f"""{subtopic_num}번 소제목 재생성.

현재: {chr(10).join([f"- {s}" for s in current_subtopics])}

새 소제목 한 줄만."""
    result = ask_ai("카피라이터", prompt, temperature=0.85)
    first_line = result.strip().split('\n')[0]
    return first_line.lstrip('- ').lstrip('0123456789.').strip()


def generate_marketing_copy(title, subtitle, topic, persona):
    prompt = f"""마케팅 카피 생성.

제목: {title}
주제: {topic}

1. 크몽 제목 (40자)
2. 헤드라인 3개
3. CTA 3개
4. 인스타 문구
5. 블로그 제목 3개"""
    return ask_ai("크몽 탑셀러 마케터", prompt, temperature=0.85)


# ==========================================
# 사이드바
# ==========================================
with st.sidebar:
    st.markdown("### Progress")
    progress_items = [
        bool(st.session_state['topic']), 
        bool(st.session_state['target_persona']),
        bool(st.session_state['outline']), 
        len(st.session_state['chapters']) > 0,
        any(ch.get('content') for ch in st.session_state['chapters'].values()) if st.session_state['chapters'] else False
    ]
    progress = sum(progress_items) / len(progress_items) * 100
    st.progress(progress / 100)
    st.caption(f"{progress:.0f}% 완료")
    
    st.markdown("---")
    st.markdown("### Info")
    if st.session_state['topic']:
        st.caption(f"주제: {st.session_state['topic']}")
    if st.session_state['book_title']:
        st.caption(f"제목: {st.session_state['book_title']}")
    if st.session_state['outline']:
        st.caption(f"목차: {len(st.session_state['outline'])}개")
    completed_chapters = sum(1 for ch in st.session_state['chapters'].values() if ch.get('content'))
    if completed_chapters:
        st.caption(f"완성: {completed_chapters}개")
    
    st.markdown("---")
    st.markdown("### 💾 저장/불러오기")
    save_data = get_auto_save_data()
    save_json = json.dumps(save_data, ensure_ascii=False, indent=2)
    file_name = st.session_state.get('book_title', '전자책') or '전자책'
    file_name = re.sub(r'[^\w\s가-힣-]', '', file_name)[:20]
    st.download_button(
        "📥 작업 저장하기", 
        save_json, 
        file_name=f"{file_name}_{datetime.now().strftime('%m%d_%H%M')}.json", 
        mime="application/json", 
        use_container_width=True
    )
    
    uploaded_file = st.file_uploader("📤 작업 불러오기", type=['json'], label_visibility="collapsed")
    if uploaded_file is not None:
        try:
            loaded_data = json.loads(uploaded_file.read().decode('utf-8'))
            if st.button("불러오기 적용", use_container_width=True):
                for key in ['topic', 'target_persona', 'pain_points', 'one_line_concept', 
                           'outline', 'chapters', 'book_title', 'subtitle', 'market_analysis', 
                           'topic_score', 'topic_verdict', 'score_details', 'generated_titles']:
                    if key in loaded_data:
                        st.session_state[key] = loaded_data[key]
                st.success("불러오기 완료!")
                st.rerun()
        except Exception as e:
            st.error(f"파일 오류: {e}")
    
    st.markdown("---")
    st.markdown("### API 설정")
    
    api_key_input = st.text_input(
        "Gemini API 키", 
        value=st.session_state['api_key'], 
        type="password", 
        placeholder="AIza...", 
        help="Google AI Studio에서 발급받은 API 키"
    )
    
    if api_key_input and api_key_input != st.session_state['api_key']:
        st.session_state['api_key'] = api_key_input
        if save_api_key(api_key_input):
            st.toast("✅ API 키가 저장되었습니다!", icon="💾")
    
    with st.expander("API 키 발급 방법 (무료)"):
        st.markdown("""**2분이면 끝!**

1. [Google AI Studio](https://aistudio.google.com/apikey) 접속
2. Google 계정으로 로그인
3. **"API 키 만들기"** 클릭
4. 생성된 키 복사
5. 위 입력창에 붙여넣기

✅ 완전 무료 ✅ 신용카드 불필요""")
    
    if not st.session_state.get('api_key'):
        st.warning("⚠️ API 키를 입력하세요")
    else:
        col_status, col_del = st.columns([3, 1])
        with col_status:
            st.caption("✅ API 키 입력됨")
        with col_del:
            if st.button("🗑️", key="del_api_key", help="API 키 삭제"):
                st.session_state['api_key'] = ''
                save_api_key('')
                st.rerun()


# ==========================================
# 메인 UI
# ==========================================
st.markdown("""
<div class="hero-section">
    <div class="hero-label">CASHMAKER</div>
    <div class="hero-title">전자책 작성 프로그램</div>
    <div class="hero-subtitle">쉽고, 빠른 전자책 수익화</div>
</div>
""", unsafe_allow_html=True)

# 탭 생성
tabs = st.tabs(["① 주제 선정", "② 타겟 & 컨셉", "③ 목차 설계", "④ 본문 작성", "⑤ 문체 다듬기", "⑥ 최종 출력"])

# === TAB 1: 주제 선정 ===
with tabs[0]:
    st.markdown("## 주제 선정 & 적합도 분석")
    st.info("💡 이미 주제가 있다면 아래에 입력 후 바로 다음 탭으로 이동하세요!")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 주제 입력")
        topic_input = st.text_input(
            "어떤 주제로 전자책을 쓰고 싶으세요?", 
            value=st.session_state['topic'], 
            placeholder="예: 크몽으로 월 500만원 벌기"
        )
        
        if topic_input != st.session_state['topic']:
            st.session_state['topic'] = topic_input
            st.session_state['topic_score'] = None
            st.session_state['score_details'] = None
        
        st.info("""**좋은 주제의 조건**
- 내가 직접 경험하고 성과를 낸 것
- 사람들이 돈 주고 배우고 싶어하는 것
- 구체적인 결과를 약속할 수 있는 것""")
        
        if st.button("📊 적합도 분석하기 (선택)", key="analyze_btn"):
            if not topic_input:
                st.error("주제를 입력해주세요.")
            else:
                with st.spinner("분석 중..."):
                    result = analyze_topic_score(topic_input)
                    try:
                        json_match = re.search(r'\{[\s\S]*\}', result)
                        if json_match:
                            score_data = json.loads(json_match.group())
                            st.session_state['topic_score'] = score_data.get('total_score', 0)
                            st.session_state['topic_verdict'] = score_data.get('verdict', '분석 실패')
                            st.session_state['score_details'] = score_data
                    except:
                        st.error("분석 결과 파싱 오류. 다시 시도해주세요.")
    
    with col2:
        st.markdown("### 분석 결과")
        if st.session_state['topic_score'] is not None:
            score = st.session_state['topic_score']
            verdict = st.session_state['topic_verdict']
            details = st.session_state['score_details']
            
            st.metric("종합 점수", f"{score}점", verdict)
            
            if details:
                st.markdown("#### 세부 점수")
                for name, key in [
                    ("시장성", "market"), 
                    ("수익성", "profit"), 
                    ("차별화", "differentiation"), 
                    ("작성 난이도", "difficulty"), 
                    ("지속성", "sustainability")
                ]:
                    score_val = details.get(key, {}).get('score', 0)
                    reason = details.get(key, {}).get('reason', '')
                    st.markdown(f"**{name}**: {score_val}점")
                    st.caption(reason)
                
                st.info(f"**종합 의견**: {details.get('summary', '')}")
        else:
            st.info("""분석은 선택사항입니다.
주제만 입력해도 다음 단계로 진행 가능!""")


# === TAB 2: 타겟 & 컨셉 ===
with tabs[1]:
    st.markdown("## 타겟 설정 & 제목 생성")
    
    if not st.session_state['topic']:
        st.warning("💡 먼저 '① 주제 선정' 탭에서 주제를 입력해주세요.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 타겟 정의")
        
        persona = st.text_area(
            "누가 이 책을 읽나요?", 
            value=st.session_state['target_persona'], 
            placeholder="예: 30대 직장인, 퇴근 후 부업으로 월 100만원 추가 수입을 원하는 사람", 
            height=100
        )
        st.session_state['target_persona'] = persona
        
        pain_points = st.text_area(
            "타겟의 가장 큰 고민은?", 
            value=st.session_state['pain_points'], 
            placeholder="예: 시간이 없다, 뭘 해야 할지 모르겠다, 시작이 두렵다", 
            height=100
        )
        st.session_state['pain_points'] = pain_points
        
        st.markdown("---")
        st.markdown("### 한 줄 컨셉")
        
        if st.button("💡 컨셉 생성하기", key="concept_btn"):
            if not st.session_state['topic'] or not persona:
                st.error("주제와 타겟을 먼저 입력해주세요.")
            else:
                with st.spinner("생성 중..."):
                    concept = generate_concept(st.session_state['topic'], persona, pain_points)
                    st.session_state['one_line_concept'] = concept
        
        if st.session_state['one_line_concept']:
            st.info(st.session_state['one_line_concept'])
    
    with col2:
        st.markdown("### 제목 생성")
        
        if st.button("✨ 제목 생성하기", key="title_btn"):
            if not st.session_state['topic']:
                st.error("주제를 먼저 입력해주세요.")
            else:
                with st.spinner("생성 중..."):
                    titles_result = generate_titles_advanced(
                        st.session_state['topic'], 
                        st.session_state['target_persona'], 
                        st.session_state['pain_points']
                    )
                    try:
                        json_match = re.search(r'\{[\s\S]*\}', titles_result)
                        if json_match:
                            st.session_state['generated_titles'] = json.loads(json_match.group())
                    except:
                        st.session_state['generated_titles'] = None
                        st.markdown(titles_result)
        
        if st.session_state.get('generated_titles'):
            titles_data = st.session_state['generated_titles']
            if 'titles' in titles_data:
                for i, t in enumerate(titles_data['titles'], 1):
                    with st.container():
                        st.markdown(f"**옵션 {i}**")
                        st.markdown(f"# {t.get('title', '')}")
                        st.caption(t.get('subtitle', ''))
                        st.info(t.get('why_works', ''))
                        st.markdown("---")
        
        st.markdown("### 최종 선택")
        st.session_state['book_title'] = st.text_input(
            "제목", 
            value=st.session_state['book_title'], 
            placeholder="최종 제목"
        )
        st.session_state['subtitle'] = st.text_input(
            "부제", 
            value=st.session_state['subtitle'], 
            placeholder="부제"
        )


# === TAB 3: 목차 설계 ===
with tabs[2]:
    st.markdown("## 목차 설계")
    
    st.markdown("### 🎯 작업 방식 선택")
    outline_mode = st.radio(
        "목차를 어떻게 만드시겠어요?", 
        ["🤖 자동으로 목차 생성", "✍️ 내가 직접 입력"], 
        horizontal=True
    )
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if outline_mode == "🤖 자동으로 목차 생성":
            st.markdown("### 목차를 자동으로 설계합니다")
            
            if not st.session_state['topic']:
                st.warning("💡 주제를 먼저 입력해주세요")
            
            if st.button("🚀 목차 생성하기", key="outline_btn"):
                if not st.session_state['topic']:
                    st.error("주제를 먼저 입력해주세요.")
                else:
                    with st.spinner("설계 중... (30초 정도 소요)"):
                        outline_text = generate_outline(
                            st.session_state['topic'], 
                            st.session_state['target_persona'], 
                            st.session_state['pain_points']
                        )
                        
                        # 목차 파싱
                        lines = outline_text.split('\n')
                        chapters = []
                        current_chapter = None
                        chapter_subtopics = {}
                        
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                            
                            # 챕터 감지
                            if line.startswith('##') or 'PART' in line.upper():
                                chapter_name = line.lstrip('#').strip()
                                chapter_name = re.sub(r'\*\*(.+?)\*\*', r'\1', chapter_name)
                                if chapter_name and 'PART' in chapter_name.upper():
                                    current_chapter = chapter_name
                                    chapters.append(current_chapter)
                                    chapter_subtopics[current_chapter] = []
                            
                            # 소제목 감지
                            elif current_chapter and line.startswith('-'):
                                subtopic = line.lstrip('- ').strip()
                                subtopic = re.sub(r'\*\*(.+?)\*\*', r'\1', subtopic)
                                subtopic = re.sub(r'^\d+\.\d+\s*', '', subtopic)
                                subtopic = re.sub(r'^\d+\.\s*', '', subtopic)
                                if subtopic and len(subtopic) > 2:
                                    chapter_subtopics[current_chapter].append(subtopic)
                        
                        # 결과 저장
                        if chapters:
                            st.session_state['outline'] = chapters
                            
                            clean_outline = ""
                            for ch in chapters:
                                clean_outline += f"## {ch}\n"
                                for st_name in chapter_subtopics.get(ch, []):
                                    clean_outline += f"- {st_name}\n"
                                clean_outline += "\n"
                            st.session_state['full_outline'] = clean_outline.strip()
                            
                            for ch in chapters:
                                subtopics = chapter_subtopics.get(ch, [])
                                st.session_state['chapters'][ch] = {
                                    'subtopics': subtopics, 
                                    'subtopic_data': {
                                        st: {'questions': [], 'answers': [], 'content': ''} 
                                        for st in subtopics
                                    }
                                }
                            
                            total_subtopics = sum(len(chapter_subtopics.get(ch, [])) for ch in chapters)
                            st.success(f"✅ {len(chapters)}개 챕터, {total_subtopics}개 소제목 생성됨!")
                            st.rerun()
                        else:
                            st.error("목차 생성 실패. 다시 시도해주세요.")
            
            if 'full_outline' in st.session_state and st.session_state['full_outline']:
                st.markdown("**📋 현재 목차**")
                st.code(st.session_state['full_outline'], language=None)
        
        else:  # 직접 입력
            st.markdown("### 목차를 직접 입력하세요")
            
            st.info("""**📌 입력 형식 예시**
## 챕터1: 첫 번째 챕터 제목
- 소제목 1
- 소제목 2""")
            
            existing_outline = ""
            if st.session_state['outline']:
                for ch in st.session_state['outline']:
                    existing_outline += f"## {ch}\n"
                    if ch in st.session_state['chapters']:
                        for st_name in st.session_state['chapters'][ch].get('subtopics', []):
                            existing_outline += f"- {st_name}\n"
            
            manual_outline = st.text_area(
                "목차 입력", 
                value=existing_outline, 
                height=350, 
                placeholder="## 챕터1: 제목\n- 소제목1\n- 소제목2",
                key="manual_outline_input"
            )
            
            if st.button("✅ 목차 저장하기", key="save_manual_outline"):
                if manual_outline.strip():
                    # 목차 파싱
                    lines = manual_outline.strip().split('\n')
                    chapters = []
                    current_chapter = None
                    chapter_subtopics = {}
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        if line.startswith('##') or any(line.lower().startswith(kw) for kw in ['챕터', 'chapter']):
                            chapter_name = line.lstrip('#').strip()
                            current_chapter = chapter_name
                            chapters.append(current_chapter)
                            chapter_subtopics[current_chapter] = []
                        
                        elif current_chapter and line.startswith('-'):
                            subtopic = line.lstrip('- ').strip()
                            if subtopic:
                                chapter_subtopics[current_chapter].append(subtopic)
                    
                    st.session_state['outline'] = chapters
                    st.session_state['full_outline'] = manual_outline
                    
                    for ch in chapters:
                        subtopics = chapter_subtopics.get(ch, [])
                        st.session_state['chapters'][ch] = {
                            'subtopics': subtopics, 
                            'subtopic_data': {
                                st_name: {'questions': [], 'answers': [], 'content': ''} 
                                for st_name in subtopics
                            }
                        }
                    
                    trigger_auto_save()
                    total_subtopics = sum(len(chapter_subtopics.get(ch, [])) for ch in chapters)
                    st.success(f"✅ {len(chapters)}개 챕터, {total_subtopics}개 소제목 저장됨!")
                    st.rerun()
    
    with col2:
        st.markdown("### 📋 현재 목차 관리")
        
        if st.session_state['outline']:
            for i, chapter in enumerate(st.session_state['outline']):
                subtopic_count = len(st.session_state['chapters'].get(chapter, {}).get('subtopics', []))
                
                with st.expander(f"**{chapter}** ({subtopic_count}개 소제목)", expanded=False):
                    # 챕터 편집
                    new_title = st.text_input(
                        "챕터 제목", 
                        value=chapter, 
                        key=f"edit_chapter_{i}"
                    )
                    
                    col_save, col_del = st.columns(2)
                    with col_save:
                        if new_title != chapter and new_title.strip():
                            if st.button("💾 저장", key=f"save_ch_{i}"):
                                st.session_state['outline'][i] = new_title
                                if chapter in st.session_state['chapters']:
                                    st.session_state['chapters'][new_title] = st.session_state['chapters'].pop(chapter)
                                trigger_auto_save()
                                st.rerun()
                    
                    with col_del:
                        if st.button("🗑️ 삭제", key=f"del_ch_{i}"):
                            st.session_state['outline'].pop(i)
                            if chapter in st.session_state['chapters']:
                                del st.session_state['chapters'][chapter]
                            trigger_auto_save()
                            st.rerun()
                    
                    # 소제목 표시
                    if chapter in st.session_state['chapters']:
                        subtopics = st.session_state['chapters'][chapter].get('subtopics', [])
                        for j, st_name in enumerate(subtopics):
                            st.caption(f"{j+1}. {st_name}")
            
            st.markdown("---")
            if st.button("➕ 새 챕터 추가"):
                new_ch_name = f"챕터{len(st.session_state['outline'])+1}: 새 챕터"
                st.session_state['outline'].append(new_ch_name)
                st.session_state['chapters'][new_ch_name] = {'subtopics': [], 'subtopic_data': {}}
                trigger_auto_save()
                st.rerun()
        else:
            st.info("왼쪽에서 목차를 생성하거나 직접 입력하세요")


# === TAB 4: 본문 작성 ===
with tabs[3]:
    st.markdown("## 본문 작성")
    
    if not st.session_state['outline']:
        st.warning("⚠️ 먼저 '③ 목차 설계' 탭에서 목차를 작성해주세요.")
        st.stop()
    
    chapter_list = st.session_state['outline']
    if not chapter_list:
        st.warning("⚠️ 챕터가 없습니다.")
        st.stop()
    
    # 챕터 선택
    selected_chapter = st.selectbox("📚 챕터 선택", chapter_list)
    
    if selected_chapter not in st.session_state['chapters']:
        st.session_state['chapters'][selected_chapter] = {
            'subtopics': [], 
            'subtopic_data': {}
        }
    
    chapter_data = st.session_state['chapters'][selected_chapter]
    
    if 'subtopics' not in chapter_data:
        chapter_data['subtopics'] = []
    if 'subtopic_data' not in chapter_data:
        chapter_data['subtopic_data'] = {}
    
    st.markdown("---")
    
    # 소제목 목록
    with st.expander(f"📋 '{selected_chapter}' 소제목 ({len(chapter_data.get('subtopics', []))}개)", expanded=True):
        if chapter_data.get('subtopics'):
            for j, st_name in enumerate(chapter_data['subtopics']):
                has_content = bool(chapter_data['subtopic_data'].get(st_name, {}).get('content', '').strip())
                status_icon = "✅" if has_content else "⬜"
                
                col1, col2 = st.columns([10, 1])
                with col1:
                    st.write(f"{status_icon} {j+1}. {st_name}")
                with col2:
                    if st.button("🗑️", key=f"del_st_{j}", help="삭제"):
                        chapter_data['subtopics'].pop(j)
                        if st_name in chapter_data['subtopic_data']:
                            del chapter_data['subtopic_data'][st_name]
                        st.rerun()
            
            # 소제목 추가
            st.markdown("---")
            new_subtopic = st.text_input("새 소제목 추가", key=f"add_st_{selected_chapter}")
            if st.button("➕ 추가"):
                if new_subtopic.strip() and new_subtopic not in chapter_data['subtopics']:
                    chapter_data['subtopics'].append(new_subtopic)
                    chapter_data['subtopic_data'][new_subtopic] = {
                        'questions': [], 
                        'answers': [], 
                        'content': ''
                    }
                    st.rerun()
        else:
            st.info("소제목이 없습니다. 아래에서 추가하세요.")
    
    st.markdown("---")
    
    # 본문 작성
    if chapter_data['subtopics']:
        st.markdown("### ✍️ 본문 작성")
        
        selected_subtopic = st.selectbox(
            "작성할 소제목", 
            chapter_data['subtopics'],
            format_func=lambda x: f"{'✅' if chapter_data['subtopic_data'].get(x, {}).get('content') else '⬜'} {x}"
        )
        
        # 진행률
        completed = sum(1 for s in chapter_data['subtopics'] if chapter_data['subtopic_data'].get(s, {}).get('content'))
        total = len(chapter_data['subtopics'])
        st.progress(completed / total if total > 0 else 0)
        st.caption(f"진행: {completed}/{total} 완료")
        
        st.markdown("---")
        
        if selected_subtopic:
            if selected_subtopic not in chapter_data['subtopic_data']:
                chapter_data['subtopic_data'][selected_subtopic] = {
                    'questions': [], 
                    'answers': [], 
                    'content': ''
                }
            
            subtopic_data = chapter_data['subtopic_data'][selected_subtopic]
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown(f"### 🎤 인터뷰: {selected_subtopic}")
                
                if st.button("🎤 질문 생성하기"):
                    with st.spinner("질문 생성 중..."):
                        questions_text = generate_interview_questions(
                            selected_subtopic, 
                            selected_chapter, 
                            st.session_state['topic']
                        )
                        
                        questions = re.findall(r'Q\d+:\s*(.+)', questions_text)
                        if not questions:
                            questions = [q.strip() for q in questions_text.split('\n') if q.strip() and '?' in q][:3]
                        
                        subtopic_data['questions'] = questions
                        subtopic_data['answers'] = [''] * len(questions)
                        st.rerun()
                
                if subtopic_data['questions']:
                    for i, q in enumerate(subtopic_data['questions']):
                        st.markdown(f"**Q{i+1}.** {q}")
                        if i >= len(subtopic_data['answers']):
                            subtopic_data['answers'].append('')
                        
                        subtopic_data['answers'][i] = st.text_area(
                            f"A{i+1}", 
                            value=subtopic_data['answers'][i], 
                            key=f"answer_{selected_chapter}_{selected_subtopic}_{i}", 
                            height=80,
                            label_visibility="collapsed"
                        )
                else:
                    st.info("👆 '질문 생성하기' 버튼을 눌러 인터뷰를 시작하세요.")
            
            with col2:
                st.markdown(f"### 📝 본문: {selected_subtopic}")
                
                has_answers = subtopic_data.get('questions') and any(a.strip() for a in subtopic_data.get('answers', []))
                
                if has_answers:
                    if st.button("✨ 본문 생성하기"):
                        with st.spinner("집필 중... (30초~1분)"):
                            content = generate_subtopic_content(
                                selected_subtopic, 
                                selected_chapter, 
                                subtopic_data['questions'], 
                                subtopic_data['answers'], 
                                st.session_state['topic'], 
                                st.session_state['target_persona']
                            )
                            
                            chapter_data['subtopic_data'][selected_subtopic]['content'] = content
                            trigger_auto_save()
                            st.rerun()
                else:
                    st.info("👈 먼저 인터뷰 질문에 답변해주세요.")
                
                # 본문 편집
                content_key = f"content_{selected_chapter}_{selected_subtopic}"
                if content_key not in st.session_state:
                    st.session_state[content_key] = chapter_data['subtopic_data'][selected_subtopic].get('content', '')
                
                edited_content = st.text_area(
                    "본문 내용", 
                    value=st.session_state[content_key],
                    height=400, 
                    key=f"edit_{content_key}",
                    label_visibility="collapsed"
                )
                
                # 본문 저장
                chapter_data['subtopic_data'][selected_subtopic]['content'] = edited_content
                st.session_state[content_key] = edited_content
                
                if edited_content:
                    char_count = calculate_char_count(edited_content)
                    st.caption(f"📊 {char_count:,}자")
    else:
        st.warning("⚠️ 이 챕터에 소제목이 없습니다.")


# === TAB 5: 문체 다듬기 ===
with tabs[4]:
    st.markdown("## 문체 다듬기 & 품질 검사")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 문체 다듬기")
        
        # 콘텐츠 선택
        content_options = []
        for ch in st.session_state['outline']:
            if ch in st.session_state['chapters']:
                ch_data = st.session_state['chapters'][ch]
                if 'subtopic_data' in ch_data:
                    for st_name, st_data in ch_data['subtopic_data'].items():
                        if st_data.get('content'):
                            content_options.append(f"{ch} > {st_name}")
        
        if content_options:
            selected_content = st.selectbox("다듬을 콘텐츠", content_options)
            style = st.selectbox("목표 스타일", ["친근한", "전문적", "직설적", "스토리텔링"])
            
            if st.button("✨ 문체 다듬기"):
                if selected_content:
                    parts = selected_content.split(" > ")
                    if len(parts) == 2:
                        ch, st_name = parts
                        content_to_refine = st.session_state['chapters'][ch]['subtopic_data'][st_name]['content']
                        
                        with st.spinner("다듬는 중..."):
                            refined = refine_content(content_to_refine, style)
                            st.session_state['refined_content'] = refined
            
            if st.session_state.get('refined_content'):
                st.text_area("다듬어진 본문", value=st.session_state['refined_content'], height=400)
                
                if st.button("원본에 적용"):
                    if selected_content:
                        parts = selected_content.split(" > ")
                        if len(parts) == 2:
                            ch, st_name = parts
                            st.session_state['chapters'][ch]['subtopic_data'][st_name]['content'] = st.session_state['refined_content']
                            trigger_auto_save()
                            st.success("적용됨!")
                            st.rerun()
        else:
            st.info("💡 먼저 본문을 작성해주세요.")
    
    with col2:
        st.markdown("### 품질 검사")
        
        if content_options:
            if st.button("🔍 베스트셀러 체크"):
                if selected_content:
                    parts = selected_content.split(" > ")
                    if len(parts) == 2:
                        ch, st_name = parts
                        content_to_check = st.session_state['chapters'][ch]['subtopic_data'][st_name]['content']
                        
                        with st.spinner("분석 중..."):
                            quality_result = check_quality(content_to_check)
                            st.session_state['quality_result'] = quality_result
            
            if st.session_state.get('quality_result'):
                st.info(st.session_state['quality_result'])


# === TAB 6: 최종 출력 ===
with tabs[5]:
    st.markdown("## 최종 출력 & 다운로드")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown("### 전자책 다운로드")
        
        book_title = st.text_input(
            "전자책 제목", 
            value=st.session_state.get('book_title', ''), 
            key="final_title"
        )
        subtitle = st.text_input(
            "부제", 
            value=st.session_state.get('subtitle', ''), 
            key="final_subtitle"
        )
        
        st.session_state['book_title'] = book_title
        st.session_state['subtitle'] = subtitle
        
        # 전체 책 내용 생성
        full_book_txt = ""
        full_book_html = ""
        
        if book_title:
            full_book_txt += f"{book_title}\n"
            full_book_html += f"<h1>{book_title}</h1>\n"
        if subtitle:
            full_book_txt += f"{subtitle}\n"
            full_book_html += f"<p style='color: #666;'>{subtitle}</p>\n"
        
        full_book_txt += "\n" + "="*50 + "\n\n"
        full_book_html += "<hr>\n"
        
        for chapter in st.session_state['outline']:
            if chapter in st.session_state['chapters']:
                ch_data = st.session_state['chapters'][chapter]
                if 'subtopic_data' in ch_data:
                    chapter_has_content = any(
                        ch_data['subtopic_data'].get(st_name, {}).get('content') 
                        for st_name in ch_data.get('subtopics', [])
                    )
                    
                    if chapter_has_content:
                        full_book_txt += f"\n{chapter}\n" + "-"*40 + "\n\n"
                        full_book_html += f"<h2>{chapter}</h2>\n"
                        
                        for st_name in ch_data.get('subtopics', []):
                            st_data = ch_data['subtopic_data'].get(st_name, {})
                            if st_data.get('content'):
                                full_book_txt += f"\n{st_name}\n\n{st_data['content']}\n\n"
                                full_book_html += f"<h3>{st_name}</h3>\n"
                                
                                for para in st_data['content'].split('\n\n'):
                                    if para.strip():
                                        full_book_html += f"<p>{para.strip()}</p>\n"
        
        # HTML 완성
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>{book_title or '전자책'}</title>
    <style>
        body {{ 
            font-family: 'Pretendard', sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 40px 20px; 
            line-height: 1.8; 
        }}
        h1 {{ font-size: 32px; margin-bottom: 10px; }}
        h2 {{ font-size: 24px; margin-top: 50px; }}
        h3 {{ font-size: 18px; margin-top: 30px; }}
        p {{ font-size: 16px; margin: 16px 0; }}
    </style>
</head>
<body>{full_book_html}</body>
</html>"""
        
        # 다운로드 버튼
        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            st.download_button(
                "📄 TXT 다운로드", 
                full_book_txt, 
                file_name=f"{book_title or 'ebook'}_{datetime.now().strftime('%Y%m%d')}.txt", 
                mime="text/plain", 
                use_container_width=True
            )
        
        with col_dl2:
            st.download_button(
                "🌐 HTML 다운로드", 
                html_content, 
                file_name=f"{book_title or 'ebook'}_{datetime.now().strftime('%Y%m%d')}.html", 
                mime="text/html", 
                use_container_width=True
            )
        
        # RTF 다운로드
        rtf_content = "{\\rtf1\\ansi\\ansicpg949\\deff0\n{\\fonttbl{\\f0\\fnil 맑은 고딕;}}\n\\f0\\fs24\n"
        rtf_content += escape_rtf_unicode(book_title or '') + "\\par\n"
        rtf_content += escape_rtf_unicode(subtitle or '') + "\\par\\par\n"
        
        for chapter in st.session_state['outline']:
            if chapter in st.session_state['chapters']:
                ch_data = st.session_state['chapters'][chapter]
                if 'subtopic_data' in ch_data:
                    chapter_has_content = any(
                        ch_data['subtopic_data'].get(st_name, {}).get('content') 
                        for st_name in ch_data.get('subtopics', [])
                    )
                    
                    if chapter_has_content:
                        rtf_content += "\\par\\b " + escape_rtf_unicode(chapter) + "\\b0\\par\\par\n"
                        
                        for st_name in ch_data.get('subtopics', []):
                            st_data = ch_data['subtopic_data'].get(st_name, {})
                            if st_data.get('content'):
                                rtf_content += "\\b " + escape_rtf_unicode(st_name) + "\\b0\\par\n"
                                rtf_content += escape_rtf_unicode(st_data['content']) + "\\par\\par\n"
        
        rtf_content += "}"
        
        st.download_button(
            "📗 RTF 다운로드", 
            rtf_content.encode('utf-8'), 
            file_name=f"{book_title or 'ebook'}_{datetime.now().strftime('%Y%m%d')}.rtf", 
            mime="application/rtf", 
            use_container_width=True
        )
        
        # 통계
        st.markdown("---")
        st.markdown("### 📖 전체 통계")
        
        pure_content = get_all_content_text()
        if pure_content:
            total_chars = calculate_char_count(pure_content)
            content_count = sum(
                1 for ch in st.session_state['chapters'].values() 
                for st_data in ch.get('subtopic_data', {}).values() 
                if st_data.get('content')
            )
            
            st.success(f"✅ 총 {content_count}개 소제목 | {total_chars:,}자 | 약 {total_chars//500}페이지")
        else:
            st.info("💡 아직 작성된 본문이 없습니다.")
    
    with col2:
        st.markdown("### 마케팅 카피")
        
        if st.button("✨ 카피 생성하기"):
            with st.spinner("생성 중..."):
                marketing = generate_marketing_copy(
                    st.session_state.get('book_title', st.session_state['topic']), 
                    st.session_state.get('subtitle', ''), 
                    st.session_state['topic'], 
                    st.session_state['target_persona']
                )
                st.session_state['marketing_copy'] = marketing
        
        if st.session_state.get('marketing_copy'):
            st.info(st.session_state['marketing_copy'])


# --- 푸터 ---
st.markdown("""
<div style='text-align: center; padding: 60px 20px; margin-top: 80px; border-top: 1px solid rgba(255, 215, 0, 0.15);'>
    <span style='color: rgba(255, 255, 255, 0.4); font-size: 14px;'>전자책 작성 프로그램 — </span>
    <span style='color: #FFD700; font-weight: 700;'>남현우 작가</span>
</div>
""", unsafe_allow_html=True)
