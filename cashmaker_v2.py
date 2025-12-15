import streamlit as st
import google.generativeai as genai
import re
import json
import io
import os
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from io import BytesIO
import tempfile

# --- 페이지 설정 ---
st.set_page_config(
    page_title="전자책 수익화 시스템", 
    layout="wide", 
    page_icon="💰"
)

# --- 한글 폰트 다운로드 및 캐싱 ---
@st.cache_resource
def get_korean_font(size=60, weight="Bold"):
    """한글 폰트 다운로드 및 로드"""
    font_urls = {
        "Bold": "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansCJKkr-Bold.otf",
        "Regular": "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansCJKkr-Regular.otf",
        "Black": "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansCJKkr-Black.otf",
        "Medium": "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansCJKkr-Medium.otf",
    }
    
    try:
        url = font_urls.get(weight, font_urls["Bold"])
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            font_data = BytesIO(response.content)
            return ImageFont.truetype(font_data, size)
    except Exception as e:
        st.warning(f"폰트 로드 실패: {e}")
    
    return ImageFont.load_default()

# --- CSS 스타일 ---
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    * { font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif; }
    
    .stDeployButton {display:none;} 
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
    }
    
    .stApp { background: #ffffff; }
    
    .main .block-container {
        background: #ffffff;
        padding: 2rem 3rem;
        max-width: 1400px;
    }
    
    [data-testid="stSidebar"] {
        background: #fafafa;
        border-right: 1px solid #eeeeee;
    }
    
    .stMarkdown, .stText, p, span, label, .stMarkdown p {
        color: #222222 !important;
        line-height: 1.7;
    }
    
    h1 { color: #111111 !important; font-weight: 700 !important; font-size: 2rem !important; }
    h2 { color: #111111 !important; font-weight: 700 !important; font-size: 1.4rem !important; margin-top: 2rem !important; }
    h3 { color: #222222 !important; font-weight: 600 !important; font-size: 1.1rem !important; }
    
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        gap: 0;
        border-bottom: 2px solid #eeeeee;
        padding: 0;
        flex-wrap: wrap;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #888888 !important;
        border-radius: 0;
        font-weight: 500;
        padding: 12px 16px;
        font-size: 14px;
        border-bottom: 2px solid transparent;
        margin-bottom: -2px;
    }
    
    .stTabs [aria-selected="true"] {
        background: transparent !important;
        color: #111111 !important;
        font-weight: 700 !important;
        border-bottom: 2px solid #111111 !important;
    }
    
    .stButton > button { 
        width: 100%; 
        border-radius: 30px; 
        font-weight: 600; 
        background: #111111 !important;
        color: #ffffff !important;
        border: none !important;
        padding: 14px 32px;
        font-size: 15px;
    }
    
    .stButton > button:hover { 
        background: #333333 !important;
        transform: translateY(-1px);
    }
    
    .stButton > button p, .stButton > button span, .stButton > button * {
        color: #ffffff !important;
    }
    
    .stDownloadButton > button {
        background: #2d5a27 !important;
        color: #ffffff !important;
        border-radius: 30px;
    }
    
    .stDownloadButton > button p, .stDownloadButton > button * {
        color: #ffffff !important;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #ffffff !important;
        border: 1px solid #dddddd !important;
        border-radius: 8px !important;
        color: #222222 !important;
        padding: 14px 16px !important;
    }
    
    .stSelectbox > div > div {
        background: #ffffff !important;
        border: 1px solid #dddddd !important;
        border-radius: 8px !important;
    }
    
    .hero-section {
        text-align: center;
        padding: 40px 20px;
        margin-bottom: 30px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        color: white;
    }
    
    .hero-title {
        font-size: 36px;
        font-weight: 800;
        color: #ffffff !important;
        margin-bottom: 10px;
    }
    
    .hero-subtitle {
        font-size: 16px;
        color: rgba(255,255,255,0.9) !important;
    }
    
    .info-card {
        background: #f8f8f8;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
    }
    
    .info-card-title {
        font-size: 12px;
        font-weight: 700;
        color: #888888;
        letter-spacing: 1px;
        margin-bottom: 12px;
        text-transform: uppercase;
    }
    
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        color: white;
    }
    
    .score-number {
        font-size: 60px;
        font-weight: 800;
        color: #ffffff;
    }
    
    .metric-card {
        background: #f8f8f8;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #111111;
    }
    
    .metric-label {
        font-size: 13px;
        color: #666666;
        margin-top: 5px;
    }
    
    .funnel-step {
        background: #f0f0f0;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# --- 비밀번호 ---
CORRECT_PASSWORD = "cashmaker2024"

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown("""
    <div style="max-width: 400px; margin: 100px auto; padding: 40px; background: #fff; border: 1px solid #eee; border-radius: 20px; text-align: center;">
        <h1 style="font-size: 28px; margin-bottom: 5px;">💰 CASHMAKER</h1>
        <p style="color: #888; margin-bottom: 30px;">전자책 수익화 시스템</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        password_input = st.text_input("비밀번호", type="password", placeholder="비밀번호 입력")
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
    'outline': [], 'chapters': {}, 'book_title': '', 'subtitle': '',
    'topic_score': None, 'score_details': None, 'generated_titles': None,
    'market_analysis': None, 'pricing_strategy': None, 'sales_page_copy': None,
    'lead_magnet': None, 'email_sequence': None, 'design_settings': {},
    'api_key': ''
}

for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- 사이드바 ---
with st.sidebar:
    st.markdown("### 💰 수익화 진행률")
    
    progress_items = [
        bool(st.session_state['topic']),
        bool(st.session_state['market_analysis']),
        bool(st.session_state['outline']),
        bool(st.session_state['pricing_strategy']),
        bool(st.session_state['sales_page_copy']),
    ]
    progress = sum(progress_items) / len(progress_items) * 100
    st.progress(progress / 100)
    st.caption(f"{progress:.0f}% 완료")
    
    st.markdown("---")
    
    if st.session_state['topic']:
        st.caption(f"📚 {st.session_state['topic']}")
    if st.session_state['book_title']:
        st.caption(f"📖 {st.session_state['book_title']}")
    
    st.markdown("---")
    st.markdown("### ⚙️ API 설정")
    
    api_key_input = st.text_input(
        "Gemini API 키",
        value=st.session_state['api_key'],
        type="password",
        placeholder="AIza..."
    )
    if api_key_input:
        st.session_state['api_key'] = api_key_input
    
    with st.expander("API 키 발급 (무료)"):
        st.markdown("""
        1. [Google AI Studio](https://aistudio.google.com/apikey) 접속
        2. 구글 로그인
        3. "API 키 만들기" 클릭
        4. 복사해서 붙여넣기
        """)
    
    if st.session_state.get('api_key'):
        st.caption("✅ API 연결됨")
    else:
        st.caption("⚠️ API 키 필요")

# --- AI 함수 ---
def get_api_key():
    return st.session_state.get('api_key', '')

def ask_ai(system_role, prompt, temperature=0.7):
    api_key = get_api_key()
    if not api_key:
        return "⚠️ API 키를 먼저 입력해주세요."
    
    try:
        genai.configure(api_key=api_key)
        ai_model = genai.GenerativeModel('models/gemini-2.0-flash')
        generation_config = genai.types.GenerationConfig(temperature=temperature)
        full_prompt = f"당신은 {system_role}입니다.\n\n{prompt}\n\n한국어로 답변해주세요."
        response = ai_model.generate_content(full_prompt, generation_config=generation_config)
        return response.text
    except Exception as e:
        return f"오류 발생: {str(e)}"

# --- 전문가급 이미지 생성 함수 ---
def create_book_cover(title, subtitle, style="premium_dark"):
    """프리미엄 전자책 표지 이미지 생성"""
    width, height = 800, 1200
    
    # 폰트 로드
    title_font = get_korean_font(72, "Black")
    subtitle_font = get_korean_font(28, "Regular")
    author_font = get_korean_font(20, "Medium")
    
    # 스타일별 설정
    styles = {
        "premium_dark": {
            "bg_colors": [(15, 15, 25), (35, 35, 55)],
            "accent": (255, 215, 0),  # 골드
            "text_color": (255, 255, 255),
            "sub_color": (180, 180, 180),
        },
        "modern_gradient": {
            "bg_colors": [(102, 126, 234), (118, 75, 162)],
            "accent": (255, 255, 255),
            "text_color": (255, 255, 255),
            "sub_color": (220, 220, 255),
        },
        "elegant_white": {
            "bg_colors": [(250, 250, 250), (235, 235, 240)],
            "accent": (30, 30, 30),
            "text_color": (20, 20, 20),
            "sub_color": (100, 100, 100),
        },
        "bold_red": {
            "bg_colors": [(180, 40, 50), (120, 20, 30)],
            "accent": (255, 255, 255),
            "text_color": (255, 255, 255),
            "sub_color": (255, 200, 200),
        },
        "professional_navy": {
            "bg_colors": [(20, 40, 80), (10, 25, 50)],
            "accent": (100, 200, 255),
            "text_color": (255, 255, 255),
            "sub_color": (180, 200, 220),
        },
    }
    
    s = styles.get(style, styles["premium_dark"])
    
    # 이미지 생성
    img = Image.new('RGB', (width, height), s["bg_colors"][0])
    draw = ImageDraw.Draw(img)
    
    # 그라데이션 배경
    for i in range(height):
        ratio = i / height
        r = int(s["bg_colors"][0][0] + (s["bg_colors"][1][0] - s["bg_colors"][0][0]) * ratio)
        g = int(s["bg_colors"][0][1] + (s["bg_colors"][1][1] - s["bg_colors"][0][1]) * ratio)
        b = int(s["bg_colors"][0][2] + (s["bg_colors"][1][2] - s["bg_colors"][0][2]) * ratio)
        draw.line([(0, i), (width, i)], fill=(r, g, b))
    
    # 장식 요소 - 상단 악센트 라인
    draw.rectangle([(60, 120), (width - 60, 125)], fill=s["accent"])
    
    # 장식 요소 - 기하학적 도형
    if style in ["premium_dark", "professional_navy"]:
        # 우측 상단 원
        for i in range(3):
            offset = i * 30
            alpha_color = tuple(max(0, min(255, c - 50 + i * 20)) for c in s["accent"])
            draw.ellipse([(width - 200 + offset, 180 + offset), (width - 80 + offset, 300 + offset)], 
                        outline=alpha_color, width=2)
    
    # 제목 텍스트 - 여러 줄 처리
    title_lines = []
    current_line = ""
    for char in title:
        test_line = current_line + char
        bbox = draw.textbbox((0, 0), test_line, font=title_font)
        if bbox[2] - bbox[0] < width - 120:
            current_line = test_line
        else:
            if current_line:
                title_lines.append(current_line)
            current_line = char
    if current_line:
        title_lines.append(current_line)
    
    # 제목 그리기 (중앙 배치)
    title_y = 450
    line_height = 95
    
    for i, line in enumerate(title_lines[:3]):  # 최대 3줄
        bbox = draw.textbbox((0, 0), line, font=title_font)
        line_width = bbox[2] - bbox[0]
        x = (width - line_width) // 2
        y = title_y + (i * line_height)
        
        # 그림자 효과
        shadow_offset = 3
        draw.text((x + shadow_offset, y + shadow_offset), line, font=title_font, 
                  fill=(0, 0, 0))
        draw.text((x, y), line, font=title_font, fill=s["text_color"])
    
    # 부제목
    if subtitle:
        subtitle_y = title_y + len(title_lines) * line_height + 50
        bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        sub_width = bbox[2] - bbox[0]
        sub_x = (width - sub_width) // 2
        draw.text((sub_x, subtitle_y), subtitle, font=subtitle_font, fill=s["sub_color"])
    
    # 하단 악센트 라인
    draw.rectangle([(60, height - 150), (width - 60, height - 145)], fill=s["accent"])
    
    # 저자 영역 (선택사항)
    author_text = "CASHMAKER"
    bbox = draw.textbbox((0, 0), author_text, font=author_font)
    author_width = bbox[2] - bbox[0]
    draw.text(((width - author_width) // 2, height - 100), author_text, 
              font=author_font, fill=s["sub_color"])
    
    return img


def create_thumbnail(title, style="modern"):
    """크몽 썸네일 이미지 생성 (800x600)"""
    width, height = 800, 600
    
    # 폰트 로드
    title_font = get_korean_font(52, "Black")
    sub_font = get_korean_font(24, "Medium")
    
    styles = {
        "modern": {
            "bg_colors": [(102, 126, 234), (118, 75, 162)],
            "text_color": (255, 255, 255),
            "accent": (255, 215, 0),
        },
        "professional": {
            "bg_colors": [(25, 25, 35), (45, 45, 65)],
            "text_color": (255, 255, 255),
            "accent": (0, 200, 150),
        },
        "energetic": {
            "bg_colors": [(255, 100, 100), (255, 150, 50)],
            "text_color": (255, 255, 255),
            "accent": (255, 255, 255),
        },
        "clean": {
            "bg_colors": [(255, 255, 255), (245, 245, 250)],
            "text_color": (30, 30, 30),
            "accent": (102, 126, 234),
        },
        "luxury": {
            "bg_colors": [(20, 20, 30), (40, 40, 60)],
            "text_color": (255, 215, 0),
            "accent": (255, 215, 0),
        },
    }
    
    s = styles.get(style, styles["modern"])
    
    img = Image.new('RGB', (width, height), s["bg_colors"][0])
    draw = ImageDraw.Draw(img)
    
    # 그라데이션
    for i in range(height):
        ratio = i / height
        r = int(s["bg_colors"][0][0] + (s["bg_colors"][1][0] - s["bg_colors"][0][0]) * ratio)
        g = int(s["bg_colors"][0][1] + (s["bg_colors"][1][1] - s["bg_colors"][0][1]) * ratio)
        b = int(s["bg_colors"][0][2] + (s["bg_colors"][1][2] - s["bg_colors"][0][2]) * ratio)
        draw.line([(0, i), (width, i)], fill=(r, g, b))
    
    # 악센트 라인 (상단)
    draw.rectangle([(0, 0), (width, 8)], fill=s["accent"])
    
    # 제목 줄바꿈 처리
    title_lines = []
    current_line = ""
    for char in title:
        test_line = current_line + char
        bbox = draw.textbbox((0, 0), test_line, font=title_font)
        if bbox[2] - bbox[0] < width - 100:
            current_line = test_line
        else:
            if current_line:
                title_lines.append(current_line)
            current_line = char
    if current_line:
        title_lines.append(current_line)
    
    # 제목 중앙 배치
    line_height = 70
    total_height = len(title_lines) * line_height
    start_y = (height - total_height) // 2
    
    for i, line in enumerate(title_lines[:2]):  # 최대 2줄
        bbox = draw.textbbox((0, 0), line, font=title_font)
        line_width = bbox[2] - bbox[0]
        x = (width - line_width) // 2
        y = start_y + i * line_height
        
        # 그림자
        draw.text((x + 2, y + 2), line, font=title_font, fill=(0, 0, 0, 100))
        draw.text((x, y), line, font=title_font, fill=s["text_color"])
    
    # 하단 악센트
    draw.rectangle([(0, height - 8), (width, height)], fill=s["accent"])
    
    return img


def create_sales_page_header(headline, subheadline, cta_text, style="dark"):
    """상세페이지 헤더 이미지 생성 (1200x628 - 소셜 최적화)"""
    width, height = 1200, 628
    
    # 폰트 로드
    headline_font = get_korean_font(56, "Black")
    sub_font = get_korean_font(26, "Regular")
    cta_font = get_korean_font(22, "Bold")
    
    styles = {
        "dark": {
            "bg_colors": [(20, 20, 35), (40, 40, 70)],
            "text_color": (255, 255, 255),
            "sub_color": (180, 180, 200),
            "cta_bg": (102, 126, 234),
            "cta_text": (255, 255, 255),
        },
        "gradient": {
            "bg_colors": [(102, 126, 234), (118, 75, 162)],
            "text_color": (255, 255, 255),
            "sub_color": (220, 220, 255),
            "cta_bg": (255, 255, 255),
            "cta_text": (102, 126, 234),
        },
        "light": {
            "bg_colors": [(255, 255, 255), (245, 245, 250)],
            "text_color": (30, 30, 30),
            "sub_color": (100, 100, 100),
            "cta_bg": (30, 30, 30),
            "cta_text": (255, 255, 255),
        },
    }
    
    s = styles.get(style, styles["dark"])
    
    img = Image.new('RGB', (width, height), s["bg_colors"][0])
    draw = ImageDraw.Draw(img)
    
    # 그라데이션
    for i in range(height):
        ratio = i / height
        r = int(s["bg_colors"][0][0] + (s["bg_colors"][1][0] - s["bg_colors"][0][0]) * ratio)
        g = int(s["bg_colors"][0][1] + (s["bg_colors"][1][1] - s["bg_colors"][0][1]) * ratio)
        b = int(s["bg_colors"][0][2] + (s["bg_colors"][1][2] - s["bg_colors"][0][2]) * ratio)
        draw.line([(0, i), (width, i)], fill=(r, g, b))
    
    # 장식 원
    if style == "dark":
        draw.ellipse([(width - 250, -80), (width + 50, 220)], 
                     fill=(102, 126, 234, 30), outline=(102, 126, 234, 50))
        draw.ellipse([(-100, height - 200), (200, height + 100)], 
                     fill=(118, 75, 162, 30), outline=(118, 75, 162, 50))
    
    # 헤드라인 줄바꿈
    headline_lines = []
    current_line = ""
    for char in headline:
        test_line = current_line + char
        bbox = draw.textbbox((0, 0), test_line, font=headline_font)
        if bbox[2] - bbox[0] < width - 150:
            current_line = test_line
        else:
            if current_line:
                headline_lines.append(current_line)
            current_line = char
    if current_line:
        headline_lines.append(current_line)
    
    # 헤드라인 그리기
    y_pos = 150
    line_height = 75
    
    for i, line in enumerate(headline_lines[:2]):
        bbox = draw.textbbox((0, 0), line, font=headline_font)
        line_width = bbox[2] - bbox[0]
        x = (width - line_width) // 2
        
        # 그림자
        draw.text((x + 3, y_pos + 3), line, font=headline_font, fill=(0, 0, 0))
        draw.text((x, y_pos), line, font=headline_font, fill=s["text_color"])
        y_pos += line_height
    
    # 서브헤드라인
    if subheadline:
        y_pos += 30
        bbox = draw.textbbox((0, 0), subheadline, font=sub_font)
        sub_width = bbox[2] - bbox[0]
        draw.text(((width - sub_width) // 2, y_pos), subheadline, 
                  font=sub_font, fill=s["sub_color"])
    
    # CTA 버튼
    if cta_text:
        btn_width, btn_height = 320, 60
        btn_x = (width - btn_width) // 2
        btn_y = height - 120
        
        # 버튼 배경 (둥근 모서리)
        draw.rounded_rectangle(
            [(btn_x, btn_y), (btn_x + btn_width, btn_y + btn_height)],
            radius=30,
            fill=s["cta_bg"]
        )
        
        # 버튼 텍스트
        bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = btn_x + (btn_width - text_width) // 2
        text_y = btn_y + (btn_height - text_height) // 2 - 3
        draw.text((text_x, text_y), cta_text, font=cta_font, fill=s["cta_text"])
    
    return img


def create_benefit_card(title, benefits, style="dark"):
    """혜택 카드 이미지 생성"""
    width, height = 800, 1000
    
    title_font = get_korean_font(42, "Bold")
    benefit_font = get_korean_font(26, "Regular")
    icon_font = get_korean_font(32, "Bold")
    
    if style == "dark":
        bg_color = (25, 25, 40)
        text_color = (255, 255, 255)
        accent = (102, 126, 234)
    else:
        bg_color = (255, 255, 255)
        text_color = (30, 30, 30)
        accent = (102, 126, 234)
    
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # 상단 악센트
    draw.rectangle([(0, 0), (width, 6)], fill=accent)
    
    # 제목
    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = bbox[2] - bbox[0]
    draw.text(((width - title_width) // 2, 60), title, font=title_font, fill=text_color)
    
    # 구분선
    draw.rectangle([(100, 140), (width - 100, 142)], fill=accent)
    
    # 혜택 리스트
    y_pos = 200
    for i, benefit in enumerate(benefits[:6]):
        # 체크 아이콘
        draw.text((60, y_pos), "✓", font=icon_font, fill=accent)
        
        # 혜택 텍스트
        draw.text((110, y_pos + 5), benefit, font=benefit_font, fill=text_color)
        y_pos += 80
    
    # 하단 악센트
    draw.rectangle([(0, height - 6), (width, height)], fill=accent)
    
    return img


# --- 메인 UI ---
st.markdown("""
<div class="hero-section">
    <div class="hero-title">💰 전자책 수익화 시스템</div>
    <div class="hero-subtitle">기획부터 판매까지, 원스톱 자동화</div>
</div>
""", unsafe_allow_html=True)

# 메인 탭
tabs = st.tabs([
    "1️⃣ 주제 선정", 
    "2️⃣ 시장 분석",
    "3️⃣ 매출 설계",
    "4️⃣ 목차 & 본문", 
    "5️⃣ 디자인 생성",
    "6️⃣ 판매페이지",
    "7️⃣ 리드마그넷",
    "8️⃣ 이메일 퍼널",
    "9️⃣ 최종 출력"
])

# === TAB 1: 주제 선정 ===
with tabs[0]:
    st.markdown("## 📌 주제 선정 & 적합도 분석")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Step 1. 주제 입력")
        
        topic_input = st.text_input(
            "어떤 주제로 전자책을 쓸까요?",
            value=st.session_state['topic'],
            placeholder="예: 크몽으로 월 500만원 벌기"
        )
        st.session_state['topic'] = topic_input
        
        persona = st.text_area(
            "타겟 독자는 누구인가요?",
            value=st.session_state['target_persona'],
            placeholder="예: 30대 직장인, 퇴근 후 부업으로 월 100만원 원하는 사람",
            height=80
        )
        st.session_state['target_persona'] = persona
        
        pain_points = st.text_area(
            "타겟의 가장 큰 고민은?",
            value=st.session_state['pain_points'],
            placeholder="예: 시간이 없다, 뭘 해야 할지 모르겠다",
            height=80
        )
        st.session_state['pain_points'] = pain_points
        
        if st.button("🔍 적합도 분석하기", key="analyze_btn"):
            if not topic_input:
                st.error("주제를 입력해주세요.")
            else:
                with st.spinner("AI가 분석 중..."):
                    prompt = f"""'{topic_input}' 주제의 전자책 수익화 적합도를 분석해주세요.

5가지 항목을 0~100점으로 채점하세요:
1. 시장성 - 수요가 있는가?
2. 수익성 - 사람들이 돈을 낼 주제인가?
3. 차별화 - 경쟁에서 이길 수 있는가?
4. 작성 난이도 - 만들기 쉬운가?
5. 지속성 - 오래 팔릴 수 있는가?

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
                    result = ask_ai("전자책 시장 분석가", prompt, 0.3)
                    try:
                        json_match = re.search(r'\{[\s\S]*\}', result)
                        if json_match:
                            st.session_state['score_details'] = json.loads(json_match.group())
                            st.session_state['topic_score'] = st.session_state['score_details'].get('total_score', 0)
                    except:
                        st.error("분석 오류. 다시 시도해주세요.")
    
    with col2:
        st.markdown("### Step 2. 분석 결과")
        
        if st.session_state.get('topic_score'):
            score = st.session_state['topic_score']
            details = st.session_state['score_details']
            
            st.markdown(f"""
            <div class="score-card">
                <div class="score-number">{score}</div>
                <div style="color: rgba(255,255,255,0.8);">종합 점수</div>
                <div style="margin-top: 15px; padding: 8px 20px; background: rgba(255,255,255,0.2); border-radius: 20px; display: inline-block;">
                    {details.get('verdict', '분석중')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### 세부 점수")
            
            metrics = [
                ("시장성", "market"), ("수익성", "profit"), ("차별화", "differentiation"),
                ("난이도", "difficulty"), ("지속성", "sustainability")
            ]
            
            cols = st.columns(5)
            for i, (name, key) in enumerate(metrics):
                with cols[i]:
                    val = details.get(key, {}).get('score', 0)
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{val}</div>
                        <div class="metric-label">{name}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.info(f"💡 {details.get('summary', '')}")
        else:
            st.markdown("""
            <div style="text-align: center; padding: 60px; background: #f8f8f8; border-radius: 16px;">
                <p style="color: #888;">주제를 입력하고 분석 버튼을 클릭하세요</p>
            </div>
            """, unsafe_allow_html=True)

# === TAB 2: 시장 분석 ===
with tabs[1]:
    st.markdown("## 🔍 시장 분석 & 경쟁 조사")
    
    if not st.session_state['topic']:
        st.warning("먼저 '주제 선정' 탭에서 주제를 입력해주세요.")
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 경쟁 분석 & 포지셔닝")
            
            if st.button("🎯 시장 분석 시작", key="market_analysis_btn"):
                with st.spinner("시장 데이터 분석 중..."):
                    prompt = f"""'{st.session_state['topic']}' 주제로 전자책 시장을 분석해주세요.

타겟: {st.session_state['target_persona']}
타겟 고민: {st.session_state['pain_points']}

다음을 분석해주세요:

1. **경쟁 현황** - 주요 경쟁자 3개와 강점/약점, 평균 가격대
2. **타겟 고객 심층 분석** - 표면적/본질적 페인포인트, 구매 트리거
3. **차별화 기회** - 블루오션 포지셔닝
4. **키워드** - 타겟이 검색할 키워드 10개

JSON 형식:
{{
    "competitors": [{{"name": "경쟁자", "price": "가격", "strength": "강점", "weakness": "약점"}}],
    "avg_price": "평균가격",
    "target_analysis": {{"surface_pain": ["표면적 고민"], "deep_pain": ["본질적 고민"], "triggers": ["구매 트리거"]}},
    "differentiation": {{"positioning": "포지셔닝 전략", "unique_angle": "독특한 각도"}},
    "keywords": ["키워드1", "키워드2"],
    "summary": "요약"
}}"""
                    result = ask_ai("시장 분석 전문가", prompt, 0.5)
                    try:
                        json_match = re.search(r'\{[\s\S]*\}', result)
                        if json_match:
                            st.session_state['market_analysis'] = json.loads(json_match.group())
                    except:
                        st.session_state['market_analysis'] = {"raw": result}
            
            if st.session_state.get('market_analysis'):
                data = st.session_state['market_analysis']
                
                if 'competitors' in data:
                    st.markdown("#### 🏆 경쟁자 분석")
                    for comp in data.get('competitors', [])[:3]:
                        st.markdown(f"""
                        <div class="info-card">
                            <strong>{comp.get('name', '')}</strong> - {comp.get('price', '')}
                            <br>✅ {comp.get('strength', '')}
                            <br>❌ {comp.get('weakness', '')}
                        </div>
                        """, unsafe_allow_html=True)
        
        with col2:
            if st.session_state.get('market_analysis'):
                data = st.session_state['market_analysis']
                
                st.markdown("#### 🎯 타겟 심층 분석")
                if 'target_analysis' in data:
                    ta = data['target_analysis']
                    st.markdown("**본질적 고민:**")
                    for pain in ta.get('deep_pain', []):
                        st.markdown(f"- 💎 {pain}")
                    st.markdown("**구매 트리거:**")
                    for trigger in ta.get('triggers', []):
                        st.markdown(f"- 🎯 {trigger}")
                
                st.markdown("#### ✨ 차별화 전략")
                if 'differentiation' in data:
                    diff = data['differentiation']
                    st.success(f"**포지셔닝:** {diff.get('positioning', '')}")
                
                st.markdown("#### 🔑 키워드")
                keywords = data.get('keywords', [])
                if keywords:
                    st.markdown(" | ".join([f"`{kw}`" for kw in keywords[:10]]))

# === TAB 3: 매출 설계 ===
with tabs[2]:
    st.markdown("## 💰 매출 구조 설계")
    
    if not st.session_state['topic']:
        st.warning("먼저 '주제 선정' 탭에서 주제를 입력해주세요.")
    else:
        if st.button("💵 매출 전략 생성", key="pricing_btn"):
            with st.spinner("수익화 전략 설계 중..."):
                prompt = f"""'{st.session_state['topic']}' 전자책의 매출 극대화 전략을 설계해주세요.

타겟: {st.session_state['target_persona']}

다음을 설계:
1. 가격 전략 (얼리버드/정가/프리미엄)
2. 오퍼 구조 (메인 상품 + 보너스 3개 + 보증)
3. 업셀 퍼널 (프론트/미들/백엔드)
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
                    st.session_state['pricing_strategy'] = {"raw": result}
        
        if st.session_state.get('pricing_strategy'):
            data = st.session_state['pricing_strategy']
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'pricing' in data:
                    pricing = data['pricing']
                    st.markdown("#### 💵 가격 전략")
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("얼리버드", pricing.get('earlybird', ''))
                    with cols[1]:
                        st.metric("추천가", pricing.get('recommended', ''))
                    with cols[2]:
                        st.metric("프리미엄", pricing.get('premium', ''))
                    st.info(f"💡 {pricing.get('reason', '')}")
            
            with col2:
                if 'offer' in data:
                    offer = data['offer']
                    st.markdown("#### 🎁 오퍼 구성")
                    for i, bonus in enumerate(offer.get('bonuses', []), 1):
                        st.markdown(f"🎁 보너스 {i}: {bonus}")
                    st.success(f"✅ 보증: {offer.get('guarantee', '')}")
                
                if 'simulation' in data:
                    sim = data['simulation']
                    st.markdown(f"#### 💰 예상 월매출: **{sim.get('monthly_revenue', '')}**")

# === TAB 4: 목차 & 본문 ===
with tabs[3]:
    st.markdown("## 📝 목차 설계 & 본문 작성")
    
    if not st.session_state['topic']:
        st.warning("먼저 '주제 선정' 탭에서 주제를 입력해주세요.")
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 제목 생성")
            title_input = st.text_input("전자책 제목", value=st.session_state['book_title'])
            st.session_state['book_title'] = title_input
            
            subtitle_input = st.text_input("부제목", value=st.session_state['subtitle'])
            st.session_state['subtitle'] = subtitle_input
            
            if st.button("✨ AI 제목 추천", key="title_gen"):
                with st.spinner("베스트셀러급 제목 생성 중..."):
                    prompt = f"""'{st.session_state['topic']}' 주제의 전자책 제목 5개를 만들어주세요.
타겟: {st.session_state['target_persona']}

JSON 형식:
{{"titles": [{{"title": "제목", "subtitle": "부제목", "reason": "이유"}}]}}"""
                    result = ask_ai("베스트셀러 작가", prompt, 0.9)
                    try:
                        json_match = re.search(r'\{[\s\S]*\}', result)
                        if json_match:
                            st.session_state['generated_titles'] = json.loads(json_match.group())
                    except:
                        pass
            
            if st.session_state.get('generated_titles'):
                for t in st.session_state['generated_titles'].get('titles', [])[:5]:
                    st.markdown(f"**{t.get('title', '')}** - {t.get('subtitle', '')}")
        
        with col2:
            st.markdown("### 목차 생성")
            
            if st.button("📋 AI 목차 생성", key="outline_gen"):
                with st.spinner("목차 설계 중..."):
                    prompt = f"""'{st.session_state['topic']}' 주제로 6~7개 챕터 목차를 설계해주세요.
타겟: {st.session_state['target_persona']}

형식:
## 챕터1: [제목]
- 소제목1
- 소제목2
- 소제목3"""
                    result = ask_ai("출판기획자", prompt, 0.85)
                    chapters = re.findall(r'## (챕터\d+:?\s*.+)', result)
                    if not chapters:
                        chapters = [line.strip() for line in result.split('\n') if '챕터' in line][:7]
                    st.session_state['outline'] = chapters
                    st.session_state['full_outline'] = result
            
            if st.session_state.get('full_outline'):
                st.text_area("전체 목차", value=st.session_state['full_outline'], height=400)

# === TAB 5: 디자인 생성 ===
with tabs[4]:
    st.markdown("## 🎨 프리미엄 디자인 생성")
    st.info("📌 한글 폰트를 로딩합니다. 첫 생성 시 10~20초 정도 걸릴 수 있습니다.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📕 전자책 표지")
        
        cover_title = st.text_input("표지 제목", value=st.session_state.get('book_title', ''), key="cover_title")
        cover_subtitle = st.text_input("표지 부제목", value=st.session_state.get('subtitle', ''), key="cover_subtitle")
        cover_style = st.selectbox(
            "표지 스타일", 
            ["premium_dark", "modern_gradient", "elegant_white", "bold_red", "professional_navy"],
            format_func=lambda x: {
                "premium_dark": "🖤 프리미엄 다크 (골드 악센트)",
                "modern_gradient": "💜 모던 그라데이션",
                "elegant_white": "🤍 엘레강트 화이트",
                "bold_red": "❤️ 볼드 레드",
                "professional_navy": "💙 프로페셔널 네이비"
            }.get(x, x)
        )
        
        if st.button("🎨 표지 생성", key="gen_cover"):
            if cover_title:
                with st.spinner("프리미엄 표지 생성 중..."):
                    cover_img = create_book_cover(cover_title, cover_subtitle, cover_style)
                    st.session_state['cover_image'] = cover_img
                    st.success("표지 생성 완료!")
        
        if st.session_state.get('cover_image'):
            st.image(st.session_state['cover_image'], caption="전자책 표지 (800x1200)", use_container_width=True)
            buf = BytesIO()
            st.session_state['cover_image'].save(buf, format='PNG')
            st.download_button("📥 표지 다운로드", buf.getvalue(), file_name="book_cover.png", mime="image/png")
    
    with col2:
        st.markdown("### 🖼️ 크몽 썸네일")
        
        thumb_title = st.text_input("썸네일 문구", value=st.session_state.get('book_title', ''), key="thumb_title")
        thumb_style = st.selectbox(
            "썸네일 스타일", 
            ["modern", "professional", "energetic", "clean", "luxury"],
            format_func=lambda x: {
                "modern": "💜 모던 그라데이션",
                "professional": "🖤 프로페셔널 다크",
                "energetic": "🧡 에너제틱 오렌지",
                "clean": "🤍 클린 화이트",
                "luxury": "✨ 럭셔리 골드"
            }.get(x, x)
        )
        
        if st.button("🎨 썸네일 생성", key="gen_thumb"):
            if thumb_title:
                with st.spinner("썸네일 생성 중..."):
                    thumb_img = create_thumbnail(thumb_title, thumb_style)
                    st.session_state['thumbnail_image'] = thumb_img
                    st.success("썸네일 생성 완료!")
        
        if st.session_state.get('thumbnail_image'):
            st.image(st.session_state['thumbnail_image'], caption="크몽 썸네일 (800x600)", use_container_width=True)
            buf = BytesIO()
            st.session_state['thumbnail_image'].save(buf, format='PNG')
            st.download_button("📥 썸네일 다운로드", buf.getvalue(), file_name="thumbnail.png", mime="image/png")
    
    st.markdown("---")
    st.markdown("### 📄 상세페이지 헤더")
    
    col3, col4 = st.columns([1, 1])
    
    with col3:
        sales_headline = st.text_input("헤드라인", placeholder="월급만 믿다가는 평생 가난하다")
        sales_subheadline = st.text_input("서브헤드라인", placeholder="31개월 만에 10억 만든 비밀")
        sales_cta = st.text_input("CTA 버튼", value="지금 바로 시작하기")
        header_style = st.selectbox("스타일", ["dark", "gradient", "light"])
        
        if st.button("🎨 헤더 생성", key="gen_header"):
            if sales_headline:
                with st.spinner("상세페이지 헤더 생성 중..."):
                    header_img = create_sales_page_header(sales_headline, sales_subheadline, sales_cta, header_style)
                    st.session_state['header_image'] = header_img
                    st.success("헤더 생성 완료!")
    
    with col4:
        if st.session_state.get('header_image'):
            st.image(st.session_state['header_image'], caption="상세페이지 헤더 (1200x628)", use_container_width=True)
            buf = BytesIO()
            st.session_state['header_image'].save(buf, format='PNG')
            st.download_button("📥 헤더 다운로드", buf.getvalue(), file_name="sales_header.png", mime="image/png")

# === TAB 6: 판매페이지 ===
with tabs[5]:
    st.markdown("## 📄 판매페이지 카피 생성")
    
    if not st.session_state['topic']:
        st.warning("먼저 '주제 선정' 탭에서 주제를 입력해주세요.")
    else:
        if st.button("✍️ 판매페이지 카피 생성", key="sales_copy_btn"):
            with st.spinner("전환율 높은 카피 작성 중..."):
                prompt = f"""'{st.session_state['topic']}' 전자책의 크몽 상세페이지 카피를 작성해주세요.

제목: {st.session_state.get('book_title', st.session_state['topic'])}
타겟: {st.session_state['target_persona']}

작성 내용:
1. 크몽 상품 제목 (40자)
2. 후킹 헤드라인 3개
3. 문제 제기 (타겟 고통 자극)
4. 해결책 제시 (핵심 가치 3가지)
5. 오퍼 정리 (구성품 + 보너스)
6. CTA (긴급성 문구)
7. FAQ 3개

마크다운 형식으로 작성."""
                result = ask_ai("크몽 탑셀러 마케터", prompt, 0.8)
                st.session_state['sales_page_copy'] = result
        
        if st.session_state.get('sales_page_copy'):
            st.markdown("### 📝 생성된 판매페이지 카피")
            st.markdown(st.session_state['sales_page_copy'])
            st.download_button("📥 카피 다운로드", st.session_state['sales_page_copy'], file_name="sales_copy.txt")

# === TAB 7: 리드마그넷 ===
with tabs[6]:
    st.markdown("## 🎁 리드마그넷 생성")
    
    if not st.session_state['topic']:
        st.warning("먼저 '주제 선정' 탭에서 주제를 입력해주세요.")
    else:
        lead_type = st.selectbox("리드마그넷 유형", ["체크리스트", "미니 가이드", "템플릿", "케이스 스터디"])
        
        if st.button("💡 리드마그넷 생성", key="lead_gen"):
            with st.spinner("리드마그넷 생성 중..."):
                prompt = f"""'{st.session_state['topic']}' 전자책의 {lead_type} 리드마그넷을 만들어주세요.
타겟: {st.session_state['target_persona']}

5분 안에 소비 가능하고, 메인 상품 구매 욕구를 자극하는 내용으로:
1. 제목
2. 목차 (5~7개)
3. 각 항목별 핵심 내용
4. 메인 상품 유도 문구"""
                result = ask_ai("콘텐츠 마케터", prompt, 0.8)
                st.session_state['lead_magnet'] = result
        
        if st.session_state.get('lead_magnet'):
            st.markdown(st.session_state['lead_magnet'])
            st.download_button("📥 리드마그넷 다운로드", st.session_state['lead_magnet'], file_name="lead_magnet.md")

# === TAB 8: 이메일 퍼널 ===
with tabs[7]:
    st.markdown("## 📧 이메일 시퀀스 설계")
    
    if not st.session_state['topic']:
        st.warning("먼저 '주제 선정' 탭에서 주제를 입력해주세요.")
    else:
        if st.button("📧 이메일 시퀀스 생성", key="email_gen"):
            with st.spinner("이메일 퍼널 설계 중..."):
                prompt = f"""'{st.session_state['topic']}' 전자책 판매를 위한 7일 이메일 시퀀스:

Day 0: 환영 + 리드마그넷
Day 1: 가치 제공
Day 2: 스토리
Day 3: 문제 심화
Day 4: 해결책 (전자책 소개)
Day 5: 사회적 증거
Day 6: 긴급성
Day 7: 최종 마감

각 이메일: 제목 + 본문(300자) + CTA"""
                result = ask_ai("이메일 마케팅 전문가", prompt, 0.8)
                st.session_state['email_sequence'] = result
        
        if st.session_state.get('email_sequence'):
            st.markdown(st.session_state['email_sequence'])
            st.download_button("📥 이메일 시퀀스 다운로드", st.session_state['email_sequence'], file_name="email_sequence.md")

# === TAB 9: 최종 출력 ===
with tabs[8]:
    st.markdown("## 📦 최종 출력 & 다운로드")
    
    st.markdown("### ✅ 완성 체크리스트")
    
    checklist = [
        ("주제 선정", bool(st.session_state.get('topic'))),
        ("시장 분석", bool(st.session_state.get('market_analysis'))),
        ("가격 전략", bool(st.session_state.get('pricing_strategy'))),
        ("제목 & 목차", bool(st.session_state.get('outline'))),
        ("표지 디자인", bool(st.session_state.get('cover_image'))),
        ("판매페이지", bool(st.session_state.get('sales_page_copy'))),
        ("리드마그넷", bool(st.session_state.get('lead_magnet'))),
        ("이메일 퍼널", bool(st.session_state.get('email_sequence'))),
    ]
    
    cols = st.columns(4)
    for i, (name, done) in enumerate(checklist):
        with cols[i % 4]:
            st.markdown(f"{'✅' if done else '⬜'} {name}")
    
    completed = sum(1 for _, done in checklist if done)
    st.progress(completed / len(checklist))
    st.caption(f"{completed}/{len(checklist)} 완료")
    
    st.markdown("---")
    
    # 전체 데이터 JSON
    export_data = {
        "topic": st.session_state.get('topic', ''),
        "book_title": st.session_state.get('book_title', ''),
        "subtitle": st.session_state.get('subtitle', ''),
        "market_analysis": st.session_state.get('market_analysis', {}),
        "pricing_strategy": st.session_state.get('pricing_strategy', {}),
        "outline": st.session_state.get('outline', []),
        "sales_page_copy": st.session_state.get('sales_page_copy', ''),
        "lead_magnet": st.session_state.get('lead_magnet', ''),
        "email_sequence": st.session_state.get('email_sequence', ''),
        "exported_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📥 전체 데이터 (JSON)",
            json.dumps(export_data, ensure_ascii=False, indent=2),
            file_name=f"cashmaker_export_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )
    with col2:
        marketing = f"""# {st.session_state.get('book_title', '전자책')}

## 판매페이지
{st.session_state.get('sales_page_copy', '')}

## 리드마그넷
{st.session_state.get('lead_magnet', '')}

## 이메일
{st.session_state.get('email_sequence', '')}"""
        st.download_button("📥 마케팅 자료 (MD)", marketing, file_name="marketing.md", use_container_width=True)

# --- 푸터 ---
st.markdown("""
<div style="text-align: center; padding: 40px; margin-top: 60px; border-top: 1px solid #eee;">
    <span style="color: #888;">전자책 수익화 시스템 — </span>
    <span style="font-weight: 600;">CASHMAKER v2.0</span>
</div>
""", unsafe_allow_html=True)
