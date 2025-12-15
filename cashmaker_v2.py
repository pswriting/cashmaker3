import streamlit as st
import google.generativeai as genai
import re
import json
import io
import base64
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import streamlit.components.v1 as components

# --- 페이지 설정 ---
st.set_page_config(
    page_title="CASHMAKER", 
    layout="wide", 
    page_icon="◆",
    initial_sidebar_state="collapsed"
)

# --- 프리미엄 CSS ---
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    * { 
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    }
    
    /* 기본 요소 숨기기 */
    .stDeployButton, footer, #MainMenu, header {display: none !important;}
    
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
    }
    
    /* 배경 */
    .stApp {
        background: linear-gradient(180deg, #0a0a0f 0%, #111118 100%);
    }
    
    .main .block-container {
        background: transparent;
        padding: 2rem 4rem;
        max-width: 1400px;
    }
    
    /* 사이드바 */
    [data-testid="stSidebar"] {
        background: #0d0d12;
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: rgba(255,255,255,0.7) !important;
    }
    
    /* 텍스트 */
    .stMarkdown, .stText, p, span, label, .stMarkdown p, li {
        color: rgba(255,255,255,0.85) !important;
        line-height: 1.7;
        letter-spacing: -0.01em;
    }
    
    h1 { 
        color: #ffffff !important; 
        font-weight: 600 !important; 
        font-size: 2.2rem !important;
        letter-spacing: -0.03em !important;
    }
    
    h2 { 
        color: #ffffff !important; 
        font-weight: 600 !important; 
        font-size: 1.5rem !important;
        letter-spacing: -0.02em !important;
        margin-top: 2.5rem !important;
    }
    
    h3 { 
        color: rgba(255,255,255,0.9) !important; 
        font-weight: 500 !important; 
        font-size: 1.1rem !important;
        letter-spacing: -0.01em !important;
    }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        gap: 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        padding: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: rgba(255,255,255,0.4) !important;
        border-radius: 0;
        font-weight: 500;
        padding: 16px 24px;
        font-size: 14px;
        border-bottom: 2px solid transparent;
        margin-bottom: -1px;
        letter-spacing: -0.01em;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: rgba(255,255,255,0.7) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: transparent !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #ffffff !important;
    }
    
    /* 버튼 */
    .stButton > button { 
        width: 100%; 
        border-radius: 8px; 
        font-weight: 500; 
        background: #ffffff !important;
        color: #000000 !important;
        border: none !important;
        padding: 14px 28px;
        font-size: 14px;
        letter-spacing: -0.01em;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover { 
        background: rgba(255,255,255,0.9) !important;
        transform: translateY(-1px);
    }
    
    .stButton > button p, .stButton > button span, .stButton > button * {
        color: #000000 !important;
    }
    
    /* 다운로드 버튼 */
    .stDownloadButton > button {
        background: transparent !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 8px;
    }
    
    .stDownloadButton > button:hover {
        background: rgba(255,255,255,0.05) !important;
        border-color: rgba(255,255,255,0.4) !important;
    }
    
    .stDownloadButton > button p, .stDownloadButton > button * {
        color: #ffffff !important;
    }
    
    /* 인풋 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        padding: 14px 16px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(255,255,255,0.3) !important;
        box-shadow: none !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: rgba(255,255,255,0.3) !important;
    }
    
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
    }
    
    .stSelectbox > div > div > div {
        color: #ffffff !important;
    }
    
    /* 카드 */
    .premium-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 32px;
        margin: 20px 0;
    }
    
    .premium-card-dark {
        background: rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 16px;
        padding: 32px;
        margin: 20px 0;
    }
    
    /* 스코어 카드 */
    .score-display {
        text-align: center;
        padding: 48px;
    }
    
    .score-number {
        font-size: 80px;
        font-weight: 600;
        color: #ffffff;
        letter-spacing: -0.04em;
        line-height: 1;
    }
    
    .score-label {
        font-size: 14px;
        color: rgba(255,255,255,0.5);
        margin-top: 12px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    
    /* 메트릭 */
    .metric-item {
        text-align: center;
        padding: 20px;
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 600;
        color: #ffffff;
        letter-spacing: -0.02em;
    }
    
    .metric-label {
        font-size: 12px;
        color: rgba(255,255,255,0.4);
        margin-top: 8px;
        letter-spacing: 0.02em;
    }
    
    /* 프로그레스 */
    .stProgress > div > div > div > div {
        background: #ffffff !important;
    }
    
    .stProgress > div > div {
        background: rgba(255,255,255,0.1) !important;
    }
    
    /* 알림 */
    .stAlert {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        color: rgba(255,255,255,0.8) !important;
    }
    
    /* 구분선 */
    hr {
        border-color: rgba(255,255,255,0.06) !important;
    }
    
    /* 이미지 프리뷰 */
    .image-preview {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    
    /* 히어로 섹션 */
    .hero-minimal {
        padding: 60px 0 40px 0;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 40px;
    }
    
    .hero-title {
        font-size: 14px;
        font-weight: 500;
        color: rgba(255,255,255,0.4);
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 16px;
    }
    
    .hero-main {
        font-size: 48px;
        font-weight: 600;
        color: #ffffff;
        letter-spacing: -0.03em;
        line-height: 1.1;
    }
    
    /* 디자인 프리뷰 영역 */
    .design-frame {
        background: #18181b;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 24px;
        min-height: 400px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 비밀번호 ---
CORRECT_PASSWORD = "cashmaker2024"

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: center; min-height: 80vh;">
        <div style="text-align: center; max-width: 360px;">
            <div style="font-size: 12px; color: rgba(255,255,255,0.4); letter-spacing: 0.15em; margin-bottom: 24px;">CASHMAKER</div>
            <div style="font-size: 32px; font-weight: 600; color: #fff; letter-spacing: -0.02em; margin-bottom: 48px;">전자책 수익화 시스템</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 0.8, 1])
    with col2:
        password_input = st.text_input("", type="password", placeholder="비밀번호 입력", label_visibility="collapsed")
        if st.button("Enter"):
            if password_input == CORRECT_PASSWORD:
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다")
    st.stop()

# --- 세션 초기화 ---
default_states = {
    'topic': '', 'target_persona': '', 'pain_points': '',
    'outline': [], 'chapters': {}, 'book_title': '', 'subtitle': '',
    'topic_score': None, 'score_details': None, 'generated_titles': None,
    'market_analysis': None, 'pricing_strategy': None, 'sales_page_copy': None,
    'lead_magnet': None, 'email_sequence': None, 'api_key': '',
    'design_copy': None, 'cover_image': None, 'thumbnail_image': None, 'header_image': None
}

for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- 한글 폰트 로드 ---
@st.cache_resource
def load_korean_font(size=60, weight="Bold"):
    """한글 폰트 로드"""
    font_urls = {
        "Bold": "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansCJKkr-Bold.otf",
        "Regular": "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansCJKkr-Regular.otf",
        "Black": "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansCJKkr-Black.otf",
        "Medium": "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansCJKkr-Medium.otf",
        "Light": "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansCJKkr-Light.otf",
    }
    
    try:
        url = font_urls.get(weight, font_urls["Bold"])
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return ImageFont.truetype(BytesIO(response.content), size)
    except:
        pass
    return ImageFont.load_default()

# --- 사이드바 ---
with st.sidebar:
    st.markdown("""
    <div style="padding: 20px 0; border-bottom: 1px solid rgba(255,255,255,0.06); margin-bottom: 24px;">
        <div style="font-size: 11px; color: rgba(255,255,255,0.3); letter-spacing: 0.12em;">CASHMAKER</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 진행률
    progress_items = [
        bool(st.session_state['topic']),
        bool(st.session_state['market_analysis']),
        bool(st.session_state['outline']),
        bool(st.session_state['pricing_strategy']),
        bool(st.session_state['sales_page_copy']),
    ]
    progress = sum(progress_items) / len(progress_items) * 100
    
    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <div style="font-size: 12px; color: rgba(255,255,255,0.4); margin-bottom: 8px;">진행률</div>
        <div style="font-size: 28px; font-weight: 600; color: #fff;">{progress:.0f}%</div>
    </div>
    """, unsafe_allow_html=True)
    st.progress(progress / 100)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 현재 프로젝트
    if st.session_state['book_title']:
        st.markdown(f"""
        <div style="padding: 16px; background: rgba(255,255,255,0.02); border-radius: 8px; margin-bottom: 24px;">
            <div style="font-size: 11px; color: rgba(255,255,255,0.3); margin-bottom: 4px;">현재 프로젝트</div>
            <div style="font-size: 14px; color: #fff;">{st.session_state['book_title']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # API 설정
    st.markdown("""
    <div style="font-size: 11px; color: rgba(255,255,255,0.3); letter-spacing: 0.08em; margin-bottom: 12px;">API 설정</div>
    """, unsafe_allow_html=True)
    
    api_key_input = st.text_input(
        "Gemini API Key",
        value=st.session_state['api_key'],
        type="password",
        placeholder="AIza...",
        label_visibility="collapsed"
    )
    if api_key_input:
        st.session_state['api_key'] = api_key_input
    
    if st.session_state.get('api_key'):
        st.markdown('<div style="font-size: 12px; color: rgba(255,255,255,0.4);">연결됨</div>', unsafe_allow_html=True)
    else:
        with st.expander("API 키 발급"):
            st.markdown("""
            1. [Google AI Studio](https://aistudio.google.com/apikey) 접속
            2. 구글 계정 로그인
            3. API 키 생성
            4. 복사하여 입력
            """)

# --- AI 함수 ---
def get_api_key():
    return st.session_state.get('api_key', '')

def ask_ai(system_role, prompt, temperature=0.7):
    api_key = get_api_key()
    if not api_key:
        return "API 키를 먼저 입력해주세요."
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        config = genai.types.GenerationConfig(temperature=temperature)
        full_prompt = f"당신은 {system_role}입니다.\n\n{prompt}\n\n한국어로 답변해주세요."
        response = model.generate_content(full_prompt, generation_config=config)
        return response.text
    except Exception as e:
        return f"오류: {str(e)}"

# --- 고급 이미지 생성 함수 ---
def create_premium_cover(title, subtitle, author="", style="dark"):
    """프리미엄 전자책 표지"""
    width, height = 1600, 2400
    
    # 폰트 로드
    title_font = load_korean_font(140, "Black")
    subtitle_font = load_korean_font(48, "Light")
    author_font = load_korean_font(36, "Regular")
    
    # 스타일 설정
    styles = {
        "dark": {
            "bg_start": (8, 8, 12),
            "bg_end": (20, 20, 28),
            "text": (255, 255, 255),
            "sub_text": (160, 160, 170),
            "accent": (255, 255, 255),
        },
        "light": {
            "bg_start": (250, 250, 252),
            "bg_end": (240, 240, 245),
            "text": (20, 20, 25),
            "sub_text": (100, 100, 110),
            "accent": (20, 20, 25),
        },
        "navy": {
            "bg_start": (15, 25, 45),
            "bg_end": (25, 40, 70),
            "text": (255, 255, 255),
            "sub_text": (180, 195, 220),
            "accent": (100, 180, 255),
        },
        "warm": {
            "bg_start": (35, 25, 20),
            "bg_end": (55, 40, 30),
            "text": (255, 255, 255),
            "sub_text": (200, 180, 160),
            "accent": (255, 200, 150),
        },
    }
    
    s = styles.get(style, styles["dark"])
    
    # 이미지 생성
    img = Image.new('RGB', (width, height), s["bg_start"])
    draw = ImageDraw.Draw(img)
    
    # 그라데이션 배경
    for y in range(height):
        ratio = y / height
        r = int(s["bg_start"][0] + (s["bg_end"][0] - s["bg_start"][0]) * ratio)
        g = int(s["bg_start"][1] + (s["bg_end"][1] - s["bg_start"][1]) * ratio)
        b = int(s["bg_start"][2] + (s["bg_end"][2] - s["bg_start"][2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # 상단 라인 악센트
    draw.rectangle([(120, 200), (width - 120, 203)], fill=s["accent"])
    
    # 하단 라인 악센트
    draw.rectangle([(120, height - 300), (width - 120, height - 297)], fill=s["accent"])
    
    # 제목 줄바꿈 처리
    title_lines = []
    current = ""
    for char in title:
        test = current + char
        bbox = draw.textbbox((0, 0), test, font=title_font)
        if bbox[2] - bbox[0] < width - 240:
            current = test
        else:
            if current:
                title_lines.append(current)
            current = char
    if current:
        title_lines.append(current)
    
    # 제목 그리기 (중앙)
    title_y = 900
    line_height = 170
    
    for i, line in enumerate(title_lines[:3]):
        bbox = draw.textbbox((0, 0), line, font=title_font)
        x = (width - (bbox[2] - bbox[0])) // 2
        y = title_y + i * line_height
        
        # 미세한 그림자
        draw.text((x + 2, y + 2), line, font=title_font, fill=(0, 0, 0, 50))
        draw.text((x, y), line, font=title_font, fill=s["text"])
    
    # 부제목
    if subtitle:
        sub_y = title_y + len(title_lines) * line_height + 80
        bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, sub_y), subtitle, font=subtitle_font, fill=s["sub_text"])
    
    # 저자
    if author:
        bbox = draw.textbbox((0, 0), author, font=author_font)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, height - 200), author, font=author_font, fill=s["sub_text"])
    
    return img


def create_premium_thumbnail(title, style="dark"):
    """프리미엄 썸네일 (800x600)"""
    width, height = 800, 600
    
    title_font = load_korean_font(56, "Bold")
    
    styles = {
        "dark": {
            "bg_start": (15, 15, 20),
            "bg_end": (30, 30, 40),
            "text": (255, 255, 255),
            "accent": (255, 255, 255),
        },
        "gradient": {
            "bg_start": (80, 100, 200),
            "bg_end": (140, 80, 180),
            "text": (255, 255, 255),
            "accent": (255, 255, 255),
        },
        "light": {
            "bg_start": (248, 248, 252),
            "bg_end": (235, 235, 245),
            "text": (25, 25, 30),
            "accent": (25, 25, 30),
        },
        "warm": {
            "bg_start": (180, 80, 60),
            "bg_end": (220, 120, 80),
            "text": (255, 255, 255),
            "accent": (255, 255, 255),
        },
    }
    
    s = styles.get(style, styles["dark"])
    
    img = Image.new('RGB', (width, height), s["bg_start"])
    draw = ImageDraw.Draw(img)
    
    # 그라데이션
    for y in range(height):
        ratio = y / height
        r = int(s["bg_start"][0] + (s["bg_end"][0] - s["bg_start"][0]) * ratio)
        g = int(s["bg_start"][1] + (s["bg_end"][1] - s["bg_start"][1]) * ratio)
        b = int(s["bg_start"][2] + (s["bg_end"][2] - s["bg_start"][2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # 상하단 악센트 라인
    draw.rectangle([(0, 0), (width, 4)], fill=s["accent"])
    draw.rectangle([(0, height - 4), (width, height)], fill=s["accent"])
    
    # 제목 줄바꿈
    lines = []
    current = ""
    for char in title:
        test = current + char
        bbox = draw.textbbox((0, 0), test, font=title_font)
        if bbox[2] - bbox[0] < width - 100:
            current = test
        else:
            if current:
                lines.append(current)
            current = char
    if current:
        lines.append(current)
    
    # 중앙 배치
    line_height = 75
    total = len(lines) * line_height
    start_y = (height - total) // 2
    
    for i, line in enumerate(lines[:2]):
        bbox = draw.textbbox((0, 0), line, font=title_font)
        x = (width - (bbox[2] - bbox[0])) // 2
        y = start_y + i * line_height
        draw.text((x, y), line, font=title_font, fill=s["text"])
    
    return img


def create_premium_header(headline, subheadline, cta, style="dark"):
    """프리미엄 상세페이지 헤더 (1200x628)"""
    width, height = 1200, 628
    
    headline_font = load_korean_font(64, "Bold")
    sub_font = load_korean_font(28, "Regular")
    cta_font = load_korean_font(22, "Medium")
    
    styles = {
        "dark": {
            "bg_start": (12, 12, 18),
            "bg_end": (25, 25, 35),
            "text": (255, 255, 255),
            "sub_text": (160, 160, 175),
            "cta_bg": (255, 255, 255),
            "cta_text": (0, 0, 0),
        },
        "gradient": {
            "bg_start": (90, 110, 220),
            "bg_end": (150, 90, 190),
            "text": (255, 255, 255),
            "sub_text": (220, 220, 240),
            "cta_bg": (255, 255, 255),
            "cta_text": (90, 110, 220),
        },
        "light": {
            "bg_start": (252, 252, 255),
            "bg_end": (242, 242, 250),
            "text": (20, 20, 30),
            "sub_text": (90, 90, 100),
            "cta_bg": (20, 20, 30),
            "cta_text": (255, 255, 255),
        },
    }
    
    s = styles.get(style, styles["dark"])
    
    img = Image.new('RGB', (width, height), s["bg_start"])
    draw = ImageDraw.Draw(img)
    
    # 그라데이션
    for y in range(height):
        ratio = y / height
        r = int(s["bg_start"][0] + (s["bg_end"][0] - s["bg_start"][0]) * ratio)
        g = int(s["bg_start"][1] + (s["bg_end"][1] - s["bg_start"][1]) * ratio)
        b = int(s["bg_start"][2] + (s["bg_end"][2] - s["bg_start"][2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # 헤드라인 줄바꿈
    lines = []
    current = ""
    for char in headline:
        test = current + char
        bbox = draw.textbbox((0, 0), test, font=headline_font)
        if bbox[2] - bbox[0] < width - 160:
            current = test
        else:
            if current:
                lines.append(current)
            current = char
    if current:
        lines.append(current)
    
    # 헤드라인
    y_pos = 160
    for i, line in enumerate(lines[:2]):
        bbox = draw.textbbox((0, 0), line, font=headline_font)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y_pos), line, font=headline_font, fill=s["text"])
        y_pos += 85
    
    # 서브헤드라인
    if subheadline:
        y_pos += 30
        bbox = draw.textbbox((0, 0), subheadline, font=sub_font)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y_pos), subheadline, font=sub_font, fill=s["sub_text"])
    
    # CTA 버튼
    if cta:
        btn_w, btn_h = 280, 56
        btn_x = (width - btn_w) // 2
        btn_y = height - 120
        
        draw.rounded_rectangle(
            [(btn_x, btn_y), (btn_x + btn_w, btn_y + btn_h)],
            radius=8,
            fill=s["cta_bg"]
        )
        
        bbox = draw.textbbox((0, 0), cta, font=cta_font)
        text_x = btn_x + (btn_w - (bbox[2] - bbox[0])) // 2
        text_y = btn_y + (btn_h - (bbox[3] - bbox[1])) // 2 - 2
        draw.text((text_x, text_y), cta, font=cta_font, fill=s["cta_text"])
    
    return img


# --- 메인 UI ---
st.markdown("""
<div class="hero-minimal">
    <div class="hero-title">Ebook Monetization System</div>
    <div class="hero-main">CASHMAKER</div>
</div>
""", unsafe_allow_html=True)

# 탭
tabs = st.tabs([
    "주제 선정", 
    "시장 분석",
    "매출 설계",
    "목차 설계", 
    "디자인",
    "판매페이지",
    "리드마그넷",
    "이메일 퍼널",
    "출력"
])

# === TAB 1: 주제 선정 ===
with tabs[0]:
    st.markdown("## 주제 선정")
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("### 기본 정보")
        
        topic_input = st.text_input(
            "주제",
            value=st.session_state['topic'],
            placeholder="어떤 주제로 전자책을 만드시나요?"
        )
        st.session_state['topic'] = topic_input
        
        persona = st.text_area(
            "타겟 독자",
            value=st.session_state['target_persona'],
            placeholder="누구를 위한 전자책인가요?",
            height=100
        )
        st.session_state['target_persona'] = persona
        
        pain = st.text_area(
            "핵심 고민",
            value=st.session_state['pain_points'],
            placeholder="타겟이 가장 해결하고 싶은 문제는?",
            height=100
        )
        st.session_state['pain_points'] = pain
        
        if st.button("분석 시작", key="analyze"):
            if not topic_input:
                st.warning("주제를 입력해주세요.")
            else:
                with st.spinner("분석 중..."):
                    prompt = f"""'{topic_input}' 주제의 전자책 수익화 적합도를 분석해주세요.

5가지 항목을 0~100점으로 채점:
1. 시장성 - 수요가 있는가
2. 수익성 - 유료 판매 가능성
3. 차별화 - 경쟁 우위 확보 가능성
4. 난이도 - 제작 용이성
5. 지속성 - 장기 판매 가능성

JSON 형식으로만 답변:
{{
    "market": {{"score": 85, "reason": "이유"}},
    "profit": {{"score": 80, "reason": "이유"}},
    "differentiation": {{"score": 75, "reason": "이유"}},
    "difficulty": {{"score": 90, "reason": "이유"}},
    "sustainability": {{"score": 70, "reason": "이유"}},
    "total_score": 80,
    "verdict": "적합/보통/부적합",
    "summary": "종합 의견 2-3문장"
}}"""
                    result = ask_ai("전자책 시장 분석가", prompt, 0.3)
                    try:
                        json_match = re.search(r'\{[\s\S]*\}', result)
                        if json_match:
                            st.session_state['score_details'] = json.loads(json_match.group())
                            st.session_state['topic_score'] = st.session_state['score_details'].get('total_score', 0)
                    except:
                        st.error("분석 오류. 다시 시도해주세요.")
    
    with col2:
        st.markdown("### 분석 결과")
        
        if st.session_state.get('topic_score'):
            score = st.session_state['topic_score']
            details = st.session_state['score_details']
            
            st.markdown(f"""
            <div class="premium-card">
                <div class="score-display">
                    <div class="score-number">{score}</div>
                    <div class="score-label">{details.get('verdict', '')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 세부 점수
            metrics = [
                ("시장성", "market"), ("수익성", "profit"), ("차별화", "differentiation"),
                ("난이도", "difficulty"), ("지속성", "sustainability")
            ]
            
            cols = st.columns(5)
            for i, (name, key) in enumerate(metrics):
                with cols[i]:
                    val = details.get(key, {}).get('score', 0)
                    st.markdown(f"""
                    <div class="metric-item">
                        <div class="metric-value">{val}</div>
                        <div class="metric-label">{name}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="premium-card-dark" style="margin-top: 24px;">
                <p style="color: rgba(255,255,255,0.7); font-size: 14px; line-height: 1.8;">{details.get('summary', '')}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="premium-card" style="text-align: center; padding: 80px;">
                <p style="color: rgba(255,255,255,0.3);">주제를 입력하고 분석을 시작하세요</p>
            </div>
            """, unsafe_allow_html=True)

# === TAB 2: 시장 분석 ===
with tabs[1]:
    st.markdown("## 시장 분석")
    
    if not st.session_state['topic']:
        st.info("먼저 주제 선정 탭에서 주제를 입력해주세요.")
    else:
        if st.button("시장 분석 시작", key="market"):
            with st.spinner("시장 데이터 분석 중..."):
                prompt = f"""'{st.session_state['topic']}' 주제로 전자책 시장을 분석해주세요.

타겟: {st.session_state['target_persona']}

분석 항목:
1. 경쟁 현황 - 경쟁자 3개 (이름, 가격, 강점, 약점)
2. 타겟 분석 - 표면적 고민, 본질적 고민, 구매 트리거
3. 차별화 기회 - 포지셔닝 전략
4. 키워드 10개

JSON 형식:
{{
    "competitors": [{{"name": "이름", "price": "가격", "strength": "강점", "weakness": "약점"}}],
    "avg_price": "평균가격",
    "target_analysis": {{"surface_pain": ["고민"], "deep_pain": ["본질"], "triggers": ["트리거"]}},
    "differentiation": {{"positioning": "전략", "unique_angle": "각도"}},
    "keywords": ["키워드"],
    "summary": "요약"
}}"""
                result = ask_ai("시장 분석가", prompt, 0.5)
                try:
                    json_match = re.search(r'\{[\s\S]*\}', result)
                    if json_match:
                        st.session_state['market_analysis'] = json.loads(json_match.group())
                except:
                    st.session_state['market_analysis'] = {"raw": result}
        
        if st.session_state.get('market_analysis'):
            data = st.session_state['market_analysis']
            
            col1, col2 = st.columns(2, gap="large")
            
            with col1:
                st.markdown("### 경쟁자 분석")
                for comp in data.get('competitors', [])[:3]:
                    st.markdown(f"""
                    <div class="premium-card-dark">
                        <div style="font-weight: 600; margin-bottom: 8px;">{comp.get('name', '')} · {comp.get('price', '')}</div>
                        <div style="font-size: 13px; color: rgba(255,255,255,0.5); margin-bottom: 4px;">강점: {comp.get('strength', '')}</div>
                        <div style="font-size: 13px; color: rgba(255,255,255,0.5);">약점: {comp.get('weakness', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("### 타겟 인사이트")
                if 'target_analysis' in data:
                    ta = data['target_analysis']
                    
                    st.markdown("**본질적 고민**")
                    for p in ta.get('deep_pain', []):
                        st.markdown(f"· {p}")
                    
                    st.markdown("**구매 트리거**")
                    for t in ta.get('triggers', []):
                        st.markdown(f"· {t}")
                
                st.markdown("### 차별화 전략")
                if 'differentiation' in data:
                    st.markdown(f"{data['differentiation'].get('positioning', '')}")
                
                st.markdown("### 타겟 키워드")
                keywords = data.get('keywords', [])
                if keywords:
                    st.markdown(" · ".join(keywords[:10]))

# === TAB 3: 매출 설계 ===
with tabs[2]:
    st.markdown("## 매출 설계")
    
    if not st.session_state['topic']:
        st.info("먼저 주제 선정 탭에서 주제를 입력해주세요.")
    else:
        if st.button("매출 전략 생성", key="pricing"):
            with st.spinner("수익 구조 설계 중..."):
                prompt = f"""'{st.session_state['topic']}' 전자책의 매출 전략을 설계해주세요.

타겟: {st.session_state['target_persona']}

설계 항목:
1. 가격 전략 (얼리버드/정가/프리미엄)
2. 오퍼 구조 (메인 + 보너스 3개 + 보증)
3. 퍼널 (프론트/미들/백엔드)
4. 월 100명 방문 시 예상 매출

JSON 형식:
{{
    "pricing": {{"recommended": "추천가", "reason": "근거", "earlybird": "얼리버드", "regular": "정가", "premium": "프리미엄"}},
    "offer": {{"main_product": "메인", "bonuses": ["보너스1", "보너스2", "보너스3"], "guarantee": "보증"}},
    "funnel": {{"frontend": {{"name": "이름", "price": "가격"}}, "middleend": {{"name": "이름", "price": "가격"}}, "backend": {{"name": "이름", "price": "가격"}}}},
    "simulation": {{"monthly_revenue": "예상 월매출", "conversion_rate": "3%"}}
}}"""
                result = ask_ai("수익화 전략가", prompt, 0.6)
                try:
                    json_match = re.search(r'\{[\s\S]*\}', result)
                    if json_match:
                        st.session_state['pricing_strategy'] = json.loads(json_match.group())
                except:
                    pass
        
        if st.session_state.get('pricing_strategy'):
            data = st.session_state['pricing_strategy']
            
            col1, col2 = st.columns(2, gap="large")
            
            with col1:
                if 'pricing' in data:
                    p = data['pricing']
                    st.markdown("### 가격 전략")
                    
                    cols = st.columns(3)
                    with cols[0]:
                        st.markdown(f"""
                        <div class="metric-item">
                            <div style="font-size: 12px; color: rgba(255,255,255,0.4);">얼리버드</div>
                            <div class="metric-value">{p.get('earlybird', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with cols[1]:
                        st.markdown(f"""
                        <div class="metric-item" style="background: rgba(255,255,255,0.05); border-radius: 12px;">
                            <div style="font-size: 12px; color: rgba(255,255,255,0.6);">추천가</div>
                            <div class="metric-value">{p.get('recommended', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with cols[2]:
                        st.markdown(f"""
                        <div class="metric-item">
                            <div style="font-size: 12px; color: rgba(255,255,255,0.4);">프리미엄</div>
                            <div class="metric-value">{p.get('premium', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown(f"<p style='color: rgba(255,255,255,0.5); font-size: 14px; margin-top: 16px;'>{p.get('reason', '')}</p>", unsafe_allow_html=True)
            
            with col2:
                if 'offer' in data:
                    o = data['offer']
                    st.markdown("### 오퍼 구성")
                    st.markdown(f"**메인:** {o.get('main_product', '')}")
                    for i, b in enumerate(o.get('bonuses', []), 1):
                        st.markdown(f"**보너스 {i}:** {b}")
                    st.markdown(f"**보증:** {o.get('guarantee', '')}")
                
                if 'simulation' in data:
                    s = data['simulation']
                    st.markdown(f"""
                    <div class="premium-card" style="margin-top: 24px; text-align: center;">
                        <div style="font-size: 12px; color: rgba(255,255,255,0.4); margin-bottom: 8px;">예상 월매출</div>
                        <div style="font-size: 36px; font-weight: 600;">{s.get('monthly_revenue', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)

# === TAB 4: 목차 설계 ===
with tabs[3]:
    st.markdown("## 목차 설계")
    
    if not st.session_state['topic']:
        st.info("먼저 주제 선정 탭에서 주제를 입력해주세요.")
    else:
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown("### 제목")
            title = st.text_input("전자책 제목", value=st.session_state['book_title'])
            st.session_state['book_title'] = title
            
            subtitle = st.text_input("부제목", value=st.session_state['subtitle'])
            st.session_state['subtitle'] = subtitle
            
            if st.button("AI 제목 추천", key="titles"):
                with st.spinner("제목 생성 중..."):
                    prompt = f"""'{st.session_state['topic']}' 주제의 전자책 제목 5개를 만들어주세요.
타겟: {st.session_state['target_persona']}

베스트셀러 제목 원칙:
- 7자 이내 임팩트
- 상식 파괴 또는 구체적 숫자

JSON 형식:
{{"titles": [{{"title": "제목", "subtitle": "부제목"}}]}}"""
                    result = ask_ai("베스트셀러 작가", prompt, 0.9)
                    try:
                        json_match = re.search(r'\{[\s\S]*\}', result)
                        if json_match:
                            st.session_state['generated_titles'] = json.loads(json_match.group())
                    except:
                        pass
            
            if st.session_state.get('generated_titles'):
                st.markdown("**추천 제목**")
                for t in st.session_state['generated_titles'].get('titles', [])[:5]:
                    st.markdown(f"· {t.get('title', '')} — {t.get('subtitle', '')}")
        
        with col2:
            st.markdown("### 목차")
            
            if st.button("AI 목차 생성", key="outline"):
                with st.spinner("목차 설계 중..."):
                    prompt = f"""'{st.session_state['topic']}' 주제로 6-7개 챕터 목차를 설계해주세요.
타겟: {st.session_state['target_persona']}

형식:
## 챕터1: [제목]
- 소제목1
- 소제목2
- 소제목3"""
                    result = ask_ai("출판기획자", prompt, 0.85)
                    chapters = re.findall(r'## (챕터\d+:?\s*.+)', result)
                    if not chapters:
                        chapters = [l.strip() for l in result.split('\n') if '챕터' in l][:7]
                    st.session_state['outline'] = chapters
                    st.session_state['full_outline'] = result
            
            if st.session_state.get('full_outline'):
                st.text_area("전체 목차", value=st.session_state['full_outline'], height=400, label_visibility="collapsed")

# === TAB 5: 디자인 ===
with tabs[4]:
    st.markdown("## 디자인")
    st.markdown("표지, 썸네일, 상세페이지 헤더를 생성합니다.")
    
    st.markdown("---")
    
    # 표지
    st.markdown("### 전자책 표지")
    
    col1, col2 = st.columns([1, 1.2], gap="large")
    
    with col1:
        cover_title = st.text_input("표지 제목", value=st.session_state.get('book_title', ''), key="ct")
        cover_subtitle = st.text_input("표지 부제목", value=st.session_state.get('subtitle', ''), key="cs")
        cover_author = st.text_input("저자명", value="", key="ca")
        cover_style = st.selectbox(
            "스타일",
            ["dark", "light", "navy", "warm"],
            format_func=lambda x: {"dark": "다크", "light": "라이트", "navy": "네이비", "warm": "웜"}.get(x, x),
            key="cstyle"
        )
        
        if st.button("표지 생성", key="gen_cover"):
            if cover_title:
                with st.spinner("표지 생성 중..."):
                    img = create_premium_cover(cover_title, cover_subtitle, cover_author, cover_style)
                    st.session_state['cover_image'] = img
    
    with col2:
        if st.session_state.get('cover_image'):
            st.image(st.session_state['cover_image'], use_container_width=True)
            buf = BytesIO()
            st.session_state['cover_image'].save(buf, format='PNG', quality=95)
            st.download_button("표지 다운로드", buf.getvalue(), "cover.png", "image/png")
        else:
            st.markdown("""
            <div class="design-frame">
                <span style="color: rgba(255,255,255,0.2);">표지 미리보기</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 썸네일
    st.markdown("### 크몽 썸네일")
    
    col3, col4 = st.columns([1, 1.2], gap="large")
    
    with col3:
        thumb_title = st.text_input("썸네일 문구", value=st.session_state.get('book_title', ''), key="tt")
        thumb_style = st.selectbox(
            "스타일",
            ["dark", "gradient", "light", "warm"],
            format_func=lambda x: {"dark": "다크", "gradient": "그라데이션", "light": "라이트", "warm": "웜"}.get(x, x),
            key="tstyle"
        )
        
        if st.button("썸네일 생성", key="gen_thumb"):
            if thumb_title:
                with st.spinner("썸네일 생성 중..."):
                    img = create_premium_thumbnail(thumb_title, thumb_style)
                    st.session_state['thumbnail_image'] = img
    
    with col4:
        if st.session_state.get('thumbnail_image'):
            st.image(st.session_state['thumbnail_image'], use_container_width=True)
            buf = BytesIO()
            st.session_state['thumbnail_image'].save(buf, format='PNG')
            st.download_button("썸네일 다운로드", buf.getvalue(), "thumbnail.png", "image/png")
        else:
            st.markdown("""
            <div class="design-frame" style="min-height: 300px;">
                <span style="color: rgba(255,255,255,0.2);">썸네일 미리보기</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 상세페이지 헤더
    st.markdown("### 상세페이지 헤더")
    
    col5, col6 = st.columns([1, 1.2], gap="large")
    
    with col5:
        header_headline = st.text_input("헤드라인", placeholder="가장 강력한 한 문장", key="hh")
        header_sub = st.text_input("서브헤드라인", placeholder="보조 설명", key="hs")
        header_cta = st.text_input("CTA 버튼", value="지금 시작하기", key="hc")
        header_style = st.selectbox(
            "스타일",
            ["dark", "gradient", "light"],
            format_func=lambda x: {"dark": "다크", "gradient": "그라데이션", "light": "라이트"}.get(x, x),
            key="hstyle"
        )
        
        if st.button("헤더 생성", key="gen_header"):
            if header_headline:
                with st.spinner("헤더 생성 중..."):
                    img = create_premium_header(header_headline, header_sub, header_cta, header_style)
                    st.session_state['header_image'] = img
    
    with col6:
        if st.session_state.get('header_image'):
            st.image(st.session_state['header_image'], use_container_width=True)
            buf = BytesIO()
            st.session_state['header_image'].save(buf, format='PNG')
            st.download_button("헤더 다운로드", buf.getvalue(), "header.png", "image/png")
        else:
            st.markdown("""
            <div class="design-frame" style="min-height: 300px;">
                <span style="color: rgba(255,255,255,0.2);">헤더 미리보기</span>
            </div>
            """, unsafe_allow_html=True)

# === TAB 6: 판매페이지 ===
with tabs[5]:
    st.markdown("## 판매페이지 카피")
    
    if not st.session_state['topic']:
        st.info("먼저 주제 선정 탭에서 주제를 입력해주세요.")
    else:
        if st.button("카피 생성", key="sales"):
            with st.spinner("판매페이지 카피 작성 중..."):
                prompt = f"""'{st.session_state['topic']}' 전자책의 크몽 상세페이지 카피를 작성해주세요.

제목: {st.session_state.get('book_title', st.session_state['topic'])}
타겟: {st.session_state['target_persona']}

작성 내용:
1. 상품 제목 (40자 이내)
2. 후킹 헤드라인 3개
3. 문제 제기
4. 해결책 (핵심 가치 3가지)
5. 구성품 및 보너스
6. CTA 문구
7. FAQ 3개

마크다운 형식으로 작성."""
                result = ask_ai("마케팅 카피라이터", prompt, 0.8)
                st.session_state['sales_page_copy'] = result
        
        if st.session_state.get('sales_page_copy'):
            st.markdown(st.session_state['sales_page_copy'])
            st.download_button("카피 다운로드", st.session_state['sales_page_copy'], "sales_copy.txt")

# === TAB 7: 리드마그넷 ===
with tabs[6]:
    st.markdown("## 리드마그넷")
    
    if not st.session_state['topic']:
        st.info("먼저 주제 선정 탭에서 주제를 입력해주세요.")
    else:
        lead_type = st.selectbox("유형", ["체크리스트", "미니 가이드", "템플릿", "케이스 스터디"])
        
        if st.button("리드마그넷 생성", key="lead"):
            with st.spinner("리드마그넷 생성 중..."):
                prompt = f"""'{st.session_state['topic']}' 전자책의 {lead_type} 리드마그넷을 만들어주세요.
타겟: {st.session_state['target_persona']}

5분 안에 소비 가능하고 메인 상품 구매 욕구를 자극하는 내용으로:
1. 제목
2. 목차 (5-7개)
3. 각 항목별 핵심 내용
4. 메인 상품 유도 문구"""
                result = ask_ai("콘텐츠 마케터", prompt, 0.8)
                st.session_state['lead_magnet'] = result
        
        if st.session_state.get('lead_magnet'):
            st.markdown(st.session_state['lead_magnet'])
            st.download_button("리드마그넷 다운로드", st.session_state['lead_magnet'], "lead_magnet.md")

# === TAB 8: 이메일 퍼널 ===
with tabs[7]:
    st.markdown("## 이메일 퍼널")
    
    if not st.session_state['topic']:
        st.info("먼저 주제 선정 탭에서 주제를 입력해주세요.")
    else:
        if st.button("이메일 시퀀스 생성", key="email"):
            with st.spinner("이메일 퍼널 설계 중..."):
                prompt = f"""'{st.session_state['topic']}' 전자책 판매를 위한 7일 이메일 시퀀스:

Day 0: 환영 + 리드마그넷
Day 1: 가치 제공
Day 2: 스토리
Day 3: 문제 심화
Day 4: 해결책
Day 5: 사회적 증거
Day 6: 긴급성
Day 7: 최종 마감

각 이메일: 제목 + 본문(300자) + CTA"""
                result = ask_ai("이메일 마케팅 전문가", prompt, 0.8)
                st.session_state['email_sequence'] = result
        
        if st.session_state.get('email_sequence'):
            st.markdown(st.session_state['email_sequence'])
            st.download_button("이메일 시퀀스 다운로드", st.session_state['email_sequence'], "email_sequence.md")

# === TAB 9: 최종 출력 ===
with tabs[8]:
    st.markdown("## 최종 출력")
    
    st.markdown("### 완료 현황")
    
    checklist = [
        ("주제 선정", bool(st.session_state.get('topic'))),
        ("시장 분석", bool(st.session_state.get('market_analysis'))),
        ("매출 설계", bool(st.session_state.get('pricing_strategy'))),
        ("목차 설계", bool(st.session_state.get('outline'))),
        ("표지 디자인", bool(st.session_state.get('cover_image'))),
        ("판매페이지", bool(st.session_state.get('sales_page_copy'))),
        ("리드마그넷", bool(st.session_state.get('lead_magnet'))),
        ("이메일 퍼널", bool(st.session_state.get('email_sequence'))),
    ]
    
    cols = st.columns(4)
    for i, (name, done) in enumerate(checklist):
        with cols[i % 4]:
            status = "●" if done else "○"
            color = "rgba(255,255,255,0.9)" if done else "rgba(255,255,255,0.2)"
            st.markdown(f"<span style='color: {color};'>{status} {name}</span>", unsafe_allow_html=True)
    
    completed = sum(1 for _, done in checklist if done)
    st.progress(completed / len(checklist))
    st.markdown(f"<p style='text-align: center; color: rgba(255,255,255,0.4); margin-top: 8px;'>{completed}/{len(checklist)} 완료</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 다운로드
    export_data = {
        "topic": st.session_state.get('topic', ''),
        "book_title": st.session_state.get('book_title', ''),
        "subtitle": st.session_state.get('subtitle', ''),
        "market_analysis": st.session_state.get('market_analysis', {}),
        "pricing_strategy": st.session_state.get('pricing_strategy', {}),
        "outline": st.session_state.get('full_outline', ''),
        "sales_page_copy": st.session_state.get('sales_page_copy', ''),
        "lead_magnet": st.session_state.get('lead_magnet', ''),
        "email_sequence": st.session_state.get('email_sequence', ''),
        "exported_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "전체 데이터 다운로드 (JSON)",
            json.dumps(export_data, ensure_ascii=False, indent=2),
            f"cashmaker_{datetime.now().strftime('%Y%m%d')}.json",
            "application/json",
            use_container_width=True
        )
    with col2:
        bundle = f"""# {st.session_state.get('book_title', '전자책')}

## 판매페이지
{st.session_state.get('sales_page_copy', '')}

---

## 리드마그넷
{st.session_state.get('lead_magnet', '')}

---

## 이메일 시퀀스
{st.session_state.get('email_sequence', '')}"""
        st.download_button("마케팅 자료 다운로드 (MD)", bundle, "marketing.md", use_container_width=True)

# --- 푸터 ---
st.markdown("""
<div style="text-align: center; padding: 60px 0 40px 0; margin-top: 80px; border-top: 1px solid rgba(255,255,255,0.06);">
    <span style="font-size: 11px; color: rgba(255,255,255,0.2); letter-spacing: 0.1em;">CASHMAKER v2.0</span>
</div>
""", unsafe_allow_html=True)
