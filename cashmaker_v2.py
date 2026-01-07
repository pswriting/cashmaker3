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

st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif; }
    .stDeployButton, footer, #MainMenu {display:none;}
    .stApp { background: #fff; }
    .main .block-container { padding: 2rem 3rem; max-width: 1400px; }
    [data-testid="stSidebar"] { background: #fff; border-right: 1px solid #eee; }
    .stButton > button { width: 100%; border-radius: 30px; font-weight: 600; background: #111 !important; color: #fff !important; border: none !important; padding: 14px 32px; }
    .stButton > button:hover { background: #333 !important; }
    .score-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; padding: 40px; text-align: center; color: white; }
    .score-number { font-size: 72px; font-weight: 800; }
    .info-card { background: #f8f8f8; border-radius: 16px; padding: 20px; margin: 12px 0; }
    .gap-report { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 20px; padding: 24px; color: white; margin: 16px 0; }
    .gap-item { background: rgba(255,255,255,0.2); border-radius: 12px; padding: 16px; margin: 10px 0; }
    .stat-box { background: #111; border-radius: 12px; padding: 16px; margin: 8px 0; color: white; text-align: center; }
    .stat-value { font-size: 24px; font-weight: 800; color: #4ade80; }
    .stat-label { font-size: 12px; color: #aaa; }
    .verdict-go { background: #4ade80; color: #000; padding: 10px 30px; border-radius: 30px; font-weight: 700; display: inline-block; }
    .verdict-wait { background: #fbbf24; color: #000; padding: 10px 30px; border-radius: 30px; font-weight: 700; display: inline-block; }
    .verdict-no { background: #f87171; color: #fff; padding: 10px 30px; border-radius: 30px; font-weight: 700; display: inline-block; }
    .summary-hub { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; padding: 20px; color: white; margin: 16px 0; }
    .data-card { background: #e0f2fe; border-left: 4px solid #0284c7; border-radius: 8px; padding: 16px; margin: 10px 0; }
    .news-card { background: #fff7ed; border-left: 4px solid #f97316; border-radius: 8px; padding: 16px; margin: 10px 0; }
    .next-section { margin-top: 40px; padding-top: 20px; border-top: 2px solid #eee; }
    .full-content-box { background: #fafafa; border: 1px solid #e0e0e0; border-radius: 12px; padding: 24px; margin: 16px 0; white-space: pre-wrap; line-height: 1.8; }
</style>
""", unsafe_allow_html=True)

# 인증
CORRECT_PASSWORD = "cashmaker2024"
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown('<div style="max-width:400px;margin:100px auto;padding:40px;background:#fff;border:1px solid #eee;border-radius:20px;text-align:center;"><div style="font-size:28px;font-weight:700;">CASHMAKER</div><div style="font-size:15px;color:#888;margin-top:8px;">전자책 작성 프로그램</div></div>', unsafe_allow_html=True)
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
    'topic': '', 'target_persona': '', 'pain_points': '', 'one_line_concept': '',
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
    st.markdown("### 진행 상황")
    progress = sum([bool(st.session_state['topic']), bool(st.session_state['target_persona']), bool(st.session_state['outline']), len(st.session_state['chapters']) > 0]) / 4
    st.progress(progress)
    
    st.markdown("---")
    st.markdown("### API 설정")
    if 'api_key' not in st.session_state:
        st.session_state['api_key'] = load_saved_api_key()
    
    api_key = st.text_input("Gemini API 키", value=st.session_state['api_key'], type="password", key="api_sidebar")
    if api_key != st.session_state['api_key']:
        st.session_state['api_key'] = api_key
        save_api_key(api_key)
    
    st.markdown("---")
    st.markdown("### 빠른 이동")
    pages = ["① 주제 & 시장분석", "② 타겟 & 컨셉", "③ 경쟁도서 분석", "④ 실력 키우기", "⑤ 목차 설계", "⑥ 본문 작성", "⑦ 최종 출력"]
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
    text = re.sub(r'「질문\d*[:\s][^」]*」', '', text)
    text = re.sub(r'Q\d+[:\s][^\n]*\n?', '', text)
    text = re.sub(r'질문\d*[:\s][^\n]*\n?', '', text)
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

이 주제로 전자책 시장을 분석해주세요. 구체적인 데이터를 포함해주세요.

JSON:
{{
    "verdict": "강력 추천/추천/보류/비추천",
    "verdict_reason": "판정 이유",
    "total_score": 85,
    "search_data": {{
        "naver_monthly": "네이버 월간 검색량 (예: 12,000회)",
        "google_monthly": "구글 월간 검색량 (예: 8,500회)",
        "naver_blog_posts": "네이버 블로그 게시물 수",
        "youtube_videos": "유튜브 관련 영상 수",
        "search_trend": "상승/유지/하락"
    }},
    "market_size": {{
        "score": 85,
        "level": "매우 큼/큼/보통/작음",
        "kmong_products": "크몽 관련 상품 수",
        "class101_courses": "클래스101 강의 수",
        "yes24_books": "yes24 도서 수",
        "estimated_market": "추정 시장 규모",
        "analysis": "분석 2문장"
    }},
    "trends": {{
        "hot_keywords": ["키워드1", "키워드2", "키워드3"],
        "news_summary": "최근 뉴스/트렌드 2문장",
        "future_outlook": "향후 전망 1문장"
    }},
    "competition": {{
        "score": 70,
        "level": "치열함/보통/낮음",
        "your_opportunity": "차별화 기회",
        "analysis": "경쟁 분석 2문장"
    }},
    "profit": {{
        "score": 80,
        "price_range": "권장 가격대",
        "monthly_revenue": "예상 월 수익"
    }},
    "timing": {{
        "score": 75,
        "status": "지금이 적기/좋음/보통",
        "why_now": "지금 진입 이유"
    }},
    "recommendation": "최종 권장 2문장"
}}"""
    return ask_ai(prompt, 0.5)


def suggest_targets(topic):
    prompt = f"""주제: {topic}

구매 가능성 높은 타겟 5개:

JSON:
{{
    "personas": [
        {{
            "name": "타겟 이름",
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
    """심층 타겟 고민 분석"""
    prompt = f"""주제: {topic}
타겟: {persona}

이 타겟의 고민을 아주 깊이 분석해주세요. 
표면적인 것뿐 아니라, 말은 안 하지만 속으로 생각하는 진짜 고민까지 파헤쳐주세요.
마치 이 사람의 마음속을 들여다보는 것처럼 구체적으로 분석해주세요.

JSON:
{{
    "surface_pains": {{
        "pains": ["표면적 고민1 (구체적으로)", "고민2", "고민3", "고민4", "고민5"],
        "description": "이들이 겉으로 드러내는 고민에 대한 상세 설명. 어떤 상황에서 이런 고민을 느끼는지, 누구에게 이런 말을 하는지 구체적으로 3문장 이상."
    }},
    "hidden_pains": {{
        "pains": ["숨겨진 진짜 고민1 (말은 안 하지만 속으로 생각하는 것)", "고민2", "고민3", "고민4"],
        "description": "이들이 입 밖으로 꺼내지 않는 진짜 속마음. 밤에 혼자 있을 때 드는 생각, 남들에게는 절대 말 못하는 고민. 3문장 이상 구체적으로."
    }},
    "emotional_pains": {{
        "pains": ["감정적 고통1 (구체적 감정)", "고통2", "고통3", "고통4"],
        "emotions": ["두려움", "불안", "좌절감", "열등감"],
        "description": "이 고민으로 인해 느끼는 감정들. 언제 이런 감정을 느끼는지, 어떤 상황에서 가장 힘든지. 3문장 이상."
    }},
    "failed_attempts": {{
        "attempts": ["시도했지만 실패한 것1", "것2", "것3", "것4"],
        "why_failed": "왜 기존 방법들이 실패했는지, 무엇이 부족했는지 구체적으로 3문장 이상",
        "frustration": "실패 후 느끼는 좌절감과 회의감"
    }},
    "dream_outcome": {{
        "ideal_result": "이들이 꿈꾸는 이상적인 결과 (아주 구체적으로)",
        "timeline": "원하는 기간",
        "fantasy": "이루면 어떤 삶을 살고 싶은지 상상",
        "what_changes": "이루면 무엇이 달라지는지. 일상의 변화, 주변 반응, 자신감 등 3문장 이상"
    }},
    "buying_triggers": {{
        "triggers": ["구매 결정 요인1", "요인2", "요인3"],
        "objections": ["구매 망설임 이유1", "이유2", "이유3"],
        "price_sensitivity": "가격 민감도와 지불 의향",
        "decision_process": "구매 결정까지의 과정. 어떤 정보를 찾아보는지, 누구와 상의하는지. 3문장 이상"
    }},
    "content_needs": {{
        "must_include": ["반드시 포함해야 독자가 만족할 내용1", "내용2", "내용3", "내용4"],
        "avoid": ["넣으면 안 되는 것1 (이유와 함께)", "것2", "것3"],
        "tone": "선호하는 말투와 분위기",
        "format": "선호하는 콘텐츠 형식 (사례 중심? 이론 중심? 실습 중심?)"
    }},
    "one_line_summary": "이 타겟을 한 문장으로 정의하면",
    "marketing_hook": "이 타겟의 마음을 단번에 사로잡을 수 있는 한 마디"
}}"""
    return ask_ai(prompt, 0.6)


def analyze_competitor_reviews(topic):
    """경쟁 도서 부정 리뷰 심층 분석 - 숨은 니즈 발굴"""
    prompt = f"""주제: {topic}

크몽, yes24, 알라딘, 교보문고에서 이 주제 관련 전자책/도서의 「부정적인 리뷰」를 집중 분석해주세요.

독자들이 기존 책에서 불만족한 점, 아쉬웠던 점, 화났던 점을 파악해서
새로운 전자책의 차별화 포인트와 컨셉을 잡을 수 있도록 해주세요.

특히 「숨겨진 니즈」를 찾는 것이 핵심입니다.
독자들이 직접 말하지 않았지만, 리뷰 속에 숨어있는 진짜 원하는 것을 찾아주세요.

JSON:
{{
    "analysis_scope": {{
        "books_analyzed": "분석 도서 수 (예: 287권)",
        "reviews_analyzed": "분석 리뷰 수 (예: 3,842개)",
        "negative_reviews": "부정 리뷰 수와 비율 (예: 892개, 23%)",
        "platforms": ["크몽", "yes24", "알라딘", "교보문고"]
    }},
    "negative_patterns": [
        {{
            "pattern": "불만 패턴 (예: 실전 사례가 너무 부족함)",
            "frequency": "빈도 (예: 67%)",
            "example_reviews": [
                "실제 부정 리뷰 예시 1 - 구체적이고 현실적으로",
                "실제 부정 리뷰 예시 2"
            ],
            "reader_emotion": "이 불만을 느끼는 독자의 감정 상태",
            "hidden_need": "이 불만 뒤에 숨겨진 진짜 니즈",
            "solution": "이걸 어떻게 해결하면 좋을지 구체적 방안"
        }},
        {{
            "pattern": "두 번째 불만 패턴",
            "frequency": "빈도",
            "example_reviews": ["리뷰1", "리뷰2"],
            "reader_emotion": "감정",
            "hidden_need": "숨겨진 니즈",
            "solution": "해결책"
        }},
        {{
            "pattern": "세 번째 불만 패턴",
            "frequency": "빈도",
            "example_reviews": ["리뷰1", "리뷰2"],
            "reader_emotion": "감정",
            "hidden_need": "숨겨진 니즈",
            "solution": "해결책"
        }},
        {{
            "pattern": "네 번째 불만 패턴",
            "frequency": "빈도",
            "example_reviews": ["리뷰1", "리뷰2"],
            "reader_emotion": "감정",
            "hidden_need": "숨겨진 니즈",
            "solution": "해결책"
        }},
        {{
            "pattern": "다섯 번째 불만 패턴",
            "frequency": "빈도",
            "example_reviews": ["리뷰1", "리뷰2"],
            "reader_emotion": "감정",
            "hidden_need": "숨겨진 니즈",
            "solution": "해결책"
        }}
    ],
    "hidden_needs_summary": {{
        "needs": [
            "숨겨진 니즈 1 - 독자들이 직접 말하지 않았지만 원하는 것",
            "숨겨진 니즈 2",
            "숨겨진 니즈 3",
            "숨겨진 니즈 4",
            "숨겨진 니즈 5"
        ],
        "insight": "이 니즈들을 종합했을 때 알 수 있는 핵심 인사이트 2문장"
    }},
    "concept_suggestions": [
        {{
            "concept": "차별화 컨셉 1 (구체적이고 매력적으로)",
            "why_works": "왜 이 컨셉이 통할지 2문장",
            "target_pain": "해결하는 핵심 고민",
            "unique_point": "기존 책과 다른 점"
        }},
        {{
            "concept": "차별화 컨셉 2",
            "why_works": "이유",
            "target_pain": "해결 고민",
            "unique_point": "차별점"
        }},
        {{
            "concept": "차별화 컨셉 3",
            "why_works": "이유",
            "target_pain": "해결 고민",
            "unique_point": "차별점"
        }}
    ],
    "success_formula": {{
        "must_have": ["반드시 포함할 것1", "것2", "것3", "것4", "것5"],
        "must_avoid": ["절대 하면 안 되는 것1", "것2", "것3"],
        "differentiation": "최종 차별화 전략 3문장"
    }},
    "recommended_angle": "이 분석을 바탕으로 추천하는 전자책 컨셉/각도 3문장"
}}"""
    return ask_ai(prompt, 0.6)


def generate_titles(topic, persona, pains):
    prompt = f"""주제: {topic}
타겟: {persona}
고민: {pains}

베스트셀러급 제목 5개:

JSON:
{{
    "titles": [
        {{"title": "제목", "subtitle": "부제", "why_works": "이유"}}
    ]
}}"""
    return ask_ai(prompt, 0.9)


def analyze_youtube_with_gemini(url):
    """Gemini 2.0 Flash를 활용한 유튜브 영상 직접 분석"""
    api_key = get_api_key()
    if not api_key:
        return None
    
    try:
        genai.configure(api_key=api_key)
        # Gemini 2.0 Flash는 유튜브 URL을 직접 처리 가능
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        
        prompt = f"""다음 유튜브 영상의 내용을 상세히 분석하고 요약해주세요.

유튜브 URL: {url}

영상의 실제 내용을 바탕으로 다음 정보를 추출해주세요:

JSON:
{{
    "title": "영상 제목",
    "creator": "크리에이터/채널명",
    "duration": "영상 길이 (추정)",
    "main_topic": "메인 주제 한 줄 요약",
    "key_points": [
        "핵심 포인트 1 - 영상에서 실제로 말한 내용 기반으로 구체적으로",
        "핵심 포인트 2",
        "핵심 포인트 3",
        "핵심 포인트 4",
        "핵심 포인트 5",
        "핵심 포인트 6",
        "핵심 포인트 7"
    ],
    "actionable_tips": [
        "바로 실행할 수 있는 팁 1",
        "팁 2",
        "팁 3",
        "팁 4"
    ],
    "memorable_quotes": [
        "영상에서 인상적이었던 말 1",
        "말 2"
    ],
    "ebook_applications": [
        "전자책에 활용할 수 있는 포인트 1",
        "포인트 2",
        "포인트 3"
    ],
    "chapter_ideas": [
        "이 내용으로 만들 수 있는 챕터 아이디어 1",
        "아이디어 2"
    ],
    "summary": "영상 전체 내용 요약 5문장 이상. 영상의 핵심 메시지와 주요 내용을 상세히."
}}"""
        
        config = genai.types.GenerationConfig(temperature=0.3, max_output_tokens=4000)
        response = model.generate_content(prompt, generation_config=config)
        return response.text
    except Exception as e:
        st.error(f"유튜브 분석 오류: {e}")
        return None


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


def summarize_knowledge(items):
    if not items:
        return None
    
    all_points = []
    all_ideas = []
    for item in items:
        if isinstance(item, dict):
            all_points.extend(item.get('key_points', []))
            all_ideas.extend(item.get('ebook_applications', item.get('ebook_ideas', [])))
    
    prompt = f"""학습 정보 종합:

포인트들: {chr(10).join([f"• {p}" for p in all_points[:20]])}
아이디어들: {chr(10).join([f"• {i}" for i in all_ideas[:10]])}

JSON:
{{
    "total_summary": "종합 요약 5문장",
    "top_insights": ["인사이트1", "인사이트2", "인사이트3", "인사이트4", "인사이트5"],
    "recommended_outline": ["목차1", "목차2", "목차3", "목차4"],
    "study_plan": {{
        "week1": "1주차",
        "week2": "2주차",
        "week3": "3주차",
        "week4": "4주차"
    }}
}}"""
    return ask_ai(prompt, 0.6)


def generate_outline(topic, persona, pains, gaps=None):
    gaps_text = ""
    if gaps:
        gaps_text = f"\n차별화: " + ", ".join(gaps[:3])
    
    prompt = f"""주제: {topic}
타겟: {persona}
고민: {pains}
{gaps_text}

전자책 목차를 만들어주세요.

[핵심]
목차만 봐도 "이거 뭐야? 당장 읽고 싶다!" 느낌

[좋은 목차 예시]
- "월급 250만원으로 3년 만에 1억 모은 통장 쪼개기"
- "퇴사하고 6개월, 오히려 월급의 3배를 벌게 된 이유"  
- "나는 왜 10년간 투자하고도 월 50만원밖에 못 벌었나"
- "주식으로 2000만원 날린 후 깨달은 것들"
- "회사 다니면서 투잡으로 월 500 버는 현실적인 구조"

[금지 표현]
- "~의 중요성", "~하는 방법", "~의 기초"
- "마법", "비밀", "필승", "완벽한"
- "99%가 모르는", "숨겨진 진실"

출력:

PART 1. [제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]

PART 2. [제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]

PART 3. [제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]

PART 4. [제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]"""
    return ask_ai(prompt, 0.9)


def generate_content_premium(subtopic, chapter, questions, answers, topic, persona):
    """자청 스타일 본문 생성 - 몰입감 있게"""
    qa = "\n".join([f"내용{i+1}: {a}" for i, (q, a) in enumerate(zip(questions, answers)) if a.strip()])
    
    prompt = f"""주제: {topic}
챕터: {chapter}
소제목: {subtopic}
타겟: {persona}

참고 내용: {qa}

[글쓰기 스타일 - 독자가 빠져들게]

당신은 베스트셀러 작가입니다. 
독자가 읽다가 멈출 수 없을 정도로 몰입감 있는 글을 써주세요.

1. 「첫 문장」에서 확 잡아당기기
   - "솔직히 말할게요."
   - "저도 처음엔 몰랐습니다."
   - "여기서 중요한 건 따로 있어요."
   - "그때 저는 완전히 틀렸습니다."

2. 「짧은 문장」으로 리듬감 있게
   - 한 문장에 하나의 생각만
   - 긴 문장 다음엔 짧은 문장
   - 강조할 땐 더 짧게. 이렇게.

3. 「독자와 대화」하듯이
   - "~하신 적 있으시죠?"
   - "아마 이렇게 생각하실 겁니다."
   - "근데요, 진짜는 따로 있어요."
   - "여기서 반전이 있습니다."

4. 「구체적인 숫자와 사례」로 신뢰감
   - 추상적인 말 대신 구체적 예시
   - "많이 벌었다" → "월 347만원을 벌었습니다"
   - 실제 경험담처럼 생생하게

5. 「감정을 건드리는」 흐름
   - 공감 → 문제 제기 → 반전 → 해결책 → 희망
   - 독자가 "어, 이거 내 얘기잖아" 싶게

6. 「긴장감」 유지하기
   - "근데 여기서 문제가 생겼습니다."
   - "그런데 말입니다."
   - "아직 끝이 아닙니다."

[절대 금지]
- 마크다운 기호(#, **, *) 사용 금지
- "~의 중요성", "~하는 방법" 같은 딱딱한 표현
- 질문 형태 그대로 넣지 말 것
- AI스러운 어색한 표현
- 너무 교과서적인 설명

[분량] 1800~2200자

'{subtopic}' 본문을 작성해주세요.
제목 없이 바로 본문부터 시작합니다.
독자가 읽다가 멈출 수 없게 써주세요."""
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
st.markdown('<div style="text-align:center;padding:20px;"><div style="font-size:13px;color:#666;letter-spacing:3px;">CASHMAKER</div><div style="font-size:32px;font-weight:800;color:#111;">전자책 작성 프로그램</div></div>', unsafe_allow_html=True)

# 페이지 네비게이션
pages = ["① 주제 & 시장분석", "② 타겟 & 컨셉", "③ 경쟁도서 분석", "④ 실력 키우기", "⑤ 목차 설계", "⑥ 본문 작성", "⑦ 최종 출력"]
current = st.session_state['current_page']

cols = st.columns(7)
for i, (col, page) in enumerate(zip(cols, pages)):
    with col:
        if i == current:
            st.markdown(f'<div style="text-align:center;padding:8px;background:#111;color:#fff;border-radius:8px;font-size:11px;">{page}</div>', unsafe_allow_html=True)
        else:
            if st.button(page, key=f"nav_{i}", use_container_width=True):
                st.session_state['current_page'] = i
                st.rerun()

st.markdown("---")


# ==========================================
# PAGE 0: 주제 & 시장분석
# ==========================================
if current == 0:
    st.markdown("## 주제 선정 & 시장 분석")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 주제 입력")
        topic = st.text_input("어떤 주제로 전자책을 쓸까요?", value=st.session_state['topic'], placeholder="예: 주식 배당으로 월 100만원", key="p0_topic")
        if topic != st.session_state['topic']:
            st.session_state['topic'] = topic
            st.session_state['score_details'] = None
        
        st.markdown("""
        <div class="info-card">
            <b>💡 좋은 주제의 조건</b><br>
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
                <div style="font-size:14px;opacity:0.9;">종합 점수</div>
                <div style="margin-top:20px;"><span class="{v_class}">{verdict}</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**📢 {d.get('verdict_reason', '')}**")
            
            sd = d.get('search_data', {})
            if sd:
                st.markdown(f"""
                <div class="data-card">
                    <b>📊 검색 데이터</b><br>
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
            
            st.success(f"**💡 최종:** {d.get('recommendation', '')}")
        else:
            st.markdown('<div style="text-align:center;padding:60px;background:#f8f8f8;border-radius:16px;"><p style="color:#888;">주제를 입력하고 분석해주세요</p></div>', unsafe_allow_html=True)
    
    # 다음 버튼
    st.markdown('<div class="next-section"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("다음 → 타겟 & 컨셉", key="p0_next", use_container_width=True):
            go_next()
            st.rerun()


# ==========================================
# PAGE 1: 타겟 & 컨셉
# ==========================================
elif current == 1:
    st.markdown("## 타겟 설정 & 제목 생성")
    
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
        persona = st.text_area("직접 입력:", value=st.session_state['target_persona'], height=60, key="p1_persona")
        st.session_state['target_persona'] = persona
        
        if persona and st.button("🔍 독자 고민 심층 분석", key="p1_analyze"):
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
                st.caption(p.get('surface_pains', {}).get('description', ''))
            
            with st.expander("🔍 숨겨진 진짜 고민", expanded=True):
                for pain in p.get('hidden_pains', {}).get('pains', []):
                    st.write(f"• {pain}")
                st.caption(p.get('hidden_pains', {}).get('description', ''))
            
            with st.expander("💔 감정적 고통", expanded=False):
                for pain in p.get('emotional_pains', {}).get('pains', []):
                    st.write(f"• {pain}")
                st.caption(p.get('emotional_pains', {}).get('description', ''))
            
            with st.expander("❌ 시도했지만 실패한 것들", expanded=False):
                fa = p.get('failed_attempts', {})
                for a in fa.get('attempts', []):
                    st.write(f"• {a}")
                st.caption(fa.get('why_failed', ''))
            
            with st.expander("🌟 꿈꾸는 결과", expanded=False):
                dr = p.get('dream_outcome', {})
                st.write(f"**이상적 결과:** {dr.get('ideal_result', '')}")
                st.write(f"**원하는 기간:** {dr.get('timeline', '')}")
                st.caption(dr.get('what_changes', ''))
            
            with st.expander("💰 구매 결정 요인", expanded=False):
                bt = p.get('buying_triggers', {})
                st.write("**구매 요인:**")
                for t in bt.get('triggers', []):
                    st.write(f"✅ {t}")
                st.write("**망설임 이유:**")
                for o in bt.get('objections', []):
                    st.write(f"❓ {o}")
            
            if p.get('marketing_hook'):
                st.info(f"🎯 **마케팅 훅:** {p.get('marketing_hook', '')}")
    
    with col2:
        st.markdown("### 제목 & 컨셉")
        
        pain_points = st.text_area("독자의 고민:", value=st.session_state['pain_points'], height=60, key="p1_pains")
        st.session_state['pain_points'] = pain_points
        
        if st.button("✨ 제목 생성", key="p1_title"):
            if st.session_state['topic']:
                with st.spinner("생성 중..."):
                    r = generate_titles(st.session_state['topic'], st.session_state['target_persona'], st.session_state['pain_points'])
                    parsed = parse_json(r)
                    if parsed:
                        st.session_state['generated_titles'] = parsed
                        st.rerun()
        
        if st.session_state.get('generated_titles'):
            for t in st.session_state['generated_titles'].get('titles', [])[:5]:
                st.markdown(f"""
                <div class="info-card">
                    <div style="font-size:18px;font-weight:700;">{t.get('title', '')}</div>
                    <div style="color:#666;">{t.get('subtitle', '')}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.session_state['book_title'] = st.text_input("최종 제목", value=st.session_state['book_title'], key="p1_book_title")
        st.session_state['subtitle'] = st.text_input("부제", value=st.session_state['subtitle'], key="p1_subtitle")
    
    # 다음/이전 버튼
    st.markdown('<div class="next-section"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("← 이전", key="p1_prev", use_container_width=True):
            go_prev()
            st.rerun()
    with c3:
        if st.button("다음 → 경쟁도서 분석", key="p1_next", use_container_width=True):
            go_next()
            st.rerun()


# ==========================================
# PAGE 2: 경쟁도서 분석
# ==========================================
elif current == 2:
    st.markdown("## 경쟁 도서 분석")
    st.markdown("**🔥 기존 도서의 부정적 리뷰를 분석해서 숨은 니즈와 차별화 포인트를 찾습니다**")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🤖 부정 리뷰 분석")
        
        st.markdown("""
        <div class="info-card">
            <b>📊 분석 내용</b><br>
            • 경쟁 도서 부정 리뷰 집중 분석<br>
            • 독자들의 불만 패턴 파악<br>
            • 숨겨진 니즈 발굴<br>
            • 차별화 컨셉 제안
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 경쟁 도서 분석하기", use_container_width=True, key="p2_analyze"):
            if not st.session_state['topic']:
                st.error("주제를 먼저 입력해주세요")
            elif not get_api_key():
                st.error("API 키를 입력해주세요")
            else:
                with st.spinner("경쟁 도서 부정 리뷰 분석 중..."):
                    result = analyze_competitor_reviews(st.session_state['topic'])
                    parsed = parse_json(result)
                    if parsed:
                        st.session_state['review_analysis'] = parsed
                        concepts = parsed.get('concept_suggestions', [])
                        st.session_state['market_gaps'] = [c.get('concept', '') for c in concepts]
                        st.success("✅ 분석 완료!")
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
        st.markdown("### 📊 분석 결과")
        
        if st.session_state.get('review_analysis'):
            a = st.session_state['review_analysis']
            
            # 불만 패턴
            patterns = a.get('negative_patterns', [])
            if patterns:
                st.markdown("#### 😤 독자 불만 TOP 5")
                for i, p in enumerate(patterns[:5], 1):
                    with st.expander(f"**{i}. {p.get('pattern', '')}** ({p.get('frequency', '')})", expanded=i<=2):
                        st.write("**실제 리뷰:**")
                        for rev in p.get('example_reviews', []):
                            st.caption(f'"{rev}"')
                        st.write(f"**독자 감정:** {p.get('reader_emotion', '')}")
                        st.info(f"🔍 **숨겨진 니즈:** {p.get('hidden_need', '')}")
                        st.success(f"💡 **해결책:** {p.get('solution', '')}")
            
            # 숨겨진 니즈 요약
            hidden = a.get('hidden_needs_summary', {})
            if hidden:
                st.markdown("#### 🔍 숨겨진 니즈 TOP 5")
                for n in hidden.get('needs', []):
                    st.write(f"• {n}")
                if hidden.get('insight'):
                    st.info(f"💡 {hidden.get('insight', '')}")
            
            # 컨셉 제안
            concepts = a.get('concept_suggestions', [])
            if concepts:
                st.markdown("#### 🎯 차별화 컨셉 제안")
                for c in concepts:
                    st.markdown(f"""
                    <div class="info-card">
                        <b>「{c.get('concept', '')}」</b><br>
                        <span style="color:#666;">{c.get('why_works', '')}</span><br>
                        <span style="color:#4ade80;">✅ 차별점: {c.get('unique_point', '')}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            # 성공 공식
            formula = a.get('success_formula', {})
            if formula:
                with st.expander("✅ 성공 공식", expanded=True):
                    st.write("**반드시 포함:**")
                    for m in formula.get('must_have', []):
                        st.write(f"✅ {m}")
                    st.write("**절대 금지:**")
                    for m in formula.get('must_avoid', []):
                        st.write(f"❌ {m}")
                    st.success(f"💡 {formula.get('differentiation', '')}")
            
            # 추천 각도
            if a.get('recommended_angle'):
                st.markdown("#### 🚀 추천 컨셉")
                st.success(a.get('recommended_angle', ''))
        else:
            st.markdown('<div style="text-align:center;padding:60px;background:#f8f8f8;border-radius:16px;"><p style="color:#888;">분석 버튼을 눌러주세요</p></div>', unsafe_allow_html=True)
    
    # 다음/이전 버튼
    st.markdown('<div class="next-section"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("← 이전", key="p2_prev", use_container_width=True):
            go_prev()
            st.rerun()
    with c3:
        if st.button("다음 → 실력 키우기", key="p2_next", use_container_width=True):
            go_next()
            st.rerun()


# ==========================================
# PAGE 3: 실력 키우기
# ==========================================
elif current == 3:
    st.markdown("## 실력 키우기")
    st.markdown("**📚 유튜브 영상이나 텍스트를 분석하고 정보를 모아보세요**")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📺 콘텐츠 추가")
        
        input_type = st.radio("입력 유형", ["유튜브 URL", "텍스트"], horizontal=True, key="p3_type")
        
        if input_type == "유튜브 URL":
            youtube_url = st.text_input("유튜브 URL", placeholder="https://youtube.com/watch?v=...", key="p3_url")
            st.caption("💡 Gemini 2.0 Flash가 영상 내용을 직접 분석합니다")
            
            if st.button("🎬 영상 분석 & 추가", use_container_width=True, key="p3_yt"):
                if youtube_url and ('youtube.com' in youtube_url or 'youtu.be' in youtube_url):
                    with st.spinner("Gemini로 유튜브 영상 분석 중..."):
                        result = analyze_youtube_with_gemini(youtube_url)
                        parsed = parse_json(result)
                        if parsed:
                            parsed['source'] = youtube_url
                            parsed['type'] = 'youtube'
                            parsed['added_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                            st.session_state['knowledge_hub'].append(parsed)
                            st.success("✅ 추가됨!")
                            st.rerun()
                        else:
                            st.error("분석 실패. URL을 확인해주세요.")
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
                    
                    if item.get('actionable_tips'):
                        st.write("**💡 실행 팁:**")
                        for tip in item.get('actionable_tips', []):
                            st.write(f"• {tip}")
                    
                    if item.get('summary'):
                        st.info(f"📝 {item['summary']}")
                    
                    if st.button("🗑️ 삭제", key=f"p3_del_{i}"):
                        st.session_state['knowledge_hub'].pop(i)
                        st.rerun()
            
            st.markdown("---")
            if st.button("📋 전체 정보 종합 요약", use_container_width=True, key="p3_summary"):
                with st.spinner("종합 분석 중..."):
                    result = summarize_knowledge(hub)
                    parsed = parse_json(result)
                    if parsed:
                        st.session_state['study_summary'] = parsed
                        st.rerun()
            
            if st.session_state.get('study_summary'):
                s = st.session_state['study_summary']
                st.markdown(f'<div class="summary-hub"><b>📊 종합 정리</b><br>{s.get("total_summary", "")}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center;padding:60px;background:#f8f8f8;border-radius:16px;"><p style="color:#888;">유튜브 URL이나 텍스트를 추가해보세요</p></div>', unsafe_allow_html=True)
    
    # 다음/이전 버튼
    st.markdown('<div class="next-section"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("← 이전", key="p3_prev", use_container_width=True):
            go_prev()
            st.rerun()
    with c3:
        if st.button("다음 → 목차 설계", key="p3_next", use_container_width=True):
            go_next()
            st.rerun()


# ==========================================
# PAGE 4: 목차 설계
# ==========================================
elif current == 4:
    st.markdown("## 목차 설계")
    
    if st.session_state.get('market_gaps'):
        st.success(f"✅ {len(st.session_state['market_gaps'])}개 차별화 포인트 반영")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🚀 목차 생성")
        
        st.markdown("""
        <div class="info-card">
            <b>💡 목차 작성 팁</b><br>
            • 목차만 봐도 "이거 뭐지?" 궁금하게<br>
            • 구체적인 숫자와 결과<br>
            • "나도 할 수 있겠다" 느낌
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✨ 혹하는 목차 생성", use_container_width=True, key="p4_outline"):
            if not st.session_state['topic']:
                st.error("주제를 입력하세요")
            else:
                with st.spinner("목차 생성 중..."):
                    result = generate_outline(
                        st.session_state['topic'],
                        st.session_state['target_persona'],
                        st.session_state['pain_points'],
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
                            if line.upper().startswith('PART'):
                                name = line.replace('#', '').strip()
                                name = re.sub(r'\*\*(.+?)\*\*', r'\1', name)
                                if name:
                                    current_ch = name
                                    chapters.append(current_ch)
                                    subtopics[current_ch] = []
                            elif current_ch and line.startswith('-'):
                                st_name = line.lstrip('- ').strip()
                                st_name = re.sub(r'\*\*(.+?)\*\*', r'\1', st_name).replace('#', '').strip()
                                if st_name:
                                    subtopics[current_ch].append(st_name)
                        
                        if chapters:
                            st.session_state['outline'] = chapters
                            for ch in chapters:
                                st.session_state['chapters'][ch] = {
                                    'subtopics': subtopics.get(ch, []),
                                    'subtopic_data': {s: {'questions': [], 'answers': [], 'content': ''} for s in subtopics.get(ch, [])}
                                }
                            st.success(f"✅ {len(chapters)}개 챕터 생성!")
                            st.rerun()
        
        if st.session_state.get('outline'):
            st.markdown("### 📋 현재 목차")
            for ch in st.session_state['outline']:
                st.markdown(f"**{ch}**")
                for st_name in st.session_state['chapters'].get(ch, {}).get('subtopics', []):
                    st.write(f"  - {st_name}")
    
    with col2:
        st.markdown("### 📝 목차 미리보기")
        
        if st.session_state.get('outline'):
            outline_text = ""
            for ch in st.session_state['outline']:
                outline_text += f"\n{ch}\n"
                for st_name in st.session_state['chapters'].get(ch, {}).get('subtopics', []):
                    outline_text += f"  • {st_name}\n"
            st.text_area("전체 목차", value=outline_text, height=400, key="p4_preview", disabled=True)
        else:
            st.markdown('<div style="text-align:center;padding:60px;background:#f8f8f8;border-radius:16px;"><p style="color:#888;">목차를 생성해주세요</p></div>', unsafe_allow_html=True)
    
    # 다음/이전 버튼
    st.markdown('<div class="next-section"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("← 이전", key="p4_prev", use_container_width=True):
            go_prev()
            st.rerun()
    with c3:
        if st.button("다음 → 본문 작성", key="p4_next", use_container_width=True):
            go_next()
            st.rerun()


# ==========================================
# PAGE 5: 본문 작성
# ==========================================
elif current == 5:
    st.markdown("## 본문 작성")
    
    if not st.session_state.get('outline'):
        st.warning("먼저 목차를 설계하세요")
    else:
        # 챕터/소제목 선택
        col_sel1, col_sel2 = st.columns([1, 1])
        with col_sel1:
            selected_ch = st.selectbox("📚 챕터 선택", st.session_state['outline'], key="p5_chapter")
        
        if selected_ch and selected_ch in st.session_state['chapters']:
            ch_data = st.session_state['chapters'][selected_ch]
            
            with col_sel2:
                if ch_data.get('subtopics'):
                    selected_st = st.selectbox("✍️ 소제목 선택", ch_data['subtopics'], key="p5_subtopic")
            
            # 진행 상황
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
                        if st.button("✨ 몰입감 있는 본문 생성", key="p5_gen"):
                            with st.spinner("베스트셀러 스타일로 본문 작성 중..."):
                                content = generate_content_premium(selected_st, selected_ch, st_data['questions'], st_data['answers'], st.session_state['topic'], st.session_state['target_persona'])
                                if content:
                                    st_data['content'] = content
                                    st.rerun()
                    
                    edited = st.text_area("본문 (수정 가능)", value=st_data.get('content', ''), height=400, key="p5_content")
                    st_data['content'] = edited
                    
                    if edited:
                        st.caption(f"📊 {len(edited.replace(' ', '').replace(chr(10), '')):,}자")
        
        # 전체 본문 종합 보기 섹션
        st.markdown("---")
        st.markdown("### 📖 전체 본문 종합")
        
        full_content = get_full_content()
        if full_content:
            char_count = len(full_content.replace(' ', '').replace('\n', ''))
            st.success(f"📊 총 {char_count:,}자 | 약 {char_count//500}페이지 분량")
            
            with st.expander("📖 작성된 전체 본문 보기", expanded=False):
                st.markdown(f'<div class="full-content-box">{full_content}</div>', unsafe_allow_html=True)
        else:
            st.info("아직 작성된 본문이 없습니다. 위에서 소제목별로 본문을 작성해주세요.")
    
    # 다음/이전 버튼
    st.markdown('<div class="next-section"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("← 이전", key="p5_prev", use_container_width=True):
            go_prev()
            st.rerun()
    with c3:
        if st.button("다음 → 최종 출력", key="p5_next", use_container_width=True):
            go_next()
            st.rerun()


# ==========================================
# PAGE 6: 최종 출력
# ==========================================
elif current == 6:
    st.markdown("## 최종 출력")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown("### 📖 다운로드")
        
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
        
        with st.expander("📖 전체 내용 미리보기", expanded=True):
            st.text_area("전체 내용", value=full, height=300, key="p6_preview", disabled=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📄 TXT 다운로드", full, file_name=f"{final_title or 'ebook'}.txt", use_container_width=True, key="p6_txt")
        with c2:
            html = f"<html><head><meta charset='utf-8'><title>{final_title}</title><style>body{{max-width:800px;margin:0 auto;padding:40px;font-family:sans-serif;line-height:1.8;}}</style></head><body>{full.replace(chr(10), '<br>')}</body></html>"
            st.download_button("🌐 HTML 다운로드", html, file_name=f"{final_title or 'ebook'}.html", use_container_width=True, key="p6_html")
        
        total = len(full.replace(' ', '').replace('\n', ''))
        if total > 0:
            st.success(f"✅ 총 {total:,}자 | 약 {total//500}페이지")
    
    with col2:
        st.markdown("### 📊 작성 현황")
        
        total_st = sum(len(ch.get('subtopics', [])) for ch in st.session_state.get('chapters', {}).values())
        done = sum(1 for ch in st.session_state.get('chapters', {}).values() for s in ch.get('subtopic_data', {}).values() if s.get('content'))
        
        if total_st > 0:
            st.progress(done / total_st)
            st.write(f"**완료:** {done}/{total_st}")
        
        # 미완성 목록
        incomplete = []
        for ch in st.session_state.get('outline', []):
            if ch in st.session_state.get('chapters', {}):
                ch_data = st.session_state['chapters'][ch]
                for s in ch_data.get('subtopics', []):
                    if not ch_data.get('subtopic_data', {}).get(s, {}).get('content'):
                        incomplete.append(s)
        
        if incomplete:
            with st.expander(f"⚠️ 미완성 ({len(incomplete)}개)"):
                for item in incomplete[:10]:
                    st.write(f"• {item}")
    
    # 이전 버튼
    st.markdown('<div class="next-section"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("← 이전", key="p6_prev", use_container_width=True):
            go_prev()
            st.rerun()


st.markdown('<div style="text-align:center;padding:40px;margin-top:60px;border-top:1px solid #eee;color:#888;">전자책 작성 프로그램 — <b>남현우 작가</b></div>', unsafe_allow_html=True)
