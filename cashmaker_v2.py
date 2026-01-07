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

# 3. AI에게 요청 (창의성을 위해 온도를 0.75로 설정)
    return ask_ai("베스트셀러 논픽션 작가", prompt, temperature=0.75)
    
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

# --- 페이지 설정 ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&display=swap');
    
    * { 
        font-family: 'Pretendard', -apple-system, sans-serif; 
        transition: all 0.3s ease;
    }
    
    /* 다크 배경 + 그라데이션 */
    .stApp { 
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    }
    
    .main .block-container { 
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 2.5rem 3rem; 
        max-width: 1200px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* 사이드바 - 글래스모피즘 */
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, rgba(26, 31, 58, 0.95) 0%, rgba(10, 14, 39, 0.95) 100%);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 215, 0, 0.2);
    }
    
    [data-testid="stSidebar"] * { 
        color: #e8e8e8 !important; 
    }
    
    /* 골드 프로그레스 바 */
    [data-testid="stSidebar"] .stProgress > div > div > div > div { 
        background: linear-gradient(90deg, #FFD700, #FFA500);
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
        border-radius: 10px; 
    }
    
    /* 텍스트 컬러 */
    .stMarkdown, .stText, p, span, label { 
        color: #e8e8e8 !important; 
        line-height: 1.7; 
    }
    
    /* 헤딩 - 그라데이션 텍스트 */
    h1 { 
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 800 !important; 
        font-size: 2.5rem !important; 
        letter-spacing: -1px;
        margin-bottom: 1rem !important;
        text-shadow: 0 0 30px rgba(255, 215, 0, 0.3);
    }
    
    h2 { 
        color: #FFD700 !important; 
        font-weight: 700 !important; 
        font-size: 1.6rem !important;
        margin-top: 2rem !important;
    }
    
    h3 { 
        color: #FFA500 !important; 
        font-weight: 600 !important; 
        font-size: 1.2rem !important;
    }
    
    /* 탭 - 네온 효과 */
    .stTabs [data-baseweb="tab-list"] { 
        background: rgba(255, 255, 255, 0.03);
        border-bottom: 2px solid rgba(255, 215, 0, 0.2);
        border-radius: 12px 12px 0 0;
        padding: 8px;
    }
    
    .stTabs [data-baseweb="tab"] { 
        background: transparent;
        color: #999 !important;
        border-radius: 8px;
        font-weight: 500;
        padding: 12px 20px;
        font-size: 14px;
    }
    
    .stTabs [data-baseweb="tab"]:hover { 
        color: #FFD700 !important;
        background: rgba(255, 215, 0, 0.1);
    }
    
    .stTabs [aria-selected="true"] { 
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.2), rgba(255, 165, 0, 0.2)) !important;
        color: #FFD700 !important;
        font-weight: 700 !important;
        border: 1px solid rgba(255, 215, 0, 0.3) !important;
        box-shadow: 0 4px 20px rgba(255, 215, 0, 0.2);
    }
    
    /* 버튼 - 프리미엄 골드 */
    .stButton > button { 
        width: 100%;
        border-radius: 12px;
        font-weight: 600;
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%) !important;
        color: #000 !important;
        border: none !important;
        padding: 14px 32px;
        font-size: 15px;
        box-shadow: 0 4px 20px rgba(255, 215, 0, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover:before {
        left: 100%;
    }
    
    .stButton > button:hover { 
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(255, 215, 0, 0.6);
    }
    
    .stButton > button * { 
        color: #000 !important; 
        font-weight: 700;
    }
    
    /* 다운로드 버튼 - 블루 그라데이션 */
    .stDownloadButton > button { 
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%) !important;
        color: #fff !important;
        box-shadow: 0 4px 20px rgba(74, 144, 226, 0.4);
    }
    
    .stDownloadButton > button:hover {
        box-shadow: 0 8px 30px rgba(74, 144, 226, 0.6);
    }
    
    /* 입력 필드 - 다크 글래스 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea { 
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 215, 0, 0.2) !important;
        border-radius: 12px !important;
        color: #e8e8e8 !important;
        padding: 14px 16px !important;
        font-size: 15px !important;
        backdrop-filter: blur(10px);
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus { 
        border-color: #FFD700 !important;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.3) !important;
    }
    
    /* 알림 박스 - 글로우 효과 */
    .stSuccess { 
        background: rgba(76, 175, 80, 0.1) !important;
        border: 1px solid rgba(76, 175, 80, 0.3) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 20px rgba(76, 175, 80, 0.2);
    }
    
    .stSuccess p { 
        color: #4CAF50 !important; 
    }
    
    .stWarning { 
        background: rgba(255, 152, 0, 0.1) !important;
        border: 1px solid rgba(255, 152, 0, 0.3) !important;
        box-shadow: 0 0 20px rgba(255, 152, 0, 0.2);
    }
    
    .stError { 
        background: rgba(244, 67, 54, 0.1) !important;
        border: 1px solid rgba(244, 67, 54, 0.3) !important;
        box-shadow: 0 0 20px rgba(244, 67, 54, 0.2);
    }
    
    /* 스코어 카드 - 3D 효과 */
    .score-card { 
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.1), rgba(255, 165, 0, 0.1));
        border: 1px solid rgba(255, 215, 0, 0.3);
        border-radius: 24px;
        padding: 50px 40px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        position: relative;
    }
    
    .score-number { 
        font-size: 90px;
        font-weight: 800;
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
        margin-bottom: 8px;
        text-shadow: 0 0 50px rgba(255, 215, 0, 0.5);
    }
    
    /* 히어로 섹션 - 임팩트 강화 */
    .hero-section { 
        text-align: center;
        padding: 80px 20px;
        margin-bottom: 40px;
        position: relative;
    }
    
    .hero-title { 
        font-size: 56px;
        font-weight: 900;
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FFD700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 16px;
        letter-spacing: -2px;
        line-height: 1.1;
        font-family: 'Space Grotesk', sans-serif;
        animation: glow 3s ease-in-out infinite;
    }
    
    @keyframes glow {
        0%, 100% { filter: drop-shadow(0 0 20px rgba(255, 215, 0, 0.5)); }
        50% { filter: drop-shadow(0 0 40px rgba(255, 215, 0, 0.8)); }
    }
    
    .hero-subtitle { 
        font-size: 20px;
        color: #999;
        font-weight: 400;
    }
    
    /* 정보 카드 - 글래스 효과 */
    .info-card { 
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 215, 0, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    .info-card:hover {
        border-color: rgba(255, 215, 0, 0.4);
        box-shadow: 0 8px 30px rgba(255, 215, 0, 0.1);
        transform: translateY(-2px);
    }
    
    /* 로그인 화면 */
    .login-container { 
        max-width: 400px;
        margin: 100px auto;
        padding: 60px 40px;
        background: rgba(26, 31, 58, 0.6);
        border: 1px solid rgba(255, 215, 0, 0.3);
        border-radius: 24px;
        text-align: center;
        backdrop-filter: blur(20px);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    }
    
    .login-title { 
        font-size: 36px;
        font-weight: 800;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
        font-family: 'Space Grotesk', sans-serif;
    }
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
    'topic': '', 'target_persona': '', 'pain_points': '', 'one_line_concept': '',
    'outline': [], 'chapters': {}, 'current_step': 1, 'market_analysis': '',
    'book_title': '', 'subtitle': '', 'topic_score': None, 'topic_verdict': None,
    'score_details': None, 'generated_titles': None, 'outline_mode': 'ai',
}
for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- 사이드바 ---
with st.sidebar:
    st.markdown("### Progress")
    progress_items = [
        bool(st.session_state['topic']), bool(st.session_state['target_persona']),
        bool(st.session_state['outline']), len(st.session_state['chapters']) > 0,
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
    save_data = {
        'topic': st.session_state.get('topic', ''), 'target_persona': st.session_state.get('target_persona', ''),
        'pain_points': st.session_state.get('pain_points', ''), 'one_line_concept': st.session_state.get('one_line_concept', ''),
        'outline': st.session_state.get('outline', []), 'chapters': st.session_state.get('chapters', {}),
        'book_title': st.session_state.get('book_title', ''), 'subtitle': st.session_state.get('subtitle', ''),
        'market_analysis': st.session_state.get('market_analysis', ''), 'topic_score': st.session_state.get('topic_score'),
        'topic_verdict': st.session_state.get('topic_verdict'), 'score_details': st.session_state.get('score_details'),
        'generated_titles': st.session_state.get('generated_titles'),
    }
    save_json = json.dumps(save_data, ensure_ascii=False, indent=2)
    file_name = st.session_state.get('book_title', '전자책') or '전자책'
    file_name = re.sub(r'[^\w\s가-힣-]', '', file_name)[:20]
    st.download_button("📥 작업 저장하기", save_json, file_name=f"{file_name}_{datetime.now().strftime('%m%d_%H%M')}.json", mime="application/json", use_container_width=True)
    
    uploaded_file = st.file_uploader("📤 작업 불러오기", type=['json'], label_visibility="collapsed")
    if uploaded_file is not None:
        try:
            loaded_data = json.loads(uploaded_file.read().decode('utf-8'))
            if st.button("불러오기 적용", use_container_width=True):
                for key in ['topic', 'target_persona', 'pain_points', 'one_line_concept', 'outline', 'chapters', 'book_title', 'subtitle', 'market_analysis', 'topic_score', 'topic_verdict', 'score_details', 'generated_titles']:
                    if key in loaded_data:
                        st.session_state[key] = loaded_data[key]
                st.success("불러오기 완료!")
                st.rerun()
        except Exception as e:
            st.error(f"파일 오류: {e}")
    
    st.markdown("---")
    st.markdown("### API 설정")
    if 'api_key' not in st.session_state:
        saved_key = load_saved_api_key()
        st.session_state['api_key'] = saved_key
    
    api_key_input = st.text_input("Gemini API 키", value=st.session_state['api_key'], type="password", placeholder="AIza...", help="Google AI Studio에서 발급받은 API 키를 입력하세요")
    if api_key_input and api_key_input != st.session_state['api_key']:
        st.session_state['api_key'] = api_key_input
        if save_api_key(api_key_input):
            st.toast("✅ API 키가 저장되었습니다!", icon="💾")
    elif api_key_input:
        st.session_state['api_key'] = api_key_input
    
    with st.expander("API 키 발급 방법 (무료)"):
        st.markdown("""**2분이면 끝!**\n\n1. [Google AI Studio](https://aistudio.google.com/apikey) 접속\n2. Google 계정으로 로그인\n3. **"API 키 만들기"** 클릭\n4. 생성된 키 복사\n5. 위 입력창에 붙여넣기\n\n✅ 완전 무료 ✅ 신용카드 불필요 ✅ 분당 15회 요청 가능""")
    
    if not st.session_state.get('api_key'):
        st.caption("⚠️ API 키를 입력하세요")
    else:
        col_status, col_del = st.columns([3, 1])
        with col_status:
            st.caption("✅ API 키 입력됨 (자동 저장)")
        with col_del:
            if st.button("🗑️", key="del_api_key", help="API 키 삭제"):
                st.session_state['api_key'] = ''
                save_api_key('')
                st.rerun()


# ==========================================
# 헬퍼 함수들
# ==========================================
def get_api_key():
    return st.session_state.get('api_key', '')

def get_auto_save_data():
    return {
        'topic': st.session_state.get('topic', ''), 'target_persona': st.session_state.get('target_persona', ''),
        'pain_points': st.session_state.get('pain_points', ''), 'one_line_concept': st.session_state.get('one_line_concept', ''),
        'outline': st.session_state.get('outline', []), 'chapters': st.session_state.get('chapters', {}),
        'book_title': st.session_state.get('book_title', ''), 'subtitle': st.session_state.get('subtitle', ''),
        'market_analysis': st.session_state.get('market_analysis', ''), 'topic_score': st.session_state.get('topic_score'),
        'topic_verdict': st.session_state.get('topic_verdict'), 'score_details': st.session_state.get('score_details'),
        'generated_titles': st.session_state.get('generated_titles'), 'saved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
    api_key = get_api_key()
    if not api_key:
        return "⚠️ API 키를 먼저 입력해주세요."
    try:
        genai.configure(api_key=api_key)
        
        # 시스템 롤에 천재 작가 페르소나 결합
        final_system_instruction = GENIUS_PERSONA + "\n\n" + f"현재 당신의 구체적인 역할: {system_role}"
        
        # 모델 생성 (flash 모델이 속도와 창의성 밸런스가 좋음)
        ai_model = genai.GenerativeModel('models/gemini-2.0-flash')
        
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=4000
        )
        
        response = ai_model.generate_content(prompt, generation_config=generation_config)
        return response.text
    except Exception as e:
        return f"오류 발생: {str(e)}"

# ==========================================
# 🔥 핵심 개선: 목차 생성 함수 (프드프 스타일)
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

나쁜 예: "성공하는 습관"  
좋은 예: "새벽 5시 기상이 헛소리인 이유"

나쁜 예: "투자 시작하기"
좋은 예: "월급쟁이는 절대 부자가 될 수 없다"

[원칙 2] 소제목 = 호기심 폭발
- "이게 뭐야?" 싶은 궁금증 유발
- 구체적 숫자, 비유, 반전 활용
- 뻔한 조언 대신 날카로운 통찰

나쁜 예: "목표 설정하기"
좋은 예: "97%가 틀리는 목표 설정의 함정"

나쁜 예: "시간 관리 팁"
좋은 예: "하루 2시간으로 연봉 2배 만든 공식"

나쁜 예: "돈 모으는 방법"
좋은 예: "적금 들면 10년 뒤에도 가난한 이유"

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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚫 절대 금지 (이거 쓰면 0점)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- "~의 중요성", "~의 필요성"
- "~하는 방법", "~하는 법", "~하기"
- "효과적인 ~", "성공적인 ~", "올바른 ~"
- "이해하기", "알아보기", "살펴보기"
- "기초", "기본", "입문", "개론"
- "팁", "노하우", "비법", "전략"
- **굵은글씨**, 번호(1.1), 들여쓰기, 부연설명

목차만 출력하세요. 설명 없이."""
    return ask_ai("베스트셀러 편집자", prompt, temperature=0.85)


# ==========================================
# 🔥 소제목 생성 함수 추가
# ==========================================
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


# ==========================================
# 🔥 핵심 개선: 본문 생성 함수 (자청 스타일, 1500자+)
# ==========================================
def generate_subtopic_content(subtopic_title, chapter_title, questions, answers, topic, persona):
    qa_pairs = ""
    for i, (q, a) in enumerate(zip(questions, answers), 1):
        if a.strip():
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

[법칙 1] 첫 문장 = 뒤통수 한 방 🥊
- 첫 문장에서 독자의 뒤통수를 쳐라
- 상식을 뒤집거나, 충격적인 사실로 시작
- 좋은 예: "월급 230만원. 그게 제 전부였습니다."
- 좋은 예: "저는 3번 망했습니다. 그리고 4번째에 성공했습니다."
- 좋은 예: "솔직히 말씀드릴게요. 저도 처음엔 사기라고 생각했습니다."
- 나쁜 예: "오늘은 ~에 대해 이야기해보겠습니다." (❌ 절대 금지)

[법칙 2] 짧은 문장, 강한 임팩트 💥
- 한 문장 = 한 호흡 (15~25자)
- 중요한 문장은 더 짧게 (10자 이하)
- 좋은 예: "그날. 모든 게 바뀌었습니다."
- 좋은 예: "단 3개월. 인생이 달라졌습니다."

[법칙 3] 문단 구성 = 리듬감 🎵
- 한 문단 = 3~5문장
- 문단과 문단 사이에 빈 줄 1개
- 절대 한 문장씩 띄어쓰지 마세요!
- 관련된 내용은 같은 문단에 묶으세요

[법칙 4] 스토리 > 설명 📖
- "~하세요"보다 "저는 ~했습니다"
- 추상적 조언 대신 구체적 경험
- Before(실패) → 깨달음 → After(성공) 구조

[법칙 5] 숫자로 증명하라 🔢
- 모호한 표현 대신 구체적 숫자
- "열심히 했다" → "새벽 4시에 일어났습니다"
- "많이 벌었다" → "월 847만원이 들어왔습니다"
- "빠르게 성장" → "3개월 만에 4배"

[법칙 6] 감정을 건드려라 ❤️
- 당시 감정을 생생하게 묘사
- "무서웠습니다", "분했습니다", "눈물이 났습니다"
- 단, 과잉 감정 표현은 금지

[법칙 7] 대화체 활용 💬
- 혼잣말, 내면의 목소리 삽입
- "이게 되겠어?" "아, 이거였구나"
- 독자와 대화하는 느낌

[법칙 8] 반복과 강조 🔄
- 핵심 메시지는 표현을 바꿔 2~3번 강조
- 같은 말을 다른 방식으로

[법칙 9] 구체적 장면 묘사 🎬
- 시간, 장소, 상황을 영화처럼
- "2019년 3월 어느 날, 강남역 스타벅스에서"
- "새벽 3시, 불 꺼진 사무실에서"

[법칙 10] 독자 = 친구 👋
- "당신"이 아니라 마치 옆에 앉은 친구에게 말하듯
- 딱딱한 설명 대신 대화하듯

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 문체 규칙 (합쇼체 100%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
모든 문장 끝:
✓ ~입니다 / ~습니다 / ~했습니다 / ~됩니다
✓ ~죠 / ~거죠 / ~셨죠 / ~네요
✓ ~세요 / ~하세요

절대 금지 (반말):
✗ ~다 / ~했다 / ~이다 / ~였다 / ~된다
✗ ~라 / ~인 것이다

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚫 AI 티 나는 표현 절대 금지
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
다음 표현 사용 시 0점 처리:
- "실수 1:", "실수 2:", "해결책:" (나열 금지)
- "첫째,", "둘째,", "셋째," (번호 금지)
- "중요합니다", "핵심입니다", "필수적입니다" (반복 금지)
- "따라서", "그러므로", "결론적으로" (딱딱한 연결어 금지)
- "~라고 할 수 있습니다" (에둘러 말하기 금지)
- "많은 분들이", "대부분의 사람들이" (일반화 금지)
- "~하는 것이 좋습니다" (조언체 금지)
- **굵은글씨**, *기울임*, 1. 2. 3. 번호 (마크다운 금지)
- "저는," (주어 뒤 쉼표 금지)
- "포기하지 마세요", "도전해보세요" (뻔한 교훈 금지)

대신 이렇게:
- 자연스러운 문장 연결로 이야기 전개
- 구체적 사례와 숫자로 설명
- "저는 ~했습니다. 결과는 ~였습니다."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ 베스트셀러급 본문 예시
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"2019년 3월. 통장 잔고를 확인했습니다. 47만원. 월급날까지 2주. 저는 완전히 바닥이었습니다.

매일 새벽 6시에 일어나서 밤 11시까지 일했습니다. 주말도 없었습니다. 성실함으로 치면 상위 1%였을 겁니다. 그런데 통장엔 47만원. 뭔가 심각하게 잘못됐다는 걸 그때 처음 깨달았습니다.

'열심히 하면 성공한다'는 말. 그게 거짓말이라는 걸 알기까지 5년이 걸렸습니다. 저는 방향이 틀렸던 겁니다. 열심히 잘못된 방향으로 달린 거죠.

그날 밤, 저는 처음으로 '왜'라는 질문을 던졌습니다. 왜 열심히 해도 안 될까? 왜 월급은 늘 부족할까? 왜 10년차도 신입과 크게 다르지 않을까?

답을 찾는 데 6개월이 걸렸습니다. 그리고 깨달았습니다. 문제는 '얼마나'가 아니라 '무엇을'이었습니다. 뭘 하느냐가 얼마나 하느냐보다 100배 중요했습니다.

그 깨달음 이후 모든 게 달라졌습니다. 3개월 만에 첫 부수입 100만원. 6개월 만에 월급을 넘었습니다. 1년 후, 저는 퇴사했습니다."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📏 분량: 1500~2000자 (공백 포함)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

반드시 1500자 이상 작성하세요. 
독자가 "이 부분만 읽어도 돈값 한다"고 느끼게 깊이 있는 내용을 담으세요.

[미션]
'{subtopic_title}'의 본문만 작성하세요.
- 자청 스타일 10가지 법칙 적용
- 합쇼체 100% 유지
- AI 티 나는 표현 완전 배제
- 1500자 이상 작성
- 첫 문장부터 뒤통수 치기"""
    return ask_ai("베스트셀러 작가", prompt, temperature=0.8)


# ==========================================
# 기타 AI 함수들
# ==========================================
def analyze_topic_score(topic):
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
}}"""
    return ask_ai("전자책 시장 분석가", prompt, temperature=0.3)


def generate_titles_advanced(topic, persona, pain_points):
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
- 물음표로 끝나는 평범한 질문형

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
}}"""
    return ask_ai("베스트셀러 작가", prompt, temperature=0.9)


def generate_concept(topic, persona, pain_points):
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

2. [한 줄 컨셉]
   → 왜 끌리는가

(5개까지)"""
    return ask_ai("카피라이터", prompt, temperature=0.9)


def generate_interview_questions(subtopic_title, chapter_title, topic):
    prompt = f"""당신은 베스트셀러 작가의 고스트라이터입니다.
'{topic}' 전자책의 '{chapter_title}' 챕터 중 '{subtopic_title}' 소제목 부분을 쓰기 위해 작가를 인터뷰합니다.

[좋은 질문의 특징]
1. 구체적 상황을 묻는다: "언제, 어디서, 어떻게"
2. 감정을 묻는다: "그때 기분이 어땠나요?"
3. 실패를 묻는다: "처음에 뭘 잘못했나요?"
4. 반전을 묻는다: "뭘 깨닫고 달라졌나요?"
5. 디테일을 묻는다: "구체적으로 어떻게 했나요?"

[좋은 질문 예시]
- "처음 이걸 시작했을 때 가장 크게 실패한 경험은 뭔가요?"
- "이걸 깨닫기 전과 후, 구체적으로 뭐가 달라졌나요? 숫자로 말해주실 수 있나요?"
- "이 방법을 처음 시도한 날, 그 상황을 자세히 묘사해주실 수 있나요?"

'{subtopic_title}' 소제목의 핵심 내용을 끌어낼 수 있는 인터뷰 질문 3개를 만들어주세요.

형식:
Q1: [질문]
Q2: [질문]
Q3: [질문]"""
    return ask_ai("베스트셀러 고스트라이터", prompt, temperature=0.7)


def refine_content(content, style="친근한"):
    style_guide = {
        "친근한": "친근한 스타일 - 합니다체, 자신감 있는 단정, 구체적 숫자와 팩트",
        "전문적": "전문가 스타일 - 합니다체, 데이터와 출처 강조, 논리적 전개",
        "직설적": "직설 스타일 - 합니다체, 핵심만 간결하게, 군더더기 제로",
        "스토리텔링": "스토리 스타일 - 합니다체, 구체적 장면 묘사, 대화체 활용"
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

다듬어진 글만 출력하세요."""
    return ask_ai("에디터", prompt, temperature=0.7)


def check_quality(content):
    prompt = f"""다음 글이 베스트셀러 수준인지 평가해주세요.

[평가할 글]
{content[:4000]}

[평가 기준]
1. 첫 문장 (10점) - 뒤통수를 치는가?
2. 몰입도 (10점) - 끝까지 읽게 되는가?
3. 공감력 (10점) - "내 얘기잖아"라고 느끼는가?
4. 구체성 (10점) - 구체적 장면/숫자가 있는가?
5. AI 티 (10점) - AI 표현이 있는가?

[출력 형식]
📊 종합 점수: __/50점

📌 각 항목 점수와 평가

✍️ 수정하면 좋을 문장 TOP 3

🎯 총평"""
    return ask_ai("베스트셀러 편집자", prompt, temperature=0.6)

def regenerate_chapter_outline(chapter_num, topic, persona, current_outline):
    """특정 챕터를 재생성"""
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


def regenerate_single_subtopic(chapter_title, subtopic_num, topic, current_subtopics):
    """특정 소제목 하나만 재생성"""
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
    result = ask_ai("카피라이터", prompt, temperature=0.85)
    # 첫 번째 줄만 반환, 불필요한 기호 제거
    first_line = result.strip().split('\n')[0]
    return first_line.lstrip('- ').lstrip('0123456789.').strip()
def generate_marketing_copy(title, subtitle, topic, persona):
    prompt = f"""당신은 크몽에서 전자책을 수천 권 판매한 탑셀러입니다.

[상품 정보]
제목: {title}
부제: {subtitle}
주제: {topic}
타겟: {persona}

다음을 만들어주세요:

1. 크몽 상품 제목 (40자 이내) - 검색 키워드 포함

2. 상세페이지 헤드라인 3개 - 스크롤을 멈추게 만드는 한 줄

3. 구매 유도 문구 (CTA) 3개 - 긴급성 + FOMO 자극

4. 인스타그램 홍보 문구 - 훅 + 스토리 + CTA + 해시태그 5개

5. 블로그 포스팅 제목 3개 - 검색 유입 + 클릭 유도"""
    return ask_ai("크몽 탑셀러 마케터", prompt, temperature=0.85)


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

tabs = st.tabs(["① 주제 선정", "② 타겟 & 컨셉", "③ 목차 설계", "④ 본문 작성", "⑤ 문체 다듬기", "⑥ 최종 출력"])

# === TAB 1: 주제 선정 ===
with tabs[0]:
    st.markdown("## 주제 선정 & 적합도 분석")
    st.markdown('<div class="quick-action-box"><p>💡 <strong>이미 주제가 있다면?</strong> 아래에 입력 후 바로 다음 탭으로 이동하세요!</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<p class="section-label">Step 01</p>', unsafe_allow_html=True)
        st.markdown("### 주제 입력")
        topic_input = st.text_input("어떤 주제로 전자책을 쓰고 싶으세요?", value=st.session_state['topic'], placeholder="예: 크몽으로 월 500만원 벌기")
        if topic_input != st.session_state['topic']:
            st.session_state['topic'] = topic_input
            st.session_state['topic_score'] = None
            st.session_state['score_details'] = None
        
        st.markdown('<div class="info-card"><div class="info-card-title">좋은 주제의 조건</div><p>• 내가 직접 경험하고 성과를 낸 것</p><p>• 사람들이 돈 주고 배우고 싶어하는 것</p><p>• 구체적인 결과를 약속할 수 있는 것</p></div>', unsafe_allow_html=True)
        
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
        st.markdown('<p class="section-label">Step 02</p>', unsafe_allow_html=True)
        st.markdown("### 분석 결과")
        if st.session_state['topic_score'] is not None:
            score = st.session_state['topic_score']
            verdict = st.session_state['topic_verdict']
            details = st.session_state['score_details']
            verdict_class = "status-excellent" if verdict == "적합" else ("status-good" if verdict == "보통" else "status-warning")
            st.markdown(f'<div class="score-card"><div class="score-number">{score}</div><div class="score-label">종합 점수</div><span class="status-badge {verdict_class}">{verdict}</span></div>', unsafe_allow_html=True)
            if details:
                st.markdown("#### 세부 점수")
                for name, key in [("시장성", "market"), ("수익성", "profit"), ("차별화", "differentiation"), ("작성 난이도", "difficulty"), ("지속성", "sustainability")]:
                    score_val = details.get(key, {}).get('score', 0)
                    reason = details.get(key, {}).get('reason', '')
                    st.markdown(f'<div class="score-item"><span class="score-item-label">{name}</span><span class="score-item-value">{score_val}</span></div><p class="score-item-reason">{reason}</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="summary-box"><p><strong>종합 의견</strong><br>{details.get("summary", "")}</p></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state"><p>분석은 선택사항입니다.</p><p>주제만 입력해도 다음 단계로 진행 가능!</p></div>', unsafe_allow_html=True)

# === TAB 2: 타겟 & 컨셉 ===
with tabs[1]:
    st.markdown("## 타겟 설정 & 제목 생성")
    if not st.session_state['topic']:
        st.info("💡 주제를 먼저 입력하면 더 정확한 결과를 얻을 수 있어요.")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<p class="section-label">Step 01</p>', unsafe_allow_html=True)
        st.markdown("### 타겟 정의")
        if not st.session_state['topic']:
            topic_here = st.text_input("주제 (여기서 입력 가능)", value=st.session_state['topic'], placeholder="예: 크몽으로 월 500만원 벌기", key="topic_tab2")
            if topic_here:
                st.session_state['topic'] = topic_here
        persona = st.text_area("누가 이 책을 읽나요?", value=st.session_state['target_persona'], placeholder="예: 30대 직장인, 퇴근 후 부업으로 월 100만원 추가 수입을 원하는 사람", height=100)
        st.session_state['target_persona'] = persona
        pain_points = st.text_area("타겟의 가장 큰 고민은?", value=st.session_state['pain_points'], placeholder="예: 시간이 없다, 뭘 해야 할지 모르겠다, 시작이 두렵다", height=100)
        st.session_state['pain_points'] = pain_points
        
        st.markdown("---")
        st.markdown('<p class="section-label">Step 02</p>', unsafe_allow_html=True)
        st.markdown("### 한 줄 컨셉")
        if st.button("컨셉 생성하기", key="concept_btn"):
            if not st.session_state['topic'] or not persona:
                st.error("주제와 타겟을 먼저 입력해주세요.")
            else:
                with st.spinner("생성 중..."):
                    concept = generate_concept(st.session_state['topic'], persona, pain_points)
                    st.session_state['one_line_concept'] = concept
        if st.session_state['one_line_concept']:
            st.markdown(f'<div class="info-card">{st.session_state["one_line_concept"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<p class="section-label">Step 03</p>', unsafe_allow_html=True)
        st.markdown("### 제목 생성")
        if st.button("제목 생성하기", key="title_btn"):
            if not st.session_state['topic']:
                st.error("주제를 먼저 입력해주세요.")
            else:
                with st.spinner("생성 중..."):
                    titles_result = generate_titles_advanced(st.session_state['topic'], st.session_state['target_persona'], st.session_state['pain_points'])
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
                    st.markdown(f'<div class="title-card"><div class="card-number">TITLE 0{i}</div><div class="main-title">{t.get("title", "")}</div><div class="sub-title">{t.get("subtitle", "")}</div><div class="reason">{t.get("why_works", "")}</div></div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<p class="section-label">Step 04</p>', unsafe_allow_html=True)
        st.markdown("### 최종 선택")
        st.session_state['book_title'] = st.text_input("제목", value=st.session_state['book_title'], placeholder="최종 제목")
        st.session_state['subtitle'] = st.text_input("부제", value=st.session_state['subtitle'], placeholder="부제")

# === TAB 3: 목차 설계 ===
with tabs[2]:
    st.markdown("## 목차 설계")
    st.markdown("### 🎯 작업 방식 선택")
    outline_mode = st.radio("목차를 어떻게 만드시겠어요?", ["🤖 자동으로 목차 생성", "✍️ 내가 직접 입력"], horizontal=True, key="outline_mode_radio")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if outline_mode == "🤖 자동으로 목차 생성":
            st.markdown('<p class="section-label">자동 목차 생성</p>', unsafe_allow_html=True)
            st.markdown("### 목차를 자동으로 설계합니다")
            if not st.session_state['topic']:
                st.warning("💡 주제를 먼저 입력해주세요")
                topic_here = st.text_input("주제", value=st.session_state['topic'], placeholder="예: 크몽으로 월 500만원 벌기", key="topic_tab3")
                if topic_here:
                    st.session_state['topic'] = topic_here
            
            if st.button("🚀 목차 생성하기", key="outline_btn"):
                if not st.session_state['topic']:
                    st.error("주제를 먼저 입력해주세요.")
                else:
                    with st.spinner("설계 중..."):
                        outline_text = generate_outline(st.session_state['topic'], st.session_state['target_persona'], st.session_state['pain_points'])
                        lines = outline_text.split('\n')
                        chapters = []
                        current_chapter = None
                        chapter_subtopics = {}
                        
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                            
                            # 챕터 감지: ## 또는 PART로 시작
                            if line.startswith('##') or 'PART' in line.upper():
                                # ## 제거하고 정리
                                chapter_name = line.lstrip('#').strip()
                                # **굵은글씨** 제거
                                chapter_name = re.sub(r'\*\*(.+?)\*\*', r'\1', chapter_name)
                                if chapter_name and 'PART' in chapter_name.upper():
                                    current_chapter = chapter_name
                                    chapters.append(current_chapter)
                                    chapter_subtopics[current_chapter] = []
                            
                            # 소제목 감지: -로 시작
                            elif current_chapter and line.startswith('-'):
                                subtopic = line.lstrip('- ').strip()
                                # **굵은글씨** 제거
                                subtopic = re.sub(r'\*\*(.+?)\*\*', r'\1', subtopic)
                                # 번호 제거 (1.1, 1.2 등)
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
                                    'subtopic_data': {st: {'questions': [], 'answers': [], 'content': ''} for st in subtopics}
                                }
                            
                            total_subtopics = sum(len(chapter_subtopics.get(ch, [])) for ch in chapters)
                            st.success(f"✅ {len(chapters)}개 챕터, {total_subtopics}개 소제목 생성됨!")
                            st.rerun()
                        else:
                            st.error("목차 생성 실패. 다시 시도해주세요.")
            
            if 'full_outline' in st.session_state and st.session_state['full_outline']:
                st.markdown("**📋 현재 목차**")
                st.code(st.session_state['full_outline'], language=None)
        else:
            st.markdown('<p class="section-label">직접 입력</p>', unsafe_allow_html=True)
            st.markdown("### 목차를 직접 입력하세요")
            st.markdown('<div class="info-card"><div class="info-card-title">📌 입력 형식 예시</div><p><b>챕터1: 첫 번째 챕터 제목</b></p><p style="margin-left: 20px;">- 소제목 1</p><p style="margin-left: 20px;">- 소제목 2</p></div>', unsafe_allow_html=True)
            existing_outline = ""
            if st.session_state['outline']:
                for ch in st.session_state['outline']:
                    existing_outline += f"## {ch}\n"
                    if ch in st.session_state['chapters']:
                        for st_name in st.session_state['chapters'][ch].get('subtopics', []):
                            existing_outline += f"- {st_name}\n"
            manual_outline = st.text_area("목차 입력", value=existing_outline, height=350, placeholder="## 챕터1: 제목\n- 소제목1\n- 소제목2\n\n## 챕터2: 제목\n- 소제목3", key="manual_outline_input")
            if st.button("✅ 목차 저장하기", key="save_manual_outline"):
                if manual_outline.strip():
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
                        st.session_state['chapters'][ch] = {'subtopics': subtopics, 'subtopic_data': {st_name: {'questions': [], 'answers': [], 'content': ''} for st_name in subtopics}}
                    trigger_auto_save()
                    total_subtopics = sum(len(chapter_subtopics.get(ch, [])) for ch in chapters)
                    st.success(f"✅ {len(chapters)}개 챕터, {total_subtopics}개 소제목 저장됨!")
                    st.rerun()
    
    with col2:
        st.markdown('<p class="section-label">목차 관리</p>', unsafe_allow_html=True)
        st.markdown("### 📋 현재 목차")
        if st.session_state['outline']:
            for i, chapter in enumerate(st.session_state['outline']):
                subtopic_count = len(st.session_state['chapters'].get(chapter, {}).get('subtopics', []))
                with st.expander(f"**{chapter}** ({subtopic_count}개 소제목)", expanded=False):
                    col_edit, col_actions = st.columns([3, 2])
                    with col_edit:
                        new_title = st.text_input("챕터 제목", value=chapter, key=f"edit_chapter_{i}", label_visibility="collapsed")
                    with col_actions:
                        col_regen, col_del = st.columns(2)
                        with col_regen:
                            if st.button("🔄", key=f"regen_chapter_{i}", help="재생성"):
                                with st.spinner("재생성 중..."):
                                    new_chapter_text = regenerate_chapter_outline(i + 1, st.session_state['topic'], st.session_state['target_persona'], st.session_state['outline'])
                                    lines = new_chapter_text.split('\n')
                                    new_chapter_title = None
                                    new_subtopics = []
                                    for line in lines:
                                        line = line.strip()
                                        if line.startswith('##'):
                                            new_chapter_title = line.lstrip('#').strip()
                                        elif line.startswith('-'):
                                            st_name = line.lstrip('- ').strip()
                                            if st_name:
                                                new_subtopics.append(st_name)
                                    if new_chapter_title:
                                        old_chapter = st.session_state['outline'][i]
                                        st.session_state['outline'][i] = new_chapter_title
                                        if old_chapter in st.session_state['chapters']:
                                            del st.session_state['chapters'][old_chapter]
                                        st.session_state['chapters'][new_chapter_title] = {'subtopics': new_subtopics, 'subtopic_data': {st: {'questions': [], 'answers': [], 'content': ''} for st in new_subtopics}}
                                        trigger_auto_save()
                                        st.rerun()
                        with col_del:
                            if st.button("🗑️", key=f"del_chapter_{i}", help="삭제"):
                                old_chapter = st.session_state['outline'].pop(i)
                                if old_chapter in st.session_state['chapters']:
                                    del st.session_state['chapters'][old_chapter]
                                trigger_auto_save()
                                st.rerun()
                    if new_title != chapter and new_title.strip():
                        if st.button("💾 제목 저장", key=f"save_chapter_title_{i}"):
                            st.session_state['outline'][i] = new_title
                            if chapter in st.session_state['chapters']:
                                st.session_state['chapters'][new_title] = st.session_state['chapters'].pop(chapter)
                            trigger_auto_save()
                            st.rerun()
                    st.markdown("---")
                    st.markdown("**📝 소제목**")
                    if chapter in st.session_state['chapters']:
                        subtopics = st.session_state['chapters'][chapter].get('subtopics', [])
                        for j, st_name in enumerate(subtopics):
                            col_st, col_st_actions = st.columns([3, 2])
                            with col_st:
                                new_st = st.text_input(f"소제목 {j+1}", value=st_name, key=f"edit_st_{i}_{j}", label_visibility="collapsed")
                            with col_st_actions:
                                col_st_regen, col_st_del = st.columns(2)
                                with col_st_regen:
                                    if st.button("🔄", key=f"regen_st_{i}_{j}", help="재생성"):
                                        with st.spinner("재생성 중..."):
                                            new_st_title = regenerate_single_subtopic(chapter, j + 1, st.session_state['topic'], subtopics)
                                            if new_st_title:
                                                old_st = st.session_state['chapters'][chapter]['subtopics'][j]
                                                st.session_state['chapters'][chapter]['subtopics'][j] = new_st_title
                                                if old_st in st.session_state['chapters'][chapter]['subtopic_data']:
                                                    st.session_state['chapters'][chapter]['subtopic_data'][new_st_title] = st.session_state['chapters'][chapter]['subtopic_data'].pop(old_st)
                                                else:
                                                    st.session_state['chapters'][chapter]['subtopic_data'][new_st_title] = {'questions': [], 'answers': [], 'content': ''}
                                                trigger_auto_save()
                                                st.rerun()
                                with col_st_del:
                                    if st.button("🗑️", key=f"del_st_{i}_{j}", help="삭제"):
                                        removed_st = st.session_state['chapters'][chapter]['subtopics'].pop(j)
                                        if removed_st in st.session_state['chapters'][chapter]['subtopic_data']:
                                            del st.session_state['chapters'][chapter]['subtopic_data'][removed_st]
                                        trigger_auto_save()
                                        st.rerun()
                            if new_st != st_name and new_st.strip():
                                if st.button("💾", key=f"save_st_{i}_{j}", help="저장"):
                                    st.session_state['chapters'][chapter]['subtopics'][j] = new_st
                                    if st_name in st.session_state['chapters'][chapter]['subtopic_data']:
                                        st.session_state['chapters'][chapter]['subtopic_data'][new_st] = st.session_state['chapters'][chapter]['subtopic_data'].pop(st_name)
                                    trigger_auto_save()
                                    st.rerun()
            st.markdown("---")
            if st.button("➕ 새 챕터 추가", key="add_chapter"):
                new_ch_name = f"챕터{len(st.session_state['outline'])+1}: 새 챕터"
                st.session_state['outline'].append(new_ch_name)
                st.session_state['chapters'][new_ch_name] = {'subtopics': [], 'subtopic_data': {}}
                trigger_auto_save()
                st.rerun()
        else:
            st.markdown('<div class="empty-state"><p>왼쪽에서 목차를 생성하거나 직접 입력하세요</p></div>', unsafe_allow_html=True)


# === TAB 4: 본문 작성 ===
with tabs[3]:
    st.markdown("## 본문 작성")
    if not st.session_state['outline']:
        st.warning("⚠️ 먼저 '③ 목차 설계' 탭에서 목차를 작성해주세요.")
        st.stop()
    
    chapter_list = [item for item in st.session_state['outline'] if not item.strip().startswith('-')]
    if not chapter_list:
        st.warning("⚠️ 챕터가 없습니다.")
        st.stop()
    
    # 챕터 선택 및 편집
    col_chapter_select, col_chapter_edit = st.columns([6, 1])
    
    with col_chapter_select:
        selected_chapter = st.selectbox("📚 챕터 선택", chapter_list, key="chapter_select_main")
    
    # 챕터 편집 모드 키
    chapter_edit_key = f"edit_mode_chapter_{selected_chapter}"
    if chapter_edit_key not in st.session_state:
        st.session_state[chapter_edit_key] = False
    
    with col_chapter_edit:
        if st.session_state[chapter_edit_key]:
            if st.button("❌", key="cancel_chapter_edit", help="취소"):
                st.session_state[chapter_edit_key] = False
                st.rerun()
        else:
            if st.button("✏️", key="edit_chapter_btn", help="챕터 수정"):
                st.session_state[chapter_edit_key] = True
                st.rerun()
    
    # 챕터 편집 UI
    if st.session_state[chapter_edit_key]:
        st.markdown("#### ✏️ 챕터 제목 수정")
        col_input, col_save = st.columns([5, 1])
        with col_input:
            new_chapter_title = st.text_input(
                "새 챕터 제목",
                value=selected_chapter,
                key="new_chapter_title_input",
                label_visibility="collapsed"
            )
        with col_save:
            if st.button("💾 저장", key="save_chapter_title"):
                if new_chapter_title.strip() and new_chapter_title != selected_chapter:
                    # 챕터 이름 변경
                    idx = st.session_state['outline'].index(selected_chapter)
                    st.session_state['outline'][idx] = new_chapter_title
                    
                    # chapters 데이터도 업데이트
                    if selected_chapter in st.session_state['chapters']:
                        st.session_state['chapters'][new_chapter_title] = st.session_state['chapters'].pop(selected_chapter)
                    
                    st.session_state[chapter_edit_key] = False
                    trigger_auto_save()
                    st.success(f"✅ 챕터 제목이 변경되었습니다!")
                    st.rerun()
                else:
                    st.session_state[chapter_edit_key] = False
                    st.rerun()
        st.markdown("---")
    if selected_chapter not in st.session_state['chapters']:
        st.session_state['chapters'][selected_chapter] = {'subtopics': [], 'subtopic_data': {}}
    chapter_data = st.session_state['chapters'][selected_chapter]
    if 'subtopics' not in chapter_data:
        chapter_data['subtopics'] = []
    if 'subtopic_data' not in chapter_data:
        chapter_data['subtopic_data'] = {}
    
    st.markdown("---")
    
# 소제목 전체 보기 (기존 코드를 이것으로 교체)
    with st.expander(f"📋 '{selected_chapter}' 소제목 ({len(chapter_data.get('subtopics', []))}개)", expanded=True):
        if chapter_data.get('subtopics'):
            for j, st_name in enumerate(chapter_data['subtopics']):
                has_content = bool(chapter_data['subtopic_data'].get(st_name, {}).get('content', '').strip())
                status_icon = "✅" if has_content else "⬜"
                
                # 편집 모드 키
                edit_key = f"edit_mode_subtopic_{selected_chapter}_{j}"
                if edit_key not in st.session_state:
                    st.session_state[edit_key] = False
                
                col_status, col_title, col_edit, col_regen = st.columns([0.5, 6, 1, 1])
                
                with col_status:
                    st.write(status_icon)
                
                with col_title:
                    if st.session_state[edit_key]:
                        # 편집 모드
                        new_title = st.text_input(
                            "소제목 수정", 
                            value=st_name, 
                            key=f"edit_input_{selected_chapter}_{j}",
                            label_visibility="collapsed"
                        )
                    else:
                        # 보기 모드
                        st.write(f"{j+1}. {st_name}")
                
                with col_edit:
                    if st.session_state[edit_key]:
                        # 저장 버튼
                        if st.button("💾", key=f"save_st_{selected_chapter}_{j}", help="저장"):
                            new_title = st.session_state.get(f"edit_input_{selected_chapter}_{j}", st_name)
                            if new_title and new_title != st_name:
                                # 소제목 이름 변경
                                chapter_data['subtopics'][j] = new_title
                                # subtopic_data도 업데이트
                                if st_name in chapter_data['subtopic_data']:
                                    chapter_data['subtopic_data'][new_title] = chapter_data['subtopic_data'].pop(st_name)
                                else:
                                    chapter_data['subtopic_data'][new_title] = {'questions': [], 'answers': [], 'content': ''}
                            st.session_state[edit_key] = False
                            st.rerun()
                    else:
                        # 편집 버튼
                        if st.button("✏️", key=f"edit_btn_{selected_chapter}_{j}", help="수정"):
                            st.session_state[edit_key] = True
                            st.rerun()
                
                with col_regen:
                    if st.session_state[edit_key]:
                        # 취소 버튼
                        if st.button("❌", key=f"cancel_st_{selected_chapter}_{j}", help="취소"):
                            st.session_state[edit_key] = False
                            st.rerun()
                    else:
                        # 재생성 버튼
                        if st.button("🔄", key=f"regen_st_tab4_{j}", help="AI 재생성"):
                            with st.spinner("재생성 중..."):
                                new_title = regenerate_single_subtopic(selected_chapter, j + 1, st.session_state['topic'], chapter_data['subtopics'])
                                if new_title:
                                    old_st = chapter_data['subtopics'][j]
                                    chapter_data['subtopics'][j] = new_title
                                    if old_st in chapter_data['subtopic_data']:
                                        chapter_data['subtopic_data'][new_title] = chapter_data['subtopic_data'].pop(old_st)
                                    else:
                                        chapter_data['subtopic_data'][new_title] = {'questions': [], 'answers': [], 'content': ''}
                                    st.rerun()
            
            # 소제목 추가 버튼
            st.markdown("---")
            col_add1, col_add2 = st.columns([4, 1])
            with col_add1:
                new_subtopic = st.text_input("새 소제목 추가", placeholder="직접 입력...", key=f"add_new_st_{selected_chapter}", label_visibility="collapsed")
            with col_add2:
                if st.button("➕ 추가", key=f"add_st_btn_{selected_chapter}"):
                    if new_subtopic.strip() and new_subtopic not in chapter_data['subtopics']:
                        chapter_data['subtopics'].append(new_subtopic)
                        chapter_data['subtopic_data'][new_subtopic] = {'questions': [], 'answers': [], 'content': ''}
                        st.rerun()
        else:
            st.info("소제목이 없습니다. 아래에서 추가하세요.")
    
    st.markdown("---")
    
    if chapter_data['subtopics']:
        st.markdown("### ✍️ 본문 작성")
        selected_subtopic = st.selectbox("작성할 소제목", chapter_data['subtopics'], key="subtopic_select_main", format_func=lambda x: f"{'✅' if chapter_data['subtopic_data'].get(x, {}).get('content') else '⬜'} {x}")
        
        completed = sum(1 for s in chapter_data['subtopics'] if chapter_data['subtopic_data'].get(s, {}).get('content'))
        total = len(chapter_data['subtopics'])
        st.progress(completed / total if total > 0 else 0)
        st.caption(f"진행: {completed}/{total} 완료")
        st.markdown("---")
        
        if selected_subtopic:
            if selected_subtopic not in chapter_data['subtopic_data']:
                chapter_data['subtopic_data'][selected_subtopic] = {'questions': [], 'answers': [], 'content': ''}
            subtopic_data = chapter_data['subtopic_data'][selected_subtopic]
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown('<p class="section-label">Step 01</p>', unsafe_allow_html=True)
                st.markdown(f"### 🎤 인터뷰: {selected_subtopic}")
                if st.button("🎤 질문 생성하기", key="gen_questions_main"):
                    with st.spinner("질문 생성 중..."):
                        questions_text = generate_interview_questions(selected_subtopic, selected_chapter, st.session_state['topic'])
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
                        subtopic_data['answers'][i] = st.text_area(f"A{i+1}", value=subtopic_data['answers'][i], key=f"answer_main_{selected_chapter}_{selected_subtopic}_{i}", height=80, label_visibility="collapsed")
                else:
                    st.info("👆 '질문 생성하기' 버튼을 눌러 인터뷰를 시작하세요.")
            
            with col2:
                st.markdown('<p class="section-label">Step 02</p>', unsafe_allow_html=True)
                st.markdown(f"### 📝 본문: {selected_subtopic}")
                has_answers = subtopic_data.get('questions') and any(a.strip() for a in subtopic_data.get('answers', []))
                content_widget_key = f"content_main_{selected_chapter}_{selected_subtopic}"
                
                if has_answers:
                    if st.button("✨ 본문 생성하기", key="gen_content_main"):
                        with st.spinner("집필 중... (30초~1분)"):
                            content = generate_subtopic_content(selected_subtopic, selected_chapter, subtopic_data['questions'], subtopic_data['answers'], st.session_state['topic'], st.session_state['target_persona'])
                            st.session_state['chapters'][selected_chapter]['subtopic_data'][selected_subtopic]['content'] = content
                            st.session_state[content_widget_key] = content
                            trigger_auto_save()
                            st.rerun()
                else:
                    st.info("👈 먼저 인터뷰 질문에 답변해주세요.")
                
                stored_content = st.session_state['chapters'][selected_chapter]['subtopic_data'][selected_subtopic].get('content', '')
                current_selection_key = f"_last_selected_{selected_chapter}"
                last_selected = st.session_state.get(current_selection_key, None)
                if last_selected != selected_subtopic:
                    st.session_state[content_widget_key] = stored_content
                    st.session_state[current_selection_key] = selected_subtopic
                elif content_widget_key not in st.session_state:
                    st.session_state[content_widget_key] = stored_content
                
                edited_content = st.text_area("본문 내용", height=400, key=content_widget_key, label_visibility="collapsed")
                if content_widget_key in st.session_state:
                    st.session_state['chapters'][selected_chapter]['subtopic_data'][selected_subtopic]['content'] = st.session_state[content_widget_key]
                
                final_content = st.session_state['chapters'][selected_chapter]['subtopic_data'][selected_subtopic].get('content', '')
                if final_content:
                    char_count = calculate_char_count(final_content)
                    st.caption(f"📊 {char_count:,}자")
                    st.success(f"✅ '{selected_subtopic}' 본문 작성 완료!")
        
        with st.expander("⚙️ 소제목 편집/추가", expanded=False):
            col_gen, col_add = st.columns(2)
            with col_gen:
                num_subtopics = st.number_input("생성할 개수", min_value=1, max_value=10, value=3, key="num_subtopics_gen_exp")
                if st.button("✨ 소제목 자동 생성", key="gen_subtopics_exp"):
                    with st.spinner("생성 중..."):
                        subtopics_text = generate_subtopics(selected_chapter, st.session_state['topic'], st.session_state['target_persona'], num_subtopics)
                        new_subtopics = []
                        for line in subtopics_text.split('\n'):
                            line = line.strip()
                            if line and (line[0].isdigit() or line.startswith('-')):
                                cleaned = re.sub(r'^[\d\.\-\s]+', '', line).strip()
                                if cleaned:
                                    new_subtopics.append(cleaned)
                        if new_subtopics:
                            chapter_data['subtopics'] = new_subtopics[:num_subtopics]
                            for st_name in new_subtopics[:num_subtopics]:
                                if st_name not in chapter_data['subtopic_data']:
                                    chapter_data['subtopic_data'][st_name] = {'questions': [], 'answers': [], 'content': ''}
                            st.success(f"✅ {len(new_subtopics[:num_subtopics])}개 생성됨!")
                            st.rerun()
            with col_add:
                new_name = st.text_input("새 소제목", placeholder="직접 입력", key="new_subtopic_exp")
                if st.button("➕ 추가", key="add_subtopic_exp"):
                    if new_name.strip() and new_name not in chapter_data['subtopics']:
                        chapter_data['subtopics'].append(new_name)
                        chapter_data['subtopic_data'][new_name] = {'questions': [], 'answers': [], 'content': ''}
                        st.rerun()
    else:
        st.warning("⚠️ 이 챕터에 소제목이 없습니다.")
        col_gen, col_add = st.columns(2)
        with col_gen:
            num_subtopics = st.number_input("생성할 개수", min_value=1, max_value=10, value=3, key="num_subtopics_gen_empty")
            if st.button("✨ 소제목 자동 생성", key="gen_subtopics_empty"):
                with st.spinner("생성 중..."):
                    subtopics_text = generate_subtopics(selected_chapter, st.session_state['topic'], st.session_state['target_persona'], num_subtopics)
                    new_subtopics = []
                    for line in subtopics_text.split('\n'):
                        line = line.strip()
                        if line and (line[0].isdigit() or line.startswith('-')):
                            cleaned = re.sub(r'^[\d\.\-\s]+', '', line).strip()
                            if cleaned:
                                new_subtopics.append(cleaned)
                    if new_subtopics:
                        chapter_data['subtopics'] = new_subtopics[:num_subtopics]
                        for st_name in new_subtopics[:num_subtopics]:
                            chapter_data['subtopic_data'][st_name] = {'questions': [], 'answers': [], 'content': ''}
                        st.success(f"✅ {len(new_subtopics[:num_subtopics])}개 생성됨!")
                        st.rerun()
        with col_add:
            new_subtopic_name = st.text_input("소제목 이름", placeholder="직접 입력", key="new_subtopic_empty")
            if st.button("➕ 소제목 추가", key="add_subtopic_empty"):
                if new_subtopic_name.strip():
                    chapter_data['subtopics'].append(new_subtopic_name)
                    chapter_data['subtopic_data'][new_subtopic_name] = {'questions': [], 'answers': [], 'content': ''}
                    st.rerun()
    
    # 전체 본문 보기
    st.markdown("---")
    st.markdown("### 📖 작성된 본문")
    pure_content = get_all_content_text()
    if pure_content:
        total_chars = calculate_char_count(pure_content)
        content_count = sum(1 for ch in st.session_state['chapters'].values() for st_data in ch.get('subtopic_data', {}).values() if st_data.get('content'))
        st.success(f"✅ 총 {content_count}개 소제목 | {total_chars:,}자")
        with st.expander("📖 전체 본문 펼쳐보기", expanded=False):
            for ch in st.session_state['outline']:
                if ch in st.session_state['chapters']:
                    ch_data = st.session_state['chapters'][ch]
                    if 'subtopic_data' in ch_data:
                        has_content = any(ch_data['subtopic_data'].get(s, {}).get('content') for s in ch_data.get('subtopics', []))
                        if has_content:
                            st.markdown(f"## {ch}")
                            for st_name in ch_data.get('subtopics', []):
                                st_data = ch_data['subtopic_data'].get(st_name, {})
                                if st_data.get('content'):
                                    st.markdown(f"**{st_name}**")
                                    st.markdown(clean_content_for_display(st_data['content'], st_name, ch))
                                    st.markdown("")
    else:
        st.info("💡 아직 작성된 본문이 없습니다.")


# === TAB 5: 문체 다듬기 ===
with tabs[4]:
    st.markdown("## 문체 다듬기 & 품질 검사")
    
    has_content = any(st_data.get('content') for ch_data in st.session_state['chapters'].values() for st_data in ch_data.get('subtopic_data', {}).values())
    if not has_content:
        st.info("💡 먼저 본문을 작성해주세요.")
        direct_content = st.text_area("다듬을 텍스트 직접 입력", height=300, placeholder="다듬고 싶은 텍스트를 여기에 붙여넣으세요...")
        if direct_content:
            has_content = True
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<p class="section-label">Style</p>', unsafe_allow_html=True)
        st.markdown("### 문체 다듬기")
        content_options = []
        for ch in st.session_state['outline']:
            if ch in st.session_state['chapters']:
                ch_data = st.session_state['chapters'][ch]
                if 'subtopic_data' in ch_data:
                    for st_name, st_data in ch_data['subtopic_data'].items():
                        if st_data.get('content'):
                            content_options.append(f"{ch} > {st_name}")
        if content_options:
            selected_content = st.selectbox("다듬을 콘텐츠 선택", content_options, key="refine_select")
        style = st.selectbox("목표 스타일", ["친근한", "전문적", "직설적", "스토리텔링"], key="style_select")
        
        if st.button("✨ 문체 다듬기", key="refine_btn"):
            content_to_refine = ""
            if content_options and 'selected_content' in dir() and selected_content:
                parts = selected_content.split(" > ")
                if len(parts) == 2:
                    ch, st_name = parts
                    content_to_refine = st.session_state['chapters'][ch]['subtopic_data'][st_name]['content']
            elif 'direct_content' in dir() and direct_content:
                content_to_refine = direct_content
            if content_to_refine:
                with st.spinner("다듬는 중..."):
                    refined = refine_content(content_to_refine, style)
                    st.session_state['refined_content'] = refined
            else:
                st.error("다듬을 콘텐츠를 선택해주세요.")
        
        if st.session_state.get('refined_content'):
            st.text_area("다듬어진 본문", value=st.session_state['refined_content'], height=400)
            if st.button("원본에 적용", key="apply_refined"):
                if content_options and 'selected_content' in dir() and selected_content:
                    parts = selected_content.split(" > ")
                    if len(parts) == 2:
                        ch, st_name = parts
                        st.session_state['chapters'][ch]['subtopic_data'][st_name]['content'] = st.session_state['refined_content']
                        trigger_auto_save()
                        st.success("적용됨!")
                        st.rerun()
    
    with col2:
        st.markdown('<p class="section-label">Quality</p>', unsafe_allow_html=True)
        st.markdown("### 품질 검사")
        if st.button("🔍 베스트셀러 체크", key="quality_btn"):
            content_to_check = ""
            if content_options and 'selected_content' in dir() and selected_content:
                parts = selected_content.split(" > ")
                if len(parts) == 2:
                    ch, st_name = parts
                    content_to_check = st.session_state['chapters'][ch]['subtopic_data'][st_name]['content']
            elif 'direct_content' in dir() and direct_content:
                content_to_check = direct_content
            if content_to_check:
                with st.spinner("분석 중..."):
                    quality_result = check_quality(content_to_check)
                    st.session_state['quality_result'] = quality_result
            else:
                st.error("검사할 콘텐츠를 선택해주세요.")
        if st.session_state.get('quality_result'):
            st.markdown(f'<div class="info-card">{st.session_state["quality_result"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)


# === TAB 6: 최종 출력 ===
with tabs[5]:
    st.markdown("## 최종 출력 & 마케팅")
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown('<p class="section-label">Export</p>', unsafe_allow_html=True)
        st.markdown("### 전자책 다운로드")
        book_title = st.text_input("전자책 제목", value=st.session_state.get('book_title', ''), key="final_title")
        subtitle = st.text_input("부제", value=st.session_state.get('subtitle', ''), key="final_subtitle")
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
                    chapter_has_content = any(ch_data['subtopic_data'].get(st_name, {}).get('content') for st_name in ch_data.get('subtopics', []))
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
        
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>{book_title or '전자책'}</title>
    <style>
        body {{ font-family: 'Pretendard', sans-serif; max-width: 800px; margin: 0 auto; padding: 40px 20px; line-height: 1.8; }}
        h1 {{ font-size: 32px; margin-bottom: 10px; }}
        h2 {{ font-size: 24px; margin-top: 50px; }}
        h3 {{ font-size: 18px; margin-top: 30px; }}
        p {{ font-size: 16px; margin: 16px 0; }}
    </style>
</head>
<body>{full_book_html}</body>
</html>"""
        
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button("📄 TXT 다운로드", full_book_txt, file_name=f"{book_title or 'ebook'}_{datetime.now().strftime('%Y%m%d')}.txt", mime="text/plain", use_container_width=True)
        with col_dl2:
            st.download_button("🌐 HTML 다운로드", html_content, file_name=f"{book_title or 'ebook'}_{datetime.now().strftime('%Y%m%d')}.html", mime="text/html", use_container_width=True)
        
        # RTF 다운로드
        rtf_content = "{\\rtf1\\ansi\\ansicpg949\\deff0\n{\\fonttbl{\\f0\\fnil 맑은 고딕;}}\n\\f0\\fs24\n"
        rtf_content += escape_rtf_unicode(book_title or '') + "\\par\n"
        rtf_content += escape_rtf_unicode(subtitle or '') + "\\par\\par\n"
        for chapter in st.session_state['outline']:
            if chapter in st.session_state['chapters']:
                ch_data = st.session_state['chapters'][chapter]
                if 'subtopic_data' in ch_data:
                    chapter_has_content = any(ch_data['subtopic_data'].get(st_name, {}).get('content') for st_name in ch_data.get('subtopics', []))
                    if chapter_has_content:
                        rtf_content += "\\par\\b " + escape_rtf_unicode(chapter) + "\\b0\\par\\par\n"
                        for st_name in ch_data.get('subtopics', []):
                            st_data = ch_data['subtopic_data'].get(st_name, {})
                            if st_data.get('content'):
                                rtf_content += "\\b " + escape_rtf_unicode(st_name) + "\\b0\\par\n"
                                rtf_content += escape_rtf_unicode(st_data['content']) + "\\par\\par\n"
        rtf_content += "}"
        st.download_button("📗 RTF 다운로드", rtf_content.encode('utf-8'), file_name=f"{book_title or 'ebook'}_{datetime.now().strftime('%Y%m%d')}.rtf", mime="application/rtf", use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 📖 전체 본문")
        pure_content = get_all_content_text()
        if pure_content:
            total_chars = calculate_char_count(pure_content)
            content_count = sum(1 for ch in st.session_state['chapters'].values() for st_data in ch.get('subtopic_data', {}).values() if st_data.get('content'))
            st.success(f"✅ 총 {content_count}개 소제목 | {total_chars:,}자 | 약 {total_chars//500}페이지")
            with st.expander("📖 전체 본문 펼쳐보기", expanded=False):
                for ch in st.session_state['outline']:
                    if ch in st.session_state['chapters']:
                        ch_data = st.session_state['chapters'][ch]
                        if 'subtopic_data' in ch_data:
                            has_content = any(ch_data['subtopic_data'].get(s, {}).get('content') for s in ch_data.get('subtopics', []))
                            if has_content:
                                st.markdown(f"## {ch}")
                                for st_name in ch_data.get('subtopics', []):
                                    st_data = ch_data['subtopic_data'].get(st_name, {})
                                    if st_data.get('content'):
                                        st.markdown(f"**{st_name}**")
                                        st.markdown(clean_content_for_display(st_data['content'], st_name, ch))
        else:
            st.info("💡 아직 작성된 본문이 없습니다.")
    
    with col2:
        st.markdown('<p class="section-label">Marketing</p>', unsafe_allow_html=True)
        st.markdown("### 마케팅 카피")
        if st.button("카피 생성하기", key="marketing_btn"):
            with st.spinner("생성 중..."):
                marketing = generate_marketing_copy(st.session_state.get('book_title', st.session_state['topic']), st.session_state.get('subtitle', ''), st.session_state['topic'], st.session_state['target_persona'])
                st.session_state['marketing_copy'] = marketing
        if st.session_state.get('marketing_copy'):
            st.markdown(f'<div class="info-card">{st.session_state["marketing_copy"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)


# --- 자동 저장 처리 ---
if st.session_state.get('auto_save_trigger'):
    st.session_state['auto_save_trigger'] = False
    auto_save_data = get_auto_save_data()
    auto_save_json = json.dumps(auto_save_data, ensure_ascii=False, indent=2)
    file_name = st.session_state.get('book_title', '전자책') or '전자책'
    file_name = re.sub(r'[^\w\s가-힣-]', '', file_name)[:20]
    st.toast("💾 자동 저장됨!")

# --- 푸터 ---
st.markdown('<div class="premium-footer"><span class="premium-footer-text">전자책 작성 프로그램 — </span><span class="premium-footer-author">남현우 작가</span></div>', unsafe_allow_html=True)
