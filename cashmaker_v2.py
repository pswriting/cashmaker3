import streamlit as st
import google.generativeai as genai
import re
import json
from datetime import datetime
from pathlib import Path

# ==========================================
# 설정
# ==========================================
def get_config_path():
    return Path.home() / ".ebook_app_config.json"

def load_saved_api_key():
    try:
        if get_config_path().exists():
            with open(get_config_path(), 'r') as f:
                return json.load(f).get('api_key', '')
    except:
        pass
    return ''

def save_api_key(api_key):
    try:
        with open(get_config_path(), 'w') as f:
            json.dump({'api_key': api_key}, f)
    except:
        pass

st.set_page_config(page_title="전자책 작성 프로그램", layout="wide", page_icon="◆")

# 고급스러운 디자인
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    * { font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif; }
    
    .stDeployButton, footer, #MainMenu {display:none;}
    
    .stApp { 
        background: linear-gradient(180deg, #fafafa 0%, #f5f5f5 100%); 
    }
    
    .main .block-container { 
        padding: 2rem 3rem; 
        max-width: 1400px; 
    }
    
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: none;
    }
    
    [data-testid="stSidebar"] * {
        color: #e8e8e8 !important;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: #fff !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.2) !important;
    }
    
    h1, h2, h3 {
        color: #1a1a2e !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    .stButton > button { 
        width: 100%; 
        border-radius: 12px; 
        font-weight: 600; 
        background: linear-gradient(135deg, #1a1a2e 0%, #2d2d44 100%) !important; 
        color: #fff !important; 
        border: none !important; 
        padding: 16px 32px;
        font-size: 15px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(26,26,46,0.3);
    }
    
    .stButton > button:hover { 
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(26,26,46,0.4);
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        padding: 12px 16px;
        font-size: 15px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #1a1a2e;
        box-shadow: 0 0 0 3px rgba(26,26,46,0.1);
    }
    
    .stSelectbox > div > div {
        border-radius: 12px;
    }
    
    .score-card { 
        background: linear-gradient(135deg, #1a1a2e 0%, #2d2d44 100%); 
        border-radius: 24px; 
        padding: 48px; 
        text-align: center; 
        color: white;
        box-shadow: 0 20px 40px rgba(26,26,46,0.3);
    }
    
    .score-number { 
        font-size: 80px; 
        font-weight: 800;
        background: linear-gradient(135deg, #fff 0%, #e0e0e0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .info-card { 
        background: #fff; 
        border-radius: 16px; 
        padding: 24px; 
        margin: 16px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
    }
    
    .info-card b {
        color: #1a1a2e;
        font-size: 16px;
    }
    
    .stat-box { 
        background: linear-gradient(135deg, #1a1a2e 0%, #2d2d44 100%); 
        border-radius: 16px; 
        padding: 20px; 
        margin: 10px 0; 
        color: white; 
        text-align: center;
        box-shadow: 0 4px 15px rgba(26,26,46,0.2);
    }
    
    .stat-value { 
        font-size: 28px; 
        font-weight: 800; 
        color: #4ade80; 
    }
    
    .stat-label { 
        font-size: 13px; 
        color: rgba(255,255,255,0.7);
        margin-top: 4px;
    }
    
    .verdict-go { 
        background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%); 
        color: #000; 
        padding: 12px 32px; 
        border-radius: 30px; 
        font-weight: 700; 
        display: inline-block;
        box-shadow: 0 4px 15px rgba(74,222,128,0.4);
    }
    
    .verdict-wait { 
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); 
        color: #000; 
        padding: 12px 32px; 
        border-radius: 30px; 
        font-weight: 700; 
        display: inline-block;
    }
    
    .verdict-no { 
        background: linear-gradient(135deg, #f87171 0%, #ef4444 100%); 
        color: #fff; 
        padding: 12px 32px; 
        border-radius: 30px; 
        font-weight: 700; 
        display: inline-block;
    }
    
    .summary-hub { 
        background: linear-gradient(135deg, #1a1a2e 0%, #2d2d44 100%); 
        border-radius: 20px; 
        padding: 24px; 
        color: white; 
        margin: 16px 0;
        box-shadow: 0 8px 30px rgba(26,26,46,0.3);
    }
    
    .data-card { 
        background: #fff; 
        border-left: 4px solid #1a1a2e; 
        border-radius: 12px; 
        padding: 20px; 
        margin: 12px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .next-section { 
        margin-top: 48px; 
        padding-top: 24px; 
        border-top: 2px solid #e8e8e8; 
    }
    
    .full-content-box { 
        background: #fff; 
        border: 1px solid #e8e8e8; 
        border-radius: 16px; 
        padding: 32px; 
        margin: 16px 0; 
        white-space: pre-wrap; 
        line-height: 1.9;
        font-size: 15px;
        color: #333;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }
    
    .nav-active {
        background: linear-gradient(135deg, #1a1a2e 0%, #2d2d44 100%);
        color: #fff;
        padding: 10px 16px;
        border-radius: 10px;
        text-align: center;
        font-size: 12px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(26,26,46,0.3);
    }
    
    .stExpander {
        background: #fff;
        border-radius: 12px;
        border: 1px solid #e8e8e8;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #1a1a2e 0%, #2d2d44 100%);
    }
    
    .title-card {
        background: #fff;
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
        border: 2px solid #f0f0f0;
        transition: all 0.3s ease;
    }
    
    .title-card:hover {
        border-color: #1a1a2e;
        box-shadow: 0 8px 25px rgba(26,26,46,0.15);
    }
    
    .title-main {
        font-size: 20px;
        font-weight: 700;
        color: #1a1a2e;
        line-height: 1.4;
    }
    
    .title-sub {
        font-size: 14px;
        color: #666;
        margin-top: 8px;
    }
    
    .knowledge-item {
        background: #fff;
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        border: 1px solid #e8e8e8;
    }
</style>
""", unsafe_allow_html=True)

# 인증
CORRECT_PASSWORD = "cashmaker2024"
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown("""
    <div style="max-width:420px;margin:100px auto;padding:48px;background:#fff;border-radius:24px;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.1);">
        <div style="font-size:32px;font-weight:800;color:#1a1a2e;">CASHMAKER</div>
        <div style="font-size:14px;color:#888;margin-top:8px;letter-spacing:2px;">전자책 작성 프로그램</div>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        pw = st.text_input("비밀번호", type="password", key="pw_login")
        if st.button("입장", key="btn_login"):
            if pw == CORRECT_PASSWORD:
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("비밀번호 오류")
    st.stop()

# 세션 초기화
defaults = {
    'topic': '', 'target_persona': '', 'pain_points': '',
    'outline': [], 'chapters': {}, 'book_title': '', 'subtitle': '',
    'score_details': None, 'generated_titles': None, 'suggested_targets': None,
    'analyzed_pains': None, 'review_analysis': None, 'market_gaps': None,
    'knowledge_hub': [], 'study_summary': None, 'current_page': 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# 사이드바
with st.sidebar:
    st.markdown("### ⚡ 진행 상황")
    progress = sum([bool(st.session_state['topic']), bool(st.session_state['target_persona']), bool(st.session_state['outline']), len(st.session_state['chapters']) > 0]) / 4
    st.progress(progress)
    
    st.markdown("---")
    st.markdown("### 🔑 API 설정")
    if 'api_key' not in st.session_state:
        st.session_state['api_key'] = load_saved_api_key()
    
    api_key = st.text_input("Gemini API 키", value=st.session_state['api_key'], type="password", key="api_sidebar")
    if api_key != st.session_state['api_key']:
        st.session_state['api_key'] = api_key
        save_api_key(api_key)
    
    st.markdown("---")
    st.markdown("### 🚀 빠른 이동")
    pages = ["① 시장분석", "② 타겟", "③ 경쟁분석", "④ 학습", "⑤ 목차", "⑥ 본문", "⑦ 출력"]
    for i, p in enumerate(pages):
        if st.button(p, key=f"sidebar_nav_{i}", use_container_width=True):
            st.session_state['current_page'] = i
            st.rerun()

# ==========================================
# 헬퍼 함수
# ==========================================
def get_api_key():
    return st.session_state.get('api_key', '')

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*([^*]+)\*\*', r'「\1」', text)
    text = text.replace('**', '').replace('*', '').replace('###', '').replace('##', '').replace('#', '')
    return text.strip()

def clean_content(text):
    if not text:
        return ""
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    text = text.replace('###', '').replace('##', '').replace('#', '').replace('**', '').replace('*', '')
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def parse_json(response):
    if not response:
        return None
    try:
        match = re.search(r'\{[\s\S]*\}', response)
        if match:
            return json.loads(match.group())
    except:
        pass
    return None

def ask_ai(prompt, temp=0.7):
    api_key = get_api_key()
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        config = genai.types.GenerationConfig(temperature=temp, max_output_tokens=8000)
        response = model.generate_content(prompt, generation_config=config)
        return response.text
    except Exception as e:
        st.error(f"AI 오류: {e}")
        return None

def get_youtube_transcript(url):
    """유튜브 자막 가져오기"""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        # URL에서 video_id 추출
        video_id = None
        if 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[-1].split('?')[0]
        elif 'v=' in url:
            video_id = url.split('v=')[-1].split('&')[0]
        
        if not video_id:
            return None
        
        # 자막 가져오기 (한국어 우선, 없으면 영어)
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
        except:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_transcript(['ko', 'en']).fetch()
        
        # 텍스트로 변환
        full_text = ' '.join([t['text'] for t in transcript])
        return full_text[:15000]  # 15000자 제한
        
    except Exception as e:
        return None

def get_full_content():
    full = ""
    for ch in st.session_state.get('outline', []):
        if ch in st.session_state.get('chapters', {}):
            ch_data = st.session_state['chapters'][ch]
            ch_content = ""
            for s in ch_data.get('subtopics', []):
                c = ch_data.get('subtopic_data', {}).get(s, {}).get('content', '')
                if c:
                    ch_content += f"\n\n【{s}】\n\n{clean_content(c)}"
            if ch_content:
                full += f"\n\n{'='*50}\n{ch}\n{'='*50}{ch_content}"
    return full.strip()

def go_next():
    if st.session_state['current_page'] < 6:
        st.session_state['current_page'] += 1

def go_prev():
    if st.session_state['current_page'] > 0:
        st.session_state['current_page'] -= 1


# ==========================================
# AI 함수들
# ==========================================
def analyze_market_deep(topic):
    prompt = f"""주제: {topic}

이 주제로 전자책 시장을 분석해주세요.

[중요] 모든 답변은 반드시 한국어로만 작성하세요.

JSON:
{{
    "verdict": "강력 추천/추천/보류/비추천 중 하나",
    "verdict_reason": "판정 이유 한국어로",
    "total_score": 85,
    "search_data": {{
        "naver_monthly": "네이버 월간 검색량 예시: 12,000회",
        "google_monthly": "구글 월간 검색량 예시: 8,500회",
        "naver_blog_posts": "블로그 게시물 수",
        "youtube_videos": "유튜브 영상 수",
        "search_trend": "상승 또는 유지 또는 하락"
    }},
    "market_size": {{
        "score": 85,
        "level": "매우 큼/큼/보통/작음 중 하나",
        "analysis": "분석 2문장 한국어로"
    }},
    "competition": {{
        "score": 70,
        "level": "치열함/보통/낮음 중 하나",
        "your_opportunity": "차별화 기회 한국어로"
    }},
    "profit": {{
        "score": 80,
        "price_range": "권장 가격대",
        "monthly_revenue": "예상 월 수익"
    }},
    "recommendation": "최종 권장 2문장 한국어로"
}}"""
    return ask_ai(prompt, 0.5)


def suggest_targets(topic):
    prompt = f"""주제: {topic}

구매 가능성 높은 타겟 5개를 추천해주세요.

[중요] 모든 답변은 반드시 한국어로만 작성하세요.

JSON:
{{
    "personas": [
        {{
            "name": "타겟 이름 한국어로",
            "demographics": "연령, 직업, 소득",
            "needs": "핵심 니즈",
            "buying_power": "상/중/하",
            "market_size": "추정 인원",
            "pain_points": ["고민1", "고민2", "고민3"]
        }}
    ]
}}"""
    return ask_ai(prompt, 0.7)


def analyze_pains_deep(topic, persona):
    prompt = f"""주제: {topic}
타겟: {persona}

이 타겟의 고민을 아주 깊이 분석해주세요.

[중요] 모든 답변은 반드시 한국어로만 작성하세요. 외국어 사용 금지.

JSON:
{{
    "surface_pains": {{
        "pains": ["표면적 고민1", "고민2", "고민3", "고민4", "고민5"],
        "description": "표면적 고민 설명 3문장"
    }},
    "hidden_pains": {{
        "pains": ["숨겨진 진짜 고민1", "고민2", "고민3", "고민4"],
        "description": "숨겨진 고민 설명 3문장"
    }},
    "emotional_pains": {{
        "pains": ["감정적 고통1", "고통2", "고통3"],
        "description": "감정적 고통 설명 2문장"
    }},
    "failed_attempts": {{
        "attempts": ["시도했지만 실패한 것1", "것2", "것3"],
        "why_failed": "실패 이유 2문장"
    }},
    "dream_outcome": {{
        "ideal_result": "이상적인 결과",
        "timeline": "원하는 기간",
        "what_changes": "달라지는 것 2문장"
    }},
    "buying_triggers": {{
        "triggers": ["구매 요인1", "요인2", "요인3"],
        "objections": ["망설임 이유1", "이유2"]
    }},
    "marketing_hook": "마케팅 훅 한 문장"
}}"""
    return ask_ai(prompt, 0.6)


def analyze_competitor_reviews(topic):
    prompt = f"""주제: {topic}

이 주제 관련 전자책/도서의 부정적 리뷰를 분석해주세요.

[매우 중요] 
- 모든 답변은 반드시 한국어로만 작성하세요.
- 영어, 러시아어 등 외국어 절대 사용 금지
- 한글과 숫자만 사용하세요.

JSON:
{{
    "analysis_scope": {{
        "books_analyzed": "287권",
        "reviews_analyzed": "3,842개",
        "negative_reviews": "892개 (23%)",
        "platforms": ["크몽", "예스24", "알라딘", "교보문고"]
    }},
    "negative_patterns": [
        {{
            "pattern": "불만 패턴 한국어로",
            "frequency": "67%",
            "example_reviews": ["실제 리뷰 예시 한국어로", "리뷰2"],
            "reader_emotion": "독자 감정 한국어로",
            "hidden_need": "숨겨진 니즈 한국어로",
            "solution": "해결책 한국어로"
        }},
        {{
            "pattern": "두 번째 불만",
            "frequency": "54%",
            "example_reviews": ["리뷰1", "리뷰2"],
            "reader_emotion": "감정",
            "hidden_need": "니즈",
            "solution": "해결책"
        }},
        {{
            "pattern": "세 번째 불만",
            "frequency": "41%",
            "example_reviews": ["리뷰1", "리뷰2"],
            "reader_emotion": "감정",
            "hidden_need": "니즈",
            "solution": "해결책"
        }}
    ],
    "hidden_needs_summary": {{
        "needs": ["숨겨진 니즈1", "니즈2", "니즈3"],
        "insight": "핵심 인사이트 2문장"
    }},
    "concept_suggestions": [
        {{
            "concept": "차별화 컨셉1 한국어로",
            "why_works": "이유 한국어로",
            "unique_point": "차별점 한국어로"
        }},
        {{
            "concept": "컨셉2",
            "why_works": "이유",
            "unique_point": "차별점"
        }}
    ],
    "success_formula": {{
        "must_have": ["필수1", "필수2", "필수3"],
        "must_avoid": ["금지1", "금지2"],
        "differentiation": "차별화 전략 한국어로 2문장"
    }}
}}"""
    return ask_ai(prompt, 0.6)


def generate_titles_bestseller(topic, persona, pains):
    prompt = f"""주제: {topic}
타겟: {persona}
고민: {pains}

[베스트셀러 제목 분석]
다음 베스트셀러 전자책 제목들의 패턴을 분석하고 적용해주세요:

1. "퇴사 후 월 천만원 벌게 해준 단 하나의 습관"
2. "월급 250으로 3년 만에 1억 모은 직장인의 비밀 가계부"
3. "나는 왜 회사만 가면 우울해지는가"
4. "하루 30분, 6개월 만에 영어 프리토킹 된 공부법"
5. "서울 아파트 없이 30대에 파이어족 된 부부 이야기"
6. "투잡으로 본업보다 3배 버는 직장인들의 시간표"

[베스트셀러 제목 패턴]
- 구체적 숫자 + 결과 (월 천만원, 3년 만에 1억, 6개월)
- 반전 요소 (월급 250으로, 회사 다니면서, 서울 아파트 없이)
- 감정 자극 (우울해지는가, 비밀, 파이어족)
- 독자 특정 (직장인, 30대, 부부)

위 패턴을 분석해서 이 주제에 맞는 베스트셀러급 제목 5개를 만들어주세요.

JSON:
{{
    "titles": [
        {{
            "title": "베스트셀러 스타일 제목 (구체적 숫자 + 결과 포함)",
            "subtitle": "부제목",
            "pattern_used": "사용한 패턴 설명",
            "why_works": "왜 팔리는지 이유"
        }},
        {{
            "title": "두 번째 제목",
            "subtitle": "부제목",
            "pattern_used": "패턴",
            "why_works": "이유"
        }},
        {{
            "title": "세 번째 제목",
            "subtitle": "부제목",
            "pattern_used": "패턴",
            "why_works": "이유"
        }},
        {{
            "title": "네 번째 제목",
            "subtitle": "부제목",
            "pattern_used": "패턴",
            "why_works": "이유"
        }},
        {{
            "title": "다섯 번째 제목",
            "subtitle": "부제목",
            "pattern_used": "패턴",
            "why_works": "이유"
        }}
    ]
}}"""
    return ask_ai(prompt, 0.9)


def analyze_youtube_content(transcript, url):
    """유튜브 자막 내용 분석"""
    prompt = f"""다음은 유튜브 영상의 자막 내용입니다. 이 내용을 분석해주세요.

URL: {url}
자막 내용:
{transcript[:10000]}

[중요] 반드시 위 자막 내용을 기반으로 분석하세요.

JSON:
{{
    "title": "영상의 핵심 주제",
    "creator": "크리에이터 (알 수 있다면)",
    "main_topic": "메인 주제 한 줄 요약",
    "key_points": [
        "핵심 포인트 1 - 자막에서 실제로 언급된 내용",
        "핵심 포인트 2",
        "핵심 포인트 3",
        "핵심 포인트 4",
        "핵심 포인트 5"
    ],
    "actionable_tips": [
        "실행할 수 있는 팁 1",
        "팁 2",
        "팁 3"
    ],
    "quotes": [
        "인상적인 문장 1",
        "문장 2"
    ],
    "ebook_applications": [
        "전자책 활용 포인트 1",
        "포인트 2"
    ],
    "summary": "영상 전체 요약 5문장"
}}"""
    return ask_ai(prompt, 0.3)


def analyze_text_content(text, source=""):
    prompt = f"""출처: {source}
내용: {text[:5000]}

분석:

JSON:
{{
    "title": "주제",
    "key_points": ["핵심1", "핵심2", "핵심3", "핵심4", "핵심5"],
    "insights": ["인사이트1", "인사이트2", "인사이트3"],
    "action_items": ["실행1", "실행2", "실행3"],
    "ebook_ideas": ["아이디어1", "아이디어2"],
    "summary": "요약 3문장"
}}"""
    return ask_ai(prompt, 0.5)


def summarize_all_knowledge(items, topic):
    """전체 학습 내용 통합 요약"""
    all_points = []
    all_tips = []
    all_ideas = []
    
    for item in items:
        if isinstance(item, dict):
            all_points.extend(item.get('key_points', []))
            all_tips.extend(item.get('actionable_tips', item.get('action_items', [])))
            all_ideas.extend(item.get('ebook_applications', item.get('ebook_ideas', [])))
    
    prompt = f"""전자책 주제: {topic}

학습한 모든 정보를 통합 분석해주세요.

수집된 핵심 포인트들:
{chr(10).join([f"• {p}" for p in all_points[:25]])}

실행 팁들:
{chr(10).join([f"• {t}" for t in all_tips[:15]])}

전자책 활용 아이디어:
{chr(10).join([f"• {i}" for i in all_ideas[:10]])}

JSON:
{{
    "integrated_summary": "전체 학습 내용 통합 요약 5문장",
    "core_insights": [
        "핵심 인사이트 1",
        "인사이트 2",
        "인사이트 3",
        "인사이트 4",
        "인사이트 5"
    ],
    "action_plan": [
        "즉시 실행할 것 1",
        "실행 2",
        "실행 3"
    ],
    "ebook_structure": [
        "추천 목차 1장",
        "2장",
        "3장",
        "4장"
    ],
    "unique_angle": "이 전자책만의 차별화된 관점",
    "study_plan": {{
        "week1": "1주차: 무엇을 할지",
        "week2": "2주차: 무엇을 할지",
        "week3": "3주차: 무엇을 할지",
        "week4": "4주차: 무엇을 할지"
    }},
    "expert_tips": [
        "전문가 팁 1",
        "팁 2",
        "팁 3"
    ]
}}"""
    return ask_ai(prompt, 0.6)


def generate_outline(topic, persona, pains, gaps=None):
    gaps_text = ""
    if gaps:
        gaps_text = f"\n차별화 포인트: " + ", ".join(gaps[:3])
    
    prompt = f"""주제: {topic}
타겟: {persona}
고민: {pains}
{gaps_text}

전자책 목차를 만들어주세요.

[좋은 목차 예시]
- "월급 250만원으로 3년 만에 1억 모은 통장 쪼개기"
- "퇴사하고 6개월, 오히려 월급의 3배를 벌게 된 이유"  
- "나는 왜 10년간 투자하고도 월 50만원밖에 못 벌었나"
- "주식으로 2000만원 날린 후 깨달은 것들"

[금지 표현]
- "~의 중요성", "~하는 방법", "~의 기초"
- "마법", "비밀", "필승", "완벽한"
- "99%가 모르는", "숨겨진 진실"

반드시 아래 형식으로 출력해주세요:

PART 1. [파트1 제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]

PART 2. [파트2 제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]

PART 3. [파트3 제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]

PART 4. [파트4 제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]"""
    return ask_ai(prompt, 0.9)


def generate_content_premium(subtopic, chapter, questions, answers, topic, persona):
    qa = "\n".join([f"내용{i+1}: {a}" for i, (q, a) in enumerate(zip(questions, answers)) if a.strip()])
    
    prompt = f"""주제: {topic}
챕터: {chapter}
소제목: {subtopic}
타겟: {persona}

참고 내용: {qa}

[글쓰기 스타일]
1. 첫 문장에서 확 잡기
2. 짧은 문장으로 리듬감
3. 독자와 대화하듯
4. 구체적 숫자와 사례
5. 감정 건드리기

[금지]
- 마크다운 기호 금지
- 딱딱한 표현 금지

분량: 1800~2200자

'{subtopic}' 본문을 작성해주세요."""
    result = ask_ai(prompt, 0.85)
    return clean_content(result)


def generate_questions(subtopic, chapter, topic):
    prompt = f"""'{topic}' 전자책 '{chapter}' 챕터의 '{subtopic}' 작성용 질문 3개:

Q1: [질문]
Q2: [질문]
Q3: [질문]"""
    return ask_ai(prompt, 0.7)


# ==========================================
# 메인 UI
# ==========================================
st.markdown("""
<div style="text-align:center;padding:24px;">
    <div style="font-size:12px;color:#888;letter-spacing:4px;font-weight:500;">CASHMAKER</div>
    <div style="font-size:36px;font-weight:800;color:#1a1a2e;margin-top:4px;">전자책 작성 프로그램</div>
</div>
""", unsafe_allow_html=True)

# 페이지 네비게이션
pages = ["① 시장분석", "② 타겟", "③ 경쟁분석", "④ 학습", "⑤ 목차", "⑥ 본문", "⑦ 출력"]
current = st.session_state['current_page']

cols = st.columns(7)
for i, (col, page) in enumerate(zip(cols, pages)):
    with col:
        if i == current:
            st.markdown(f'<div class="nav-active">{page}</div>', unsafe_allow_html=True)
        else:
            if st.button(page, key=f"nav_{i}", use_container_width=True):
                st.session_state['current_page'] = i
                st.rerun()

st.markdown("---")


# ==========================================
# PAGE 0: 주제 & 시장분석
# ==========================================
if current == 0:
    st.markdown("## 📊 주제 선정 & 시장 분석")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 주제 입력")
        topic = st.text_input("어떤 주제로 전자책을 쓸까요?", value=st.session_state['topic'], placeholder="예: 주식 배당으로 월 100만원", key="p0_topic")
        if topic != st.session_state['topic']:
            st.session_state['topic'] = topic
            st.session_state['score_details'] = None
        
        st.markdown("""
        <div class="info-card">
            <b>💡 좋은 주제의 조건</b><br><br>
            • 내가 직접 경험하고 성과를 낸 것<br>
            • 사람들이 돈 주고 배우고 싶어하는 것<br>
            • 구체적인 결과를 약속할 수 있는 것
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 시장 분석하기", use_container_width=True, key="p0_analyze"):
            if not topic:
                st.error("주제를 입력해주세요")
            elif not get_api_key():
                st.error("API 키를 입력해주세요")
            else:
                with st.spinner("시장 분석 중..."):
                    result = analyze_market_deep(topic)
                    parsed = parse_json(result)
                    if parsed:
                        st.session_state['score_details'] = parsed
                        st.rerun()
    
    with col2:
        st.markdown("### 분석 결과")
        
        if st.session_state.get('score_details'):
            d = st.session_state['score_details']
            score = d.get('total_score', 0)
            verdict = d.get('verdict', '')
            v_class = "verdict-go" if "추천" in verdict else ("verdict-wait" if "보류" in verdict else "verdict-no")
            
            st.markdown(f"""
            <div class="score-card">
                <div class="score-number">{score}</div>
                <div style="font-size:14px;opacity:0.8;margin-top:8px;">종합 점수</div>
                <div style="margin-top:24px;"><span class="{v_class}">{verdict}</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"<br>**📢 {d.get('verdict_reason', '')}**", unsafe_allow_html=True)
            
            sd = d.get('search_data', {})
            if sd:
                st.markdown(f"""
                <div class="data-card">
                    <b>📊 검색 데이터</b><br><br>
                    • 네이버 검색량: <b>{sd.get('naver_monthly', 'N/A')}</b><br>
                    • 구글 검색량: <b>{sd.get('google_monthly', 'N/A')}</b><br>
                    • 블로그 게시물: <b>{sd.get('naver_blog_posts', 'N/A')}</b><br>
                    • 유튜브 영상: <b>{sd.get('youtube_videos', 'N/A')}</b>
                </div>
                """, unsafe_allow_html=True)
            
            ms = d.get('market_size', {})
            st.markdown(f'<div class="stat-box"><div class="stat-value">{ms.get("level", "")} ({ms.get("score", 0)}점)</div><div class="stat-label">시장 규모</div></div>', unsafe_allow_html=True)
            
            comp = d.get('competition', {})
            if comp.get('your_opportunity'):
                st.success(f"💡 **차별화 기회:** {comp.get('your_opportunity', '')}")
        else:
            st.markdown('<div style="text-align:center;padding:80px;background:#fff;border-radius:20px;box-shadow:0 4px 20px rgba(0,0,0,0.05);"><p style="color:#888;font-size:15px;">주제를 입력하고 분석해주세요</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="next-section"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("다음 → 타겟 설정", key="p0_next", use_container_width=True):
            go_next()
            st.rerun()


# ==========================================
# PAGE 1: 타겟 & 컨셉
# ==========================================
elif current == 1:
    st.markdown("## 🎯 타겟 설정 & 제목 생성")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 타겟 선정")
        
        if st.button("🎯 AI 타겟 추천", key="p1_target"):
            if st.session_state['topic'] and get_api_key():
                with st.spinner("분석 중..."):
                    result = suggest_targets(st.session_state['topic'])
                    parsed = parse_json(result)
                    if parsed:
                        st.session_state['suggested_targets'] = parsed
                        st.rerun()
        
        if st.session_state.get('suggested_targets'):
            for i, p in enumerate(st.session_state['suggested_targets'].get('personas', [])):
                with st.expander(f"🎯 {p.get('name', '')} ({p.get('buying_power', '')})", expanded=False):
                    st.write(f"**인구:** {p.get('demographics', '')}")
                    st.write(f"**니즈:** {p.get('needs', '')}")
                    if st.button("선택", key=f"p1_sel_{i}"):
                        st.session_state['target_persona'] = f"{p.get('name', '')} - {p.get('demographics', '')}"
                        st.session_state['pain_points'] = ", ".join(p.get('pain_points', [])[:5])
                        st.rerun()
        
        st.markdown("---")
        persona = st.text_area("타겟 직접 입력:", value=st.session_state['target_persona'], height=60, key="p1_persona")
        st.session_state['target_persona'] = persona
        
        if persona and st.button("🔍 고민 심층 분석", key="p1_analyze"):
            with st.spinner("심층 분석 중..."):
                r = analyze_pains_deep(st.session_state['topic'], persona)
                parsed = parse_json(r)
                if parsed:
                    st.session_state['analyzed_pains'] = parsed
                    surface = parsed.get('surface_pains', {}).get('pains', [])
                    hidden = parsed.get('hidden_pains', {}).get('pains', [])
                    st.session_state['pain_points'] = ", ".join((surface + hidden)[:6])
                    st.rerun()
        
        if st.session_state.get('analyzed_pains'):
            p = st.session_state['analyzed_pains']
            with st.expander("📊 표면적 고민", expanded=True):
                for pain in p.get('surface_pains', {}).get('pains', []):
                    st.write(f"• {pain}")
            with st.expander("🔍 숨겨진 진짜 고민", expanded=True):
                for pain in p.get('hidden_pains', {}).get('pains', []):
                    st.write(f"• {pain}")
            if p.get('marketing_hook'):
                st.info(f"🎯 **마케팅 훅:** {p.get('marketing_hook', '')}")
    
    with col2:
        st.markdown("### 베스트셀러급 제목 생성")
        
        pain_points = st.text_area("독자의 고민:", value=st.session_state['pain_points'], height=60, key="p1_pains")
        st.session_state['pain_points'] = pain_points
        
        if st.button("✨ 베스트셀러 제목 생성", key="p1_title"):
            if st.session_state['topic']:
                with st.spinner("베스트셀러 패턴 분석 중..."):
                    r = generate_titles_bestseller(st.session_state['topic'], st.session_state['target_persona'], st.session_state['pain_points'])
                    parsed = parse_json(r)
                    if parsed:
                        st.session_state['generated_titles'] = parsed
                        st.rerun()
        
        if st.session_state.get('generated_titles'):
            for t in st.session_state['generated_titles'].get('titles', [])[:5]:
                st.markdown(f"""
                <div class="title-card">
                    <div class="title-main">{t.get('title', '')}</div>
                    <div class="title-sub">{t.get('subtitle', '')}</div>
                    <div style="font-size:12px;color:#888;margin-top:12px;">📌 {t.get('pattern_used', '')}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.session_state['book_title'] = st.text_input("최종 제목", value=st.session_state['book_title'], key="p1_book_title")
        st.session_state['subtitle'] = st.text_input("부제", value=st.session_state['subtitle'], key="p1_subtitle")
    
    st.markdown('<div class="next-section"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("← 이전", key="p1_prev", use_container_width=True):
            go_prev()
            st.rerun()
    with c3:
        if st.button("다음 → 경쟁분석", key="p1_next", use_container_width=True):
            go_next()
            st.rerun()


# ==========================================
# PAGE 2: 경쟁도서 분석
# ==========================================
elif current == 2:
    st.markdown("## 📚 경쟁 도서 분석")
    st.markdown("기존 도서의 부정 리뷰를 분석해서 숨은 니즈를 찾습니다")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 부정 리뷰 분석")
        
        if st.button("🔍 경쟁 도서 분석하기", use_container_width=True, key="p2_analyze"):
            if not st.session_state['topic']:
                st.error("주제를 먼저 입력해주세요")
            elif not get_api_key():
                st.error("API 키를 입력해주세요")
            else:
                with st.spinner("경쟁 도서 분석 중..."):
                    result = analyze_competitor_reviews(st.session_state['topic'])
                    parsed = parse_json(result)
                    if parsed:
                        st.session_state['review_analysis'] = parsed
                        concepts = parsed.get('concept_suggestions', [])
                        st.session_state['market_gaps'] = [c.get('concept', '') for c in concepts]
                        st.rerun()
        
        if st.session_state.get('review_analysis'):
            a = st.session_state['review_analysis']
            scope = a.get('analysis_scope', {})
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.markdown(f'<div class="stat-box"><div class="stat-value">{scope.get("books_analyzed", "N/A")}</div><div class="stat-label">분석 도서</div></div>', unsafe_allow_html=True)
            with col_s2:
                st.markdown(f'<div class="stat-box"><div class="stat-value">{scope.get("negative_reviews", "N/A")}</div><div class="stat-label">부정 리뷰</div></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 분석 결과")
        
        if st.session_state.get('review_analysis'):
            a = st.session_state['review_analysis']
            
            patterns = a.get('negative_patterns', [])
            if patterns:
                st.markdown("#### 😤 독자 불만 패턴")
                for i, p in enumerate(patterns[:3], 1):
                    with st.expander(f"**{i}. {p.get('pattern', '')}** ({p.get('frequency', '')})", expanded=i==1):
                        for rev in p.get('example_reviews', []):
                            st.caption(f'"{rev}"')
                        st.info(f"🔍 **숨겨진 니즈:** {p.get('hidden_need', '')}")
                        st.success(f"💡 **해결책:** {p.get('solution', '')}")
            
            concepts = a.get('concept_suggestions', [])
            if concepts:
                st.markdown("#### 🎯 차별화 컨셉")
                for c in concepts[:2]:
                    st.markdown(f"""
                    <div class="info-card">
                        <b>「{c.get('concept', '')}」</b><br>
                        <span style="color:#666;">{c.get('why_works', '')}</span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center;padding:60px;background:#fff;border-radius:16px;"><p style="color:#888;">분석 버튼을 눌러주세요</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="next-section"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("← 이전", key="p2_prev", use_container_width=True):
            go_prev()
            st.rerun()
    with c3:
        if st.button("다음 → 학습", key="p2_next", use_container_width=True):
            go_next()
            st.rerun()


# ==========================================
# PAGE 3: 실력 키우기 (학습)
# ==========================================
elif current == 3:
    st.markdown("## 📚 실력 키우기")
    st.markdown("유튜브 영상이나 텍스트를 분석하고 학습 정보를 통합합니다")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 콘텐츠 추가")
        
        # youtube-transcript-api 설치 안내
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            yt_available = True
        except ImportError:
            yt_available = False
            st.warning("유튜브 자막 분석을 위해 터미널에서 `pip install youtube-transcript-api` 를 실행해주세요")
        
        input_type = st.radio("입력 유형", ["유튜브 URL", "텍스트"], horizontal=True, key="p3_type")
        
        if input_type == "유튜브 URL":
            youtube_url = st.text_input("유튜브 URL", placeholder="https://youtube.com/watch?v=...", key="p3_url")
            st.caption("💡 영상의 자막을 가져와서 분석합니다")
            
            if st.button("🎬 영상 분석 & 추가", use_container_width=True, key="p3_yt"):
                if not yt_available:
                    st.error("youtube-transcript-api가 설치되지 않았습니다")
                elif youtube_url and ('youtube.com' in youtube_url or 'youtu.be' in youtube_url):
                    with st.spinner("유튜브 자막 가져오는 중..."):
                        transcript = get_youtube_transcript(youtube_url)
                        if transcript:
                            st.success("✅ 자막 가져오기 성공!")
                            with st.spinner("내용 분석 중..."):
                                result = analyze_youtube_content(transcript, youtube_url)
                                parsed = parse_json(result)
                                if parsed:
                                    parsed['source'] = youtube_url
                                    parsed['type'] = 'youtube'
                                    parsed['added_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                                    st.session_state['knowledge_hub'].append(parsed)
                                    st.success("✅ 분석 완료!")
                                    st.rerun()
                        else:
                            st.error("자막을 가져올 수 없습니다. 자막이 없는 영상일 수 있습니다.")
                else:
                    st.error("올바른 유튜브 URL을 입력하세요")
        else:
            source_name = st.text_input("출처/제목", key="p3_source")
            content_text = st.text_area("콘텐츠 내용", height=150, key="p3_content")
            
            if st.button("📝 분석 & 추가", use_container_width=True, key="p3_text"):
                if content_text and len(content_text) > 50:
                    with st.spinner("분석 중..."):
                        result = analyze_text_content(content_text, source_name)
                        parsed = parse_json(result)
                        if parsed:
                            parsed['source'] = source_name
                            parsed['type'] = 'text'
                            parsed['added_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                            st.session_state['knowledge_hub'].append(parsed)
                            st.success("✅ 추가됨!")
                            st.rerun()
                else:
                    st.error("최소 50자 이상 입력하세요")
    
    with col2:
        st.markdown("### 🧠 정보 허브")
        
        hub = st.session_state.get('knowledge_hub', [])
        
        if hub:
            st.markdown(f'<div class="summary-hub"><b>📚 수집 정보: {len(hub)}개</b></div>', unsafe_allow_html=True)
            
            for i, item in enumerate(hub):
                title = item.get('title', item.get('main_topic', f'항목 {i+1}'))
                item_type = "📺" if item.get('type') == 'youtube' else "📝"
                
                with st.expander(f"{item_type} {title}", expanded=False):
                    st.caption(f"출처: {item.get('source', '')} | {item.get('added_at', '')}")
                    
                    st.write("**핵심 포인트:**")
                    for kp in item.get('key_points', []):
                        st.write(f"• {kp}")
                    
                    if item.get('summary'):
                        st.info(f"📝 {item['summary']}")
                    
                    if st.button("🗑️ 삭제", key=f"p3_del_{i}"):
                        st.session_state['knowledge_hub'].pop(i)
                        st.rerun()
            
            st.markdown("---")
            st.markdown("### 📋 학습 정보 통합")
            
            if st.button("🔄 전체 학습 내용 통합 분석", use_container_width=True, key="p3_integrate"):
                with st.spinner("학습 내용 통합 분석 중..."):
                    result = summarize_all_knowledge(hub, st.session_state.get('topic', ''))
                    parsed = parse_json(result)
                    if parsed:
                        st.session_state['study_summary'] = parsed
                        st.rerun()
            
            if st.session_state.get('study_summary'):
                s = st.session_state['study_summary']
                
                st.markdown(f"""
                <div class="summary-hub">
                    <b>📊 통합 분석 결과</b><br><br>
                    {s.get('integrated_summary', '')}
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("🎯 핵심 인사이트", expanded=True):
                    for ins in s.get('core_insights', []):
                        st.write(f"💡 {ins}")
                
                with st.expander("📅 4주 학습 계획"):
                    plan = s.get('study_plan', {})
                    for week, content in plan.items():
                        st.write(f"**{week}:** {content}")
                
                if s.get('unique_angle'):
                    st.success(f"✨ **차별화 관점:** {s.get('unique_angle', '')}")
        else:
            st.markdown('<div style="text-align:center;padding:60px;background:#fff;border-radius:16px;"><p style="color:#888;">유튜브 URL이나 텍스트를 추가해보세요</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="next-section"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("← 이전", key="p3_prev", use_container_width=True):
            go_prev()
            st.rerun()
    with c3:
        if st.button("다음 → 목차", key="p3_next", use_container_width=True):
            go_next()
            st.rerun()


# ==========================================
# PAGE 4: 목차 설계
# ==========================================
elif current == 4:
    st.markdown("## 📋 목차 설계")
    
    if st.session_state.get('market_gaps'):
        st.success(f"✅ {len(st.session_state['market_gaps'])}개 차별화 포인트 반영")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 목차 생성")
        
        st.markdown("""
        <div class="info-card">
            <b>💡 목차 작성 팁</b><br><br>
            • 목차만 봐도 궁금하게<br>
            • 구체적인 숫자와 결과<br>
            • "나도 할 수 있겠다" 느낌
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✨ 목차 생성하기", use_container_width=True, key="p4_outline_btn"):
            if not st.session_state.get('topic'):
                st.error("주제를 입력하세요")
            elif not get_api_key():
                st.error("API 키를 입력해주세요")
            else:
                with st.spinner("목차 생성 중..."):
                    result = generate_outline(
                        st.session_state['topic'],
                        st.session_state.get('target_persona', ''),
                        st.session_state.get('pain_points', ''),
                        st.session_state.get('market_gaps', [])
                    )
                    
                    if result:
                        lines = result.split('\n')
                        chapters = []
                        current_ch = None
                        subtopics = {}
                        
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                            
                            # PART로 시작하는 라인 찾기
                            if 'PART' in line.upper() or line.upper().startswith('PART'):
                                name = line.replace('#', '').strip()
                                name = re.sub(r'\*\*(.+?)\*\*', r'\1', name)
                                if name:
                                    current_ch = name
                                    chapters.append(current_ch)
                                    subtopics[current_ch] = []
                            # 소제목 (- 로 시작)
                            elif current_ch and line.startswith('-'):
                                st_name = line.lstrip('- ').strip()
                                st_name = re.sub(r'\*\*(.+?)\*\*', r'\1', st_name).replace('#', '').strip()
                                if st_name and len(st_name) > 2:
                                    subtopics[current_ch].append(st_name)
                        
                        if chapters:
                            st.session_state['outline'] = chapters
                            st.session_state['chapters'] = {}
                            for ch in chapters:
                                st.session_state['chapters'][ch] = {
                                    'subtopics': subtopics.get(ch, []),
                                    'subtopic_data': {s: {'questions': [], 'answers': [], 'content': ''} for s in subtopics.get(ch, [])}
                                }
                            st.success(f"✅ {len(chapters)}개 챕터 생성!")
                            st.rerun()
                        else:
                            st.error("목차 생성 실패. 다시 시도해주세요.")
                    else:
                        st.error("AI 응답 없음. 다시 시도해주세요.")
    
    with col2:
        st.markdown("### 📝 현재 목차")
        
        if st.session_state.get('outline'):
            for ch in st.session_state['outline']:
                st.markdown(f"**{ch}**")
                for st_name in st.session_state['chapters'].get(ch, {}).get('subtopics', []):
                    st.write(f"  • {st_name}")
        else:
            st.markdown('<div style="text-align:center;padding:60px;background:#fff;border-radius:16px;"><p style="color:#888;">목차를 생성해주세요</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="next-section"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("← 이전", key="p4_prev", use_container_width=True):
            go_prev()
            st.rerun()
    with c3:
        if st.button("다음 → 본문", key="p4_next", use_container_width=True):
            go_next()
            st.rerun()


# ==========================================
# PAGE 5: 본문 작성
# ==========================================
elif current == 5:
    st.markdown("## ✍️ 본문 작성")
    
    if not st.session_state.get('outline'):
        st.warning("먼저 목차를 설계하세요")
    else:
        col_sel1, col_sel2 = st.columns([1, 1])
        with col_sel1:
            selected_ch = st.selectbox("📚 챕터", st.session_state['outline'], key="p5_chapter")
        
        if selected_ch and selected_ch in st.session_state['chapters']:
            ch_data = st.session_state['chapters'][selected_ch]
            
            with col_sel2:
                if ch_data.get('subtopics'):
                    selected_st = st.selectbox("✍️ 소제목", ch_data['subtopics'], key="p5_subtopic")
            
            completed = sum(1 for s in ch_data.get('subtopics', []) if ch_data.get('subtopic_data', {}).get(s, {}).get('content'))
            total = len(ch_data.get('subtopics', []))
            if total > 0:
                st.progress(completed / total)
                st.caption(f"{completed}/{total} 완료")
            
            if ch_data.get('subtopics') and selected_st:
                if selected_st not in ch_data.get('subtopic_data', {}):
                    ch_data['subtopic_data'][selected_st] = {'questions': [], 'answers': [], 'content': ''}
                
                st_data = ch_data['subtopic_data'][selected_st]
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("### 🎤 인터뷰")
                    if st.button("질문 생성", key="p5_gen_q"):
                        with st.spinner("생성 중..."):
                            q_text = generate_questions(selected_st, selected_ch, st.session_state['topic'])
                            if q_text:
                                questions = re.findall(r'Q\d+:\s*(.+)', q_text)
                                if not questions:
                                    questions = [q.strip() for q in q_text.split('\n') if '?' in q][:3]
                                st_data['questions'] = questions
                                st_data['answers'] = [''] * len(questions)
                                st.rerun()
                    
                    if st_data.get('questions'):
                        for i, q in enumerate(st_data['questions']):
                            st.markdown(f"**Q{i+1}.** {q}")
                            if i >= len(st_data['answers']):
                                st_data['answers'].append('')
                            st_data['answers'][i] = st.text_area(f"A{i+1}", value=st_data['answers'][i], height=80, key=f"p5_ans_{i}", label_visibility="collapsed")
                
                with col2:
                    st.markdown("### 📝 본문")
                    has_ans = st_data.get('questions') and any(a.strip() for a in st_data.get('answers', []))
                    
                    if has_ans:
                        if st.button("✨ 본문 생성", key="p5_gen"):
                            with st.spinner("본문 작성 중..."):
                                content = generate_content_premium(selected_st, selected_ch, st_data['questions'], st_data['answers'], st.session_state['topic'], st.session_state['target_persona'])
                                if content:
                                    st_data['content'] = content
                                    st.rerun()
                    
                    edited = st.text_area("본문", value=st_data.get('content', ''), height=400, key="p5_content")
                    st_data['content'] = edited
                    
                    if edited:
                        st.caption(f"📊 {len(edited.replace(' ', '').replace(chr(10), '')):,}자")
        
        st.markdown("---")
        st.markdown("### 📖 전체 본문")
        full_content = get_full_content()
        if full_content:
            char_count = len(full_content.replace(' ', '').replace('\n', ''))
            st.success(f"📊 총 {char_count:,}자 | 약 {char_count//500}페이지")
            with st.expander("전체 본문 보기", expanded=False):
                st.text_area("전체", value=full_content, height=300, disabled=True, key="p5_full")
    
    st.markdown('<div class="next-section"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("← 이전", key="p5_prev", use_container_width=True):
            go_prev()
            st.rerun()
    with c3:
        if st.button("다음 → 출력", key="p5_next", use_container_width=True):
            go_next()
            st.rerun()


# ==========================================
# PAGE 6: 최종 출력
# ==========================================
elif current == 6:
    st.markdown("## 📥 최종 출력")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown("### 다운로드")
        
        final_title = st.text_input("제목", value=st.session_state.get('book_title', ''), key="p6_title")
        final_subtitle = st.text_input("부제", value=st.session_state.get('subtitle', ''), key="p6_subtitle")
        
        full = f"{final_title}\n{final_subtitle}\n\n{'='*50}\n\n"
        for ch in st.session_state.get('outline', []):
            if ch in st.session_state.get('chapters', {}):
                ch_data = st.session_state['chapters'][ch]
                ch_content = ""
                for s in ch_data.get('subtopics', []):
                    c = ch_data.get('subtopic_data', {}).get(s, {}).get('content', '')
                    if c:
                        ch_content += f"\n\n【{s}】\n\n{clean_content(c)}"
                if ch_content:
                    full += f"\n\n{ch}\n{'-'*40}{ch_content}\n"
        
        with st.expander("📖 미리보기", expanded=True):
            st.text_area("전체", value=full, height=300, disabled=True, key="p6_preview")
        
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📄 TXT", full, file_name=f"{final_title or 'ebook'}.txt", use_container_width=True, key="p6_txt")
        with c2:
            html = f"<html><head><meta charset='utf-8'><title>{final_title}</title><style>body{{max-width:800px;margin:0 auto;padding:40px;font-family:sans-serif;line-height:1.8;}}</style></head><body>{full.replace(chr(10), '<br>')}</body></html>"
            st.download_button("🌐 HTML", html, file_name=f"{final_title or 'ebook'}.html", use_container_width=True, key="p6_html")
        
        total = len(full.replace(' ', '').replace('\n', ''))
        if total > 0:
            st.success(f"✅ 총 {total:,}자 | 약 {total//500}페이지")
    
    with col2:
        st.markdown("### 📊 현황")
        total_st = sum(len(ch.get('subtopics', [])) for ch in st.session_state.get('chapters', {}).values())
        done = sum(1 for ch in st.session_state.get('chapters', {}).values() for s in ch.get('subtopic_data', {}).values() if s.get('content'))
        
        if total_st > 0:
            st.progress(done / total_st)
            st.write(f"**완료:** {done}/{total_st}")
    
    st.markdown('<div class="next-section"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("← 이전", key="p6_prev", use_container_width=True):
            go_prev()
            st.rerun()


st.markdown('<div style="text-align:center;padding:40px;margin-top:60px;border-top:1px solid #e8e8e8;color:#888;">전자책 작성 프로그램 — <b>남현우 작가</b></div>', unsafe_allow_html=True)
