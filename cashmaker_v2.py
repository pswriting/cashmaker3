# --- 하이엔드 UI 스타일 (Glassmorphism & Neon) ---
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    /* 전체 폰트 및 배경 설정 */
    * { font-family: 'Pretendard', sans-serif !important; }
    
    .stApp {
        background-color: #050505;
        background-image: 
            radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.1) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(139, 92, 246, 0.1) 0px, transparent 50%);
        background-attachment: fixed;
    }

    /* 상단 헤더 숨김 및 여백 조정 */
    header, footer, .stDeployButton { display: none !important; }
    .main .block-container { padding-top: 2rem; max-width: 1200px; }

    /* --------------------------------------------------
       UI 컴포넌트: 유리 질감 (Glassmorphism)
    -------------------------------------------------- */
    
    /* 탭 디자인 */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        padding: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 10px;
        color: rgba(255, 255, 255, 0.5);
        border: none;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #fff !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }

    /* 입력 필드 (Text Input, Text Area) */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background-color: rgba(25, 25, 30, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #fff !important;
        transition: all 0.3s;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
        background-color: rgba(25, 25, 30, 0.9) !important;
    }

    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: transform 0.2s, box-shadow 0.2s;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
    }
    
    .stDownloadButton > button {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #fff !important;
    }

    /* --------------------------------------------------
       커스텀 클래스 (HTML 렌더링용)
    -------------------------------------------------- */
    
    /* 메인 타이틀 */
    .hero-title {
        text-align: center;
        margin: 60px 0;
    }
    .hero-title h1 {
        background: linear-gradient(to right, #fff, #a5b4fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 10px;
        letter-spacing: -2px;
    }
    .hero-title p {
        color: rgba(255, 255, 255, 0.6);
        font-size: 1.1rem;
    }

    /* 카드 디자인 */
    .pro-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 30px;
        transition: transform 0.3s;
    }
    .pro-card:hover {
        border-color: rgba(139, 92, 246, 0.3);
        transform: translateY(-5px);
    }

    /* 사이드바 */
    [data-testid="stSidebar"] {
        background-color: #08080a;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)
