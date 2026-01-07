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

# --- 페이지 설정 ---
st.set_page_config(
    page_title="전자책 작성 프로그램", 
    layout="wide", 
    page_icon="◆"
)

# --- 지구인사이트 스타일 CSS ---
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    * { font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif; }
    
    .stDeployButton {display:none;} 
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
    [data-testid="collapsedControl"] { display: flex !important; visibility: visible !important; }
    
    .stApp { background: #ffffff; }
    
    .main .block-container { background: #ffffff; padding: 2rem 3rem; max-width: 1200px; }
    
    [data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #eeeeee; }
    [data-testid="stSidebar"] * { color: #222222 !important; }
    [data-testid="stSidebar"] .stProgress > div > div > div > div { background: #222222; border-radius: 10px; }
    
    .stMarkdown, .stText, p, span, label, .stMarkdown p { color: #222222 !important; line-height: 1.7; }
    
    h1 { color: #111111 !important; font-weight: 700 !important; font-size: 2rem !important; letter-spacing: -0.5px; margin-bottom: 1rem !important; }
    h2 { color: #111111 !important; font-weight: 700 !important; font-size: 1.4rem !important; margin-top: 2rem !important; margin-bottom: 1rem !important; }
    h3 { color: #222222 !important; font-weight: 600 !important; font-size: 1.1rem !important; margin-bottom: 0.8rem !important; }
    
    .stTabs [data-baseweb="tab-list"] { background: transparent; gap: 0; border-bottom: 2px solid #eeeeee; padding: 0; }
    .stTabs [data-baseweb="tab"] { background: transparent; color: #888888 !important; border-radius: 0; font-weight: 500; padding: 16px 24px; font-size: 15px; border-bottom: 2px solid transparent; margin-bottom: -2px; transition: all 0.2s; }
    .stTabs [data-baseweb="tab"]:hover { color: #222222 !important; }
    .stTabs [aria-selected="true"] { background: transparent !important; color: #111111 !important; font-weight: 700 !important; border-bottom: 2px solid #111111 !important; }
    
    .stButton > button { width: 100%; border-radius: 30px; font-weight: 600; background: #111111 !important; color: #ffffff !important; border: none !important; padding: 14px 32px; font-size: 15px; transition: all 0.2s; box-shadow: none; }
    .stButton > button:hover { background: #333333 !important; color: #ffffff !important; box-shadow: 0 4px 12px rgba(0,0,0,0.15); transform: translateY(-1px); }
    .stButton > button:active { transform: translateY(0); }
    .stButton > button p, .stButton > button span, .stButton > button div, .stButton > button * { color: #ffffff !important; }
    
    .stDownloadButton > button { background: #2d5a27 !important; color: #ffffff !important; border-radius: 30px; }
    .stDownloadButton > button:hover { background: #3d7a37 !important; }
    .stDownloadButton > button p, .stDownloadButton > button span, .stDownloadButton > button * { color: #ffffff !important; }
    
    .stTextInput > div > div > input, .stTextArea > div > div > textarea { background: #ffffff !important; border: 1px solid #dddddd !important; border-radius: 8px !important; color: #222222 !important; padding: 14px 16px !important; font-size: 15px !important; }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus { border-color: #111111 !important; box-shadow: none !important; }
    .stTextInput > div > div > input::placeholder, .stTextArea > div > div > textarea::placeholder { color: #aaaaaa !important; }
    
    .stSelectbox > div > div { background: #ffffff !important; border: 1px solid #dddddd !important; border-radius: 8px !important; }
    .stSelectbox > div > div > div { color: #222222 !important; }
    
    [data-testid="stMetricValue"] { color: #111111 !important; font-size: 2rem !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #666666 !important; }
    
    .stSuccess { background: #f0f9f0 !important; border: 1px solid #c8e6c9 !important; border-radius: 8px !important; }
    .stSuccess p { color: #2e7d32 !important; }
    .stWarning { background: #fff8e1 !important; border: 1px solid #ffecb3 !important; border-radius: 8px !important; }
    .stWarning p { color: #f57c00 !important; }
    .stError { background: #ffebee !important; border: 1px solid #ffcdd2 !important; border-radius: 8px !important; }
    .stError p { color: #c62828 !important; }
    .stInfo { background: #e3f2fd !important; border: 1px solid #bbdefb !important; border-radius: 8px !important; }
    .stInfo p { color: #1565c0 !important; }
    
    hr { border: none !important; border-top: 1px solid #eeeeee !important; margin: 2rem 0 !important; }
    .stProgress > div > div > div > div { background: #222222; border-radius: 10px; }
    
    .login-container { max-width: 400px; margin: 100px auto; padding: 40px; background: #ffffff; border: 1px solid #eeeeee; border-radius: 20px; text-align: center; }
    .login-title { font-size: 28px; font-weight: 700; color: #111111; margin-bottom: 8px; }
    .login-subtitle { font-size: 15px; color: #888888; margin-bottom: 30px; }
    
    .hero-section { text-align: center; padding: 60px 20px; margin-bottom: 40px; }
    .hero-label { font-size: 13px; font-weight: 600; color: #666666; letter-spacing: 3px; margin-bottom: 16px; text-transform: uppercase; }
    .hero-title { font-size: 42px; font-weight: 800; color: #111111; margin-bottom: 16px; letter-spacing: -1px; line-height: 1.2; }
    .hero-subtitle { font-size: 18px; color: #666666; font-weight: 400; }
    
    .section-label { font-size: 12px; font-weight: 600; color: #888888; letter-spacing: 2px; margin-bottom: 8px; text-transform: uppercase; }
    
    .score-card { background: #f8f8f8; border-radius: 20px; padding: 50px 40px; text-align: center; }
    .score-number { font-size: 80px; font-weight: 800; color: #111111; line-height: 1; margin-bottom: 8px; }
    .score-label { color: #888888; font-size: 14px; font-weight: 500; }
    
    .status-badge { display: inline-block; padding: 8px 20px; border-radius: 20px; font-weight: 600; font-size: 13px; margin-top: 20px; }
    .status-excellent { background: #111111; color: #ffffff; }
    .status-good { background: #f0f0f0; color: #333333; }
    .status-warning { background: #fff3e0; color: #e65100; }
    
    .info-card { background: #f8f8f8; border-radius: 16px; padding: 24px; margin: 16px 0; }
    .info-card-title { font-size: 12px; font-weight: 700; color: #888888; letter-spacing: 1px; margin-bottom: 12px; text-transform: uppercase; }
    .info-card p { color: #333333 !important; font-size: 15px; line-height: 1.8; margin: 8px 0; }
    
    .title-card { background: #ffffff; border: 1px solid #eeeeee; border-radius: 16px; padding: 24px; margin: 12px 0; transition: all 0.2s; }
    .title-card:hover { border-color: #cccccc; box-shadow: 0 4px 20px rgba(0,0,0,0.06); }
    .title-card .card-number { font-size: 12px; font-weight: 600; color: #aaaaaa; margin-bottom: 8px; }
    .title-card .main-title { color: #111111; font-size: 18px; font-weight: 700; margin-bottom: 6px; }
    .title-card .sub-title { color: #666666; font-size: 14px; margin-bottom: 16px; }
    .title-card .reason { color: #444444; font-size: 14px; padding: 14px 16px; background: #f8f8f8; border-radius: 10px; line-height: 1.6; }
    
    .score-item { background: #ffffff; border: 1px solid #eeeeee; border-radius: 12px; padding: 16px 20px; margin: 10px 0; display: flex; justify-content: space-between; align-items: center; }
    .score-item-label { color: #333333; font-weight: 500; font-size: 15px; }
    .score-item-value { color: #111111; font-weight: 700; font-size: 20px; }
    .score-item-reason { color: #666666; font-size: 14px; margin-top: 4px; line-height: 1.5; }
    
    .summary-box { background: #f8f8f8; border-radius: 12px; padding: 20px; margin-top: 20px; }
    .summary-box p { color: #333333 !important; font-size: 15px; line-height: 1.7; }
    
    .premium-footer { text-align: center; padding: 40px 20px; margin-top: 60px; border-top: 1px solid #eeeeee; }
    .premium-footer-text { color: #888888; font-size: 14px; }
    .premium-footer-author { color: #222222; font-weight: 600; }
    
    .empty-state { text-align: center; padding: 60px 20px; background: #f8f8f8; border-radius: 16px; }
    .empty-state p { color: #888888 !important; }
    
    .quick-action-box { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border: 1px dashed #dee2e6; border-radius: 16px; padding: 24px; margin: 16px 0; text-align: center; }
    .quick-action-box p { color: #495057 !important; font-size: 14px; margin-bottom: 12px; }
    
    .target-card { background: #ffffff; border: 2px solid #eeeeee; border-radius: 16px; padding: 20px; margin: 10px 0; cursor: pointer; transition: all 0.2s; }
    .target-card:hover { border-color: #111111; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .target-card.selected { border-color: #111111; background: #f8f8f8; }
    
    .review-card { background: #fff3e0; border-left: 4px solid #ff9800; padding: 16px; margin: 8px 0; border-radius: 0 8px 8px 0; }
    .review-card-negative { background: #ffebee; border-left-color: #f44336; }
    
    .gap-card { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); border-radius: 16px; padding: 20px; margin: 10px 0; }
    .gap-card-title { font-weight: 700; color: #2e7d32; margin-bottom: 8px; }
    
    .roadmap-step { background: #ffffff; border: 1px solid #eeeeee; border-radius: 12px; padding: 20px; margin: 12px 0; position: relative; }
    .roadmap-step::before { content: ''; position: absolute; left: 30px; top: 60px; bottom: -12px; width: 2px; background: #eeeeee; }
    .roadmap-step:last-child::before { display: none; }
    .step-number { width: 40px; height: 40px; background: #111111; color: #ffffff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; margin-right: 16px; }
    
    .next-btn-container { margin-top: 40px; padding-top: 20px; border-top: 1px solid #eeeeee; }
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
    'suggested_targets': None, 'selected_target_idx': None, 'analyzed_pains': None,
    'competitor_reviews': '', 'review_analysis': None, 'market_gaps': None,
    'roadmap_steps': [], 'youtube_summary': '', 'skill_checklist': [],
    'current_tab': 0,
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
# 🆕 새로운 AI 함수들 (추가된 기능)
# ==========================================

def suggest_target_personas(topic):
    """주제 기반 타겟 페르소나 추천"""
    prompt = f"""당신은 전자책 시장 분석 전문가입니다.

[주제]: {topic}

이 주제의 전자책을 구매할 가능성이 가장 높은 타겟 페르소나 5개를 제안해주세요.

각 페르소나는 다음을 포함해야 합니다:
1. 구체적인 인구통계 (나이, 직업, 상황)
2. 핵심 니즈 (왜 이 책이 필요한가)
3. 구매력 수준 (상/중/하)
4. 추정 시장 규모

JSON 형식으로만 출력:
{{
    "personas": [
        {{
            "name": "페르소나 이름 (예: 퇴사 준비 직장인)",
            "demographics": "30대 초반, 대기업 3~5년차, 연봉 4000~5000만원",
            "needs": "본업 외 월 100만원 추가 수입 필요",
            "buying_power": "중상",
            "market_size": "약 50만명 추정",
            "pain_points": ["시간 부족", "뭘 해야 할지 모름", "실패 두려움"]
        }}
    ]
}}"""
    return ask_ai("시장 분석가", prompt, temperature=0.7)


def analyze_target_pains(topic, target_persona):
    """타겟의 고민 자동 분석"""
    prompt = f"""당신은 소비자 심리 전문가입니다.

[주제]: {topic}
[타겟]: {target_persona}

이 타겟이 가진 고민을 깊이 분석해주세요.

분석 항목:
1. 표면적 고민 (직접 말하는 것)
2. 숨겨진 고민 (말 안 하지만 진짜 원하는 것)
3. 감정적 고통 (이 문제로 느끼는 감정)
4. 실패 경험 (과거에 시도했다 실패한 것)
5. 장애물 (해결 못 하는 이유)

JSON 형식으로 출력:
{{
    "surface_pains": ["표면적 고민 1", "표면적 고민 2"],
    "hidden_pains": ["숨겨진 고민 1", "숨겨진 고민 2"],
    "emotional_pains": ["감정적 고통 1", "감정적 고통 2"],
    "past_failures": ["과거 실패 1", "과거 실패 2"],
    "obstacles": ["장애물 1", "장애물 2"],
    "summary": "종합 분석 2~3문장"
}}"""
    return ask_ai("소비자 심리 전문가", prompt, temperature=0.6)


def analyze_competitor_reviews(topic, reviews_text):
    """경쟁사 리뷰 분석 (결핍 추출)"""
    prompt = f"""당신은 시장 조사 전문가입니다. 베스트셀러의 리뷰에서 '결핍'을 찾아내는 것이 임무입니다.

[주제]: {topic}
[분석할 리뷰들]:
{reviews_text}

위 리뷰들을 분석해서 다음을 추출하세요:

1. 부정 리뷰 핵심 키워드 (별점 1~3점 또는 "아쉬워요", "없네요", "부족해요" 등)
2. 5점 리뷰 중에서도 아쉬움을 표현한 내용
3. 독자들이 원하지만 기존 책에 없는 것 (GAP)
4. 이 GAP을 채우면 차별화될 수 있는 콘텐츠 아이디어

JSON 형식으로 출력:
{{
    "negative_keywords": ["키워드1", "키워드2"],
    "negative_reviews": [
        {{"content": "리뷰 내용 요약", "pain_point": "핵심 불만"}},
    ],
    "positive_but_lacking": [
        {{"content": "좋지만 아쉬운 점", "gap": "부족한 부분"}}
    ],
    "market_gaps": [
        {{"gap": "시장의 빈틈", "opportunity": "기회 포인트", "priority": "상/중/하"}}
    ],
    "content_ideas": [
        {{"idea": "콘텐츠 아이디어", "fills_gap": "어떤 GAP을 채우는지"}}
    ],
    "summary": "종합 분석 및 권장 사항"
}}"""
    return ask_ai("시장 조사 전문가", prompt, temperature=0.5)


def generate_gap_based_outline(topic, persona, pain_points, market_gaps):
    """시장 GAP 기반 목차 생성"""
    gaps_text = "\n".join([f"- {gap}" for gap in market_gaps]) if market_gaps else "없음"
    
    prompt = f"""당신은 "부의 추월차선", "역행자", "돈의 속성"을 기획한 편집자입니다.

[주제]: {topic}
[타겟]: {persona}
[타겟의 고민]: {pain_points}

🔥 핵심 차별화 포인트 - 경쟁사가 놓친 시장의 빈틈:
{gaps_text}

위 시장의 빈틈(GAP)을 1순위로 반영하여 목차를 작성하세요.
기존 베스트셀러의 장점은 유지하되, 리뷰에서 지적된 단점을 해결하는 '업그레이드 패치형 전자책'입니다.

[목차 설계 원칙]
1. PART 1: 시장 GAP 중 가장 중요한 것을 첫 챕터로
2. PART 2: 경쟁사에 없는 구체적 실행 가이드/템플릿
3. PART 3: 독자가 바로 따라할 수 있는 체크리스트
4. PART 4: 차별화된 비전 제시

출력 형식:
## PART 1. [GAP 해결 챕터 제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]

## PART 2. [실행 가이드 챕터 제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]

(4개 PART까지)

목차만 출력하세요."""
    return ask_ai("베스트셀러 편집자", prompt, temperature=0.8)


def analyze_market_deep(topic):
    """주제별 심층 시장 분석"""
    prompt = f"""당신은 전자책 시장 분석 전문가입니다.

[분석 주제]: {topic}

다음 항목을 심층 분석해주세요:

1. 시장 규모 추정
   - 국내 전자책 시장에서 이 주제의 예상 규모
   - 월간 검색량 추정
   - 크몽/클래스101 등 관련 강의 수

2. 경쟁 강도 분석
   - 기존 베스트셀러 수
   - 진입 장벽 수준
   - 차별화 가능성

3. 수익 가능성
   - 예상 가격대
   - 월 판매량 추정
   - 연 매출 잠재력

4. 타이밍 분석
   - 트렌드 상승/하락 여부
   - 계절성 유무
   - 최적 출시 시기

5. 리스크 요인
   - 시장 포화도
   - 대체재 위협
   - 규제/법적 이슈

JSON 형식으로 출력:
{{
    "market_size": {{
        "estimate": "추정 규모",
        "monthly_searches": "월 검색량",
        "related_courses": "관련 강의 수",
        "score": 85
    }},
    "competition": {{
        "level": "상/중/하",
        "bestsellers": 10,
        "entry_barrier": "낮음/보통/높음",
        "differentiation_potential": "차별화 가능성 설명",
        "score": 75
    }},
    "profit_potential": {{
        "price_range": "9,900~29,900원",
        "monthly_sales_estimate": "50~100권",
        "annual_revenue": "600만~3000만원",
        "score": 80
    }},
    "timing": {{
        "trend": "상승/정체/하락",
        "seasonality": "있음/없음",
        "best_launch": "추천 출시 시기",
        "score": 70
    }},
    "risks": [
        {{"risk": "리스크 1", "level": "상/중/하", "mitigation": "대응 방안"}}
    ],
    "overall_score": 78,
    "verdict": "적합/보통/부적합",
    "recommendation": "종합 권장 사항 2~3문장"
}}"""
    return ask_ai("시장 분석 전문가", prompt, temperature=0.5)


def summarize_youtube_video(video_url_or_transcript):
    """유튜브 영상 요약 (트랜스크립트 기반)"""
    prompt = f"""당신은 콘텐츠 요약 전문가입니다.

다음 유튜브 영상/트랜스크립트를 분석해주세요:

{video_url_or_transcript}

다음 형식으로 요약:

1. **핵심 메시지** (3줄 이내)
2. **주요 포인트** (5개)
3. **실행 가능한 액션 아이템** (3개)
4. **인용할 만한 문구** (2개)
5. **전자책에 적용할 수 있는 아이디어** (3개)

마크다운 형식으로 출력하세요."""
    return ask_ai("콘텐츠 큐레이터", prompt, temperature=0.6)


def generate_skill_roadmap(topic):
    """실력 키우기 로드맵 생성"""
    prompt = f"""당신은 온라인 교육 전문가입니다.

[주제]: {topic}

이 주제로 전자책을 쓰기 위해 실력을 키우는 로드맵을 만들어주세요.

로드맵 단계:
1. 기초 학습 (1주차)
2. 실전 적용 (2~3주차)
3. 성과 만들기 (4주차)
4. 무료 테스터 모집 (5주차)
5. 전자책 작성 (6주차)

각 단계별로:
- 구체적 할 일
- 추천 학습 자료 (유튜브, 블로그 등)
- 완료 체크리스트
- 예상 소요 시간

JSON 형식으로 출력:
{{
    "roadmap": [
        {{
            "week": 1,
            "title": "기초 학습",
            "description": "설명",
            "tasks": ["할 일 1", "할 일 2"],
            "resources": ["추천 자료 1", "추천 자료 2"],
            "checklist": ["체크 1", "체크 2"],
            "hours": "10시간"
        }}
    ],
    "total_duration": "6주",
    "success_metrics": ["성공 지표 1", "성공 지표 2"]
}}"""
    return ask_ai("교육 설계 전문가", prompt, temperature=0.6)


# ==========================================
# 기존 AI 함수들
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

[원칙 2] 소제목 = 호기심 폭발
- "이게 뭐야?" 싶은 궁금증 유발
- 구체적 숫자, 비유, 반전 활용
- 뻔한 조언 대신 날카로운 통찰

[원칙 3] 심리적 흐름 설계
1부: 충격과 공감 - "내 얘기잖아" + "뭔가 잘못됐구나"
2부: 원인 폭로 - "이래서 안 됐던 거구나"
3부: 해결책 공개 - "이렇게 하면 되는구나"  
4부: 실행과 비전 - "나도 할 수 있겠다"

출력 형식:
## PART 1. [충격적인 챕터 제목]
- [호기심 자극하는 소제목 1]
- [호기심 자극하는 소제목 2]
- [호기심 자극하는 소제목 3]

(4개 PART까지)

목차만 출력하세요."""
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

출력: 번호와 소제목만"""
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

[작가 인터뷰]
{qa_pairs}

[자청 스타일 글쓰기 법칙]
1. 첫 문장 = 뒤통수 한 방
2. 짧은 문장, 강한 임팩트 (15~25자)
3. 스토리 > 설명
4. 숫자로 증명
5. 감정을 건드려라
6. 합쇼체 100% 유지

분량: 1500~2000자

'{subtopic_title}'의 본문만 작성하세요."""
    return ask_ai("베스트셀러 작가", prompt, temperature=0.8)


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
1. "읽는 순간 뒤통수를 맞은 느낌"
2. "이건 나만 몰랐던 거 아냐?"
3. "구체적 숫자는 신뢰를 만든다"
4. "짧을수록 강하다" - 7자 이내 메인 타이틀

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

출력 형식:
1. [한 줄 컨셉]
   → 왜 끌리는가

(5개까지)"""
    return ask_ai("카피라이터", prompt, temperature=0.9)


def generate_interview_questions(subtopic_title, chapter_title, topic):
    prompt = f"""당신은 베스트셀러 작가의 고스트라이터입니다.
'{topic}' 전자책의 '{chapter_title}' 챕터 중 '{subtopic_title}' 소제목 부분을 쓰기 위해 작가를 인터뷰합니다.

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

[목표 스타일]
{style_guide.get(style, style_guide["친근한"])}

다듬어진 글만 출력하세요."""
    return ask_ai("에디터", prompt, temperature=0.7)


def check_quality(content):
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

🎯 총평"""
    return ask_ai("베스트셀러 편집자", prompt, temperature=0.6)


def regenerate_chapter_outline(chapter_num, topic, persona, current_outline):
    prompt = f"""주제 '{topic}'의 전자책에서 챕터 {chapter_num}을 새롭게 작성해주세요.

현재 목차:
{chr(10).join(current_outline)}

챕터 {chapter_num}만 새롭게 작성하세요.

출력 형식:
## [새로운 챕터 제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]
"""
    return ask_ai("베스트셀러 편집자", prompt, temperature=0.85)


def regenerate_single_subtopic(chapter_title, subtopic_num, topic, current_subtopics):
    prompt = f"""주제 '{topic}'의 챕터 '{chapter_title}'에서 소제목 {subtopic_num}번을 새롭게 작성해주세요.

현재 소제목들:
{chr(10).join([f"- {s}" for s in current_subtopics])}

출력: 새 소제목 한 줄만
"""
    result = ask_ai("카피라이터", prompt, temperature=0.85)
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

1. 크몽 상품 제목 (40자 이내)
2. 상세페이지 헤드라인 3개
3. 구매 유도 문구 (CTA) 3개
4. 인스타그램 홍보 문구
5. 블로그 포스팅 제목 3개"""
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

tabs = st.tabs(["① 주제 & 시장분석", "② 타겟 & 컨셉", "③ 경쟁사 분석", "④ 목차 설계", "⑤ 본문 작성", "⑥ 문체 다듬기", "⑦ 최종 출력", "⑧ 실력 로드맵"])

# ==========================================
# === TAB 1: 주제 선정 & 시장 분석 ===
# ==========================================
with tabs[0]:
    st.markdown("## 주제 선정 & 시장 분석")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<p class="section-label">Step 01</p>', unsafe_allow_html=True)
        st.markdown("### 주제 입력")
        topic_input = st.text_input("어떤 주제로 전자책을 쓰고 싶으세요?", value=st.session_state['topic'], placeholder="예: 크몽으로 월 500만원 벌기", key="topic_input_tab1")
        if topic_input != st.session_state['topic']:
            st.session_state['topic'] = topic_input
            st.session_state['topic_score'] = None
            st.session_state['score_details'] = None
        
        st.markdown('<div class="info-card"><div class="info-card-title">좋은 주제의 조건</div><p>• 내가 직접 경험하고 성과를 낸 것</p><p>• 사람들이 돈 주고 배우고 싶어하는 것</p><p>• 구체적인 결과를 약속할 수 있는 것</p></div>', unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("📊 빠른 적합도 분석", key="quick_analyze_btn"):
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
                            st.error("분석 결과 파싱 오류")
        
        with col_btn2:
            if st.button("🔬 심층 시장 분석", key="deep_analyze_btn"):
                if not topic_input:
                    st.error("주제를 입력해주세요.")
                else:
                    with st.spinner("심층 분석 중... (30초~1분)"):
                        result = analyze_market_deep(topic_input)
                        try:
                            json_match = re.search(r'\{[\s\S]*\}', result)
                            if json_match:
                                st.session_state['deep_market_analysis'] = json.loads(json_match.group())
                        except:
                            st.session_state['deep_market_analysis'] = result
    
    with col2:
        st.markdown('<p class="section-label">Step 02</p>', unsafe_allow_html=True)
        st.markdown("### 분석 결과")
        
        if st.session_state.get('topic_score') is not None:
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
        
        if st.session_state.get('deep_market_analysis'):
            st.markdown("---")
            st.markdown("#### 🔬 심층 시장 분석")
            analysis = st.session_state['deep_market_analysis']
            
            if isinstance(analysis, dict):
                # 시장 규모
                if 'market_size' in analysis:
                    with st.expander("📈 시장 규모", expanded=True):
                        ms = analysis['market_size']
                        st.write(f"**추정 규모:** {ms.get('estimate', 'N/A')}")
                        st.write(f"**월 검색량:** {ms.get('monthly_searches', 'N/A')}")
                        st.write(f"**관련 강의 수:** {ms.get('related_courses', 'N/A')}")
                
                # 경쟁 분석
                if 'competition' in analysis:
                    with st.expander("⚔️ 경쟁 분석"):
                        comp = analysis['competition']
                        st.write(f"**경쟁 강도:** {comp.get('level', 'N/A')}")
                        st.write(f"**차별화 가능성:** {comp.get('differentiation_potential', 'N/A')}")
                
                # 수익 잠재력
                if 'profit_potential' in analysis:
                    with st.expander("💰 수익 잠재력"):
                        profit = analysis['profit_potential']
                        st.write(f"**예상 가격대:** {profit.get('price_range', 'N/A')}")
                        st.write(f"**월 판매 추정:** {profit.get('monthly_sales_estimate', 'N/A')}")
                        st.write(f"**연 매출 잠재력:** {profit.get('annual_revenue', 'N/A')}")
                
                # 종합 권장
                if 'recommendation' in analysis:
                    st.success(f"**💡 권장사항:** {analysis['recommendation']}")
            else:
                st.markdown(analysis)
        
        if not st.session_state.get('topic_score') and not st.session_state.get('deep_market_analysis'):
            st.markdown('<div class="empty-state"><p>주제를 입력하고 분석 버튼을 눌러주세요</p></div>', unsafe_allow_html=True)
    
    # 다음 버튼
    st.markdown('<div class="next-btn-container"></div>', unsafe_allow_html=True)
    if st.button("다음 단계로 → 타겟 & 컨셉", key="next_to_tab2", use_container_width=True):
        st.session_state['current_tab'] = 1
        st.rerun()


# ==========================================
# === TAB 2: 타겟 & 컨셉 (레이아웃 수정됨) ===
# ==========================================
with tabs[1]:
    st.markdown("## 타겟 설정 & 제목 생성")
    
    if not st.session_state['topic']:
        st.info("💡 주제를 먼저 입력하면 더 정확한 결과를 얻을 수 있어요.")
        topic_here = st.text_input("주제 입력", placeholder="예: 크몽으로 월 500만원 벌기", key="topic_tab2_input")
        if topic_here:
            st.session_state['topic'] = topic_here
    
    # ========== 좌측: 타겟 정의 ==========
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<p class="section-label">Step 01</p>', unsafe_allow_html=True)
        st.markdown("### 타겟 정의")
        
        # AI 타겟 추천 버튼
        if st.button("🎯 AI가 타겟 추천해주기", key="suggest_targets_btn"):
            if not st.session_state['topic']:
                st.error("주제를 먼저 입력해주세요.")
            else:
                with st.spinner("타겟 분석 중..."):
                    result = suggest_target_personas(st.session_state['topic'])
                    try:
                        json_match = re.search(r'\{[\s\S]*\}', result)
                        if json_match:
                            st.session_state['suggested_targets'] = json.loads(json_match.group())
                    except:
                        st.error("타겟 추천 실패")
        
        # 추천 타겟 표시
        if st.session_state.get('suggested_targets'):
            st.markdown("**🎯 추천 타겟 (클릭하여 선택)**")
            personas = st.session_state['suggested_targets'].get('personas', [])
            
            for i, p in enumerate(personas):
                with st.expander(f"**{p.get('name', f'타겟 {i+1}')}** - 구매력: {p.get('buying_power', 'N/A')}"):
                    st.write(f"**인구통계:** {p.get('demographics', '')}")
                    st.write(f"**핵심 니즈:** {p.get('needs', '')}")
                    st.write(f"**시장 규모:** {p.get('market_size', '')}")
                    
                    if st.button(f"이 타겟 선택", key=f"select_target_{i}"):
                        st.session_state['target_persona'] = f"{p.get('name', '')} - {p.get('demographics', '')}"
                        st.session_state['selected_target_idx'] = i
                        # 고민 자동 분석
                        with st.spinner("고민 분석 중..."):
                            pain_result = analyze_target_pains(st.session_state['topic'], st.session_state['target_persona'])
                            try:
                                json_match = re.search(r'\{[\s\S]*\}', pain_result)
                                if json_match:
                                    st.session_state['analyzed_pains'] = json.loads(json_match.group())
                                    # 고민 자동 채우기
                                    pains = st.session_state['analyzed_pains']
                                    all_pains = pains.get('surface_pains', []) + pains.get('hidden_pains', [])
                                    st.session_state['pain_points'] = ", ".join(all_pains[:5])
                            except:
                                pass
                        st.rerun()
        
        st.markdown("---")
        
        # 직접 입력
        st.markdown("**또는 직접 입력:**")
        persona = st.text_area("누구한테 판매하실 건가요?", value=st.session_state['target_persona'], placeholder="예: 30대 직장인, 퇴근 후 부업으로 월 100만원 추가 수입을 원하는 사람", height=80, key="persona_input")
        st.session_state['target_persona'] = persona
        
        # 고민 분석 결과 표시
        if st.session_state.get('analyzed_pains'):
            pains = st.session_state['analyzed_pains']
            with st.expander("🔍 AI 분석: 타겟의 고민", expanded=True):
                if pains.get('surface_pains'):
                    st.markdown("**표면적 고민:**")
                    for p in pains['surface_pains']:
                        st.write(f"• {p}")
                if pains.get('hidden_pains'):
                    st.markdown("**숨겨진 고민:**")
                    for p in pains['hidden_pains']:
                        st.write(f"• {p}")
                if pains.get('summary'):
                    st.info(pains['summary'])
        
        pain_points = st.text_area("독자의 가장 큰 고민은?", value=st.session_state['pain_points'], placeholder="AI가 자동 분석하거나 직접 입력하세요", height=80, key="pain_input")
        st.session_state['pain_points'] = pain_points
        
        # 수동 고민 분석 버튼
        if persona and st.button("🔍 고민 AI 분석", key="analyze_pains_btn"):
            with st.spinner("고민 분석 중..."):
                pain_result = analyze_target_pains(st.session_state['topic'], persona)
                try:
                    json_match = re.search(r'\{[\s\S]*\}', pain_result)
                    if json_match:
                        st.session_state['analyzed_pains'] = json.loads(json_match.group())
                        pains = st.session_state['analyzed_pains']
                        all_pains = pains.get('surface_pains', []) + pains.get('hidden_pains', [])
                        st.session_state['pain_points'] = ", ".join(all_pains[:5])
                        st.rerun()
                except:
                    st.error("분석 실패")
    
    # ========== 우측: 제목 생성 & 최종 선택 ==========
    with col2:
        st.markdown('<p class="section-label">Step 02</p>', unsafe_allow_html=True)
        st.markdown("### 제목 생성")
        
        if st.button("✨ 제목 생성하기", key="title_gen_btn"):
            if not st.session_state['topic']:
                st.error("주제를 먼저 입력해주세요.")
            else:
                with st.spinner("제목 생성 중..."):
                    titles_result = generate_titles_advanced(st.session_state['topic'], st.session_state['target_persona'], st.session_state['pain_points'])
                    try:
                        json_match = re.search(r'\{[\s\S]*\}', titles_result)
                        if json_match:
                            st.session_state['generated_titles'] = json.loads(json_match.group())
                    except:
                        st.session_state['generated_titles'] = None
        
        if st.session_state.get('generated_titles'):
            titles_data = st.session_state['generated_titles']
            if 'titles' in titles_data:
                for i, t in enumerate(titles_data['titles'][:3], 1):
                    st.markdown(f'<div class="title-card"><div class="card-number">TITLE 0{i}</div><div class="main-title">{t.get("title", "")}</div><div class="sub-title">{t.get("subtitle", "")}</div><div class="reason">{t.get("why_works", "")}</div></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown('<p class="section-label">Step 03</p>', unsafe_allow_html=True)
        st.markdown("### 최종 선택")
        st.session_state['book_title'] = st.text_input("제목", value=st.session_state['book_title'], placeholder="최종 제목을 입력하세요", key="final_title_input")
        st.session_state['subtitle'] = st.text_input("부제", value=st.session_state['subtitle'], placeholder="부제를 입력하세요", key="final_subtitle_input")
        
        # 한 줄 컨셉
        st.markdown("---")
        if st.button("💡 한 줄 컨셉 생성", key="concept_gen_btn"):
            if st.session_state['topic'] and persona:
                with st.spinner("생성 중..."):
                    concept = generate_concept(st.session_state['topic'], persona, pain_points)
                    st.session_state['one_line_concept'] = concept
        
        if st.session_state['one_line_concept']:
            st.markdown(f'<div class="info-card">{st.session_state["one_line_concept"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
    
    # 다음 버튼
    st.markdown('<div class="next-btn-container"></div>', unsafe_allow_html=True)
    if st.button("다음 단계로 → 경쟁사 분석", key="next_to_tab3", use_container_width=True):
        st.session_state['current_tab'] = 2
        st.rerun()


# ==========================================
# === TAB 3: 경쟁사 리뷰 분석 (신규) ===
# ==========================================
with tabs[2]:
    st.markdown("## 경쟁사 리뷰 분석")
    st.markdown("**🔥 베스트셀러의 리뷰를 분석해서 시장의 '빈틈'을 찾아냅니다**")
    
    st.markdown('<div class="info-card"><div class="info-card-title">💡 사용 방법</div><p>1. 크몽, yes24, 알라딘 등에서 경쟁 전자책의 리뷰를 복사합니다</p><p>2. 특히 별점 1~3점 리뷰, "아쉬워요" 등의 부정적 피드백을 포함하세요</p><p>3. AI가 분석해서 차별화 포인트를 찾아줍니다</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<p class="section-label">Step 01</p>', unsafe_allow_html=True)
        st.markdown("### 리뷰 입력")
        
        reviews_input = st.text_area(
            "경쟁사 리뷰 붙여넣기",
            value=st.session_state.get('competitor_reviews', ''),
            height=400,
            placeholder="""예시:
★★★☆☆ (3점) - 내용은 좋은데 실제로 따라할 수 있는 템플릿이 없어요.

★★☆☆☆ (2점) - 2023년 기준이라 지금은 안 맞는 정보가 많네요.

★★★★★ (5점) - 좋긴 한데... 초보자용이라 저한텐 너무 쉬웠어요.

★★★☆☆ (3점) - PDF 형식이라 모바일에서 보기 불편함""",
            key="reviews_input"
        )
        st.session_state['competitor_reviews'] = reviews_input
        
        if st.button("🔍 리뷰 분석하기", key="analyze_reviews_btn"):
            if not reviews_input.strip():
                st.error("리뷰를 입력해주세요.")
            elif not st.session_state['topic']:
                st.error("주제를 먼저 입력해주세요.")
            else:
                with st.spinner("리뷰 분석 중... (AI가 결핍을 추출합니다)"):
                    result = analyze_competitor_reviews(st.session_state['topic'], reviews_input)
                    try:
                        json_match = re.search(r'\{[\s\S]*\}', result)
                        if json_match:
                            st.session_state['review_analysis'] = json.loads(json_match.group())
                    except:
                        st.session_state['review_analysis'] = result
    
    with col2:
        st.markdown('<p class="section-label">Step 02</p>', unsafe_allow_html=True)
        st.markdown("### 분석 결과")
        
        if st.session_state.get('review_analysis'):
            analysis = st.session_state['review_analysis']
            
            if isinstance(analysis, dict):
                # 부정 키워드
                if analysis.get('negative_keywords'):
                    st.markdown("**🚨 부정 리뷰 핵심 키워드:**")
                    keywords = " | ".join([f"`{k}`" for k in analysis['negative_keywords']])
                    st.markdown(keywords)
                
                st.markdown("---")
                
                # 시장의 빈틈 (GAP)
                if analysis.get('market_gaps'):
                    st.markdown("**🎯 시장의 빈틈 (차별화 기회)**")
                    gaps = analysis['market_gaps']
                    st.session_state['market_gaps'] = [g.get('gap', '') for g in gaps]
                    
                    for i, gap in enumerate(gaps):
                        priority_color = "#f44336" if gap.get('priority') == "상" else ("#ff9800" if gap.get('priority') == "중" else "#4caf50")
                        st.markdown(f"""
                        <div class="gap-card">
                            <div class="gap-card-title">GAP {i+1}: {gap.get('gap', '')}</div>
                            <p><strong>기회:</strong> {gap.get('opportunity', '')}</p>
                            <p><strong>우선순위:</strong> <span style="color:{priority_color};font-weight:bold;">{gap.get('priority', '')}</span></p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # 콘텐츠 아이디어
                if analysis.get('content_ideas'):
                    with st.expander("💡 차별화 콘텐츠 아이디어"):
                        for idea in analysis['content_ideas']:
                            st.write(f"• **{idea.get('idea', '')}** - {idea.get('fills_gap', '')}")
                
                # 종합 분석
                if analysis.get('summary'):
                    st.success(f"**📊 종합 분석:** {analysis['summary']}")
            else:
                st.markdown(analysis)
        else:
            st.markdown('<div class="empty-state"><p>리뷰를 입력하고 분석 버튼을 눌러주세요</p><p>경쟁사의 약점이 당신의 기회입니다!</p></div>', unsafe_allow_html=True)
    
    # 다음 버튼
    st.markdown('<div class="next-btn-container"></div>', unsafe_allow_html=True)
    if st.button("다음 단계로 → 목차 설계 (GAP 반영)", key="next_to_tab4", use_container_width=True):
        st.session_state['current_tab'] = 3
        st.rerun()


# ==========================================
# === TAB 4: 목차 설계 ===
# ==========================================
with tabs[3]:
    st.markdown("## 목차 설계")
    
    # GAP 기반 목차 생성 안내
    if st.session_state.get('market_gaps'):
        st.success(f"✅ 경쟁사 분석에서 {len(st.session_state['market_gaps'])}개의 시장 GAP이 발견되었습니다. 이를 목차에 반영합니다!")
    
    st.markdown("### 🎯 작업 방식 선택")
    outline_mode = st.radio("목차를 어떻게 만드시겠어요?", 
                           ["🤖 AI 자동 생성 (GAP 반영)", "🔥 GAP 기반 목차 생성", "✍️ 내가 직접 입력"], 
                           horizontal=True, key="outline_mode_radio")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if outline_mode == "🤖 AI 자동 생성 (GAP 반영)":
            st.markdown('<p class="section-label">자동 목차 생성</p>', unsafe_allow_html=True)
            
            if not st.session_state['topic']:
                st.warning("💡 주제를 먼저 입력해주세요")
            
            if st.button("🚀 목차 생성하기", key="outline_btn"):
                if not st.session_state['topic']:
                    st.error("주제를 먼저 입력해주세요.")
                else:
                    with st.spinner("목차 설계 중..."):
                        outline_text = generate_outline(st.session_state['topic'], st.session_state['target_persona'], st.session_state['pain_points'])
                        lines = outline_text.split('\n')
                        chapters = []
                        current_chapter = None
                        chapter_subtopics = {}
                        
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                            if line.startswith('##') or 'PART' in line.upper():
                                chapter_name = line.lstrip('#').strip()
                                chapter_name = re.sub(r'\*\*(.+?)\*\*', r'\1', chapter_name)
                                if chapter_name and 'PART' in chapter_name.upper():
                                    current_chapter = chapter_name
                                    chapters.append(current_chapter)
                                    chapter_subtopics[current_chapter] = []
                            elif current_chapter and line.startswith('-'):
                                subtopic = line.lstrip('- ').strip()
                                subtopic = re.sub(r'\*\*(.+?)\*\*', r'\1', subtopic)
                                subtopic = re.sub(r'^\d+\.\d+\s*', '', subtopic)
                                subtopic = re.sub(r'^\d+\.\s*', '', subtopic)
                                if subtopic and len(subtopic) > 2:
                                    chapter_subtopics[current_chapter].append(subtopic)
                        
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
        
        elif outline_mode == "🔥 GAP 기반 목차 생성":
            st.markdown('<p class="section-label">GAP 기반 목차 생성</p>', unsafe_allow_html=True)
            
            if not st.session_state.get('market_gaps'):
                st.warning("⚠️ 먼저 '③ 경쟁사 분석' 탭에서 리뷰 분석을 해주세요.")
            else:
                st.markdown("**발견된 시장 GAP:**")
                for gap in st.session_state['market_gaps']:
                    st.write(f"• {gap}")
                
                if st.button("🔥 GAP 반영 목차 생성", key="gap_outline_btn"):
                    with st.spinner("GAP 기반 목차 생성 중..."):
                        outline_text = generate_gap_based_outline(
                            st.session_state['topic'],
                            st.session_state['target_persona'],
                            st.session_state['pain_points'],
                            st.session_state['market_gaps']
                        )
                        # 파싱 로직 (동일)
                        lines = outline_text.split('\n')
                        chapters = []
                        current_chapter = None
                        chapter_subtopics = {}
                        
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                            if line.startswith('##') or 'PART' in line.upper():
                                chapter_name = line.lstrip('#').strip()
                                chapter_name = re.sub(r'\*\*(.+?)\*\*', r'\1', chapter_name)
                                if chapter_name:
                                    current_chapter = chapter_name
                                    chapters.append(current_chapter)
                                    chapter_subtopics[current_chapter] = []
                            elif current_chapter and line.startswith('-'):
                                subtopic = line.lstrip('- ').strip()
                                subtopic = re.sub(r'\*\*(.+?)\*\*', r'\1', subtopic)
                                if subtopic and len(subtopic) > 2:
                                    chapter_subtopics[current_chapter].append(subtopic)
                        
                        if chapters:
                            st.session_state['outline'] = chapters
                            for ch in chapters:
                                subtopics = chapter_subtopics.get(ch, [])
                                st.session_state['chapters'][ch] = {
                                    'subtopics': subtopics,
                                    'subtopic_data': {st: {'questions': [], 'answers': [], 'content': ''} for st in subtopics}
                                }
                            st.success(f"✅ GAP 반영 목차 생성 완료!")
                            st.rerun()
        
        else:  # 직접 입력
            st.markdown('<p class="section-label">직접 입력</p>', unsafe_allow_html=True)
            existing_outline = ""
            if st.session_state['outline']:
                for ch in st.session_state['outline']:
                    existing_outline += f"## {ch}\n"
                    if ch in st.session_state['chapters']:
                        for st_name in st.session_state['chapters'][ch].get('subtopics', []):
                            existing_outline += f"- {st_name}\n"
            
            manual_outline = st.text_area("목차 입력", value=existing_outline, height=350, 
                                         placeholder="## PART 1. 제목\n- 소제목1\n- 소제목2", key="manual_outline_input")
            
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
                        if line.startswith('##') or any(line.lower().startswith(kw) for kw in ['챕터', 'chapter', 'part']):
                            chapter_name = line.lstrip('#').strip()
                            current_chapter = chapter_name
                            chapters.append(current_chapter)
                            chapter_subtopics[current_chapter] = []
                        elif current_chapter and line.startswith('-'):
                            subtopic = line.lstrip('- ').strip()
                            if subtopic:
                                chapter_subtopics[current_chapter].append(subtopic)
                    
                    st.session_state['outline'] = chapters
                    for ch in chapters:
                        subtopics = chapter_subtopics.get(ch, [])
                        st.session_state['chapters'][ch] = {'subtopics': subtopics, 'subtopic_data': {st_name: {'questions': [], 'answers': [], 'content': ''} for st_name in subtopics}}
                    st.success(f"✅ 저장 완료!")
                    st.rerun()
        
        if 'full_outline' in st.session_state and st.session_state['full_outline']:
            st.markdown("**📋 현재 목차**")
            st.code(st.session_state['full_outline'], language=None)
    
    with col2:
        st.markdown('<p class="section-label">목차 관리</p>', unsafe_allow_html=True)
        st.markdown("### 📋 현재 목차")
        
        if st.session_state['outline']:
            for i, chapter in enumerate(st.session_state['outline']):
                subtopic_count = len(st.session_state['chapters'].get(chapter, {}).get('subtopics', []))
                with st.expander(f"**{chapter}** ({subtopic_count}개)", expanded=False):
                    # 챕터 편집
                    new_title = st.text_input("챕터 제목", value=chapter, key=f"edit_ch_{i}", label_visibility="collapsed")
                    if new_title != chapter and new_title.strip():
                        if st.button("💾 저장", key=f"save_ch_{i}"):
                            st.session_state['outline'][i] = new_title
                            if chapter in st.session_state['chapters']:
                                st.session_state['chapters'][new_title] = st.session_state['chapters'].pop(chapter)
                            st.rerun()
                    
                    # 소제목 표시
                    if chapter in st.session_state['chapters']:
                        for j, st_name in enumerate(st.session_state['chapters'][chapter].get('subtopics', [])):
                            st.write(f"{j+1}. {st_name}")
            
            if st.button("➕ 새 챕터 추가", key="add_chapter"):
                new_ch = f"PART {len(st.session_state['outline'])+1}. 새 챕터"
                st.session_state['outline'].append(new_ch)
                st.session_state['chapters'][new_ch] = {'subtopics': [], 'subtopic_data': {}}
                st.rerun()
        else:
            st.markdown('<div class="empty-state"><p>왼쪽에서 목차를 생성하세요</p></div>', unsafe_allow_html=True)
    
    # 다음 버튼
    st.markdown('<div class="next-btn-container"></div>', unsafe_allow_html=True)
    if st.button("다음 단계로 → 본문 작성", key="next_to_tab5", use_container_width=True):
        st.session_state['current_tab'] = 4
        st.rerun()


# ==========================================
# === TAB 5: 본문 작성 ===
# ==========================================
with tabs[4]:
    st.markdown("## 본문 작성")
    
    if not st.session_state['outline']:
        st.warning("⚠️ 먼저 '④ 목차 설계' 탭에서 목차를 작성해주세요.")
        if st.button("← 목차 설계로 이동"):
            st.session_state['current_tab'] = 3
        st.stop()
    
    chapter_list = [item for item in st.session_state['outline'] if not item.strip().startswith('-')]
    if not chapter_list:
        st.warning("⚠️ 챕터가 없습니다.")
        st.stop()
    
    selected_chapter = st.selectbox("📚 챕터 선택", chapter_list, key="chapter_select_main")
    
    if selected_chapter not in st.session_state['chapters']:
        st.session_state['chapters'][selected_chapter] = {'subtopics': [], 'subtopic_data': {}}
    chapter_data = st.session_state['chapters'][selected_chapter]
    
    # 소제목 목록
    with st.expander(f"📋 '{selected_chapter}' 소제목 ({len(chapter_data.get('subtopics', []))}개)", expanded=True):
        if chapter_data.get('subtopics'):
            for j, st_name in enumerate(chapter_data['subtopics']):
                has_content = bool(chapter_data['subtopic_data'].get(st_name, {}).get('content', '').strip())
                status_icon = "✅" if has_content else "⬜"
                st.write(f"{status_icon} {j+1}. {st_name}")
        else:
            st.info("소제목이 없습니다.")
        
        # 소제목 추가
        col_add1, col_add2 = st.columns([4, 1])
        with col_add1:
            new_subtopic = st.text_input("새 소제목", placeholder="직접 입력...", key=f"add_st_{selected_chapter}", label_visibility="collapsed")
        with col_add2:
            if st.button("➕", key=f"add_st_btn_{selected_chapter}"):
                if new_subtopic.strip() and new_subtopic not in chapter_data['subtopics']:
                    chapter_data['subtopics'].append(new_subtopic)
                    chapter_data['subtopic_data'][new_subtopic] = {'questions': [], 'answers': [], 'content': ''}
                    st.rerun()
    
    st.markdown("---")
    
    if chapter_data['subtopics']:
        st.markdown("### ✍️ 본문 작성")
        selected_subtopic = st.selectbox("작성할 소제목", chapter_data['subtopics'], key="subtopic_select",
                                        format_func=lambda x: f"{'✅' if chapter_data['subtopic_data'].get(x, {}).get('content') else '⬜'} {x}")
        
        # 진행률
        completed = sum(1 for s in chapter_data['subtopics'] if chapter_data['subtopic_data'].get(s, {}).get('content'))
        total = len(chapter_data['subtopics'])
        st.progress(completed / total if total > 0 else 0)
        st.caption(f"진행: {completed}/{total}")
        
        if selected_subtopic:
            if selected_subtopic not in chapter_data['subtopic_data']:
                chapter_data['subtopic_data'][selected_subtopic] = {'questions': [], 'answers': [], 'content': ''}
            subtopic_data = chapter_data['subtopic_data'][selected_subtopic]
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown(f"### 🎤 인터뷰: {selected_subtopic}")
                if st.button("🎤 질문 생성", key="gen_q"):
                    with st.spinner("질문 생성 중..."):
                        q_text = generate_interview_questions(selected_subtopic, selected_chapter, st.session_state['topic'])
                        questions = re.findall(r'Q\d+:\s*(.+)', q_text)
                        if not questions:
                            questions = [q.strip() for q in q_text.split('\n') if q.strip() and '?' in q][:3]
                        subtopic_data['questions'] = questions
                        subtopic_data['answers'] = [''] * len(questions)
                        st.rerun()
                
                if subtopic_data['questions']:
                    for i, q in enumerate(subtopic_data['questions']):
                        st.markdown(f"**Q{i+1}.** {q}")
                        if i >= len(subtopic_data['answers']):
                            subtopic_data['answers'].append('')
                        subtopic_data['answers'][i] = st.text_area(f"A{i+1}", value=subtopic_data['answers'][i], key=f"ans_{i}", height=80, label_visibility="collapsed")
            
            with col2:
                st.markdown(f"### 📝 본문: {selected_subtopic}")
                has_answers = subtopic_data.get('questions') and any(a.strip() for a in subtopic_data.get('answers', []))
                
                if has_answers:
                    if st.button("✨ 본문 생성", key="gen_content"):
                        with st.spinner("집필 중... (30초~1분)"):
                            content = generate_subtopic_content(selected_subtopic, selected_chapter, subtopic_data['questions'], subtopic_data['answers'], st.session_state['topic'], st.session_state['target_persona'])
                            subtopic_data['content'] = content
                            st.rerun()
                else:
                    st.info("👈 먼저 인터뷰 질문에 답변하세요")
                
                edited_content = st.text_area("본문", value=subtopic_data.get('content', ''), height=400, key="content_edit", label_visibility="collapsed")
                subtopic_data['content'] = edited_content
                
                if edited_content:
                    st.caption(f"📊 {calculate_char_count(edited_content):,}자")
    
    # 다음 버튼
    st.markdown('<div class="next-btn-container"></div>', unsafe_allow_html=True)
    if st.button("다음 단계로 → 문체 다듬기", key="next_to_tab6", use_container_width=True):
        st.session_state['current_tab'] = 5
        st.rerun()


# ==========================================
# === TAB 6: 문체 다듬기 ===
# ==========================================
with tabs[5]:
    st.markdown("## 문체 다듬기 & 품질 검사")
    
    has_content = any(st_data.get('content') for ch_data in st.session_state['chapters'].values() for st_data in ch_data.get('subtopic_data', {}).values())
    
    if not has_content:
        st.info("💡 먼저 본문을 작성해주세요.")
        direct_content = st.text_area("또는 직접 입력", height=300, placeholder="다듬고 싶은 텍스트...")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 문체 다듬기")
        content_options = []
        for ch in st.session_state['outline']:
            if ch in st.session_state['chapters']:
                ch_data = st.session_state['chapters'][ch]
                for st_name, st_data in ch_data.get('subtopic_data', {}).items():
                    if st_data.get('content'):
                        content_options.append(f"{ch} > {st_name}")
        
        if content_options:
            selected_content = st.selectbox("콘텐츠 선택", content_options, key="refine_select")
        
        style = st.selectbox("목표 스타일", ["친근한", "전문적", "직설적", "스토리텔링"])
        
        if st.button("✨ 문체 다듬기", key="refine_btn"):
            content_to_refine = ""
            if content_options and 'selected_content' in dir():
                parts = selected_content.split(" > ")
                if len(parts) == 2:
                    ch, st_name = parts
                    content_to_refine = st.session_state['chapters'][ch]['subtopic_data'][st_name]['content']
            
            if content_to_refine:
                with st.spinner("다듬는 중..."):
                    refined = refine_content(content_to_refine, style)
                    st.session_state['refined_content'] = refined
        
        if st.session_state.get('refined_content'):
            st.text_area("다듬어진 본문", value=st.session_state['refined_content'], height=400)
    
    with col2:
        st.markdown("### 품질 검사")
        if st.button("🔍 베스트셀러 체크", key="quality_btn"):
            content_to_check = ""
            if content_options and 'selected_content' in dir():
                parts = selected_content.split(" > ")
                if len(parts) == 2:
                    ch, st_name = parts
                    content_to_check = st.session_state['chapters'][ch]['subtopic_data'][st_name]['content']
            
            if content_to_check:
                with st.spinner("분석 중..."):
                    st.session_state['quality_result'] = check_quality(content_to_check)
        
        if st.session_state.get('quality_result'):
            st.markdown(st.session_state['quality_result'])
    
    # 다음 버튼
    st.markdown('<div class="next-btn-container"></div>', unsafe_allow_html=True)
    if st.button("다음 단계로 → 최종 출력", key="next_to_tab7", use_container_width=True):
        st.session_state['current_tab'] = 6
        st.rerun()


# ==========================================
# === TAB 7: 최종 출력 ===
# ==========================================
with tabs[6]:
    st.markdown("## 최종 출력 & 마케팅")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
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
<head><meta charset="UTF-8"><title>{book_title or '전자책'}</title>
<style>body {{ font-family: 'Pretendard', sans-serif; max-width: 800px; margin: 0 auto; padding: 40px 20px; line-height: 1.8; }}</style>
</head>
<body>{full_book_html}</body>
</html>"""
        
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button("📄 TXT 다운로드", full_book_txt, file_name=f"{book_title or 'ebook'}.txt", mime="text/plain", use_container_width=True)
        with col_dl2:
            st.download_button("🌐 HTML 다운로드", html_content, file_name=f"{book_title or 'ebook'}.html", mime="text/html", use_container_width=True)
        
        # 통계
        pure_content = get_all_content_text()
        if pure_content:
            total_chars = calculate_char_count(pure_content)
            st.success(f"✅ 총 {total_chars:,}자 | 약 {total_chars//500}페이지")
    
    with col2:
        st.markdown("### 마케팅 카피")
        if st.button("카피 생성", key="marketing_btn"):
            with st.spinner("생성 중..."):
                marketing = generate_marketing_copy(st.session_state.get('book_title', ''), st.session_state.get('subtitle', ''), st.session_state['topic'], st.session_state['target_persona'])
                st.session_state['marketing_copy'] = marketing
        
        if st.session_state.get('marketing_copy'):
            st.markdown(st.session_state['marketing_copy'])
    
    # 다음 버튼
    st.markdown('<div class="next-btn-container"></div>', unsafe_allow_html=True)
    if st.button("보너스 → 실력 키우기 로드맵", key="next_to_tab8", use_container_width=True):
        st.session_state['current_tab'] = 7
        st.rerun()


# ==========================================
# === TAB 8: 실력 키우기 로드맵 (신규) ===
# ==========================================
with tabs[7]:
    st.markdown("## 실력 키우기 로드맵")
    st.markdown("**📚 전자책을 쓰기 전, 해당 분야의 실력을 먼저 키우세요**")
    
    st.markdown('<div class="info-card"><div class="info-card-title">💡 전자책 성공 공식</div><p>1. 유튜브/강의로 학습 → 2. 직접 적용 → 3. 성과 만들기 → 4. 무료 테스터 모집 → 5. 전자책 작성</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📺 유튜브 영상 요약")
        st.markdown("학습할 유튜브 영상의 자막/트랜스크립트를 붙여넣으세요")
        
        youtube_input = st.text_area("영상 자막/트랜스크립트", height=250, placeholder="유튜브 자막을 복사해서 붙여넣기...", key="youtube_input")
        
        if st.button("🎬 영상 요약하기", key="summarize_youtube"):
            if youtube_input.strip():
                with st.spinner("영상 요약 중..."):
                    summary = summarize_youtube_video(youtube_input)
                    st.session_state['youtube_summary'] = summary
            else:
                st.error("자막을 입력해주세요")
        
        if st.session_state.get('youtube_summary'):
            st.markdown("#### 📝 요약 결과")
            st.markdown(st.session_state['youtube_summary'])
    
    with col2:
        st.markdown("### 🗺️ 6주 실력 로드맵")
        
        if st.button("🚀 로드맵 생성하기", key="gen_roadmap"):
            if not st.session_state['topic']:
                st.error("주제를 먼저 입력해주세요")
            else:
                with st.spinner("로드맵 생성 중..."):
                    result = generate_skill_roadmap(st.session_state['topic'])
                    try:
                        json_match = re.search(r'\{[\s\S]*\}', result)
                        if json_match:
                            st.session_state['skill_roadmap'] = json.loads(json_match.group())
                    except:
                        st.session_state['skill_roadmap'] = result
        
        if st.session_state.get('skill_roadmap'):
            roadmap = st.session_state['skill_roadmap']
            
            if isinstance(roadmap, dict) and 'roadmap' in roadmap:
                for step in roadmap['roadmap']:
                    with st.expander(f"**{step.get('week', '')}주차: {step.get('title', '')}**", expanded=False):
                        st.write(f"**설명:** {step.get('description', '')}")
                        st.write(f"**예상 시간:** {step.get('hours', '')}")
                        
                        if step.get('tasks'):
                            st.markdown("**할 일:**")
                            for task in step['tasks']:
                                st.checkbox(task, key=f"task_{step.get('week')}_{task[:20]}")
                        
                        if step.get('resources'):
                            st.markdown("**추천 자료:**")
                            for res in step['resources']:
                                st.write(f"• {res}")
                
                if roadmap.get('success_metrics'):
                    st.markdown("---")
                    st.markdown("**🎯 성공 지표:**")
                    for metric in roadmap['success_metrics']:
                        st.write(f"• {metric}")
            else:
                st.markdown(roadmap)
    
    st.markdown("---")
    st.markdown("### ✅ 나만의 체크리스트")
    
    default_checklist = [
        "관련 유튜브 영상 10개 이상 시청",
        "핵심 내용 노트 정리",
        "직접 실행해보기",
        "첫 번째 성과 만들기",
        "무료 테스터 3명 이상 모집",
        "테스터 피드백 수집",
        "전자책 목차 작성",
        "본문 집필 시작"
    ]
    
    st.markdown("**진행 상황을 체크하세요:**")
    for i, item in enumerate(default_checklist):
        st.checkbox(item, key=f"checklist_{i}")


# --- 푸터 ---
st.markdown('<div class="premium-footer"><span class="premium-footer-text">전자책 작성 프로그램 — </span><span class="premium-footer-author">남현우 작가</span></div>', unsafe_allow_html=True)
