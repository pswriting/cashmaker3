import streamlit as st
import google.generativeai as genai
import re
import json
import io
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

# --- 페이지 설정 ---
st.set_page_config(
    page_title="전자책 수익화 시스템", 
    layout="wide", 
    page_icon="💰"
)

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
    
    .design-preview {
        border: 1px solid #ddd;
        border-radius: 12px;
        padding: 20px;
        background: #fafafa;
        text-align: center;
    }
    
    .funnel-step {
        background: #f0f0f0;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
    }
    
    .email-template {
        background: #ffffff;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
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

# --- 이미지 생성 함수 ---
def create_book_cover(title, subtitle, style="gradient"):
    """전자책 표지 이미지 생성"""
    width, height = 800, 1200
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # 배경 그라데이션 효과
    if style == "gradient":
        for i in range(height):
            r = int(102 + (118 - 102) * i / height)
            g = int(126 + (75 - 126) * i / height)
            b = int(234 + (162 - 234) * i / height)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
    elif style == "dark":
        for i in range(height):
            c = int(20 + 15 * i / height)
            draw.line([(0, i), (width, i)], fill=(c, c, c))
    elif style == "warm":
        for i in range(height):
            r = int(255 - 30 * i / height)
            g = int(120 + 50 * i / height)
            b = int(50 + 30 * i / height)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
    
    # 텍스트 (기본 폰트 사용)
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # 제목 중앙 배치
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    
    # 그림자 효과
    draw.text((title_x + 3, 503), title, font=title_font, fill=(0, 0, 0, 100))
    draw.text((title_x, 500), title, font=title_font, fill='white')
    
    # 부제목
    if subtitle:
        sub_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        sub_width = sub_bbox[2] - sub_bbox[0]
        sub_x = (width - sub_width) // 2
        draw.text((sub_x, 600), subtitle, font=subtitle_font, fill='rgba(255,255,255,0.9)')
    
    # 하단 장식 라인
    draw.rectangle([(100, height - 150), (width - 100, height - 145)], fill='white')
    
    return img

def create_thumbnail(title, style="modern"):
    """크몽 썸네일 이미지 생성 (800x600)"""
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # 배경
    if style == "modern":
        for i in range(height):
            r = int(102 + (118 - 102) * i / height)
            g = int(126 + (75 - 126) * i / height)
            b = int(234 + (162 - 234) * i / height)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
    elif style == "professional":
        draw.rectangle([(0, 0), (width, height)], fill=(30, 30, 40))
        # 악센트 라인
        draw.rectangle([(0, height-10), (width, height)], fill=(102, 126, 234))
    elif style == "bright":
        draw.rectangle([(0, 0), (width, height)], fill=(255, 250, 240))
        draw.rectangle([(0, 0), (width, 8)], fill=(255, 100, 100))
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
    except:
        font = ImageFont.load_default()
    
    # 텍스트 줄바꿈 처리
    words = title.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] < width - 100:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    # 텍스트 그리기
    total_height = len(lines) * 60
    start_y = (height - total_height) // 2
    
    text_color = 'white' if style in ['modern', 'professional'] else '#222222'
    
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        x = (width - line_width) // 2
        y = start_y + i * 60
        draw.text((x, y), line, font=font, fill=text_color)
    
    return img

def create_sales_page_image(headline, subheadline, cta_text):
    """상세페이지 헤더 이미지 생성"""
    width, height = 1200, 800
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # 그라데이션 배경
    for i in range(height):
        r = int(30 + 10 * i / height)
        g = int(30 + 10 * i / height)
        b = int(45 + 15 * i / height)
        draw.line([(0, i), (width, i)], fill=(r, g, b))
    
    # 악센트 도형
    draw.ellipse([(width-300, -100), (width+100, 300)], fill=(102, 126, 234, 50))
    draw.ellipse([(-100, height-200), (200, height+100)], fill=(118, 75, 162, 50))
    
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 56)
        sub_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        cta_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        title_font = sub_font = cta_font = ImageFont.load_default()
    
    # 헤드라인
    y_pos = 200
    for line in headline.split('\n')[:2]:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y_pos), line, font=title_font, fill='white')
        y_pos += 70
    
    # 서브헤드라인
    y_pos += 30
    bbox = draw.textbbox((0, 0), subheadline, font=sub_font)
    x = (width - (bbox[2] - bbox[0])) // 2
    draw.text((x, y_pos), subheadline, font=sub_font, fill='#aaaaaa')
    
    # CTA 버튼
    btn_width, btn_height = 300, 60
    btn_x = (width - btn_width) // 2
    btn_y = height - 150
    
    # 버튼 배경
    draw.rounded_rectangle(
        [(btn_x, btn_y), (btn_x + btn_width, btn_y + btn_height)],
        radius=30,
        fill=(102, 126, 234)
    )
    
    # 버튼 텍스트
    bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
    text_x = btn_x + (btn_width - (bbox[2] - bbox[0])) // 2
    text_y = btn_y + (btn_height - (bbox[3] - bbox[1])) // 2
    draw.text((text_x, text_y), cta_text, font=cta_font, fill='white')
    
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

1. **경쟁 현황** (크몽, 탈잉, 클래스101 등에서 비슷한 전자책/강의)
   - 주요 경쟁자 3개와 그들의 강점/약점
   - 평균 가격대
   - 베스트셀러의 공통점

2. **타겟 고객 심층 분석**
   - 진짜 페인포인트 (표면적 vs 본질적)
   - 구매를 망설이는 이유
   - 구매를 결정하는 트리거

3. **차별화 기회**
   - 경쟁자들이 놓치고 있는 것
   - 블루오션 포지셔닝 전략
   - 내가 가진 독특한 강점

4. **키워드 & 수요**
   - 타겟이 검색할 키워드 10개
   - 트렌드 상승/하락 예측
   - SNS에서 핫한 관련 주제

JSON 형식으로 답변:
{{
    "competitors": [
        {{"name": "경쟁자", "price": "가격", "strength": "강점", "weakness": "약점"}}
    ],
    "avg_price": "평균가격",
    "target_analysis": {{
        "surface_pain": ["표면적 고민"],
        "deep_pain": ["본질적 고민"],
        "objections": ["구매 망설이는 이유"],
        "triggers": ["구매 트리거"]
    }},
    "differentiation": {{
        "gaps": ["경쟁자가 놓친 것"],
        "positioning": "포지셔닝 전략",
        "unique_angle": "독특한 각도"
    }},
    "keywords": ["키워드1", "키워드2"],
    "trend": "상승/유지/하락",
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
                    
                    st.markdown(f"**평균 가격대:** {data.get('avg_price', 'N/A')}")
        
        with col2:
            if st.session_state.get('market_analysis'):
                data = st.session_state['market_analysis']
                
                st.markdown("#### 🎯 타겟 심층 분석")
                
                if 'target_analysis' in data:
                    ta = data['target_analysis']
                    
                    st.markdown("**표면적 고민:**")
                    for pain in ta.get('surface_pain', []):
                        st.markdown(f"- {pain}")
                    
                    st.markdown("**본질적 고민 (진짜 원하는 것):**")
                    for pain in ta.get('deep_pain', []):
                        st.markdown(f"- 💎 {pain}")
                    
                    st.markdown("**구매 트리거:**")
                    for trigger in ta.get('triggers', []):
                        st.markdown(f"- 🎯 {trigger}")
                
                st.markdown("#### ✨ 차별화 전략")
                if 'differentiation' in data:
                    diff = data['differentiation']
                    st.success(f"**포지셔닝:** {diff.get('positioning', '')}")
                    st.info(f"**독특한 각도:** {diff.get('unique_angle', '')}")
                
                st.markdown("#### 🔑 타겟 키워드")
                keywords = data.get('keywords', [])
                if keywords:
                    st.markdown(" | ".join([f"`{kw}`" for kw in keywords[:10]]))

# === TAB 3: 매출 설계 ===
with tabs[2]:
    st.markdown("## 💰 매출 구조 설계")
    
    if not st.session_state['topic']:
        st.warning("먼저 '주제 선정' 탭에서 주제를 입력해주세요.")
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 가격 & 오퍼 설계")
            
            if st.button("💵 매출 전략 생성", key="pricing_btn"):
                with st.spinner("수익화 전략 설계 중..."):
                    market_data = st.session_state.get('market_analysis', {})
                    avg_price = market_data.get('avg_price', '미정')
                    
                    prompt = f"""'{st.session_state['topic']}' 전자책의 매출 극대화 전략을 설계해주세요.

타겟: {st.session_state['target_persona']}
경쟁 평균가: {avg_price}

다음을 설계해주세요:

1. **가격 전략**
   - 추천 가격 (근거 포함)
   - 가격 앵커링 전략
   - 얼리버드/정가/프리미엄 3단계

2. **오퍼 구조** (구매 저항 제거)
   - 메인 상품 구성
   - 보너스 3개 (가치 극대화)
   - 보증/환불 정책
   - 긴급성/희소성 요소

3. **업셀 퍼널**
   - 프론트엔드 (진입 상품)
   - 미들엔드 (메인 상품)
   - 백엔드 (고가 상품)
   - 각 단계별 가격과 구성

4. **예상 매출 시뮬레이션**
   - 월 100명 방문 시 예상 매출
   - 전환율 가정과 근거

JSON 형식:
{{
    "pricing": {{
        "recommended": "추천가격",
        "reason": "근거",
        "earlybird": "얼리버드가",
        "regular": "정가",
        "premium": "프리미엄가"
    }},
    "offer": {{
        "main_product": "메인 상품 설명",
        "bonuses": ["보너스1", "보너스2", "보너스3"],
        "guarantee": "보증 정책",
        "urgency": "긴급성 요소",
        "scarcity": "희소성 요소"
    }},
    "funnel": {{
        "frontend": {{"name": "이름", "price": "가격", "desc": "설명"}},
        "middleend": {{"name": "이름", "price": "가격", "desc": "설명"}},
        "backend": {{"name": "이름", "price": "가격", "desc": "설명"}}
    }},
    "simulation": {{
        "visitors": 100,
        "conversion_rate": "3%",
        "avg_order_value": "금액",
        "monthly_revenue": "예상 월매출"
    }}
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
                
                if 'pricing' in data:
                    pricing = data['pricing']
                    st.markdown("#### 💵 가격 전략")
                    
                    cols = st.columns(3)
                    with cols[0]:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div style="font-size: 12px; color: #888;">얼리버드</div>
                            <div class="metric-value" style="color: #2d5a27;">{pricing.get('earlybird', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with cols[1]:
                        st.markdown(f"""
                        <div class="metric-card" style="background: linear-gradient(135deg, #667eea, #764ba2); color: white;">
                            <div style="font-size: 12px; opacity: 0.8;">추천가</div>
                            <div style="font-size: 28px; font-weight: 700;">{pricing.get('recommended', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with cols[2]:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div style="font-size: 12px; color: #888;">프리미엄</div>
                            <div class="metric-value">{pricing.get('premium', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.info(f"💡 {pricing.get('reason', '')}")
        
        with col2:
            if st.session_state.get('pricing_strategy'):
                data = st.session_state['pricing_strategy']
                
                st.markdown("#### 🎁 오퍼 구성")
                if 'offer' in data:
                    offer = data['offer']
                    st.markdown(f"**메인 상품:** {offer.get('main_product', '')}")
                    
                    st.markdown("**보너스:**")
                    for i, bonus in enumerate(offer.get('bonuses', []), 1):
                        st.markdown(f"🎁 보너스 {i}: {bonus}")
                    
                    st.success(f"✅ 보증: {offer.get('guarantee', '')}")
                    st.warning(f"⏰ 긴급성: {offer.get('urgency', '')}")
                
                st.markdown("#### 📈 퍼널 구조")
                if 'funnel' in data:
                    funnel = data['funnel']
                    for stage, info in funnel.items():
                        if isinstance(info, dict):
                            label = {"frontend": "프론트엔드", "middleend": "미들엔드", "backend": "백엔드"}.get(stage, stage)
                            st.markdown(f"""
                            <div class="funnel-step">
                                <strong>{label}</strong>: {info.get('name', '')} - {info.get('price', '')}
                                <br><small>{info.get('desc', '')}</small>
                            </div>
                            """, unsafe_allow_html=True)
                
                if 'simulation' in data:
                    sim = data['simulation']
                    st.markdown("#### 💰 예상 매출")
                    st.markdown(f"""
                    <div class="metric-card" style="background: #f0fff0;">
                        <div class="metric-label">월 100명 방문 시</div>
                        <div class="metric-value" style="color: #2d5a27;">{sim.get('monthly_revenue', '')}</div>
                        <div style="font-size: 12px; color: #666;">전환율 {sim.get('conversion_rate', '')} 기준</div>
                    </div>
                    """, unsafe_allow_html=True)

# === TAB 4: 목차 & 본문 ===
with tabs[3]:
    st.markdown("## 📝 목차 설계 & 본문 작성")
    
    if not st.session_state['topic']:
        st.warning("먼저 '주제 선정' 탭에서 주제를 입력해주세요.")
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 제목 생성")
            
            title_input = st.text_input("전자책 제목", value=st.session_state['book_title'], placeholder="제목 입력")
            st.session_state['book_title'] = title_input
            
            subtitle_input = st.text_input("부제목", value=st.session_state['subtitle'], placeholder="부제목 입력")
            st.session_state['subtitle'] = subtitle_input
            
            if st.button("✨ AI 제목 추천", key="title_gen"):
                with st.spinner("베스트셀러급 제목 생성 중..."):
                    prompt = f"""'{st.session_state['topic']}' 주제의 전자책 제목 5개를 만들어주세요.

타겟: {st.session_state['target_persona']}

[베스트셀러 제목 원칙]
- 7자 이내 임팩트
- 상식 파괴 or 구체적 숫자
- "역행자", "부의 추월차선" 수준

JSON 형식:
{{
    "titles": [
        {{"title": "제목", "subtitle": "부제목", "reason": "이유"}}
    ]
}}"""
                    result = ask_ai("베스트셀러 작가", prompt, 0.9)
                    try:
                        json_match = re.search(r'\{[\s\S]*\}', result)
                        if json_match:
                            st.session_state['generated_titles'] = json.loads(json_match.group())
                    except:
                        pass
            
            if st.session_state.get('generated_titles'):
                for t in st.session_state['generated_titles'].get('titles', [])[:5]:
                    st.markdown(f"""
                    <div class="info-card">
                        <strong>{t.get('title', '')}</strong><br>
                        <small>{t.get('subtitle', '')}</small><br>
                        <span style="color: #888; font-size: 12px;">{t.get('reason', '')}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 목차 생성")
            
            if st.button("📋 AI 목차 생성", key="outline_gen"):
                with st.spinner("목차 설계 중..."):
                    prompt = f"""'{st.session_state['topic']}' 주제로 6~7개 챕터 목차를 설계해주세요.

타겟: {st.session_state['target_persona']}
타겟 고민: {st.session_state['pain_points']}

[챕터 제목 규칙]
- 호기심 자극: "왜 ~할까?"
- 도발적: "~는 거짓말이다"
- 구체적 숫자/스토리

[감정선 흐름]
1. 공감 → 2. 문제 제기 → 3. 반전 → 4. 깨달음 → 5. 실전 → 6. 마인드셋 → 7. 비전

형식:
## 챕터1: [제목]
- 소제목1
- 소제목2
- 소제목3

(6~7개 챕터)"""
                    result = ask_ai("출판기획자", prompt, 0.85)
                    
                    chapters = re.findall(r'## (챕터\d+:?\s*.+)', result)
                    if not chapters:
                        chapters = [line.strip() for line in result.split('\n') if '챕터' in line][:7]
                    
                    st.session_state['outline'] = chapters
                    st.session_state['full_outline'] = result
            
            if st.session_state.get('full_outline'):
                st.text_area("전체 목차", value=st.session_state['full_outline'], height=400)
                
                if st.session_state['outline']:
                    st.success(f"✅ {len(st.session_state['outline'])}개 챕터 생성됨")

# === TAB 5: 디자인 생성 ===
with tabs[4]:
    st.markdown("## 🎨 디자인 자동 생성")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📕 전자책 표지")
        
        cover_title = st.text_input("표지 제목", value=st.session_state.get('book_title', ''), key="cover_title")
        cover_subtitle = st.text_input("표지 부제목", value=st.session_state.get('subtitle', ''), key="cover_subtitle")
        cover_style = st.selectbox("표지 스타일", ["gradient", "dark", "warm"], format_func=lambda x: {"gradient": "그라데이션 (보라)", "dark": "다크 모드", "warm": "따뜻한 톤"}.get(x, x))
        
        if st.button("🎨 표지 생성", key="gen_cover"):
            if cover_title:
                cover_img = create_book_cover(cover_title, cover_subtitle, cover_style)
                st.session_state['cover_image'] = cover_img
                st.success("표지 생성 완료!")
        
        if st.session_state.get('cover_image'):
            st.image(st.session_state['cover_image'], caption="전자책 표지", use_container_width=True)
            
            # 다운로드
            buf = BytesIO()
            st.session_state['cover_image'].save(buf, format='PNG')
            st.download_button(
                "📥 표지 다운로드 (PNG)",
                buf.getvalue(),
                file_name="book_cover.png",
                mime="image/png"
            )
    
    with col2:
        st.markdown("### 🖼️ 크몽 썸네일")
        
        thumb_title = st.text_input("썸네일 문구", value=st.session_state.get('book_title', ''), key="thumb_title", placeholder="짧고 임팩트 있게")
        thumb_style = st.selectbox("썸네일 스타일", ["modern", "professional", "bright"], format_func=lambda x: {"modern": "모던 (그라데이션)", "professional": "프로페셔널 (다크)", "bright": "밝은 톤"}.get(x, x))
        
        if st.button("🎨 썸네일 생성", key="gen_thumb"):
            if thumb_title:
                thumb_img = create_thumbnail(thumb_title, thumb_style)
                st.session_state['thumbnail_image'] = thumb_img
                st.success("썸네일 생성 완료!")
        
        if st.session_state.get('thumbnail_image'):
            st.image(st.session_state['thumbnail_image'], caption="크몽 썸네일 (800x600)", use_container_width=True)
            
            buf = BytesIO()
            st.session_state['thumbnail_image'].save(buf, format='PNG')
            st.download_button(
                "📥 썸네일 다운로드 (PNG)",
                buf.getvalue(),
                file_name="kmong_thumbnail.png",
                mime="image/png"
            )
    
    st.markdown("---")
    st.markdown("### 📄 상세페이지 헤더 이미지")
    
    col3, col4 = st.columns([1, 1])
    
    with col3:
        sales_headline = st.text_input("헤드라인", placeholder="월급만 믿다가는 평생 가난하다")
        sales_subheadline = st.text_input("서브헤드라인", placeholder="31개월 만에 10억 만든 비밀")
        sales_cta = st.text_input("CTA 버튼 문구", value="지금 바로 시작하기")
        
        if st.button("🎨 상세페이지 헤더 생성", key="gen_sales_img"):
            if sales_headline:
                sales_img = create_sales_page_image(sales_headline, sales_subheadline, sales_cta)
                st.session_state['sales_header_image'] = sales_img
                st.success("상세페이지 헤더 생성 완료!")
    
    with col4:
        if st.session_state.get('sales_header_image'):
            st.image(st.session_state['sales_header_image'], caption="상세페이지 헤더", use_container_width=True)
            
            buf = BytesIO()
            st.session_state['sales_header_image'].save(buf, format='PNG')
            st.download_button(
                "📥 헤더 이미지 다운로드",
                buf.getvalue(),
                file_name="sales_header.png",
                mime="image/png"
            )

# === TAB 6: 판매페이지 ===
with tabs[5]:
    st.markdown("## 📄 판매페이지 카피 생성")
    
    if not st.session_state['topic']:
        st.warning("먼저 '주제 선정' 탭에서 주제를 입력해주세요.")
    else:
        if st.button("✍️ 판매페이지 카피 생성", key="sales_copy_btn"):
            with st.spinner("전환율 높은 카피 작성 중..."):
                pricing = st.session_state.get('pricing_strategy', {})
                
                prompt = f"""'{st.session_state['topic']}' 전자책의 크몽 상세페이지 카피를 작성해주세요.

제목: {st.session_state.get('book_title', st.session_state['topic'])}
타겟: {st.session_state['target_persona']}
타겟 고민: {st.session_state['pain_points']}

[작성할 내용]

1. **크몽 상품 제목** (40자 이내, 검색 키워드 포함)

2. **후킹 헤드라인** 3개
   - 스크롤 멈추게 만드는 한 줄
   - 상식 파괴 or 충격적 숫자

3. **문제 제기** (타겟의 고통 자극)
   - "이런 경험 있으시죠?" 형식
   - 구체적 상황 묘사 3가지

4. **해결책 제시** (이 전자책이 답인 이유)
   - 핵심 가치 3가지
   - 각각 구체적 설명

5. **사회적 증거** (신뢰 구축)
   - 자격/경력 어필 포인트
   - 후기 유도 문구

6. **오퍼 정리**
   - 구성품 나열
   - 보너스 강조
   - 가격 앵커링

7. **CTA (구매 유도)**
   - 긴급성 문구 3개
   - 최종 CTA 문구

8. **FAQ** 3개
   - 예상 질문과 답변

전체를 마크다운 형식으로 작성해주세요."""
                
                result = ask_ai("크몽 탑셀러 마케터", prompt, 0.8)
                st.session_state['sales_page_copy'] = result
        
        if st.session_state.get('sales_page_copy'):
            st.markdown("### 📝 생성된 판매페이지 카피")
            st.markdown(st.session_state['sales_page_copy'])
            
            st.download_button(
                "📥 카피 다운로드 (TXT)",
                st.session_state['sales_page_copy'],
                file_name="sales_page_copy.txt",
                mime="text/plain"
            )

# === TAB 7: 리드마그넷 ===
with tabs[6]:
    st.markdown("## 🎁 리드마그넷 생성")
    st.markdown("무료 PDF로 잠재고객 이메일을 수집하세요")
    
    if not st.session_state['topic']:
        st.warning("먼저 '주제 선정' 탭에서 주제를 입력해주세요.")
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 리드마그넷 아이디어")
            
            lead_type = st.selectbox(
                "리드마그넷 유형",
                ["체크리스트", "미니 가이드", "템플릿", "케이스 스터디", "무료 챕터"]
            )
            
            if st.button("💡 리드마그넷 생성", key="lead_gen"):
                with st.spinner("리드마그넷 콘텐츠 생성 중..."):
                    prompt = f"""'{st.session_state['topic']}' 전자책의 리드마그넷을 만들어주세요.

유형: {lead_type}
타겟: {st.session_state['target_persona']}
메인 상품: {st.session_state.get('book_title', st.session_state['topic'])}

[리드마그넷 원칙]
- 5분 안에 소비 가능
- 즉각적인 가치 제공
- 메인 상품 구매 욕구 자극
- "이게 무료라고?" 느낌

다음을 생성해주세요:

1. **제목** (호기심 자극)
2. **부제목**
3. **목차** (5~7개 항목)
4. **각 항목별 핵심 내용** (2~3문장씩)
5. **마지막에 메인 상품 유도 문구**

마크다운 형식으로 작성해주세요."""
                    
                    result = ask_ai("콘텐츠 마케터", prompt, 0.8)
                    st.session_state['lead_magnet'] = result
        
        with col2:
            if st.session_state.get('lead_magnet'):
                st.markdown("### 📄 리드마그넷 콘텐츠")
                st.markdown(st.session_state['lead_magnet'])
                
                st.download_button(
                    "📥 리드마그넷 다운로드",
                    st.session_state['lead_magnet'],
                    file_name="lead_magnet.md",
                    mime="text/markdown"
                )
                
                st.markdown("---")
                st.markdown("### 🔗 배포 채널 추천")
                st.markdown("""
                1. **블로그** - 검색 유입용 포스팅
                2. **인스타그램** - 스토리/피드에 "DM 주시면 무료 제공"
                3. **네이버 카페** - 관련 커뮤니티에 공유
                4. **카카오톡 오픈채팅** - 관심사 기반 방
                5. **유튜브 커뮤니티** - 구독자 대상
                """)

# === TAB 8: 이메일 퍼널 ===
with tabs[7]:
    st.markdown("## 📧 이메일 시퀀스 설계")
    st.markdown("리드마그넷 다운로드 후 자동 발송될 이메일 시리즈")
    
    if not st.session_state['topic']:
        st.warning("먼저 '주제 선정' 탭에서 주제를 입력해주세요.")
    else:
        if st.button("📧 이메일 시퀀스 생성", key="email_gen"):
            with st.spinner("이메일 퍼널 설계 중..."):
                prompt = f"""'{st.session_state['topic']}' 전자책 판매를 위한 이메일 시퀀스를 만들어주세요.

메인 상품: {st.session_state.get('book_title', st.session_state['topic'])}
타겟: {st.session_state['target_persona']}
가격: {st.session_state.get('pricing_strategy', {}).get('pricing', {}).get('recommended', '미정')}

[이메일 시퀀스 구조 - 7일]

Day 0: 환영 + 리드마그넷 전달
Day 1: 가치 제공 (팁/인사이트)
Day 2: 스토리 (내 경험담)
Day 3: 문제 심화 (왜 해결해야 하는지)
Day 4: 해결책 힌트 (전자책 소개)
Day 5: 사회적 증거 (후기/결과)
Day 6: 긴급성 + 마감 임박
Day 7: 최종 마감

각 이메일마다:
- 제목 (오픈율 높이는)
- 본문 (300자 내외)
- CTA

마크다운 형식으로 작성해주세요."""
                
                result = ask_ai("이메일 마케팅 전문가", prompt, 0.8)
                st.session_state['email_sequence'] = result
        
        if st.session_state.get('email_sequence'):
            st.markdown("### 📬 7일 이메일 시퀀스")
            st.markdown(st.session_state['email_sequence'])
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "📥 이메일 시퀀스 다운로드",
                    st.session_state['email_sequence'],
                    file_name="email_sequence.md",
                    mime="text/markdown"
                )
            
            with col2:
                st.markdown("### 📮 추천 발송 툴")
                st.markdown("""
                - **스티비** (국내, 무료 플랜 있음)
                - **메일침프** (해외, 무료 플랜 있음)
                - **카카오톡 채널** (국내, 친구 기반)
                """)

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
        ("판매페이지 카피", bool(st.session_state.get('sales_page_copy'))),
        ("리드마그넷", bool(st.session_state.get('lead_magnet'))),
        ("이메일 퍼널", bool(st.session_state.get('email_sequence'))),
    ]
    
    cols = st.columns(4)
    for i, (name, done) in enumerate(checklist):
        with cols[i % 4]:
            status = "✅" if done else "⬜"
            st.markdown(f"{status} {name}")
    
    completed = sum(1 for _, done in checklist if done)
    st.progress(completed / len(checklist))
    st.caption(f"{completed}/{len(checklist)} 완료")
    
    st.markdown("---")
    st.markdown("### 📥 전체 다운로드")
    
    # 전체 데이터 JSON
    export_data = {
        "topic": st.session_state.get('topic', ''),
        "book_title": st.session_state.get('book_title', ''),
        "subtitle": st.session_state.get('subtitle', ''),
        "target_persona": st.session_state.get('target_persona', ''),
        "pain_points": st.session_state.get('pain_points', ''),
        "market_analysis": st.session_state.get('market_analysis', {}),
        "pricing_strategy": st.session_state.get('pricing_strategy', {}),
        "outline": st.session_state.get('outline', []),
        "sales_page_copy": st.session_state.get('sales_page_copy', ''),
        "lead_magnet": st.session_state.get('lead_magnet', ''),
        "email_sequence": st.session_state.get('email_sequence', ''),
        "exported_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            "📥 전체 데이터 (JSON)",
            json.dumps(export_data, ensure_ascii=False, indent=2),
            file_name=f"cashmaker_export_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # 마케팅 자료 통합
        marketing_bundle = f"""# {st.session_state.get('book_title', '전자책')} - 마케팅 자료

## 판매페이지 카피
{st.session_state.get('sales_page_copy', '아직 생성되지 않음')}

---

## 리드마그넷
{st.session_state.get('lead_magnet', '아직 생성되지 않음')}

---

## 이메일 시퀀스
{st.session_state.get('email_sequence', '아직 생성되지 않음')}
"""
        st.download_button(
            "📥 마케팅 자료 (MD)",
            marketing_bundle,
            file_name="marketing_bundle.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    with col3:
        if st.session_state.get('cover_image'):
            buf = BytesIO()
            st.session_state['cover_image'].save(buf, format='PNG')
            st.download_button(
                "📥 표지 이미지 (PNG)",
                buf.getvalue(),
                file_name="book_cover.png",
                mime="image/png",
                use_container_width=True
            )
        else:
            st.button("표지 없음", disabled=True, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 🚀 다음 단계")
    
    st.markdown("""
    <div class="info-card">
        <div class="info-card-title">크몽 등록 순서</div>
        <p>1. 크몽 판매자 등록 (사업자/개인)</p>
        <p>2. 전자책 PDF 완성</p>
        <p>3. 썸네일 업로드</p>
        <p>4. 상세페이지 카피 입력</p>
        <p>5. 가격 설정 & 옵션 구성</p>
        <p>6. 검수 신청 → 승인 후 판매 시작!</p>
    </div>
    """, unsafe_allow_html=True)

# --- 푸터 ---
st.markdown("""
<div style="text-align: center; padding: 40px 20px; margin-top: 60px; border-top: 1px solid #eee;">
    <span style="color: #888;">전자책 수익화 시스템 — </span>
    <span style="color: #222; font-weight: 600;">CASHMAKER v2.0</span>
</div>
""", unsafe_allow_html=True)
