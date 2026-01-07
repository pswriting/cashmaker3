import streamlit as st
import google.generativeai as genai
import re
import json
from datetime import datetime
from pathlib import Path

# ==========================================
# GENIUS_PERSONA 및 프롬프트
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

# ==========================================
# API 키 저장/불러오기
# ==========================================
def get_config_path():
    home = Path.home()
    return home / ".ebook_app_config.json"

def load_saved_api_key():
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
# 페이지 설정 - 애플 스타일 프리미엄 디자인
# ==========================================
st.set_page_config(page_title="CASHMAKER 전자책 프로그램", page_icon="✨", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700;800;900&display=swap');
    
    /* 애니메이션 정의 */
    @keyframes float {
        0%, 100% { transform: translateY(0px) translateX(0px); opacity: 0.3; }
        50% { transform: translateY(-20px) translateX(10px); opacity: 0.6; }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.9); }
        to { opacity: 1; transform: scale(1); }
    }
    
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(255, 215, 0, 0.3), 0 0 40px rgba(255, 215, 0, 0.1); }
        50% { box-shadow: 0 0 40px rgba(255, 215, 0, 0.6), 0 0 80px rgba(255, 215, 0, 0.3); }
    }
    
    * { 
        font-family: 'Pretendard', 'SF Pro Display', -apple-system, sans-serif; 
        transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* 다크 배경 + 파티클 */
    .stApp { 
        background: linear-gradient(180deg, #000000 0%, #0a0e27 50%, #1a1f3a 100%);
        position: relative;
        overflow-x: hidden;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-image: 
            radial-gradient(2px 2px at 20% 30%, rgba(255, 215, 0, 0.3), transparent),
            radial-gradient(2px 2px at 60% 70%, rgba(255, 165, 0, 0.2), transparent),
            radial-gradient(1px 1px at 50% 50%, rgba(255, 255, 255, 0.1), transparent),
            radial-gradient(1px 1px at 80% 10%, rgba(255, 255, 255, 0.15), transparent),
            radial-gradient(2px 2px at 90% 60%, rgba(255, 215, 0, 0.25), transparent);
        background-size: 200% 200%;
        animation: float 20s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    .main .block-container { 
        background: rgba(255, 255, 255, 0.01);
        backdrop-filter: blur(40px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 32px;
        padding: 3rem 4rem; 
        max-width: 1400px;
        box-shadow: 0 30px 90px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        animation: fadeInUp 0.8s ease-out;
        position: relative;
        z-index: 1;
    }
    
    /* 사이드바 */
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, rgba(10, 14, 39, 0.98) 0%, rgba(26, 31, 58, 0.95) 100%);
        backdrop-filter: blur(60px) saturate(200%);
        border-right: 1px solid rgba(255, 215, 0, 0.15);
        box-shadow: inset -1px 0 0 rgba(255, 215, 0, 0.1), 4px 0 40px rgba(255, 215, 0, 0.05);
        animation: slideInLeft 0.6s ease-out;
    }
    
    [data-testid="stSidebar"] * { color: #e8e8e8 !important; }
    
    [data-testid="stSidebar"] .stProgress > div > div > div > div { 
        background: linear-gradient(90deg, #FFD700, #FFA500, #FFD700);
        background-size: 200% 100%;
        animation: shimmer 3s linear infinite;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.6), 0 4px 20px rgba(255, 165, 0, 0.4);
        border-radius: 10px; 
    }
    
    /* 텍스트 */
    .stMarkdown, .stText, p, span, label { 
        color: #e8e8e8 !important; 
        line-height: 1.8;
        letter-spacing: -0.01em;
    }
    
    /* 헤딩 - 초대형 */
    h1 { 
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 25%, #FFD700 50%, #FF8C00 75%, #FFD700 100%);
        background-size: 300% 100%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 900 !important; 
        font-size: 3.5rem !important;
        letter-spacing: -2.5px !important;
        margin-bottom: 1.5rem !important;
        animation: shimmer 6s ease-in-out infinite, fadeInUp 1s ease-out;
        line-height: 1.1 !important;
    }
    
    h2 { 
        color: #FFD700 !important; 
        font-weight: 800 !important; 
        font-size: 2rem !important;
        margin-top: 3rem !important;
        letter-spacing: -1px !important;
        animation: fadeInUp 0.8s ease-out;
    }
    
    h3 { 
        color: #FFA500 !important; 
        font-weight: 700 !important; 
        font-size: 1.4rem !important;
        letter-spacing: -0.5px !important;
        animation: fadeInUp 0.8s ease-out;
    }
    
    /* 탭 */
    .stTabs [data-baseweb="tab-list"] { 
        background: rgba(255, 255, 255, 0.02);
        border-bottom: 2px solid rgba(255, 215, 0, 0.1);
        border-radius: 20px 20px 0 0;
        padding: 12px 16px;
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] { 
        background: transparent;
        color: #999 !important;
        border-radius: 12px;
        font-weight: 600;
        padding: 14px 24px;
        font-size: 15px;
        position: relative;
        overflow: hidden;
    }
    
    .stTabs [data-baseweb="tab"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 215, 0, 0.1), transparent);
        transform: translateX(-100%);
        transition: transform 0.6s;
    }
    
    .stTabs [data-baseweb="tab"]:hover::before { transform: translateX(100%); }
    
    .stTabs [data-baseweb="tab"]:hover { 
        color: #FFD700 !important;
        background: rgba(255, 215, 0, 0.08);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] { 
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.25), rgba(255, 165, 0, 0.25)) !important;
        color: #FFD700 !important;
        font-weight: 800 !important;
        border: 1px solid rgba(255, 215, 0, 0.4) !important;
        box-shadow: 0 8px 32px rgba(255, 215, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2);
        transform: scale(1.02);
    }
    
    /* 버튼 - 3D 효과 */
    .stButton > button { 
        width: 100%;
        border-radius: 16px;
        font-weight: 700;
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%) !important;
        color: #000 !important;
        border: none !important;
        padding: 18px 36px;
        font-size: 16px;
        box-shadow: 
            0 8px 32px rgba(255, 215, 0, 0.4),
            0 2px 8px rgba(0, 0, 0, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
        position: relative;
        overflow: hidden;
        transform-style: preserve-3d;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before { left: 100%; }
    
    .stButton > button:hover { 
        transform: translateY(-4px) scale(1.02);
        box-shadow: 
            0 16px 48px rgba(255, 215, 0, 0.6),
            0 4px 16px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.4);
    }
    
    .stButton > button:active { transform: translateY(-1px) scale(0.98); }
    
    .stButton > button * { color: #000 !important; font-weight: 800; }
    
    /* 다운로드 버튼 */
    .stDownloadButton > button { 
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%) !important;
        color: #fff !important;
        box-shadow: 0 8px 32px rgba(74, 144, 226, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }
    
    .stDownloadButton > button:hover {
        box-shadow: 0 16px 48px rgba(74, 144, 226, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.4);
        transform: translateY(-4px);
    }
    
    /* 입력 필드 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea { 
        background: rgba(255, 255, 255, 0.03) !important;
        border: 2px solid rgba(255, 215, 0, 0.15) !important;
        border-radius: 16px !important;
        color: #e8e8e8 !important;
        padding: 16px 20px !important;
        font-size: 15px !important;
        backdrop-filter: blur(20px);
        box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.2), 0 1px 0 rgba(255, 255, 255, 0.05);
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus { 
        border-color: #FFD700 !important;
        box-shadow: 
            0 0 0 4px rgba(255, 215, 0, 0.1),
            inset 0 2px 8px rgba(0, 0, 0, 0.2),
            0 8px 32px rgba(255, 215, 0, 0.2) !important;
        transform: translateY(-2px);
    }
    
    /* 알림 */
    .stSuccess { 
        background: rgba(76, 175, 80, 0.08) !important;
        border: 1px solid rgba(76, 175, 80, 0.3) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(76, 175, 80, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        animation: scaleIn 0.4s ease-out;
    }
    
    .stSuccess p { color: #4CAF50 !important; font-weight: 600; }
    
    .stWarning { 
        background: rgba(255, 152, 0, 0.08) !important;
        border: 1px solid rgba(255, 152, 0, 0.3) !important;
        box-shadow: 0 8px 32px rgba(255, 152, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        animation: scaleIn 0.4s ease-out;
    }
    
    .stError { 
        background: rgba(244, 67, 54, 0.08) !important;
        border: 1px solid rgba(244, 67, 54, 0.3) !important;
        box-shadow: 0 8px 32px rgba(244, 67, 54, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        animation: scaleIn 0.4s ease-out;
    }
    
    /* 스코어 카드 */
    .score-card { 
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.12), rgba(255, 165, 0, 0.12));
        border: 2px solid rgba(255, 215, 0, 0.3);
        border-radius: 32px;
        padding: 60px 50px;
        text-align: center;
        box-shadow: 
            0 20px 80px rgba(255, 215, 0, 0.3),
            0 8px 32px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.15);
        animation: scaleIn 0.6s ease-out, glow 4s ease-in-out infinite;
        transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .score-card:hover {
        transform: translateY(-8px) rotateX(2deg);
        box-shadow: 0 30px 100px rgba(255, 215, 0, 0.5), 0 12px 48px rgba(0, 0, 0, 0.5);
    }
    
    .score-number { 
        font-size: 110px;
        font-weight: 900;
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FFD700 100%);
        background-size: 200% 100%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
        margin-bottom: 12px;
        animation: shimmer 3s ease-in-out infinite;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* 히어로 섹션 */
    .hero-section { 
        text-align: center;
        padding: 100px 20px 120px;
        margin-bottom: 60px;
        animation: fadeInUp 1s ease-out;
    }
    
    .hero-label {
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 4px;
        color: #FFD700;
        margin-bottom: 20px;
        text-transform: uppercase;
        opacity: 0.8;
        animation: fadeInUp 0.8s ease-out;
    }
    
    .hero-title { 
        font-size: 72px;
        font-weight: 900;
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 25%, #FFD700 50%, #FF8C00 75%, #FFD700 100%);
        background-size: 300% 100%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 24px;
        letter-spacing: -3px;
        line-height: 1;
        font-family: 'Space Grotesk', sans-serif;
        animation: shimmer 8s ease-in-out infinite, fadeInUp 1.2s ease-out;
        filter: drop-shadow(0 0 40px rgba(255, 215, 0, 0.6));
    }
    
    .hero-subtitle { 
        font-size: 24px;
        color: #aaa;
        font-weight: 400;
        letter-spacing: -0.5px;
        animation: fadeInUp 1.4s ease-out;
    }
    
    /* 정보 카드 */
    .info-card { 
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 215, 0, 0.15);
        border-radius: 24px;
        padding: 32px;
        margin: 20px 0;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);
        animation: scaleIn 0.5s ease-out;
        transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .info-card:hover {
        border-color: rgba(255, 215, 0, 0.4);
        box-shadow: 0 16px 64px rgba(255, 215, 0, 0.2), 0 8px 32px rgba(0, 0, 0, 0.4);
        transform: translateY(-4px) scale(1.01);
    }
    
    /* 로그인 화면 */
    .login-container { 
        max-width: 420px;
        margin: 120px auto;
        padding: 70px 50px;
        background: rgba(26, 31, 58, 0.5);
        border: 2px solid rgba(255, 215, 0, 0.2);
        border-radius: 32px;
        text-align: center;
        backdrop-filter: blur(40px) saturate(180%);
        box-shadow: 0 40px 120px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        animation: scaleIn 0.8s ease-out;
    }
    
    .login-title { 
        font-size: 48px;
        font-weight: 900;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        background-size: 200% 100%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 12px;
        font-family: 'Space Grotesk', sans-serif;
        animation: shimmer 4s ease-in-out infinite;
    }
    
    .login-subtitle {
        font-size: 18px;
        color: #999;
        font-weight: 400;
        margin-top: 8px;
    }
    
    .section-label {
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 2px;
        color: #FFD700;
        text-transform: uppercase;
        opacity: 0.7;
        margin-bottom: 16px;
    }
    
    .premium-footer {
        text-align: center;
        padding: 40px 20px;
        margin-top: 80px;
        border-top: 1px solid rgba(255, 215, 0, 0.1);
        font-size: 14px;
        color: #666;
    }
    
    .premium-footer-text { color: #999; }
    .premium-footer-author { color: #FFD700; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 비밀번호
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
        if st.button("입장하기"):
            if password_input == CORRECT_PASSWORD:
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다")
    st.stop()

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

st.info("✨ **프리미엄 디자인이 적용된 데모 버전입니다!**")
st.success("🎨 애플 스타일 애니메이션과 3D 효과가 적용되었습니다.")

st.markdown('<div class="premium-footer"><span class="premium-footer-text">전자책 작성 프로그램 — </span><span class="premium-footer-author">남현우 작가</span></div>', unsafe_allow_html=True)
