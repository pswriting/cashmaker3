import streamlit as st
import google.generativeai as genai
import re
import json
from datetime import datetime
from pathlib import Path

# ==========================================
# 🎯 페이지 설정 (반드시 첫 번째!)
# ==========================================
st.set_page_config(
    page_title="CASHMAKER 전자책 프로그램",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🎨 프리미엄 CSS (안정화 버전)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800;900&display=swap');
    
    /* 애니메이션 */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(255, 215, 0, 0.3); }
        50% { box-shadow: 0 0 40px rgba(255, 215, 0, 0.6); }
    }
    
    * { 
        font-family: 'Pretendard', -apple-system, sans-serif !important; 
    }
    
    /* 다크 배경 */
    .stApp { 
        background: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%) !important;
    }
    
    /* 메인 컨테이너 */
    .main .block-container { 
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 215, 0, 0.1) !important;
        border-radius: 24px !important;
        padding: 2rem 3rem !important; 
        max-width: 1400px !important;
        animation: fadeIn 0.6s ease-out;
    }
    
    /* 사이드바 */
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 100%) !important;
        border-right: 1px solid rgba(255, 215, 0, 0.15) !important;
    }
    
    [data-testid="stSidebar"] * { 
        color: #e0e0e0 !important; 
    }
    
    /* 프로그레스 바 */
    [data-testid="stSidebar"] .stProgress > div > div > div > div { 
        background: linear-gradient(90deg, #FFD700, #FFA500) !important;
        border-radius: 10px !important; 
    }
    
    /* 텍스트 */
    .stMarkdown, .stText, p, span, label, li { 
        color: #e0e0e0 !important; 
        line-height: 1.7 !important;
    }
    
    /* 헤딩 */
    h1 { 
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FFD700 100%) !important;
        background-size: 200% auto !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        font-weight: 900 !important; 
        font-size: 2.8rem !important;
        animation: shimmer 3s linear infinite;
    }
    
    h2 { 
        color: #FFD700 !important; 
        font-weight: 700 !important; 
        font-size: 1.8rem !important;
        border-bottom: 2px solid rgba(255, 215, 0, 0.3) !important;
        padding-bottom: 0.5rem !important;
    }
    
    h3 { 
        color: #FFA500 !important; 
        font-weight: 600 !important; 
    }
    
    /* 탭 */
    .stTabs [data-baseweb="tab-list"] { 
        background: rgba(255, 255, 255, 0.02) !important;
        border-radius: 12px !important;
        padding: 8px !important;
        gap: 4px !important;
    }
    
    .stTabs [data-baseweb="tab"] { 
        background: transparent !important;
        color: #888 !important;
        border-radius: 8px !important;
        padding: 12px 20px !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover { 
        color: #FFD700 !important;
        background: rgba(255, 215, 0, 0.1) !important;
    }
    
    .stTabs [aria-selected="true"] { 
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.2), rgba(255, 165, 0, 0.2)) !important;
        color: #FFD700 !important;
        font-weight: 700 !important;
    }
    
    /* 버튼 */
    .stButton > button { 
        width: 100% !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%) !important;
        color: #000 !important;
        border: none !important;
        padding: 16px 32px !important;
        box-shadow: 0 4px 20px rgba(255, 215, 0, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover { 
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(255, 215, 0, 0.5) !important;
    }
    
    .stButton > button * { 
        color: #000 !important; 
    }
    
    /* 다운로드 버튼 */
    .stDownloadButton > button { 
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%) !important;
        color: #fff !important;
    }
    
    .stDownloadButton > button * { 
        color: #fff !important; 
    }
    
    /* 입력 필드 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea { 
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 215, 0, 0.2) !important;
        border-radius: 12px !important;
        color: #e0e0e0 !important;
        padding: 14px 16px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus { 
        border-color: #FFD700 !important;
        box-shadow: 0 0 0 2px rgba(255, 215, 0, 0.2) !important;
    }
    
    /* 셀렉트박스 */
    .stSelectbox > div > div { 
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 215, 0, 0.2) !important;
        border-radius: 12px !important;
    }
    
    /* 알림 */
    .stSuccess { 
        background: rgba(76, 175, 80, 0.1) !important;
        border: 1px solid rgba(76, 175, 80, 0.3) !important;
        border-radius: 12px !important;
    }
    
    .stWarning { 
        background: rgba(255, 152, 0, 0.1) !important;
        border: 1px solid rgba(255, 152, 0, 0.3) !important;
        border-radius: 12px !important;
    }
    
    .stError { 
        background: rgba(244, 67, 54, 0.1) !important;
        border: 1px solid rgba(244, 67, 54, 0.3) !important;
        border-radius: 12px !important;
    }
    
    .stInfo { 
        background: rgba(33, 150, 243, 0.1) !important;
        border: 1px solid rgba(33, 150, 243, 0.3) !important;
        border-radius: 12px !important;
    }
    
    /* 익스팬더 */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 215, 0, 0.1) !important;
        border-radius: 12px !important;
    }
    
    /* 커스텀 클래스 */
    .hero-section { 
        text-align: center;
        padding: 60px 20px;
        margin-bottom: 40px;
    }
    
    .hero-title { 
        font-size: 56px;
        font-weight: 900;
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FFD700 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 16px;
        animation: shimmer 3s linear infinite;
    }
    
    .hero-subtitle { 
        font-size: 20px;
        color: #888;
    }
    
    .score-card { 
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.1), rgba(255, 165, 0, 0.05));
        border: 2px solid rgba(255, 215, 0, 0.3);
        border-radius: 24px;
        padding: 40px;
        text-align: center;
        animation: glow 3s ease-in-out infinite;
    }
    
    .score-number { 
        font-size: 80px;
        font-weight: 900;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
    }
    
    .info-card { 
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 215, 0, 0.15);
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
    }
    
    .info-card:hover {
        border-color: rgba(255, 215, 0, 0.3);
    }
    
    .title-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 215, 0, 0.15);
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
    }
    
    .main-title {
        font-size: 24px;
        font-weight: 800;
        color: #FFD700;
        margin-bottom: 8px;
    }
    
    .sub-title {
        font-size: 16px;
        color: #aaa;
        margin-bottom: 16px;
    }
    
    .section-label {
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 2px;
        color: #FFD700;
        text-transform: uppercase;
        opacity: 0.8;
    }
    
    .login-container { 
        max-width: 400px;
        margin: 100px auto;
        padding: 50px 40px;
        background: rgba(26, 26, 46, 0.8);
        border: 1px solid rgba(255, 215, 0, 0.2);
        border-radius: 24px;
        text-align: center;
    }
    
    .login-title { 
        font-size: 36px;
        font-weight: 900;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    
    .login-subtitle {
        font-size: 16px;
        color: #888;
    }
    
    .premium-footer {
        text-align: center;
        padding: 30px 20px;
        margin-top: 60px;
        border-top: 1px solid rgba(255, 215, 0, 0.1);
        color: #666;
    }
    
    .premium-footer-author {
        color: #FFD700;
        font-weight: 700;
    }
    
    .quick-action-box {
        background: rgba(255, 215, 0, 0.05);
        border-left: 4px solid #FFD700;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 16px 0;
    }
    
    .status-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
    }
    
    .status-excellent {
        background: rgba(76, 175, 80, 0.2);
        color: #4CAF50;
    }
    
    .status-good {
        background: rgba(255, 152, 0, 0.2);
        color: #FF9800;
    }
    
    .status-warning {
        background: rgba(244, 67, 54, 0.2);
        color: #F44336;
    }
    
    .empty-state {
        text-align: center;
        padding: 40px;
        color: #666;
    }
    
    .score-item {
        display: flex;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid rgba(255, 215, 0, 0.1);
    }
    
    .score-item-label { color: #ccc; }
    .score-item-value { color: #FFD700; font-weight: 700; font-size: 20px; }
    .score-item-reason { color: #888; font-size: 14px; margin-top: 4px; }
    
    .summary-box {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        padding: 20px;
        margin-top: 16px;
    }
    
    .card-number {
        font-size: 11px;
        letter-spacing: 2px;
        color: #FFD700;
        opacity: 0.7;
        margin-bottom: 12px;
    }
    
    .reason {
        font-size: 14px;
        color: #888;
        line-height: 1.6;
    }
    
    .info-card-title {
        color: #FFD700;
        font-weight: 700;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 프롬프트 정의
# ==========================================
GENIUS_PERSONA = """
# Role Definition
당신은 대한민국 상위 1% 전자책 매출을 기록하는 '초고수익 전자책 기획자'이자 '심리 설계자'입니다.
당신의 문장은 읽는 순간 독자의 뇌리에 박히며, 밤을 새워서라도 다음 내용을 읽게 만드는 마력이 있습니다.

# Writing Principles (천재 작가의 5원칙)
1. **[통찰의 재해석]**: 뻔한 이야기를 하지 않습니다. 현상을 비틀어 충격적인 진실을 드러냅니다.
2. **[리듬감 부여]**: 짧은 문장으로 때리고(Impact), 긴 문장으로 설득(Logic)합니다.
3. **[구체성의 마법]**: "열심히" 대신 "새벽 4시 기상"이라고 씁니다.
4. **[차가운 공감]**: 무조건적인 위로 대신, 독자의 게으름과 실패를 날카롭게 지적하고 해결책을 줍니다.
5. **[어려운 말 금지]**: 중학생도 이해 못 할 전문 용어는 쓰레기통에 버립니다.
"""

# ==========================================
# API 키 관리
# ==========================================
def get_config_path():
    return Path.home() / ".ebook_app_config.json"

def load_saved_api_key():
    config_path = get_config_path()
    try:
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f).get('api_key', '')
    except:
        pass
    return ''

def save_api_key(api_key):
    try:
        config = {'api_key': api_key}
        with open(get_config_path(), 'w') as f:
            json.dump(config, f)
        return True
    except:
        return False

# ==========================================
# 비밀번호 인증
# ==========================================
CORRECT_PASSWORD = "cashmaker2024"

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
        if st.button("입장하기", use_container_width=True):
            if password_input == CORRECT_PASSWORD:
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다")
    st.stop()

# ==========================================
# 세션 초기화
# ==========================================
default_states = {
    'topic': '', 'target_persona': '', 'pain_points': '', 'one_line_concept': '',
    'outline': [], 'chapters': {}, 'book_title': '', 'subtitle': '',
    'topic_score': None, 'topic_verdict': None, 'score_details': None,
    'generated_titles': None, 'market_analysis': '', 'full_outline': ''
}
for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ==========================================
# 사이드바
# ==========================================
with st.sidebar:
    st.markdown("### 📊 Progress")
    progress_items = [
        bool(st.session_state['topic']),
        bool(st.session_state['target_persona']),
        bool(st.session_state['outline']),
        len(st.session_state['chapters']) > 0,
    ]
    progress = sum(progress_items) / len(progress_items) * 100
    st.progress(progress / 100)
    st.caption(f"{progress:.0f}% 완료")
    
    st.markdown("---")
    st.markdown("### 📋 Info")
    if st.session_state['topic']:
        st.caption(f"주제: {st.session_state['topic'][:20]}...")
    if st.session_state['book_title']:
        st.caption(f"제목: {st.session_state['book_title'][:20]}...")
    if st.session_state['outline']:
        st.caption(f"목차: {len(st.session_state['outline'])}개 챕터")
    
    st.markdown("---")
    st.markdown("### 💾 저장/불러오기")
    
    save_data = {k: st.session_state.get(k, v) for k, v in default_states.items()}
    save_json = json.dumps(save_data, ensure_ascii=False, indent=2)
    file_name = re.sub(r'[^\w\s가-힣-]', '', st.session_state.get('book_title', '전자책') or '전자책')[:20]
    
    st.download_button(
        "📥 작업 저장하기", 
        save_json, 
        file_name=f"{file_name}_{datetime.now().strftime('%m%d_%H%M')}.json",
        mime="application/json",
        use_container_width=True
    )
    
    uploaded_file = st.file_uploader("📤 작업 불러오기", type=['json'], label_visibility="collapsed")
    if uploaded_file:
        try:
            loaded_data = json.loads(uploaded_file.read().decode('utf-8'))
            if st.button("불러오기 적용", use_container_width=True):
                for key in default_states.keys():
                    if key in loaded_data:
                        st.session_state[key] = loaded_data[key]
                st.success("불러오기 완료!")
                st.rerun()
        except Exception as e:
            st.error(f"파일 오류: {e}")
    
    st.markdown("---")
    st.markdown("### 🔑 API 설정")
    
    if 'api_key' not in st.session_state:
        st.session_state['api_key'] = load_saved_api_key()
    
    api_key_input = st.text_input(
        "Gemini API 키",
        value=st.session_state['api_key'],
        type="password",
        placeholder="AIza..."
    )
    
    if api_key_input != st.session_state['api_key']:
        st.session_state['api_key'] = api_key_input
        save_api_key(api_key_input)
    
    if st.session_state.get('api_key'):
        st.caption("✅ API 키 입력됨")
    else:
        st.caption("⚠️ API 키를 입력하세요")
    
    with st.expander("API 키 발급 방법"):
        st.markdown("""
        1. [Google AI Studio](https://aistudio.google.com/apikey) 접속
        2. Google 계정으로 로그인
        3. "API 키 만들기" 클릭
        4. 생성된 키 복사 후 위에 붙여넣기
        """)

# ==========================================
# 헬퍼 함수들
# ==========================================
def get_api_key():
    return st.session_state.get('api_key', '')

def ask_ai(system_role, prompt, temperature=0.7):
    api_key = get_api_key()
    if not api_key:
        return "⚠️ API 키를 먼저 입력해주세요."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        config = genai.types.GenerationConfig(temperature=temperature, max_output_tokens=4000)
        response = model.generate_content(
            GENIUS_PERSONA + f"\n\n현재 역할: {system_role}\n\n" + prompt,
            generation_config=config
        )
        return response.text
    except Exception as e:
        return f"오류 발생: {str(e)}"

def calculate_char_count(text):
    return len(text.replace('\n', '').replace(' ', '')) if text else 0

def get_all_content_text():
    content = ""
    for ch in st.session_state.get('outline', []):
        if ch in st.session_state.get('chapters', {}):
            ch_data = st.session_state['chapters'][ch]
            for st_name in ch_data.get('subtopics', []):
                st_data = ch_data.get('subtopic_data', {}).get(st_name, {})
                if st_data.get('content'):
                    content += st_data['content']
    return content

def sync_full_outline():
    outline_text = ""
    for ch in st.session_state.get('outline', []):
        outline_text += f"## {ch}\n"
        if ch in st.session_state.get('chapters', {}):
            for st_name in st.session_state['chapters'][ch].get('subtopics', []):
                outline_text += f"- {st_name}\n"
        outline_text += "\n"
    st.session_state['full_outline'] = outline_text.strip()

# ==========================================
# AI 함수들
# ==========================================
def analyze_topic_score(topic):
    prompt = f"""'{topic}' 주제의 전자책 적합도를 분석해주세요.

다음 5가지 항목을 각각 0~100점으로 채점하세요:
1. 시장성 (수요가 있는가?)
2. 수익성 (돈을 지불할 의향이 있는 주제인가?)
3. 차별화 가능성 (경쟁에서 이길 수 있는가?)
4. 작성 난이도 (전자책으로 만들기 쉬운가?)
5. 지속성 (오래 팔릴 수 있는가?)

반드시 아래 JSON 형식으로만 답변:
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
    return ask_ai("전자책 시장 분석가", prompt, 0.3)

def generate_titles_advanced(topic, persona, pain_points):
    prompt = f"""[분석 대상]
주제: {topic}
타겟: {persona}
타겟의 속마음: {pain_points}

베스트셀러급 전자책 제목 5개를 만들어주세요.

형식 (JSON만 출력):
{{
    "titles": [
        {{
            "title": "7자 이내 임팩트 제목",
            "subtitle": "15자 이내 보조 설명",
            "why_works": "왜 끌리는지"
        }}
    ]
}}"""
    return ask_ai("베스트셀러 작가", prompt, 0.9)

def generate_concept(topic, persona, pain_points):
    prompt = f"""주제: {topic}
타겟: {persona}
타겟의 고민: {pain_points}

"이 책 안 읽으면 손해"라는 느낌을 주는 한 줄 컨셉 5개를 만들어주세요.

출력 형식:
1. [한 줄 컨셉]
   → 왜 끌리는가
(5개)"""
    return ask_ai("카피라이터", prompt, 0.9)

def generate_outline(topic, persona, pain_points):
    prompt = f"""[주제]: {topic}
[타겟]: {persona}
[타겟의 고민]: {pain_points}

베스트셀러급 전자책 목차를 만드세요.

출력 형식:
## PART 1. [충격적인 챕터 제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]

## PART 2. [반전 있는 챕터 제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]

(4개 파트, 각 3개 소제목)

금지: "~의 중요성", "~하는 방법", "기초", "입문" """
    return ask_ai("베스트셀러 편집자", prompt, 0.85)

def generate_subtopics(chapter_title, topic, persona, count=3):
    prompt = f"""[전자책 주제]: {topic}
[챕터 제목]: {chapter_title}
[타겟]: {persona}

이 챕터의 소제목 {count}개를 만들어주세요.

출력 형식:
1. [소제목]
2. [소제목]
3. [소제목]"""
    return ask_ai("편집자", prompt, 0.8)

def generate_interview_questions(subtopic_title, chapter_title, topic):
    prompt = f"""'{topic}' 전자책의 '{chapter_title}' 챕터 중 '{subtopic_title}' 소제목을 쓰기 위한 인터뷰 질문 3개를 만들어주세요.

형식:
Q1: [질문]
Q2: [질문]
Q3: [질문]"""
    return ask_ai("고스트라이터", prompt, 0.7)

def generate_subtopic_content(subtopic_title, chapter_title, questions, answers, topic, persona):
    qa_pairs = "\n".join([f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(zip(questions, answers)) if a.strip()])
    
    prompt = f"""[집필 정보]
주제: {topic}
챕터: {chapter_title}
소제목: {subtopic_title}
타겟: {persona}

[인터뷰 내용]
{qa_pairs}

위 인터뷰 내용을 바탕으로 '{subtopic_title}' 본문을 작성하세요.

규칙:
- 첫 문장은 뒤통수를 치듯 시작
- 합쇼체(~입니다, ~습니다) 사용
- 구체적 숫자와 사례 포함
- 1500자 이상
- AI 티 나는 표현 금지 ("따라서", "중요합니다" 반복 등)"""
    return ask_ai("베스트셀러 작가", prompt, 0.8)

def refine_content(content, style="친근한"):
    prompt = f"""다음 글을 다듬어주세요.

[원본]
{content}

[스타일]: {style}
[규칙]: 합쇼체 통일, AI 티 제거, 마크다운 제거

다듬어진 글만 출력하세요."""
    return ask_ai("에디터", prompt, 0.7)

def check_quality(content):
    prompt = f"""다음 글이 베스트셀러 수준인지 평가해주세요.

[글]
{content[:3000]}

[평가 기준] 각 10점
1. 첫 문장 임팩트
2. 몰입도
3. 공감력
4. 구체성
5. AI 티 없음

출력: 점수와 개선점"""
    return ask_ai("편집자", prompt, 0.6)

def generate_marketing_copy(title, subtitle, topic, persona):
    prompt = f"""[상품 정보]
제목: {title}
부제: {subtitle}
주제: {topic}
타겟: {persona}

다음을 만들어주세요:
1. 크몽 상품 제목 (40자 이내)
2. 상세페이지 헤드라인 3개
3. 구매 유도 문구 3개
4. 인스타그램 홍보 문구
5. 블로그 포스팅 제목 3개"""
    return ask_ai("마케터", prompt, 0.85)

# ==========================================
# 메인 UI
# ==========================================
st.markdown("""
<div class="hero-section">
    <div class="hero-title">CASHMAKER</div>
    <div class="hero-subtitle">전자책 작성 프로그램</div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["① 주제 선정", "② 타겟 & 컨셉", "③ 목차 설계", "④ 본문 작성", "⑤ 문체 다듬기", "⑥ 최종 출력"])

# === TAB 1: 주제 선정 ===
with tabs[0]:
    st.markdown("## 주제 선정 & 적합도 분석")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<p class="section-label">STEP 01</p>', unsafe_allow_html=True)
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
        
        st.markdown("""
        <div class="info-card">
            <div class="info-card-title">💡 좋은 주제의 조건</div>
            <p>• 내가 직접 경험하고 성과를 낸 것</p>
            <p>• 사람들이 돈 주고 배우고 싶어하는 것</p>
            <p>• 구체적인 결과를 약속할 수 있는 것</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 적합도 분석하기", key="analyze_btn"):
            if not topic_input:
                st.error("주제를 입력해주세요.")
            else:
                with st.spinner("분석 중..."):
                    result = analyze_topic_score(topic_input)
                    try:
                        json_match = re.search(r'\{[\s\S]*\}', result)
                        if json_match:
                            data = json.loads(json_match.group())
                            st.session_state['topic_score'] = data.get('total_score', 0)
                            st.session_state['topic_verdict'] = data.get('verdict', '분석 실패')
                            st.session_state['score_details'] = data
                            st.rerun()
                    except:
                        st.error("분석 결과 파싱 오류")
    
    with col2:
        st.markdown('<p class="section-label">STEP 02</p>', unsafe_allow_html=True)
        st.markdown("### 분석 결과")
        
        if st.session_state['topic_score'] is not None:
            score = st.session_state['topic_score']
            verdict = st.session_state['topic_verdict']
            details = st.session_state['score_details']
            
            verdict_class = "status-excellent" if verdict == "적합" else ("status-good" if verdict == "보통" else "status-warning")
            
            st.markdown(f"""
            <div class="score-card">
                <div class="score-number">{score}</div>
                <div style="color: #888; margin-bottom: 12px;">종합 점수</div>
                <span class="status-badge {verdict_class}">{verdict}</span>
            </div>
            """, unsafe_allow_html=True)
            
            if details:
                st.markdown("#### 세부 점수")
                for name, key in [("시장성", "market"), ("수익성", "profit"), ("차별화", "differentiation"), ("작성 난이도", "difficulty"), ("지속성", "sustainability")]:
                    item = details.get(key, {})
                    st.markdown(f"""
                    <div class="score-item">
                        <span class="score-item-label">{name}</span>
                        <span class="score-item-value">{item.get('score', 0)}</span>
                    </div>
                    <p class="score-item-reason">{item.get('reason', '')}</p>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="summary-box">
                    <strong>종합 의견</strong><br>{details.get('summary', '')}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <p>📊 분석 결과가 여기에 표시됩니다</p>
                <p style="font-size: 14px;">주제를 입력하고 분석 버튼을 눌러주세요</p>
            </div>
            """, unsafe_allow_html=True)

# === TAB 2: 타겟 & 컨셉 ===
with tabs[1]:
    st.markdown("## 타겟 설정 & 제목 생성")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<p class="section-label">STEP 01</p>', unsafe_allow_html=True)
        st.markdown("### 타겟 정의")
        
        if not st.session_state['topic']:
            topic_here = st.text_input("주제", placeholder="예: 크몽으로 월 500만원 벌기", key="topic_tab2")
            if topic_here:
                st.session_state['topic'] = topic_here
        
        persona = st.text_area(
            "누가 이 책을 읽나요?",
            value=st.session_state['target_persona'],
            placeholder="예: 30대 직장인, 퇴근 후 부업으로 월 100만원 원하는 사람",
            height=100
        )
        st.session_state['target_persona'] = persona
        
        pain_points = st.text_area(
            "타겟의 가장 큰 고민은?",
            value=st.session_state['pain_points'],
            placeholder="예: 시간이 없다, 뭘 해야 할지 모르겠다",
            height=100
        )
        st.session_state['pain_points'] = pain_points
        
        st.markdown("---")
        st.markdown('<p class="section-label">STEP 02</p>', unsafe_allow_html=True)
        st.markdown("### 한 줄 컨셉")
        
        if st.button("✨ 컨셉 생성하기", key="concept_btn"):
            if st.session_state['topic'] and persona:
                with st.spinner("생성 중..."):
                    st.session_state['one_line_concept'] = generate_concept(
                        st.session_state['topic'], persona, pain_points
                    )
                    st.rerun()
            else:
                st.error("주제와 타겟을 먼저 입력해주세요.")
        
        if st.session_state.get('one_line_concept'):
            st.markdown(f"""
            <div class="info-card">
                {st.session_state['one_line_concept'].replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<p class="section-label">STEP 03</p>', unsafe_allow_html=True)
        st.markdown("### 제목 생성")
        
        if st.button("🎯 제목 생성하기", key="title_btn"):
            if st.session_state['topic']:
                with st.spinner("생성 중..."):
                    result = generate_titles_advanced(
                        st.session_state['topic'],
                        st.session_state['target_persona'],
                        st.session_state['pain_points']
                    )
                    try:
                        json_match = re.search(r'\{[\s\S]*\}', result)
                        if json_match:
                            st.session_state['generated_titles'] = json.loads(json_match.group())
                            st.rerun()
                    except:
                        st.markdown(result)
            else:
                st.error("주제를 먼저 입력해주세요.")
        
        if st.session_state.get('generated_titles'):
            titles = st.session_state['generated_titles'].get('titles', [])
            for i, t in enumerate(titles, 1):
                st.markdown(f"""
                <div class="title-card">
                    <div class="card-number">TITLE 0{i}</div>
                    <div class="main-title">{t.get('title', '')}</div>
                    <div class="sub-title">{t.get('subtitle', '')}</div>
                    <div class="reason">{t.get('why_works', '')}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown('<p class="section-label">STEP 04</p>', unsafe_allow_html=True)
        st.markdown("### 최종 선택")
        
        st.session_state['book_title'] = st.text_input(
            "제목",
            value=st.session_state['book_title'],
            placeholder="최종 제목 입력"
        )
        st.session_state['subtitle'] = st.text_input(
            "부제",
            value=st.session_state['subtitle'],
            placeholder="부제 입력"
        )

# === TAB 3: 목차 설계 ===
with tabs[2]:
    st.markdown("## 목차 설계")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<p class="section-label">목차 생성</p>', unsafe_allow_html=True)
        st.markdown("### 자동 목차 생성")
        
        if not st.session_state['topic']:
            st.warning("💡 주제를 먼저 입력해주세요")
            topic_here = st.text_input("주제", placeholder="예: 크몽으로 월 500만원 벌기", key="topic_tab3")
            if topic_here:
                st.session_state['topic'] = topic_here
        
        if st.button("🚀 목차 생성하기", key="outline_btn"):
            if st.session_state['topic']:
                with st.spinner("설계 중..."):
                    result = generate_outline(
                        st.session_state['topic'],
                        st.session_state['target_persona'],
                        st.session_state['pain_points']
                    )
                    
                    chapters = []
                    chapter_subtopics = {}
                    current_chapter = None
                    
                    for line in result.split('\n'):
                        line = line.strip()
                        if not line:
                            continue
                        if line.startswith('##') or 'PART' in line.upper():
                            chapter_name = re.sub(r'^##\s*', '', line).strip()
                            chapter_name = re.sub(r'\*\*(.+?)\*\*', r'\1', chapter_name)
                            if chapter_name:
                                current_chapter = chapter_name
                                chapters.append(current_chapter)
                                chapter_subtopics[current_chapter] = []
                        elif current_chapter and line.startswith('-'):
                            subtopic = line.lstrip('- ').strip()
                            subtopic = re.sub(r'\*\*(.+?)\*\*', r'\1', subtopic)
                            if subtopic:
                                chapter_subtopics[current_chapter].append(subtopic)
                    
                    if chapters:
                        st.session_state['outline'] = chapters
                        for ch in chapters:
                            subtopics = chapter_subtopics.get(ch, [])
                            st.session_state['chapters'][ch] = {
                                'subtopics': subtopics,
                                'subtopic_data': {s: {'questions': [], 'answers': [], 'content': ''} for s in subtopics}
                            }
                        sync_full_outline()
                        st.success(f"✅ {len(chapters)}개 챕터 생성됨!")
                        st.rerun()
            else:
                st.error("주제를 먼저 입력해주세요.")
        
        if st.session_state.get('full_outline'):
            st.markdown("**📋 현재 목차**")
            st.code(st.session_state['full_outline'], language=None)
    
    with col2:
        st.markdown('<p class="section-label">목차 관리</p>', unsafe_allow_html=True)
        st.markdown("### 현재 목차")
        
        if st.session_state['outline']:
            for i, chapter in enumerate(st.session_state['outline']):
                subtopics = st.session_state['chapters'].get(chapter, {}).get('subtopics', [])
                with st.expander(f"**{chapter}** ({len(subtopics)}개)", expanded=False):
                    for j, st_name in enumerate(subtopics):
                        st.write(f"  {j+1}. {st_name}")
            
            if st.button("➕ 새 챕터 추가", key="add_chapter"):
                new_name = f"챕터{len(st.session_state['outline'])+1}: 새 챕터"
                st.session_state['outline'].append(new_name)
                st.session_state['chapters'][new_name] = {'subtopics': [], 'subtopic_data': {}}
                sync_full_outline()
                st.rerun()
        else:
            st.markdown("""
            <div class="empty-state">
                <p>📝 목차가 없습니다</p>
                <p style="font-size: 14px;">왼쪽에서 목차를 생성해주세요</p>
            </div>
            """, unsafe_allow_html=True)

# === TAB 4: 본문 작성 ===
with tabs[3]:
    st.markdown("## 본문 작성")
    
    if not st.session_state['outline']:
        st.warning("⚠️ 먼저 '③ 목차 설계' 탭에서 목차를 작성해주세요.")
        st.stop()
    
    selected_chapter = st.selectbox("📚 챕터 선택", st.session_state['outline'], key="chapter_select")
    
    if selected_chapter not in st.session_state['chapters']:
        st.session_state['chapters'][selected_chapter] = {'subtopics': [], 'subtopic_data': {}}
    
    chapter_data = st.session_state['chapters'][selected_chapter]
    
    st.markdown("---")
    
    if chapter_data.get('subtopics'):
        with st.expander(f"📋 소제목 ({len(chapter_data['subtopics'])}개)", expanded=True):
            for j, st_name in enumerate(chapter_data['subtopics']):
                has_content = bool(chapter_data.get('subtopic_data', {}).get(st_name, {}).get('content'))
                icon = "✅" if has_content else "⬜"
                st.write(f"{icon} {j+1}. {st_name}")
        
        st.markdown("### ✍️ 본문 작성")
        
        selected_subtopic = st.selectbox(
            "작성할 소제목",
            chapter_data['subtopics'],
            format_func=lambda x: f"{'✅' if chapter_data.get('subtopic_data', {}).get(x, {}).get('content') else '⬜'} {x}"
        )
        
        if selected_subtopic:
            if selected_subtopic not in chapter_data.get('subtopic_data', {}):
                chapter_data['subtopic_data'][selected_subtopic] = {'questions': [], 'answers': [], 'content': ''}
            
            st_data = chapter_data['subtopic_data'][selected_subtopic]
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### 🎤 인터뷰")
                
                if st.button("질문 생성하기", key="gen_q"):
                    with st.spinner("생성 중..."):
                        result = generate_interview_questions(selected_subtopic, selected_chapter, st.session_state['topic'])
                        questions = re.findall(r'Q\d+:\s*(.+)', result)
                        if not questions:
                            questions = [q.strip() for q in result.split('\n') if '?' in q][:3]
                        st_data['questions'] = questions
                        st_data['answers'] = [''] * len(questions)
                        st.rerun()
                
                if st_data.get('questions'):
                    for i, q in enumerate(st_data['questions']):
                        st.markdown(f"**Q{i+1}.** {q}")
                        if i >= len(st_data.get('answers', [])):
                            st_data['answers'].append('')
                        st_data['answers'][i] = st.text_area(
                            f"A{i+1}",
                            value=st_data['answers'][i],
                            height=80,
                            key=f"ans_{selected_chapter}_{selected_subtopic}_{i}",
                            label_visibility="collapsed"
                        )
            
            with col2:
                st.markdown("#### 📝 본문")
                
                has_answers = st_data.get('questions') and any(a.strip() for a in st_data.get('answers', []))
                
                if has_answers:
                    if st.button("✨ 본문 생성하기", key="gen_content"):
                        with st.spinner("집필 중..."):
                            content = generate_subtopic_content(
                                selected_subtopic, selected_chapter,
                                st_data['questions'], st_data['answers'],
                                st.session_state['topic'], st.session_state['target_persona']
                            )
                            st_data['content'] = content
                            st.rerun()
                else:
                    st.info("👈 먼저 인터뷰 질문에 답변해주세요.")
                
                content = st.text_area(
                    "본문 내용",
                    value=st_data.get('content', ''),
                    height=400,
                    key=f"content_{selected_chapter}_{selected_subtopic}",
                    label_visibility="collapsed"
                )
                st_data['content'] = content
                
                if content:
                    st.caption(f"📊 {calculate_char_count(content):,}자")
    else:
        st.warning("소제목이 없습니다. 목차 탭에서 추가해주세요.")

# === TAB 5: 문체 다듬기 ===
with tabs[4]:
    st.markdown("## 문체 다듬기 & 품질 검사")
    
    content_options = []
    for ch in st.session_state['outline']:
        if ch in st.session_state['chapters']:
            for st_name, st_data in st.session_state['chapters'][ch].get('subtopic_data', {}).items():
                if st_data.get('content'):
                    content_options.append(f"{ch} > {st_name}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 문체 다듬기")
        
        if content_options:
            selected = st.selectbox("다듬을 콘텐츠", content_options, key="refine_select")
            style = st.selectbox("스타일", ["친근한", "전문적", "직설적", "스토리텔링"])
            
            if st.button("✨ 다듬기", key="refine_btn"):
                parts = selected.split(" > ")
                if len(parts) == 2:
                    content = st.session_state['chapters'][parts[0]]['subtopic_data'][parts[1]]['content']
                    with st.spinner("다듬는 중..."):
                        st.session_state['refined_content'] = refine_content(content, style)
                        st.rerun()
            
            if st.session_state.get('refined_content'):
                st.text_area("다듬어진 본문", st.session_state['refined_content'], height=400)
                if st.button("원본에 적용"):
                    parts = selected.split(" > ")
                    if len(parts) == 2:
                        st.session_state['chapters'][parts[0]]['subtopic_data'][parts[1]]['content'] = st.session_state['refined_content']
                        st.success("적용됨!")
                        st.rerun()
        else:
            st.info("먼저 본문을 작성해주세요.")
    
    with col2:
        st.markdown("### 품질 검사")
        
        if content_options:
            if st.button("🔍 베스트셀러 체크", key="quality_btn"):
                parts = selected.split(" > ")
                if len(parts) == 2:
                    content = st.session_state['chapters'][parts[0]]['subtopic_data'][parts[1]]['content']
                    with st.spinner("분석 중..."):
                        st.session_state['quality_result'] = check_quality(content)
                        st.rerun()
            
            if st.session_state.get('quality_result'):
                st.markdown(f"""
                <div class="info-card">
                    {st.session_state['quality_result'].replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)

# === TAB 6: 최종 출력 ===
with tabs[5]:
    st.markdown("## 최종 출력 & 마케팅")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown("### 📥 다운로드")
        
        book_title = st.text_input("전자책 제목", st.session_state.get('book_title', ''), key="final_title")
        subtitle = st.text_input("부제", st.session_state.get('subtitle', ''), key="final_subtitle")
        st.session_state['book_title'] = book_title
        st.session_state['subtitle'] = subtitle
        
        # 전체 책 내용 생성
        full_txt = f"{book_title}\n{subtitle}\n\n{'='*50}\n\n"
        full_html = f"<h1>{book_title}</h1><p>{subtitle}</p><hr>"
        
        for chapter in st.session_state['outline']:
            ch_data = st.session_state['chapters'].get(chapter, {})
            has_content = any(ch_data.get('subtopic_data', {}).get(s, {}).get('content') for s in ch_data.get('subtopics', []))
            if has_content:
                full_txt += f"\n{chapter}\n{'-'*40}\n"
                full_html += f"<h2>{chapter}</h2>"
                for st_name in ch_data.get('subtopics', []):
                    content = ch_data.get('subtopic_data', {}).get(st_name, {}).get('content', '')
                    if content:
                        full_txt += f"\n{st_name}\n\n{content}\n\n"
                        full_html += f"<h3>{st_name}</h3><p>{content}</p>"
        
        html_doc = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{book_title}</title>
<style>body{{font-family:sans-serif;max-width:800px;margin:0 auto;padding:40px;line-height:1.8;}}</style>
</head><body>{full_html}</body></html>"""
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button("📄 TXT", full_txt, f"{book_title or 'ebook'}.txt", "text/plain", use_container_width=True)
        with col_d2:
            st.download_button("🌐 HTML", html_doc, f"{book_title or 'ebook'}.html", "text/html", use_container_width=True)
        
        st.markdown("---")
        all_content = get_all_content_text()
        if all_content:
            chars = calculate_char_count(all_content)
            st.success(f"✅ 총 {chars:,}자 | 약 {chars//500}페이지")
    
    with col2:
        st.markdown("### 📣 마케팅 카피")
        
        if st.button("카피 생성하기", key="marketing_btn"):
            with st.spinner("생성 중..."):
                st.session_state['marketing_copy'] = generate_marketing_copy(
                    st.session_state.get('book_title', ''),
                    st.session_state.get('subtitle', ''),
                    st.session_state['topic'],
                    st.session_state['target_persona']
                )
                st.rerun()
        
        if st.session_state.get('marketing_copy'):
            st.markdown(f"""
            <div class="info-card">
                {st.session_state['marketing_copy'].replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)

# 푸터
st.markdown("""
<div class="premium-footer">
    전자책 작성 프로그램 — <span class="premium-footer-author">남현우 작가</span>
</div>
""", unsafe_allow_html=True)
