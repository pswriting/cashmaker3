import streamlit as st
import google.generativeai as genai
import re
import json
import io
from datetime import datetime

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
    
    .template-card {
        background: #ffffff;
        border: 2px solid #eeeeee;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        text-align: center;
        transition: all 0.3s;
    }
    
    .template-card:hover {
        border-color: #667eea;
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.15);
    }
    
    .copy-box {
        background: #f8f8f8;
        border: 1px dashed #ccc;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        font-family: monospace;
    }
    
    .canva-btn {
        display: inline-block;
        background: linear-gradient(135deg, #00C4CC 0%, #7B2FF7 100%);
        color: white !important;
        padding: 15px 40px;
        border-radius: 30px;
        text-decoration: none;
        font-weight: 700;
        font-size: 16px;
        margin: 10px 5px;
    }
    
    .canva-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(123, 47, 247, 0.3);
    }
    
    .miri-btn {
        display: inline-block;
        background: linear-gradient(135deg, #FF6B35 0%, #FF3366 100%);
        color: white !important;
        padding: 15px 40px;
        border-radius: 30px;
        text-decoration: none;
        font-weight: 700;
        font-size: 16px;
        margin: 10px 5px;
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
    'lead_magnet': None, 'email_sequence': None, 'api_key': '',
    'design_copy': None
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
    "5️⃣ 디자인 가이드",
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

# === TAB 5: 디자인 가이드 (Canva 연동) ===
with tabs[4]:
    st.markdown("## 🎨 디자인 가이드")
    st.markdown("**전문 디자인 툴로 고퀄리티 디자인을 만드세요!**")
    
    # 디자인 텍스트 생성
    st.markdown("---")
    st.markdown("### 📝 Step 1. 디자인용 텍스트 생성")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 표지 & 썸네일용")
        
        design_title = st.text_input("제목", value=st.session_state.get('book_title', ''), key="design_title")
        design_subtitle = st.text_input("부제목", value=st.session_state.get('subtitle', ''), key="design_subtitle")
        design_author = st.text_input("저자명", value="", placeholder="표지에 들어갈 저자명")
        
        if st.button("✨ 카피 자동 생성", key="gen_design_copy"):
            with st.spinner("디자인용 카피 생성 중..."):
                prompt = f"""'{st.session_state['topic']}' 전자책 디자인에 들어갈 카피를 만들어주세요.

제목: {design_title}
타겟: {st.session_state['target_persona']}

다음을 생성해주세요:
1. 표지 메인 카피 (7자 이내, 임팩트 있게)
2. 표지 서브 카피 (15자 이내)
3. 썸네일 헤드라인 (10자 이내)
4. 상세페이지 메인 헤드라인 (충격적인 한 줄)
5. 상세페이지 서브 헤드라인
6. CTA 버튼 문구 3개
7. 신뢰 배지 문구 3개 (예: "1,000명 수강", "만족도 98%")

JSON 형식:
{{
    "cover_main": "메인 카피",
    "cover_sub": "서브 카피",
    "thumbnail_headline": "썸네일 헤드라인",
    "sales_headline": "상세페이지 헤드라인",
    "sales_subheadline": "서브 헤드라인",
    "cta_buttons": ["CTA1", "CTA2", "CTA3"],
    "trust_badges": ["배지1", "배지2", "배지3"]
}}"""
                result = ask_ai("마케팅 카피라이터", prompt, 0.8)
                try:
                    json_match = re.search(r'\{[\s\S]*\}', result)
                    if json_match:
                        st.session_state['design_copy'] = json.loads(json_match.group())
                except:
                    pass
    
    with col2:
        st.markdown("#### 생성된 카피")
        
        if st.session_state.get('design_copy'):
            dc = st.session_state['design_copy']
            
            st.markdown("**📕 표지용**")
            st.code(f"메인: {dc.get('cover_main', '')}\n서브: {dc.get('cover_sub', '')}")
            
            st.markdown("**🖼️ 썸네일용**")
            st.code(dc.get('thumbnail_headline', ''))
            
            st.markdown("**📄 상세페이지용**")
            st.code(f"헤드라인: {dc.get('sales_headline', '')}\n서브: {dc.get('sales_subheadline', '')}")
            
            st.markdown("**🔘 CTA 버튼**")
            for cta in dc.get('cta_buttons', []):
                st.code(cta)
            
            st.markdown("**✅ 신뢰 배지**")
            for badge in dc.get('trust_badges', []):
                st.code(badge)
    
    st.markdown("---")
    st.markdown("### 🎨 Step 2. 디자인 툴에서 제작")
    
    st.markdown("""
    <div style="text-align: center; padding: 30px;">
        <p style="font-size: 18px; margin-bottom: 20px;">아래 디자인 툴에서 전문가급 디자인을 만들어보세요!</p>
        <a href="https://www.canva.com/ko_kr/create/book-covers/" target="_blank" class="canva-btn">📕 Canva 표지 템플릿</a>
        <a href="https://www.canva.com/ko_kr/create/thumbnails/" target="_blank" class="canva-btn">🖼️ Canva 썸네일 템플릿</a>
        <a href="https://www.miricanvas.com/templates" target="_blank" class="miri-btn">🎨 미리캔버스 템플릿</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📌 디자인 가이드라인")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="template-card">
            <h4>📕 전자책 표지</h4>
            <p><strong>사이즈:</strong> 1600 x 2400px</p>
            <p><strong>비율:</strong> 2:3 (세로형)</p>
            <hr>
            <p><strong>필수 요소:</strong></p>
            <p>• 메인 타이틀 (크게)</p>
            <p>• 서브 타이틀</p>
            <p>• 저자명</p>
            <p>• 강렬한 배경색/이미지</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="template-card">
            <h4>🖼️ 크몽 썸네일</h4>
            <p><strong>사이즈:</strong> 800 x 600px</p>
            <p><strong>비율:</strong> 4:3 (가로형)</p>
            <hr>
            <p><strong>필수 요소:</strong></p>
            <p>• 한 줄 헤드라인</p>
            <p>• 핵심 키워드 강조</p>
            <p>• 가격/혜택 뱃지</p>
            <p>• 눈에 띄는 색상</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="template-card">
            <h4>📄 상세페이지</h4>
            <p><strong>사이즈:</strong> 860 x 자유</p>
            <p><strong>비율:</strong> 세로 스크롤</p>
            <hr>
            <p><strong>필수 요소:</strong></p>
            <p>• 후킹 헤드라인</p>
            <p>• 문제-해결 구조</p>
            <p>• 구성품 나열</p>
            <p>• CTA 버튼 반복</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 💡 베스트셀러 디자인 팁")
    
    st.markdown("""
    <div class="info-card">
        <h4>🎯 크몽 베스트셀러 표지 공통점</h4>
        <p>1. <strong>다크 배경 + 밝은 글씨</strong> - 가장 많이 쓰이는 조합</p>
        <p>2. <strong>그라데이션 배경</strong> - 보라/파랑 계열이 신뢰감 줌</p>
        <p>3. <strong>큰 숫자 강조</strong> - "월 500만원", "30일 만에" 등</p>
        <p>4. <strong>미니멀한 디자인</strong> - 요소를 3개 이하로 줄이기</p>
        <p>5. <strong>산세리프 폰트</strong> - 프리텐다드, 스포카한산스 추천</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
        <h4>🚫 피해야 할 디자인</h4>
        <p>❌ 너무 많은 정보 (글씨가 많으면 안 읽힘)</p>
        <p>❌ 흐릿한 색상 조합 (대비가 약하면 눈에 안 들어옴)</p>
        <p>❌ 무료 스톡 이미지 남용 (저렴해 보임)</p>
        <p>❌ 여러 폰트 혼용 (2개 이하 권장)</p>
    </div>
    """, unsafe_allow_html=True)

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
        ("디자인 카피", bool(st.session_state.get('design_copy'))),
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
        "design_copy": st.session_state.get('design_copy', {}),
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
    
    st.markdown("---")
    st.markdown("### 🚀 다음 단계")
    st.markdown("""
    1. **Canva/미리캔버스**에서 표지 & 썸네일 디자인
    2. **전자책 본문** PDF로 제작
    3. **크몽**에 상품 등록
    4. **리드마그넷** 무료 배포로 리스트 수집
    5. **이메일 시퀀스** 스티비/메일침프로 자동화
    """)

# --- 푸터 ---
st.markdown("""
<div style="text-align: center; padding: 40px; margin-top: 60px; border-top: 1px solid #eee;">
    <span style="color: #888;">전자책 수익화 시스템 — </span>
    <span style="font-weight: 600;">CASHMAKER v2.0</span>
</div>
""", unsafe_allow_html=True)
