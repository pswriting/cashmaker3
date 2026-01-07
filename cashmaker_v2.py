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

# Output Rules
- 절대 ** (별표 두개)를 사용하지 마세요. 강조가 필요하면 따옴표나 【】를 사용하세요.
- 마크다운 문법 사용 금지
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

# --- 페이지 설정 ---
st.set_page_config(
    page_title="전자책 작성 프로그램", 
    layout="wide", 
    page_icon="◆"
)

# --- CSS 스타일 ---
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    * { font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif; }
    
    .stDeployButton {display:none;} 
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
    .stApp { background: #ffffff; }
    .main .block-container { background: #ffffff; padding: 2rem 3rem; max-width: 1400px; }
    
    [data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #eeeeee; }
    [data-testid="stSidebar"] * { color: #222222 !important; }
    
    .stMarkdown, .stText, p, span, label { color: #222222 !important; line-height: 1.7; }
    
    h1 { color: #111111 !important; font-weight: 700 !important; font-size: 2rem !important; }
    h2 { color: #111111 !important; font-weight: 700 !important; font-size: 1.4rem !important; }
    h3 { color: #222222 !important; font-weight: 600 !important; font-size: 1.1rem !important; }
    
    .stTabs [data-baseweb="tab-list"] { background: transparent; gap: 0; border-bottom: 2px solid #eeeeee; }
    .stTabs [data-baseweb="tab"] { background: transparent; color: #888888 !important; padding: 16px 20px; font-size: 14px; border-bottom: 2px solid transparent; margin-bottom: -2px; }
    .stTabs [aria-selected="true"] { color: #111111 !important; font-weight: 700 !important; border-bottom: 2px solid #111111 !important; }
    
    .stButton > button { width: 100%; border-radius: 30px; font-weight: 600; background: #111111 !important; color: #ffffff !important; border: none !important; padding: 14px 32px; font-size: 15px; }
    .stButton > button:hover { background: #333333 !important; }
    .stButton > button * { color: #ffffff !important; }
    
    .stTextInput > div > div > input, .stTextArea > div > div > textarea { background: #ffffff !important; border: 1px solid #dddddd !important; border-radius: 8px !important; color: #222222 !important; }
    
    .hero-section { text-align: center; padding: 40px 20px; margin-bottom: 30px; }
    .hero-label { font-size: 13px; font-weight: 600; color: #666666; letter-spacing: 3px; margin-bottom: 12px; }
    .hero-title { font-size: 36px; font-weight: 800; color: #111111; margin-bottom: 12px; }
    .hero-subtitle { font-size: 16px; color: #666666; }
    
    .section-label { font-size: 12px; font-weight: 600; color: #888888; letter-spacing: 2px; margin-bottom: 8px; text-transform: uppercase; }
    
    .score-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; padding: 40px; text-align: center; color: white; }
    .score-number { font-size: 72px; font-weight: 800; line-height: 1; }
    .score-label { font-size: 14px; opacity: 0.9; margin-top: 8px; }
    
    .info-card { background: #f8f8f8; border-radius: 16px; padding: 24px; margin: 16px 0; }
    .info-card-title { font-size: 12px; font-weight: 700; color: #888888; letter-spacing: 1px; margin-bottom: 12px; }
    
    .gap-report { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 20px; padding: 30px; color: white; margin: 20px 0; }
    .gap-report-title { font-size: 20px; font-weight: 800; margin-bottom: 20px; }
    .gap-item { background: rgba(255,255,255,0.2); border-radius: 12px; padding: 16px; margin: 10px 0; }
    .gap-item-title { font-weight: 700; font-size: 16px; }
    .gap-item-desc { font-size: 14px; opacity: 0.9; margin-top: 8px; }
    
    .market-report { background: #111111; border-radius: 20px; padding: 30px; color: white; margin: 20px 0; }
    .market-report-title { font-size: 18px; font-weight: 700; margin-bottom: 20px; color: #ffffff; }
    .market-stat { display: inline-block; background: rgba(255,255,255,0.1); border-radius: 12px; padding: 16px 24px; margin: 8px; text-align: center; }
    .market-stat-value { font-size: 28px; font-weight: 800; color: #4ade80; }
    .market-stat-label { font-size: 12px; color: #aaaaaa; margin-top: 4px; }
    
    .verdict-badge { display: inline-block; padding: 12px 32px; border-radius: 30px; font-weight: 700; font-size: 16px; }
    .verdict-go { background: #4ade80; color: #000000; }
    .verdict-wait { background: #fbbf24; color: #000000; }
    .verdict-no { background: #f87171; color: #ffffff; }
    
    .concept-card { background: #ffffff; border: 2px solid #eeeeee; border-radius: 16px; padding: 20px; margin: 12px 0; }
    .concept-number { font-size: 12px; color: #888888; margin-bottom: 8px; }
    .concept-text { font-size: 18px; font-weight: 700; color: #111111; line-height: 1.5; }
    .concept-reason { font-size: 14px; color: #666666; margin-top: 12px; padding-top: 12px; border-top: 1px solid #eeeeee; }
    
    .knowledge-hub { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; padding: 24px; margin: 16px 0; }
    .knowledge-item { background: rgba(255,255,255,0.15); border-radius: 12px; padding: 16px; margin: 10px 0; color: white; }
    
    .next-btn-container { margin-top: 40px; padding-top: 20px; border-top: 1px solid #eeeeee; }
    
    .review-analysis-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    .review-analysis-table th { background: #111111; color: white; padding: 12px; text-align: left; }
    .review-analysis-table td { padding: 12px; border-bottom: 1px solid #eeeeee; }
    
    .premium-footer { text-align: center; padding: 40px 20px; margin-top: 60px; border-top: 1px solid #eeeeee; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 비밀번호 설정
# ==========================================
CORRECT_PASSWORD = "cashmaker2024"

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown("""
    <div style="max-width: 400px; margin: 100px auto; padding: 40px; background: #ffffff; border: 1px solid #eeeeee; border-radius: 20px; text-align: center;">
        <div style="font-size: 28px; font-weight: 700; color: #111111; margin-bottom: 8px;">CASHMAKER</div>
        <div style="font-size: 15px; color: #888888; margin-bottom: 30px;">전자책 작성 프로그램</div>
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
    'outline': [], 'chapters': {}, 'book_title': '', 'subtitle': '',
    'topic_score': None, 'score_details': None, 'generated_titles': None,
    'suggested_targets': None, 'analyzed_pains': None,
    'review_analysis': None, 'market_gaps': None, 'gap_report': None,
    'knowledge_hub': [], 'video_summaries': [],
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
    ]
    progress = sum(progress_items) / len(progress_items) * 100
    st.progress(progress / 100)
    st.caption(f"{progress:.0f}% 완료")
    
    st.markdown("---")
    st.markdown("### API 설정")
    if 'api_key' not in st.session_state:
        st.session_state['api_key'] = load_saved_api_key()
    
    api_key_input = st.text_input("Gemini API 키", value=st.session_state['api_key'], type="password", placeholder="AIza...")
    if api_key_input and api_key_input != st.session_state['api_key']:
        st.session_state['api_key'] = api_key_input
        save_api_key(api_key_input)
        st.toast("✅ API 키 저장됨!")
    
    with st.expander("API 키 발급 방법"):
        st.markdown("""1. [Google AI Studio](https://aistudio.google.com/apikey) 접속\n2. Google 계정 로그인\n3. "API 키 만들기" 클릭\n4. 키 복사 후 붙여넣기""")
    
    st.markdown("---")
    st.markdown("### 💾 저장/불러오기")
    save_data = {k: st.session_state.get(k, '') for k in ['topic', 'target_persona', 'pain_points', 'outline', 'chapters', 'book_title', 'subtitle', 'knowledge_hub']}
    st.download_button("📥 작업 저장", json.dumps(save_data, ensure_ascii=False), file_name=f"ebook_{datetime.now().strftime('%m%d_%H%M')}.json", mime="application/json", use_container_width=True)


# ==========================================
# 헬퍼 함수들
# ==========================================
def get_api_key():
    return st.session_state.get('api_key', '')

def clean_markdown(text):
    """마크다운 기호 제거"""
    if not text:
        return ""
    text = re.sub(r'\*\*([^*]+)\*\*', r'「\1」', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = text.replace('**', '')
    text = text.replace('*', '')
    return text

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
                for st_name in ch_data.get('subtopics', []):
                    st_data = ch_data['subtopic_data'].get(st_name, {})
                    if st_data.get('content'):
                        pure_content += st_data['content']
    return pure_content


# ==========================================
# AI 기본 함수
# ==========================================
def ask_ai(system_role, prompt, temperature=0.7):
    api_key = get_api_key()
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        final_instruction = GENIUS_PERSONA + "\n\n" + f"현재 역할: {system_role}"
        ai_model = genai.GenerativeModel('models/gemini-2.0-flash')
        generation_config = genai.types.GenerationConfig(temperature=temperature, max_output_tokens=4000)
        response = ai_model.generate_content(prompt, generation_config=generation_config)
        return response.text
    except Exception as e:
        st.error(f"AI 오류: {str(e)}")
        return None

def parse_json_response(response):
    """JSON 응답 안전하게 파싱"""
    if not response:
        return None
    try:
        # JSON 블록 찾기
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        pass
    return None


# ==========================================
# AI 함수들 (개선됨)
# ==========================================

def suggest_target_personas(topic):
    """주제 기반 타겟 페르소나 추천"""
    prompt = f"""주제: {topic}

이 주제의 전자책을 구매할 가능성이 높은 타겟 5개를 추천해주세요.

JSON 형식으로만 출력 (설명 없이):
{{
    "personas": [
        {{
            "name": "페르소나 이름",
            "demographics": "30대 초반, 대기업 3~5년차",
            "needs": "핵심 니즈",
            "buying_power": "상/중/하",
            "market_size": "약 50만명",
            "pain_points": ["고민1", "고민2", "고민3"]
        }}
    ]
}}"""
    return ask_ai("시장 분석가", prompt, temperature=0.7)


def analyze_target_pains(topic, target_persona):
    """타겟의 고민 자동 분석"""
    prompt = f"""주제: {topic}
타겟: {target_persona}

이 타겟의 고민을 깊이 분석해주세요.

JSON 형식으로만 출력:
{{
    "surface_pains": ["표면적 고민 1", "표면적 고민 2", "표면적 고민 3"],
    "hidden_pains": ["숨겨진 진짜 고민 1", "숨겨진 진짜 고민 2", "숨겨진 진짜 고민 3"],
    "emotional_pains": ["감정적 고통 1", "감정적 고통 2"],
    "past_failures": ["과거 실패 경험 1", "과거 실패 경험 2"],
    "summary": "종합 분석 2문장"
}}"""
    return ask_ai("소비자 심리 전문가", prompt, temperature=0.6)


def auto_analyze_competitor_reviews(topic):
    """경쟁사 리뷰 자동 분석 (AI 시뮬레이션)"""
    prompt = f"""당신은 전자책 시장 조사 전문가입니다.

주제: {topic}

크몽, yes24, 알라딘 등에서 이 주제 관련 베스트셀러 전자책들의 리뷰 패턴을 분석해주세요.
실제 시장에서 발견되는 일반적인 불만과 니즈를 기반으로 분석합니다.

다음을 분석해주세요:
1. 이 분야 전자책에서 흔히 발견되는 부정적 리뷰 패턴
2. 독자들이 자주 지적하는 부족한 점
3. 시장의 빈틈 (기존 책들이 채우지 못하는 니즈)

JSON 형식으로만 출력:
{{
    "analyzed_books_count": "분석 추정 도서 수 (예: 약 50권)",
    "review_count": "분석 추정 리뷰 수 (예: 약 500개)",
    "negative_patterns": [
        {{"pattern": "자주 발견되는 불만 패턴", "frequency": "상/중/하", "example": "예시 리뷰"}}
    ],
    "common_complaints": [
        "흔한 불만 1",
        "흔한 불만 2",
        "흔한 불만 3"
    ],
    "market_gaps": [
        {{
            "gap": "시장의 빈틈",
            "opportunity": "이 빈틈을 채우면 얻는 기회",
            "priority": "상/중/하",
            "content_idea": "이 GAP을 채울 콘텐츠 아이디어"
        }}
    ],
    "success_formula": {{
        "must_have": ["반드시 포함해야 할 요소 1", "요소 2", "요소 3"],
        "avoid": ["피해야 할 요소 1", "요소 2"],
        "differentiation": "차별화 포인트 제안"
    }},
    "summary": "종합 분석 요약 2문장"
}}"""
    return ask_ai("시장 조사 전문가", prompt, temperature=0.6)


def analyze_market_simple(topic):
    """시장 분석 (이해하기 쉽게)"""
    prompt = f"""주제: {topic}

이 주제로 전자책을 출시하면 잘 팔릴지 분석해주세요.
일반인도 이해할 수 있게 쉬운 말로 설명해주세요.

JSON 형식으로만 출력:
{{
    "verdict": "강력 추천/추천/보류/비추천 중 하나",
    "verdict_reason": "한 문장으로 이유",
    "total_score": 85,
    "market_size": {{
        "level": "매우 큼/큼/보통/작음 중 하나",
        "description": "쉬운 설명 (예: 월 1만명 이상 검색, 수요 많음)",
        "score": 85
    }},
    "competition": {{
        "level": "치열함/보통/낮음 중 하나",
        "description": "쉬운 설명 (예: 경쟁자 많지만 차별화 가능)",
        "score": 70
    }},
    "profit_potential": {{
        "price_range": "예상 가격대 (예: 9,900~19,900원)",
        "monthly_income": "예상 월 수익 (예: 50~200만원)",
        "description": "쉬운 설명",
        "score": 80
    }},
    "timing": {{
        "status": "지금이 적기/괜찮음/늦음 중 하나",
        "description": "쉬운 설명",
        "score": 75
    }},
    "recommendation": "최종 추천 의견 2~3문장. 해야 할지 말아야 할지 명확하게."
}}"""
    return ask_ai("시장 분석가", prompt, temperature=0.5)


def generate_concept_clean(topic, persona, pain_points):
    """한 줄 컨셉 생성 (마크다운 없이)"""
    prompt = f"""주제: {topic}
타겟: {persona}
고민: {pain_points}

"이 책 안 읽으면 손해"라는 느낌을 주는 한 줄 컨셉 5개를 만들어주세요.

중요: 별표(**)나 마크다운 기호를 절대 사용하지 마세요.
강조는 「」 또는 【】를 사용하세요.

출력 형식 (번호와 텍스트만):
1. 첫 번째 컨셉 문장
→ 왜 끌리는가 설명

2. 두 번째 컨셉 문장
→ 왜 끌리는가 설명

(5개까지)"""
    result = ask_ai("카피라이터", prompt, temperature=0.9)
    return clean_markdown(result) if result else None


def generate_titles_clean(topic, persona, pain_points):
    """제목 생성"""
    prompt = f"""주제: {topic}
타겟: {persona}
고민: {pain_points}

베스트셀러급 전자책 제목 5개를 만들어주세요.

JSON 형식으로만 출력:
{{
    "titles": [
        {{
            "title": "7자 이내 임팩트 제목",
            "subtitle": "15자 이내 부제",
            "why_works": "왜 이 제목이 끌리는지 설명"
        }}
    ]
}}"""
    return ask_ai("카피라이터", prompt, temperature=0.9)


def generate_killer_outline(topic, persona, pain_points, market_gaps=None):
    """자청/프드프 스타일 킬러 목차 생성"""
    gaps_text = ""
    if market_gaps:
        gaps_text = f"""
【차별화 포인트 - 경쟁사가 놓친 것들】
{chr(10).join([f"• {g}" for g in market_gaps[:3]])}
"""
    
    prompt = f"""당신은 자청(역행자), 신사임당, 프드프급 베스트셀러 편집자입니다.

【전자책 정보】
주제: {topic}
타겟: {persona}
타겟의 고민: {pain_points}
{gaps_text}

【미션】
목차만 봐도 "와, 이거 사야겠다"라는 생각이 드는 목차를 만드세요.

【킬러 목차의 비밀 공식】

1부: 뒤통수 치기 (The Shock)
→ 독자가 믿고 있던 상식을 박살내세요
→ "뭐? 내가 그동안 잘못 알고 있었다고?" 느낌

2부: 진짜 원인 폭로 (The Truth)  
→ 왜 지금까지 안 됐는지 진짜 이유를 폭로
→ "아... 이래서 안 됐던 거구나" 느낌

3부: 비밀 무기 공개 (The Secret)
→ 아무도 안 알려주는 핵심 공식/치트키
→ "이런 방법이 있었어?" 느낌

4부: 따라하기 (The Action)
→ 바로 오늘부터 실행 가능한 구체적 단계
→ "이거 그대로 따라하면 되겠네" 느낌

【제목 작성 원칙】
- 챕터 제목: 상식 파괴 + 호기심 폭발 (예: "성실함이 당신을 가난하게 만든다")
- 소제목: 구체적 숫자 + 반전 (예: "97%가 모르는 3가지 함정")

【절대 금지】
- "~의 중요성", "~하는 방법", "~하는 법"
- "기초", "기본", "입문", "개론"  
- "효과적인", "성공적인", "올바른"
- 뻔하고 지루한 표현 모두

【출력 형식】
## PART 1. [충격적인 챕터 제목]
- [호기심 폭발 소제목 1]
- [호기심 폭발 소제목 2]
- [호기심 폭발 소제목 3]

## PART 2. [원인 폭로 챕터 제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]

## PART 3. [비밀 공개 챕터 제목]
- [소제목 1]
- [소제목 2]  
- [소제목 3]

## PART 4. [실행 유도 챕터 제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]

목차만 출력하세요. 설명 금지."""
    return ask_ai("베스트셀러 편집자", prompt, temperature=0.85)


def summarize_youtube_with_gemini(video_url):
    """Gemini로 유튜브 영상 요약 (URL 기반)"""
    prompt = f"""유튜브 영상 URL: {video_url}

이 영상의 내용을 요약해주세요. 
(참고: 실제 영상 내용에 접근할 수 없다면, URL에서 유추할 수 있는 정보를 바탕으로 
해당 주제에 대한 핵심 인사이트를 제공해주세요)

JSON 형식으로 출력:
{{
    "title": "영상 제목 (추정)",
    "main_topic": "핵심 주제",
    "key_points": [
        "핵심 포인트 1",
        "핵심 포인트 2",
        "핵심 포인트 3",
        "핵심 포인트 4",
        "핵심 포인트 5"
    ],
    "action_items": [
        "실행 가능한 액션 1",
        "실행 가능한 액션 2",
        "실행 가능한 액션 3"
    ],
    "quotes": [
        "인용할 만한 문구 1",
        "인용할 만한 문구 2"
    ],
    "ebook_ideas": [
        "전자책에 적용할 수 있는 아이디어 1",
        "전자책에 적용할 수 있는 아이디어 2"
    ]
}}"""
    return ask_ai("콘텐츠 큐레이터", prompt, temperature=0.6)


def summarize_text_content(text_content, source_name=""):
    """텍스트 콘텐츠 요약 (블로그, 아티클 등)"""
    prompt = f"""다음 콘텐츠를 분석하고 핵심을 추출해주세요.

출처: {source_name}
내용:
{text_content[:3000]}

JSON 형식으로 출력:
{{
    "title": "콘텐츠 제목/주제",
    "key_points": ["핵심 포인트 1", "핵심 포인트 2", "핵심 포인트 3"],
    "insights": ["인사이트 1", "인사이트 2"],
    "action_items": ["실행 가능한 것 1", "실행 가능한 것 2"],
    "ebook_application": "전자책에 어떻게 적용할 수 있는지"
}}"""
    return ask_ai("콘텐츠 분석가", prompt, temperature=0.5)


def generate_subtopic_content(subtopic_title, chapter_title, questions, answers, topic, persona):
    qa_pairs = ""
    for i, (q, a) in enumerate(zip(questions, answers), 1):
        if a.strip():
            qa_pairs += f"\n질문{i}: {q}\n답변{i}: {a}\n"
    
    prompt = f"""당신은 자청, 신사임당급 베스트셀러 작가입니다.

【집필 정보】
주제: {topic}
챕터: {chapter_title}
소제목: {subtopic_title}
타겟: {persona}

【작가 인터뷰 내용】
{qa_pairs}

【글쓰기 규칙】
1. 첫 문장에서 뒤통수를 쳐라 (상식 파괴 or 충격적 사실)
2. 짧은 문장 위주 (15~25자)
3. 스토리 > 설명 (경험담 중심)
4. 숫자로 증명 (구체적 데이터)
5. 합쇼체 100% 유지

【금지】
- 마크다운 기호 (**, *, #)
- "따라서", "그러므로" 등 딱딱한 연결어
- "~의 중요성", "~해야 합니다" 반복

분량: 1500~2000자

'{subtopic_title}'의 본문만 작성하세요."""
    result = ask_ai("베스트셀러 작가", prompt, temperature=0.8)
    return clean_markdown(result) if result else None


def generate_interview_questions(subtopic_title, chapter_title, topic):
    prompt = f"""'{topic}' 전자책의 '{chapter_title}' 챕터 중 '{subtopic_title}' 부분을 쓰기 위한 인터뷰 질문 3개를 만들어주세요.

형식:
Q1: [질문]
Q2: [질문]
Q3: [질문]"""
    return ask_ai("인터뷰어", prompt, temperature=0.7)


# ==========================================
# 메인 UI
# ==========================================
st.markdown("""
<div class="hero-section">
    <div class="hero-label">CASHMAKER</div>
    <div class="hero-title">전자책 작성 프로그램</div>
    <div class="hero-subtitle">경쟁사 리뷰 분석 → 시장의 빈틈 발견 → 베스트셀러 탄생</div>
</div>
""", unsafe_allow_html=True)

# 탭 순서 변경: 전문성 키우기가 4번으로
tabs = st.tabs(["① 주제 & 시장분석", "② 타겟 & 컨셉", "③ 경쟁사 분석", "④ 전문성 키우기", "⑤ 목차 설계", "⑥ 본문 작성", "⑦ 최종 출력"])


# ==========================================
# TAB 1: 주제 & 시장분석
# ==========================================
with tabs[0]:
    st.markdown("## 주제 선정 & 시장 분석")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<p class="section-label">Step 01</p>', unsafe_allow_html=True)
        st.markdown("### 주제 입력")
        
        topic_input = st.text_input("어떤 주제로 전자책을 쓸까요?", value=st.session_state['topic'], placeholder="예: 월 배당으로 경제적 자유 얻기", key="topic_input_1")
        if topic_input != st.session_state['topic']:
            st.session_state['topic'] = topic_input
            st.session_state['score_details'] = None
        
        st.markdown("""
        <div class="info-card">
            <div class="info-card-title">💡 좋은 주제의 조건</div>
            <p>• 내가 직접 경험하고 성과를 낸 것</p>
            <p>• 사람들이 돈 주고 배우고 싶어하는 것</p>
            <p>• 구체적인 결과를 약속할 수 있는 것</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 시장 분석하기", key="analyze_market_btn", use_container_width=True):
            if not topic_input:
                st.error("주제를 입력해주세요.")
            elif not get_api_key():
                st.error("API 키를 먼저 입력해주세요.")
            else:
                with st.spinner("시장 분석 중... (10~20초)"):
                    result = analyze_market_simple(topic_input)
                    parsed = parse_json_response(result)
                    if parsed:
                        st.session_state['score_details'] = parsed
                        st.session_state['topic_score'] = parsed.get('total_score', 0)
                    else:
                        st.error("분석 결과를 가져오지 못했습니다. 다시 시도해주세요.")
    
    with col2:
        st.markdown('<p class="section-label">Step 02</p>', unsafe_allow_html=True)
        st.markdown("### 분석 결과")
        
        if st.session_state.get('score_details'):
            details = st.session_state['score_details']
            score = details.get('total_score', 0)
            verdict = details.get('verdict', '분석 중')
            
            # 판정 배지
            verdict_class = "verdict-go" if "추천" in verdict else ("verdict-wait" if "보류" in verdict else "verdict-no")
            
            st.markdown(f"""
            <div class="score-card">
                <div class="score-number">{score}</div>
                <div class="score-label">종합 점수</div>
                <div style="margin-top: 20px;">
                    <span class="verdict-badge {verdict_class}">{verdict}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**📢 판정 이유:** {details.get('verdict_reason', '')}")
            
            # 세부 분석
            st.markdown("---")
            st.markdown("#### 📊 세부 분석")
            
            # 시장 규모
            ms = details.get('market_size', {})
            st.markdown(f"""
            **📈 시장 규모: {ms.get('level', '')}** ({ms.get('score', 0)}점)
            > {ms.get('description', '')}
            """)
            
            # 경쟁 강도
            comp = details.get('competition', {})
            st.markdown(f"""
            **⚔️ 경쟁 강도: {comp.get('level', '')}** ({comp.get('score', 0)}점)
            > {comp.get('description', '')}
            """)
            
            # 수익 잠재력
            profit = details.get('profit_potential', {})
            st.markdown(f"""
            **💰 수익 잠재력** ({profit.get('score', 0)}점)
            > 예상 가격: {profit.get('price_range', '')}
            > 예상 월수익: {profit.get('monthly_income', '')}
            """)
            
            # 타이밍
            timing = details.get('timing', {})
            st.markdown(f"""
            **⏰ 타이밍: {timing.get('status', '')}** ({timing.get('score', 0)}점)
            > {timing.get('description', '')}
            """)
            
            # 최종 추천
            st.success(f"**💡 최종 추천:** {details.get('recommendation', '')}")
        else:
            st.markdown("""
            <div style="text-align: center; padding: 60px 20px; background: #f8f8f8; border-radius: 16px;">
                <p style="color: #888888;">주제를 입력하고 분석 버튼을 눌러주세요</p>
                <p style="color: #aaaaaa; font-size: 14px;">AI가 시장성, 경쟁, 수익성을 분석해드립니다</p>
            </div>
            """, unsafe_allow_html=True)
    
    # 다음 버튼
    st.markdown('<div class="next-btn-container"></div>', unsafe_allow_html=True)
    if st.button("다음 → 타겟 & 컨셉", key="next_1", use_container_width=True):
        pass


# ==========================================
# TAB 2: 타겟 & 컨셉
# ==========================================
with tabs[1]:
    st.markdown("## 타겟 설정 & 제목 생성")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<p class="section-label">Step 01</p>', unsafe_allow_html=True)
        st.markdown("### 누구한테 판매하실 건가요?")
        
        # AI 타겟 추천
        if st.button("🎯 AI가 타겟 추천", key="suggest_targets"):
            if not st.session_state['topic']:
                st.error("주제를 먼저 입력해주세요.")
            elif not get_api_key():
                st.error("API 키를 입력해주세요.")
            else:
                with st.spinner("타겟 분석 중..."):
                    result = suggest_target_personas(st.session_state['topic'])
                    parsed = parse_json_response(result)
                    if parsed:
                        st.session_state['suggested_targets'] = parsed
        
        # 추천 타겟 표시
        if st.session_state.get('suggested_targets'):
            personas = st.session_state['suggested_targets'].get('personas', [])
            for i, p in enumerate(personas):
                with st.expander(f"🎯 {p.get('name', f'타겟 {i+1}')} (구매력: {p.get('buying_power', '')})"):
                    st.write(f"**인구통계:** {p.get('demographics', '')}")
                    st.write(f"**핵심 니즈:** {p.get('needs', '')}")
                    st.write(f"**시장 규모:** {p.get('market_size', '')}")
                    
                    if st.button(f"이 타겟 선택", key=f"select_t_{i}"):
                        st.session_state['target_persona'] = f"{p.get('name', '')} - {p.get('demographics', '')}"
                        # 고민 자동 분석
                        with st.spinner("고민 분석 중..."):
                            pain_result = analyze_target_pains(st.session_state['topic'], st.session_state['target_persona'])
                            parsed = parse_json_response(pain_result)
                            if parsed:
                                st.session_state['analyzed_pains'] = parsed
                                all_pains = parsed.get('surface_pains', []) + parsed.get('hidden_pains', [])
                                st.session_state['pain_points'] = ", ".join(all_pains[:5])
                        st.rerun()
        
        st.markdown("---")
        
        # 직접 입력
        persona = st.text_area("또는 직접 입력:", value=st.session_state['target_persona'], height=80, placeholder="예: 30대 직장인, 퇴사 준비 중, 월 100만원 부수입 원함", key="persona_direct")
        st.session_state['target_persona'] = persona
        
        # 고민 분석 결과
        if st.session_state.get('analyzed_pains'):
            pains = st.session_state['analyzed_pains']
            with st.expander("🔍 AI 분석: 타겟의 고민", expanded=True):
                st.markdown("**표면적 고민:**")
                for p in pains.get('surface_pains', []):
                    st.write(f"• {p}")
                st.markdown("**숨겨진 고민:**")
                for p in pains.get('hidden_pains', []):
                    st.write(f"• {p}")
                if pains.get('summary'):
                    st.info(pains['summary'])
        
        pain_points = st.text_area("독자의 가장 큰 고민은?", value=st.session_state['pain_points'], height=80, key="pains_direct")
        st.session_state['pain_points'] = pain_points
        
        if persona and st.button("🔍 고민 AI 분석", key="analyze_pains"):
            with st.spinner("분석 중..."):
                result = analyze_target_pains(st.session_state['topic'], persona)
                parsed = parse_json_response(result)
                if parsed:
                    st.session_state['analyzed_pains'] = parsed
                    all_pains = parsed.get('surface_pains', []) + parsed.get('hidden_pains', [])
                    st.session_state['pain_points'] = ", ".join(all_pains[:5])
                    st.rerun()
                else:
                    st.error("분석 실패. 다시 시도해주세요.")
    
    with col2:
        st.markdown('<p class="section-label">Step 02</p>', unsafe_allow_html=True)
        st.markdown("### 제목 & 컨셉 생성")
        
        if st.button("✨ 제목 생성", key="gen_titles"):
            if st.session_state['topic']:
                with st.spinner("제목 생성 중..."):
                    result = generate_titles_clean(st.session_state['topic'], st.session_state['target_persona'], st.session_state['pain_points'])
                    parsed = parse_json_response(result)
                    if parsed:
                        st.session_state['generated_titles'] = parsed
        
        if st.session_state.get('generated_titles'):
            for i, t in enumerate(st.session_state['generated_titles'].get('titles', [])[:4], 1):
                st.markdown(f"""
                <div class="concept-card">
                    <div class="concept-number">TITLE {i}</div>
                    <div class="concept-text">{t.get('title', '')}</div>
                    <div style="color: #666; font-size: 14px;">{t.get('subtitle', '')}</div>
                    <div class="concept-reason">{t.get('why_works', '')}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown('<p class="section-label">Step 03</p>', unsafe_allow_html=True)
        st.markdown("### 최종 선택")
        
        st.session_state['book_title'] = st.text_input("제목", value=st.session_state['book_title'], placeholder="최종 제목", key="final_title")
        st.session_state['subtitle'] = st.text_input("부제", value=st.session_state['subtitle'], placeholder="부제", key="final_subtitle")
        
        # 한 줄 컨셉
        st.markdown("---")
        if st.button("💡 한 줄 컨셉 생성", key="gen_concept"):
            if st.session_state['topic'] and persona:
                with st.spinner("생성 중..."):
                    concept = generate_concept_clean(st.session_state['topic'], persona, pain_points)
                    if concept:
                        st.session_state['one_line_concept'] = concept
        
        if st.session_state.get('one_line_concept'):
            st.markdown(f"""
            <div class="info-card">
                {st.session_state['one_line_concept'].replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<div class="next-btn-container"></div>', unsafe_allow_html=True)
    if st.button("다음 → 경쟁사 분석", key="next_2", use_container_width=True):
        pass


# ==========================================
# TAB 3: 경쟁사 분석 (자동 리뷰 분석 + 리포트)
# ==========================================
with tabs[2]:
    st.markdown("## 경쟁사 리뷰 분석")
    st.markdown("**🔥 AI가 경쟁사 리뷰를 자동 분석해서 '시장의 빈틈'을 찾아냅니다**")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<p class="section-label">자동 분석</p>', unsafe_allow_html=True)
        st.markdown("### 🤖 AI 자동 리뷰 분석")
        
        st.markdown("""
        <div class="info-card">
            <div class="info-card-title">💡 작동 방식</div>
            <p>AI가 크몽, yes24, 알라딘 등의 베스트셀러 리뷰 패턴을 분석합니다.</p>
            <p>별점 1~3점 리뷰와 "아쉬워요" 키워드를 집중 분석합니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 경쟁사 리뷰 자동 분석 (1클릭)", key="auto_analyze", use_container_width=True):
            if not st.session_state['topic']:
                st.error("주제를 먼저 입력해주세요.")
            elif not get_api_key():
                st.error("API 키를 입력해주세요.")
            else:
                with st.spinner("🔍 경쟁사 리뷰 분석 중... (AI가 시장을 스캔합니다)"):
                    result = auto_analyze_competitor_reviews(st.session_state['topic'])
                    parsed = parse_json_response(result)
                    if parsed:
                        st.session_state['review_analysis'] = parsed
                        # GAP 저장
                        gaps = parsed.get('market_gaps', [])
                        st.session_state['market_gaps'] = [g.get('gap', '') for g in gaps]
                        st.success("✅ 분석 완료! 우측에서 결과를 확인하세요.")
                    else:
                        st.error("분석 실패. 다시 시도해주세요.")
        
        # 분석 통계
        if st.session_state.get('review_analysis'):
            analysis = st.session_state['review_analysis']
            st.markdown(f"""
            <div class="market-report">
                <div class="market-report-title">📊 분석 통계</div>
                <div class="market-stat">
                    <div class="market-stat-value">{analysis.get('analyzed_books_count', 'N/A')}</div>
                    <div class="market-stat-label">분석 도서</div>
                </div>
                <div class="market-stat">
                    <div class="market-stat-value">{analysis.get('review_count', 'N/A')}</div>
                    <div class="market-stat-label">분석 리뷰</div>
                </div>
                <div class="market-stat">
                    <div class="market-stat-value">{len(analysis.get('market_gaps', []))}</div>
                    <div class="market-stat-label">발견된 GAP</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<p class="section-label">분석 결과</p>', unsafe_allow_html=True)
        
        if st.session_state.get('review_analysis'):
            analysis = st.session_state['review_analysis']
            
            # 🔥 시장의 빈틈 분석 리포트 (핵심!)
            st.markdown("### 🎯 시장의 빈틈 분석 리포트")
            
            gaps = analysis.get('market_gaps', [])
            if gaps:
                st.markdown(f"""
                <div class="gap-report">
                    <div class="gap-report-title">🔥 발견된 시장의 빈틈 {len(gaps)}개</div>
                """, unsafe_allow_html=True)
                
                for i, gap in enumerate(gaps, 1):
                    priority = gap.get('priority', '중')
                    priority_emoji = "🔴" if priority == "상" else ("🟡" if priority == "중" else "🟢")
                    st.markdown(f"""
                    <div class="gap-item">
                        <div class="gap-item-title">{priority_emoji} GAP {i}: {gap.get('gap', '')}</div>
                        <div class="gap-item-desc">💡 기회: {gap.get('opportunity', '')}</div>
                        <div class="gap-item-desc">📝 콘텐츠 아이디어: {gap.get('content_idea', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # 성공 공식
            formula = analysis.get('success_formula', {})
            if formula:
                st.markdown("### ✅ 성공 공식")
                
                with st.expander("반드시 포함할 요소", expanded=True):
                    for item in formula.get('must_have', []):
                        st.write(f"✅ {item}")
                
                with st.expander("피해야 할 요소"):
                    for item in formula.get('avoid', []):
                        st.write(f"❌ {item}")
                
                st.info(f"💡 **차별화 포인트:** {formula.get('differentiation', '')}")
            
            # 흔한 불만
            complaints = analysis.get('common_complaints', [])
            if complaints:
                with st.expander("📢 경쟁사의 흔한 불만"):
                    for c in complaints:
                        st.write(f"• {c}")
            
            # 종합
            if analysis.get('summary'):
                st.success(f"**📊 종합:** {analysis['summary']}")
        else:
            st.markdown("""
            <div style="text-align: center; padding: 60px 20px; background: #f8f8f8; border-radius: 16px;">
                <p style="font-size: 48px; margin-bottom: 16px;">🔍</p>
                <p style="color: #888888;">버튼을 눌러 경쟁사 분석을 시작하세요</p>
                <p style="color: #aaaaaa; font-size: 14px;">AI가 자동으로 시장의 빈틈을 찾아냅니다</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<div class="next-btn-container"></div>', unsafe_allow_html=True)
    if st.button("다음 → 전문성 키우기", key="next_3", use_container_width=True):
        pass


# ==========================================
# TAB 4: 전문성 키우기 (정보 허브)
# ==========================================
with tabs[3]:
    st.markdown("## 전문성 키우기")
    st.markdown("**📚 영상, 아티클, 자료를 학습하고 정보 허브에 통합하세요**")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📺 콘텐츠 학습 & 요약")
        
        input_type = st.radio("입력 유형", ["유튜브 URL", "텍스트 콘텐츠 (블로그/아티클)"], horizontal=True, key="input_type")
        
        if input_type == "유튜브 URL":
            youtube_url = st.text_input("유튜브 영상 URL", placeholder="https://www.youtube.com/watch?v=...", key="yt_url")
            
            if st.button("🎬 영상 분석 & 요약", key="analyze_yt"):
                if youtube_url:
                    with st.spinner("영상 분석 중..."):
                        result = summarize_youtube_with_gemini(youtube_url)
                        parsed = parse_json_response(result)
                        if parsed:
                            # 정보 허브에 추가
                            parsed['source'] = youtube_url
                            parsed['type'] = 'youtube'
                            parsed['added_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                            st.session_state['knowledge_hub'].append(parsed)
                            st.success("✅ 정보 허브에 추가되었습니다!")
                            st.rerun()
                else:
                    st.error("URL을 입력해주세요.")
        else:
            source_name = st.text_input("출처 이름", placeholder="예: 신사임당 블로그", key="source_name")
            text_content = st.text_area("콘텐츠 내용", height=200, placeholder="복사한 텍스트를 붙여넣으세요...", key="text_content")
            
            if st.button("📝 콘텐츠 분석 & 요약", key="analyze_text"):
                if text_content:
                    with st.spinner("분석 중..."):
                        result = summarize_text_content(text_content, source_name)
                        parsed = parse_json_response(result)
                        if parsed:
                            parsed['source'] = source_name or "직접 입력"
                            parsed['type'] = 'text'
                            parsed['added_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                            st.session_state['knowledge_hub'].append(parsed)
                            st.success("✅ 정보 허브에 추가되었습니다!")
                            st.rerun()
                else:
                    st.error("내용을 입력해주세요.")
        
        # 학습 체크리스트
        st.markdown("---")
        st.markdown("### ✅ 전문성 체크리스트")
        checklist = [
            "관련 유튜브 영상 5개 이상 분석",
            "베스트셀러 전자책 3권 이상 리뷰 분석",
            "관련 블로그/아티클 10개 이상 학습",
            "직접 실행해서 성과 만들기",
            "무료 테스터 3명 이상 피드백"
        ]
        for i, item in enumerate(checklist):
            st.checkbox(item, key=f"check_{i}")
    
    with col2:
        st.markdown("### 🧠 정보 허브 (학습 내용 통합)")
        
        if st.session_state.get('knowledge_hub'):
            hub = st.session_state['knowledge_hub']
            
            st.markdown(f"""
            <div class="knowledge-hub">
                <div style="font-size: 18px; font-weight: 700; color: white; margin-bottom: 16px;">
                    📚 수집된 정보: {len(hub)}개
                </div>
            """, unsafe_allow_html=True)
            
            for i, item in enumerate(hub):
                type_emoji = "📺" if item.get('type') == 'youtube' else "📝"
                st.markdown(f"""
                <div class="knowledge-item">
                    <div style="font-weight: 700;">{type_emoji} {item.get('title', '제목 없음')}</div>
                    <div style="font-size: 12px; opacity: 0.8;">출처: {item.get('source', '')} | {item.get('added_at', '')}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 상세 보기
            for i, item in enumerate(hub):
                with st.expander(f"📌 {item.get('title', f'항목 {i+1}')} 상세"):
                    st.write(f"**출처:** {item.get('source', '')}")
                    
                    if item.get('key_points'):
                        st.markdown("**핵심 포인트:**")
                        for kp in item['key_points']:
                            st.write(f"• {kp}")
                    
                    if item.get('action_items'):
                        st.markdown("**실행 가능한 것:**")
                        for ai in item['action_items']:
                            st.write(f"✅ {ai}")
                    
                    if item.get('ebook_ideas'):
                        st.markdown("**전자책 적용 아이디어:**")
                        for idea in item['ebook_ideas']:
                            st.write(f"💡 {idea}")
                    
                    if item.get('ebook_application'):
                        st.info(f"💡 **적용 방법:** {item['ebook_application']}")
                    
                    if st.button(f"🗑️ 삭제", key=f"del_hub_{i}"):
                        st.session_state['knowledge_hub'].pop(i)
                        st.rerun()
            
            # 전체 인사이트 정리
            if st.button("📋 전체 인사이트 정리", key="compile_insights"):
                all_points = []
                all_ideas = []
                for item in hub:
                    all_points.extend(item.get('key_points', []))
                    all_ideas.extend(item.get('ebook_ideas', []) or [item.get('ebook_application', '')])
                
                st.markdown("### 📊 통합 인사이트")
                st.markdown("**핵심 포인트 모음:**")
                for p in all_points[:10]:
                    st.write(f"• {p}")
                st.markdown("**전자책 아이디어 모음:**")
                for idea in all_ideas[:5]:
                    if idea:
                        st.write(f"💡 {idea}")
        else:
            st.markdown("""
            <div style="text-align: center; padding: 60px 20px; background: #f8f8f8; border-radius: 16px;">
                <p style="font-size: 48px; margin-bottom: 16px;">🧠</p>
                <p style="color: #888888;">학습한 콘텐츠가 여기에 정리됩니다</p>
                <p style="color: #aaaaaa; font-size: 14px;">왼쪽에서 영상이나 아티클을 분석하세요</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<div class="next-btn-container"></div>', unsafe_allow_html=True)
    if st.button("다음 → 목차 설계", key="next_4", use_container_width=True):
        pass


# ==========================================
# TAB 5: 목차 설계
# ==========================================
with tabs[4]:
    st.markdown("## 목차 설계")
    
    # GAP 표시
    if st.session_state.get('market_gaps'):
        st.success(f"✅ 경쟁사 분석에서 발견된 {len(st.session_state['market_gaps'])}개의 시장 빈틈이 목차에 반영됩니다!")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🚀 킬러 목차 생성")
        
        st.markdown("""
        <div class="info-card">
            <div class="info-card-title">💡 자청/프드프 스타일 목차</div>
            <p>• 목차만 봐도 "이거 사야겠다" 느낌</p>
            <p>• 상식 파괴 + 호기심 폭발</p>
            <p>• 경쟁사 GAP 반영</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✨ 킬러 목차 생성하기", key="gen_outline", use_container_width=True):
            if not st.session_state['topic']:
                st.error("주제를 먼저 입력해주세요.")
            elif not get_api_key():
                st.error("API 키를 입력해주세요.")
            else:
                with st.spinner("킬러 목차 생성 중..."):
                    result = generate_killer_outline(
                        st.session_state['topic'],
                        st.session_state['target_persona'],
                        st.session_state['pain_points'],
                        st.session_state.get('market_gaps', [])
                    )
                    
                    if result:
                        # 파싱
                        lines = result.split('\n')
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
                            st.success(f"✅ {len(chapters)}개 챕터 생성 완료!")
                            st.rerun()
        
        # 현재 목차 표시
        if st.session_state.get('outline'):
            st.markdown("### 📋 현재 목차")
            outline_text = ""
            for ch in st.session_state['outline']:
                outline_text += f"## {ch}\n"
                if ch in st.session_state['chapters']:
                    for st_name in st.session_state['chapters'][ch].get('subtopics', []):
                        outline_text += f"- {st_name}\n"
                outline_text += "\n"
            st.code(outline_text, language=None)
    
    with col2:
        st.markdown("### 📝 목차 편집")
        
        if st.session_state.get('outline'):
            for i, chapter in enumerate(st.session_state['outline']):
                subtopics = st.session_state['chapters'].get(chapter, {}).get('subtopics', [])
                with st.expander(f"**{chapter}** ({len(subtopics)}개 소제목)"):
                    # 챕터 편집
                    new_title = st.text_input("챕터 제목", value=chapter, key=f"ch_{i}")
                    if new_title != chapter and new_title.strip():
                        if st.button("저장", key=f"save_ch_{i}"):
                            st.session_state['outline'][i] = new_title
                            if chapter in st.session_state['chapters']:
                                st.session_state['chapters'][new_title] = st.session_state['chapters'].pop(chapter)
                            st.rerun()
                    
                    # 소제목 표시
                    for j, st_name in enumerate(subtopics):
                        st.write(f"{j+1}. {st_name}")
            
            if st.button("➕ 새 챕터 추가", key="add_ch"):
                new_ch = f"PART {len(st.session_state['outline'])+1}. 새 챕터"
                st.session_state['outline'].append(new_ch)
                st.session_state['chapters'][new_ch] = {'subtopics': [], 'subtopic_data': {}}
                st.rerun()
        else:
            st.markdown("""
            <div style="text-align: center; padding: 60px 20px; background: #f8f8f8; border-radius: 16px;">
                <p style="color: #888888;">왼쪽에서 목차를 생성하세요</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<div class="next-btn-container"></div>', unsafe_allow_html=True)
    if st.button("다음 → 본문 작성", key="next_5", use_container_width=True):
        pass


# ==========================================
# TAB 6: 본문 작성
# ==========================================
with tabs[5]:
    st.markdown("## 본문 작성")
    
    if not st.session_state.get('outline'):
        st.warning("⚠️ 먼저 목차를 설계해주세요.")
        st.stop()
    
    selected_chapter = st.selectbox("📚 챕터 선택", st.session_state['outline'], key="ch_select")
    
    if selected_chapter not in st.session_state['chapters']:
        st.session_state['chapters'][selected_chapter] = {'subtopics': [], 'subtopic_data': {}}
    
    chapter_data = st.session_state['chapters'][selected_chapter]
    
    # 소제목 목록
    with st.expander(f"📋 소제목 ({len(chapter_data.get('subtopics', []))}개)", expanded=True):
        for j, st_name in enumerate(chapter_data.get('subtopics', [])):
            has_content = bool(chapter_data.get('subtopic_data', {}).get(st_name, {}).get('content', ''))
            status = "✅" if has_content else "⬜"
            st.write(f"{status} {j+1}. {st_name}")
    
    if chapter_data.get('subtopics'):
        st.markdown("---")
        selected_subtopic = st.selectbox("✍️ 작성할 소제목", chapter_data['subtopics'], key="st_select")
        
        if selected_subtopic not in chapter_data.get('subtopic_data', {}):
            chapter_data['subtopic_data'][selected_subtopic] = {'questions': [], 'answers': [], 'content': ''}
        
        subtopic_data = chapter_data['subtopic_data'][selected_subtopic]
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f"### 🎤 인터뷰")
            if st.button("질문 생성", key="gen_q"):
                with st.spinner("생성 중..."):
                    q_text = generate_interview_questions(selected_subtopic, selected_chapter, st.session_state['topic'])
                    if q_text:
                        questions = re.findall(r'Q\d+:\s*(.+)', q_text)
                        if not questions:
                            questions = [q.strip() for q in q_text.split('\n') if '?' in q][:3]
                        subtopic_data['questions'] = questions
                        subtopic_data['answers'] = [''] * len(questions)
                        st.rerun()
            
            if subtopic_data.get('questions'):
                for i, q in enumerate(subtopic_data['questions']):
                    st.markdown(f"**Q{i+1}.** {q}")
                    if i >= len(subtopic_data['answers']):
                        subtopic_data['answers'].append('')
                    subtopic_data['answers'][i] = st.text_area(f"답변 {i+1}", value=subtopic_data['answers'][i], height=80, key=f"ans_{i}", label_visibility="collapsed")
        
        with col2:
            st.markdown(f"### 📝 본문")
            has_answers = subtopic_data.get('questions') and any(a.strip() for a in subtopic_data.get('answers', []))
            
            if has_answers:
                if st.button("✨ 본문 생성", key="gen_content"):
                    with st.spinner("집필 중... (30초~1분)"):
                        content = generate_subtopic_content(
                            selected_subtopic, selected_chapter,
                            subtopic_data['questions'], subtopic_data['answers'],
                            st.session_state['topic'], st.session_state['target_persona']
                        )
                        if content:
                            subtopic_data['content'] = content
                            st.rerun()
            
            edited_content = st.text_area("본문 편집", value=subtopic_data.get('content', ''), height=400, key="content_edit", label_visibility="collapsed")
            subtopic_data['content'] = edited_content
            
            if edited_content:
                st.caption(f"📊 {calculate_char_count(edited_content):,}자")
    
    st.markdown('<div class="next-btn-container"></div>', unsafe_allow_html=True)
    if st.button("다음 → 최종 출력", key="next_6", use_container_width=True):
        pass


# ==========================================
# TAB 7: 최종 출력
# ==========================================
with tabs[6]:
    st.markdown("## 최종 출력")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown("### 📖 전자책 다운로드")
        
        book_title = st.text_input("제목", value=st.session_state.get('book_title', ''), key="dl_title")
        subtitle = st.text_input("부제", value=st.session_state.get('subtitle', ''), key="dl_subtitle")
        
        # 전체 내용 생성
        full_text = ""
        if book_title:
            full_text += f"{book_title}\n"
        if subtitle:
            full_text += f"{subtitle}\n"
        full_text += "\n" + "="*50 + "\n\n"
        
        for chapter in st.session_state.get('outline', []):
            if chapter in st.session_state.get('chapters', {}):
                ch_data = st.session_state['chapters'][chapter]
                has_content = any(ch_data.get('subtopic_data', {}).get(st, {}).get('content') for st in ch_data.get('subtopics', []))
                if has_content:
                    full_text += f"\n{chapter}\n" + "-"*40 + "\n\n"
                    for st_name in ch_data.get('subtopics', []):
                        st_data = ch_data.get('subtopic_data', {}).get(st_name, {})
                        if st_data.get('content'):
                            full_text += f"\n{st_name}\n\n{st_data['content']}\n\n"
        
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button("📄 TXT 다운로드", full_text, file_name=f"{book_title or 'ebook'}.txt", use_container_width=True)
        with col_dl2:
            html = f"<html><head><meta charset='utf-8'><title>{book_title}</title></head><body style='max-width:800px;margin:0 auto;padding:40px;font-family:sans-serif;'>{full_text.replace(chr(10), '<br>')}</body></html>"
            st.download_button("🌐 HTML 다운로드", html, file_name=f"{book_title or 'ebook'}.html", use_container_width=True)
        
        # 통계
        pure_content = get_all_content_text()
        if pure_content:
            total_chars = calculate_char_count(pure_content)
            st.success(f"✅ 총 {total_chars:,}자 | 약 {total_chars//500}페이지")
    
    with col2:
        st.markdown("### 📊 작성 현황")
        
        total_subtopics = sum(len(ch.get('subtopics', [])) for ch in st.session_state.get('chapters', {}).values())
        completed = sum(1 for ch in st.session_state.get('chapters', {}).values() for st in ch.get('subtopic_data', {}).values() if st.get('content'))
        
        if total_subtopics > 0:
            progress = completed / total_subtopics
            st.progress(progress)
            st.write(f"**완료:** {completed}/{total_subtopics} 소제목")
        
        # 미완성 목록
        incomplete = []
        for ch in st.session_state.get('outline', []):
            if ch in st.session_state.get('chapters', {}):
                ch_data = st.session_state['chapters'][ch]
                for st_name in ch_data.get('subtopics', []):
                    if not ch_data.get('subtopic_data', {}).get(st_name, {}).get('content'):
                        incomplete.append(f"{ch} > {st_name}")
        
        if incomplete:
            with st.expander(f"⚠️ 미완성 ({len(incomplete)}개)"):
                for item in incomplete[:10]:
                    st.write(f"• {item}")


# --- 푸터 ---
st.markdown('<div class="premium-footer"><span style="color: #888888;">전자책 작성 프로그램 — </span><span style="color: #222222; font-weight: 600;">남현우 작가</span></div>', unsafe_allow_html=True)
