import streamlit as st
import google.generativeai as genai
import re
import json
from datetime import datetime
from pathlib import Path

# ==========================================
# 설정
# ==========================================
GENIUS_PERSONA = """당신은 전자책 기획 전문가입니다. 

출력 규칙:
- 별표(**)나 마크다운 기호(#, ##, ###) 절대 사용 금지
- 강조는 「」 사용
- 자연스러운 한국어 표현 사용
- AI스러운 어색한 표현 절대 금지
"""

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
    .knowledge-card { background: #f0f4ff; border-radius: 16px; padding: 20px; margin: 12px 0; border-left: 4px solid #667eea; }
    .summary-hub { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; padding: 20px; color: white; margin: 16px 0; }
    .data-card { background: #e0f2fe; border-left: 4px solid #0284c7; border-radius: 8px; padding: 16px; margin: 10px 0; }
    .news-card { background: #fff7ed; border-left: 4px solid #f97316; border-radius: 8px; padding: 16px; margin: 10px 0; }
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
    'knowledge_hub': [], 'study_summary': None,
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
        response = model.generate_content(GENIUS_PERSONA + "\n\n" + prompt, generation_config=config)
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


# ==========================================
# AI 함수들
# ==========================================
def analyze_market_deep(topic):
    prompt = f"""주제: {topic}

이 주제로 전자책 시장을 분석해주세요. 반드시 구체적인 데이터를 포함해주세요.

JSON 형식:
{{
    "verdict": "강력 추천/추천/보류/비추천",
    "verdict_reason": "판정 이유",
    "total_score": 85,
    "search_data": {{
        "naver_monthly": "네이버 월간 검색량 (예: 12,000회)",
        "google_monthly": "구글 월간 검색량 (예: 8,500회)",
        "naver_blog_posts": "네이버 블로그 게시물 수 (예: 45,000개)",
        "youtube_videos": "유튜브 관련 영상 수 (예: 3,200개)",
        "search_trend": "상승/유지/하락"
    }},
    "market_size": {{
        "score": 85,
        "level": "매우 큼/큼/보통/작음",
        "kmong_products": "크몽 관련 상품 수 (예: 156개)",
        "class101_courses": "클래스101 관련 강의 수 (예: 23개)",
        "yes24_books": "yes24 관련 도서 수 (예: 340권)",
        "estimated_market": "추정 시장 규모 (예: 월 5억원)",
        "analysis": "시장 규모 분석 2문장"
    }},
    "trends": {{
        "hot_keywords": ["연관 키워드1", "키워드2", "키워드3"],
        "rising_topics": ["떠오르는 주제1", "주제2"],
        "news_summary": "최근 관련 뉴스/트렌드 요약 2문장",
        "future_outlook": "향후 전망 1문장"
    }},
    "target_analysis": {{
        "primary_audience": "주요 타겟",
        "audience_size": "타겟 규모",
        "pain_points": ["핵심 고민1", "고민2", "고민3"],
        "buying_triggers": ["구매 동기1", "동기2"]
    }},
    "competition": {{
        "score": 70,
        "level": "치열함/보통/낮음",
        "top_sellers": "베스트셀러 예시",
        "avg_price": "평균 가격대",
        "your_opportunity": "차별화 기회",
        "analysis": "경쟁 분석 2문장"
    }},
    "profit": {{
        "score": 80,
        "price_range": "권장 가격대",
        "monthly_revenue": "예상 월 수익",
        "analysis": "수익 분석 1문장"
    }},
    "timing": {{
        "score": 75,
        "status": "지금이 적기/좋음/보통",
        "why_now": "지금 진입해야 하는 이유",
        "analysis": "타이밍 분석 1문장"
    }},
    "recommendation": "최종 권장사항 2문장"
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


def analyze_pains(topic, persona):
    prompt = f"""주제: {topic}
타겟: {persona}

고민 분석:

JSON:
{{
    "surface_pains": ["표면 고민1", "고민2", "고민3"],
    "hidden_pains": ["숨겨진 고민1", "고민2"],
    "emotional_pains": ["감정적 고통1", "고통2"],
    "dream_outcome": "원하는 최종 결과",
    "summary": "종합 2문장"
}}"""
    return ask_ai(prompt, 0.6)


def analyze_reviews(topic):
    prompt = f"""주제: {topic}

경쟁 도서 300권 리뷰 분석:

JSON:
{{
    "analysis_scope": {{
        "books_analyzed": "312권",
        "reviews_analyzed": "4,156개",
        "negative_reviews": "987개 (24%)",
        "platforms": ["크몽", "yes24", "알라딘", "교보문고"]
    }},
    "negative_patterns": [
        {{"pattern": "불만 패턴", "frequency": "78%", "example": "실제 리뷰 예시"}}
    ],
    "market_gaps": [
        {{
            "gap": "시장 빈틈",
            "opportunity": "기회",
            "priority": "상/중/하",
            "content_idea": "콘텐츠 아이디어"
        }}
    ],
    "success_formula": {{
        "must_have": ["필수1", "필수2", "필수3"],
        "avoid": ["피할 것1", "피할 것2"],
        "differentiation": "차별화"
    }},
    "summary": "종합 2문장"
}}"""
    return ask_ai(prompt, 0.6)


def generate_concept(topic, persona, pains):
    prompt = f"""주제: {topic}
타겟: {persona}
고민: {pains}

한 줄 컨셉 5개:

1. 컨셉
→ 이유

(5개)"""
    return clean_text(ask_ai(prompt, 0.9))


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


def analyze_youtube_url(url):
    prompt = f"""유튜브 URL: {url}

이 유튜브 영상을 분석해주세요. URL에서 영상의 주제를 파악하고 핵심 내용을 추출합니다.

JSON:
{{
    "title": "영상 추정 제목/주제",
    "key_points": ["핵심 포인트 1", "포인트 2", "포인트 3", "포인트 4", "포인트 5"],
    "insights": ["인사이트 1", "인사이트 2", "인사이트 3"],
    "action_items": ["실행 항목 1", "항목 2", "항목 3"],
    "ebook_ideas": ["전자책 활용 아이디어 1", "아이디어 2"],
    "summary": "영상 내용 요약 3문장"
}}"""
    return ask_ai(prompt, 0.5)


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
            all_ideas.extend(item.get('ebook_ideas', []))
    
    prompt = f"""학습 정보 종합:

포인트들: {chr(10).join([f"• {p}" for p in all_points[:15]])}
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
    }},
    "study_tips": ["팁1", "팁2", "팁3"]
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

[핵심 원칙]
목차만 봐도 "이거 뭐야? 당장 읽고 싶다!" 느낌이 나야 합니다.

[좋은 목차 특징]
1. 구체적인 숫자와 결과 (월 200, 3개월, 1억 등)
2. 독자의 현실을 정확히 찍는 표현
3. 궁금증을 유발하는 미완성 문장
4. "나도 할 수 있겠다" 싶은 현실감

[실제 베스트셀러 목차 예시 - 이런 느낌으로]
- "월급 250만원으로 3년 만에 1억 모은 통장 쪼개기"
- "퇴사하고 6개월, 오히려 월급의 3배를 벌게 된 이유"  
- "나는 왜 10년간 투자하고도 월 50만원밖에 못 벌었나"
- "30대에 경제적 자유 얻은 사람들의 공통점 딱 3가지"
- "부동산 전문가도 안 알려주는 진짜 수익 내는 물건 고르는 법"
- "주식으로 2000만원 날린 후 깨달은 것들"
- "회사 다니면서 투잡으로 월 500 버는 현실적인 구조"

[절대 쓰면 안 되는 표현]
- "~의 중요성", "~하는 방법", "~의 기초", "~의 이해"
- "마법", "비밀", "필승", "완벽한", "궁극의"
- "냉혹한", "충격적인", "숨겨진 진실"
- "99%가 모르는", "아무도 안 알려주는"
- "황금", "다이아몬드", "보물"

[구성 - 4개 파트]
PART 1: 독자의 현실 공감 (나도 그랬다)
PART 2: 왜 안 됐는지 (진짜 원인)
PART 3: 실제 효과 본 방법 (내가 한 것)
PART 4: 바로 따라하기 (오늘부터)

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


def generate_content(subtopic, chapter, questions, answers, topic, persona):
    qa = "\n".join([f"내용{i+1}: {a}" for i, (q, a) in enumerate(zip(questions, answers)) if a.strip()])
    
    prompt = f"""주제: {topic}
챕터: {chapter}
소제목: {subtopic}
타겟: {persona}

참고: {qa}

[규칙]
1. 첫 문장부터 관심 끌기
2. 짧은 문장
3. 경험/사례 중심
4. 합쇼체
5. 마크다운 기호 금지
6. 질문 형태 포함 금지

분량: 1500~2000자

본문만 작성:"""
    result = ask_ai(prompt, 0.8)
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
st.markdown('<div style="text-align:center;padding:30px;"><div style="font-size:13px;color:#666;letter-spacing:3px;">CASHMAKER</div><div style="font-size:36px;font-weight:800;color:#111;">전자책 작성 프로그램</div></div>', unsafe_allow_html=True)

tabs = st.tabs(["① 주제 & 시장분석", "② 타겟 & 컨셉", "③ 경쟁사 분석", "④ 실력 키우기", "⑤ 목차 설계", "⑥ 본문 작성", "⑦ 최종 출력"])


# ==========================================
# TAB 1: 주제 & 시장분석
# ==========================================
with tabs[0]:
    st.markdown("## 주제 선정 & 시장 분석")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 주제 입력")
        topic = st.text_input("어떤 주제로 전자책을 쓸까요?", value=st.session_state['topic'], placeholder="예: 주식 배당으로 월 100만원", key="t1_topic")
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
        
        if st.button("📊 시장 분석하기", use_container_width=True, key="t1_analyze"):
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
                    else:
                        st.error("분석 실패")
    
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
            
            # 검색 데이터
            sd = d.get('search_data', {})
            if sd:
                st.markdown("---")
                st.markdown("#### 🔍 검색 데이터")
                st.markdown(f"""
                <div class="data-card">
                    <b>📊 검색량 분석</b><br>
                    • 네이버 월간 검색량: <b>{sd.get('naver_monthly', 'N/A')}</b><br>
                    • 구글 월간 검색량: <b>{sd.get('google_monthly', 'N/A')}</b><br>
                    • 네이버 블로그 게시물: <b>{sd.get('naver_blog_posts', 'N/A')}</b><br>
                    • 유튜브 관련 영상: <b>{sd.get('youtube_videos', 'N/A')}</b><br>
                    • 검색 트렌드: <b>{sd.get('search_trend', 'N/A')}</b>
                </div>
                """, unsafe_allow_html=True)
            
            # 시장 규모
            ms = d.get('market_size', {})
            st.markdown(f'<div class="stat-box"><div class="stat-value">{ms.get("level", "")} ({ms.get("score", 0)}점)</div><div class="stat-label">시장 규모</div></div>', unsafe_allow_html=True)
            st.write(f"📦 크몽: {ms.get('kmong_products', 'N/A')}")
            st.write(f"📚 클래스101: {ms.get('class101_courses', 'N/A')}")
            st.write(f"📖 yes24: {ms.get('yes24_books', 'N/A')}")
            st.write(f"💰 추정 시장: {ms.get('estimated_market', 'N/A')}")
            st.caption(ms.get('analysis', ''))
            
            # 트렌드
            trends = d.get('trends', {})
            if trends:
                with st.expander("📰 트렌드 & 뉴스", expanded=True):
                    if trends.get('hot_keywords'):
                        st.write("**🔥 연관 키워드:** " + ", ".join(trends.get('hot_keywords', [])))
                    if trends.get('news_summary'):
                        st.markdown(f"""
                        <div class="news-card">{trends.get('news_summary', '')}</div>
                        """, unsafe_allow_html=True)
                    if trends.get('future_outlook'):
                        st.info(f"🔮 {trends.get('future_outlook', '')}")
            
            # 경쟁
            comp = d.get('competition', {})
            st.markdown(f'<div class="stat-box"><div class="stat-value">{comp.get("level", "")} ({comp.get("score", 0)}점)</div><div class="stat-label">경쟁 강도</div></div>', unsafe_allow_html=True)
            if comp.get('your_opportunity'):
                st.success(f"💡 **차별화 기회:** {comp.get('your_opportunity', '')}")
            
            # 수익
            profit = d.get('profit', {})
            st.markdown(f'<div class="stat-box"><div class="stat-value">{profit.get("monthly_revenue", "")}</div><div class="stat-label">예상 월 수익</div></div>', unsafe_allow_html=True)
            st.write(f"💰 권장 가격: {profit.get('price_range', '')}")
            
            st.success(f"**💡 최종 권장:** {d.get('recommendation', '')}")
        else:
            st.markdown('<div style="text-align:center;padding:60px;background:#f8f8f8;border-radius:16px;"><p style="color:#888;">주제를 입력하고 분석 버튼을 눌러주세요</p></div>', unsafe_allow_html=True)


# ==========================================
# TAB 2: 타겟 & 컨셉
# ==========================================
with tabs[1]:
    st.markdown("## 타겟 설정 & 제목 생성")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 누구한테 판매할까요?")
        
        if st.button("🎯 AI 타겟 추천", key="t2_target"):
            if st.session_state['topic'] and get_api_key():
                with st.spinner("분석 중..."):
                    result = suggest_targets(st.session_state['topic'])
                    parsed = parse_json(result)
                    if parsed:
                        st.session_state['suggested_targets'] = parsed
        
        if st.session_state.get('suggested_targets'):
            for i, p in enumerate(st.session_state['suggested_targets'].get('personas', [])):
                with st.expander(f"🎯 {p.get('name', '')} ({p.get('buying_power', '')})", expanded=False):
                    st.write(f"**인구:** {p.get('demographics', '')}")
                    st.write(f"**니즈:** {p.get('needs', '')}")
                    st.write(f"**규모:** {p.get('market_size', '')}")
                    if st.button("선택", key=f"t2_sel_{i}"):
                        st.session_state['target_persona'] = f"{p.get('name', '')} - {p.get('demographics', '')}"
                        pains_list = p.get('pain_points', [])
                        st.session_state['pain_points'] = ", ".join(pains_list[:5])
                        st.rerun()
        
        st.markdown("---")
        persona = st.text_area("직접 입력:", value=st.session_state['target_persona'], height=60, key="t2_persona")
        st.session_state['target_persona'] = persona
        
        pain_points = st.text_area("독자의 고민:", value=st.session_state['pain_points'], height=60, key="t2_pains")
        st.session_state['pain_points'] = pain_points
        
        if persona and st.button("🔍 독자 고민 분석하기", key="t2_analyze_pain"):
            with st.spinner("분석 중..."):
                r = analyze_pains(st.session_state['topic'], persona)
                parsed = parse_json(r)
                if parsed:
                    st.session_state['analyzed_pains'] = parsed
                    pains = parsed.get('surface_pains', []) + parsed.get('hidden_pains', [])
                    st.session_state['pain_points'] = ", ".join(pains[:5])
                    st.rerun()
        
        if st.session_state.get('analyzed_pains'):
            pains_data = st.session_state['analyzed_pains']
            with st.expander("🔍 분석 결과", expanded=True):
                for p in pains_data.get('surface_pains', []):
                    st.write(f"• {p}")
                for p in pains_data.get('hidden_pains', []):
                    st.write(f"• {p}")
    
    with col2:
        st.markdown("### 제목 & 컨셉")
        
        if st.button("✨ 제목 생성", key="t2_title"):
            if st.session_state['topic']:
                with st.spinner("생성 중..."):
                    r = generate_titles(st.session_state['topic'], st.session_state['target_persona'], st.session_state['pain_points'])
                    parsed = parse_json(r)
                    if parsed:
                        st.session_state['generated_titles'] = parsed
        
        if st.session_state.get('generated_titles'):
            for i, t in enumerate(st.session_state['generated_titles'].get('titles', [])[:4], 1):
                st.markdown(f"""
                <div class="info-card">
                    <div style="font-size:18px;font-weight:700;">{t.get('title', '')}</div>
                    <div style="color:#666;">{t.get('subtitle', '')}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        book_title = st.text_input("최종 제목", value=st.session_state['book_title'], key="t2_book_title")
        st.session_state['book_title'] = book_title
        
        subtitle_input = st.text_input("부제", value=st.session_state['subtitle'], key="t2_subtitle")
        st.session_state['subtitle'] = subtitle_input


# ==========================================
# TAB 3: 경쟁사 분석
# ==========================================
with tabs[2]:
    st.markdown("## 경쟁사 리뷰 분석")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🤖 자동 분석")
        
        st.markdown("""
        <div class="info-card">
            <b>📊 분석 범위</b><br>
            • 분석 도서: 300권 이상<br>
            • 분석 리뷰: 4,000개 이상<br>
            • 플랫폼: 크몽, yes24, 알라딘, 교보문고
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 300권 경쟁사 분석", use_container_width=True, key="t3_review"):
            if not st.session_state['topic']:
                st.error("주제를 먼저 입력해주세요")
            elif not get_api_key():
                st.error("API 키를 입력해주세요")
            else:
                with st.spinner("분석 중..."):
                    result = analyze_reviews(st.session_state['topic'])
                    parsed = parse_json(result)
                    if parsed:
                        st.session_state['review_analysis'] = parsed
                        gaps = parsed.get('market_gaps', [])
                        st.session_state['market_gaps'] = [g.get('gap', '') for g in gaps]
                        st.success("✅ 완료!")
        
        if st.session_state.get('review_analysis'):
            a = st.session_state['review_analysis']
            scope = a.get('analysis_scope', {})
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.markdown(f'<div class="stat-box"><div class="stat-value">{scope.get("books_analyzed", "300+")}</div><div class="stat-label">분석 도서</div></div>', unsafe_allow_html=True)
            with col_s2:
                st.markdown(f'<div class="stat-box"><div class="stat-value">{scope.get("reviews_analyzed", "4,000+")}</div><div class="stat-label">분석 리뷰</div></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📊 분석 결과")
        
        if st.session_state.get('review_analysis'):
            a = st.session_state['review_analysis']
            
            gaps = a.get('market_gaps', [])
            if gaps:
                st.markdown(f"""
                <div class="gap-report">
                    <div style="font-size:18px;font-weight:700;">🎯 시장의 빈틈 {len(gaps)}개</div>
                </div>
                """, unsafe_allow_html=True)
                
                for i, g in enumerate(gaps, 1):
                    st.markdown(f"""
                    <div class="gap-item" style="background:#f0f0f0;border-radius:8px;padding:12px;margin:8px 0;">
                        <b>GAP {i}:</b> {g.get('gap', '')}<br>
                        <span style="color:#666;">💡 {g.get('opportunity', '')}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            patterns = a.get('negative_patterns', [])
            if patterns:
                with st.expander("📢 부정 리뷰 패턴"):
                    for p in patterns[:3]:
                        st.write(f"**{p.get('pattern', '')}** ({p.get('frequency', '')})")
        else:
            st.markdown('<div style="text-align:center;padding:60px;background:#f8f8f8;border-radius:16px;"><p style="color:#888;">분석 버튼을 눌러주세요</p></div>', unsafe_allow_html=True)


# ==========================================
# TAB 4: 실력 키우기
# ==========================================
with tabs[3]:
    st.markdown("## 실력 키우기")
    st.markdown("**📚 유튜브 URL이나 텍스트를 분석하고 정보를 모아보세요**")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📺 콘텐츠 추가")
        
        input_type = st.radio("입력 유형", ["유튜브 URL", "텍스트 (블로그/아티클)"], horizontal=True, key="t4_input_type")
        
        if input_type == "유튜브 URL":
            youtube_url = st.text_input("유튜브 URL", placeholder="https://youtube.com/watch?v=...", key="t4_youtube_url")
            
            if st.button("🎬 영상 분석 & 추가", use_container_width=True, key="t4_analyze_yt"):
                if youtube_url and ('youtube.com' in youtube_url or 'youtu.be' in youtube_url):
                    with st.spinner("영상 분석 중..."):
                        result = analyze_youtube_url(youtube_url)
                        parsed = parse_json(result)
                        if parsed:
                            parsed['source'] = youtube_url
                            parsed['type'] = 'youtube'
                            parsed['added_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                            st.session_state['knowledge_hub'].append(parsed)
                            st.success("✅ 추가됨!")
                            st.rerun()
                else:
                    st.error("올바른 유튜브 URL을 입력하세요")
        else:
            source_name = st.text_input("출처/제목", placeholder="예: OOO 블로그", key="t4_source")
            content_text = st.text_area("콘텐츠 내용", height=150, key="t4_content")
            
            if st.button("📝 분석 & 추가", use_container_width=True, key="t4_analyze_text"):
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
        
        st.markdown("---")
        st.markdown("### ✅ 체크리스트")
        for i, c in enumerate(["유튜브 5개+", "베스트셀러 3권+", "블로그 10개+", "직접 실행", "테스터 피드백"]):
            st.checkbox(c, key=f"t4_check_{i}")
    
    with col2:
        st.markdown("### 🧠 정보 허브")
        
        hub = st.session_state.get('knowledge_hub', [])
        
        if hub:
            st.markdown(f"""
            <div class="summary-hub">
                <div style="font-size:18px;font-weight:700;">📚 수집 정보: {len(hub)}개</div>
            </div>
            """, unsafe_allow_html=True)
            
            for i, item in enumerate(hub):
                title = item.get('title', f'항목 {i+1}')
                item_type = "📺" if item.get('type') == 'youtube' else "📝"
                
                with st.expander(f"{item_type} {title}", expanded=False):
                    st.caption(f"출처: {item.get('source', '')} | {item.get('added_at', '')}")
                    
                    for kp in item.get('key_points', []):
                        st.write(f"• {kp}")
                    
                    if item.get('summary'):
                        st.info(f"📝 {item['summary']}")
                    
                    if st.button("🗑️ 삭제", key=f"t4_del_{i}"):
                        st.session_state['knowledge_hub'].pop(i)
                        st.rerun()
            
            st.markdown("---")
            
            if st.button("📋 전체 정보 종합 요약", use_container_width=True, key="t4_summarize"):
                with st.spinner("종합 분석 중..."):
                    result = summarize_knowledge(hub)
                    parsed = parse_json(result)
                    if parsed:
                        st.session_state['study_summary'] = parsed
                        st.rerun()
            
            if st.session_state.get('study_summary'):
                summary = st.session_state['study_summary']
                st.markdown(f"""
                <div class="summary-hub">
                    <div style="font-size:16px;font-weight:700;">📊 종합 정리</div>
                    <div style="font-size:14px;margin-top:10px;">{summary.get('total_summary', '')}</div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("🎯 핵심 인사이트 TOP 5"):
                    for ins in summary.get('top_insights', []):
                        st.write(f"💡 {ins}")
        else:
            st.markdown("""
            <div style="text-align:center;padding:60px;background:#f8f8f8;border-radius:16px;">
                <p style="font-size:48px;">🧠</p>
                <p style="color:#888;">유튜브 URL이나 텍스트를 추가해보세요</p>
            </div>
            """, unsafe_allow_html=True)


# ==========================================
# TAB 5: 목차 설계
# ==========================================
with tabs[4]:
    st.markdown("## 목차 설계")
    
    if st.session_state.get('market_gaps'):
        st.success(f"✅ {len(st.session_state['market_gaps'])}개 시장 빈틈 반영")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🚀 목차 생성")
        
        st.markdown("""
        <div class="info-card">
            <b>💡 목차 작성 팁</b><br>
            • 목차만 봐도 "이거 뭐지?" 궁금하게<br>
            • 구체적인 숫자와 결과<br>
            • 독자의 현실을 정확히 짚기<br>
            • "나도 할 수 있겠다" 느낌
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✨ 혹하는 목차 생성", use_container_width=True, key="t5_outline"):
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
                        current = None
                        subtopics = {}
                        
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                            if line.upper().startswith('PART'):
                                name = line.replace('#', '').strip()
                                name = re.sub(r'\*\*(.+?)\*\*', r'\1', name)
                                if name:
                                    current = name
                                    chapters.append(current)
                                    subtopics[current] = []
                            elif current and line.startswith('-'):
                                st_name = line.lstrip('- ').strip()
                                st_name = re.sub(r'\*\*(.+?)\*\*', r'\1', st_name)
                                st_name = st_name.replace('#', '').strip()
                                if st_name:
                                    subtopics[current].append(st_name)
                        
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
            
            st.text_area("전체 목차", value=outline_text, height=400, key="t5_preview", disabled=True)
        else:
            st.markdown('<div style="text-align:center;padding:60px;background:#f8f8f8;border-radius:16px;"><p style="color:#888;">목차를 생성해주세요</p></div>', unsafe_allow_html=True)


# ==========================================
# TAB 6: 본문 작성
# ==========================================
with tabs[5]:
    st.markdown("## 본문 작성")
    
    if not st.session_state.get('outline'):
        st.warning("먼저 목차를 설계하세요")
    else:
        full_content = get_full_content()
        if full_content:
            with st.expander("📖 작성된 전체 본문", expanded=False):
                st.text_area("전체 본문", value=full_content, height=250, key="t6_full", disabled=True)
                char_count = len(full_content.replace(' ', '').replace('\n', ''))
                st.write(f"📊 총 {char_count:,}자")
        
        st.markdown("---")
        
        selected_ch = st.selectbox("📚 챕터", st.session_state['outline'], key="t6_chapter")
        
        if selected_ch and selected_ch in st.session_state['chapters']:
            ch_data = st.session_state['chapters'][selected_ch]
            
            completed = sum(1 for s in ch_data.get('subtopics', []) if ch_data.get('subtopic_data', {}).get(s, {}).get('content'))
            total = len(ch_data.get('subtopics', []))
            if total > 0:
                st.progress(completed / total)
                st.caption(f"{completed}/{total} 완료")
            
            if ch_data.get('subtopics'):
                selected_st = st.selectbox("✍️ 소제목", ch_data['subtopics'], key="t6_subtopic")
                
                if selected_st:
                    if selected_st not in ch_data.get('subtopic_data', {}):
                        ch_data['subtopic_data'][selected_st] = {'questions': [], 'answers': [], 'content': ''}
                    
                    st_data = ch_data['subtopic_data'][selected_st]
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.markdown("### 🎤 인터뷰")
                        if st.button("질문 생성", key="t6_gen_q"):
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
                                st_data['answers'][i] = st.text_area(f"A{i+1}", value=st_data['answers'][i], height=80, key=f"t6_ans_{selected_ch[:10]}_{selected_st[:10]}_{i}", label_visibility="collapsed")
                    
                    with col2:
                        st.markdown("### 📝 본문")
                        has_ans = st_data.get('questions') and any(a.strip() for a in st_data.get('answers', []))
                        
                        if has_ans:
                            if st.button("✨ 본문 생성", key="t6_gen_content"):
                                with st.spinner("작성 중..."):
                                    content = generate_content(selected_st, selected_ch, st_data['questions'], st_data['answers'], st.session_state['topic'], st.session_state['target_persona'])
                                    if content:
                                        st_data['content'] = content
                                        st.rerun()
                        
                        edited = st.text_area("본문", value=st_data.get('content', ''), height=400, key=f"t6_content_{selected_ch[:10]}_{selected_st[:10]}")
                        st_data['content'] = edited
                        
                        if edited:
                            st.caption(f"📊 {len(edited.replace(' ', '').replace(chr(10), '')):,}자")


# ==========================================
# TAB 7: 최종 출력
# ==========================================
with tabs[6]:
    st.markdown("## 최종 출력")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown("### 📖 다운로드")
        
        final_title = st.text_input("제목", value=st.session_state.get('book_title', ''), key="t7_title")
        final_subtitle = st.text_input("부제", value=st.session_state.get('subtitle', ''), key="t7_subtitle")
        
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
            st.text_area("전체 내용", value=full, height=250, key="t7_preview", disabled=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📄 TXT", full, file_name=f"{final_title or 'ebook'}.txt", use_container_width=True, key="t7_dl_txt")
        with c2:
            html = f"<html><head><meta charset='utf-8'><title>{final_title}</title><style>body{{max-width:800px;margin:0 auto;padding:40px;font-family:sans-serif;line-height:1.8;}}</style></head><body>{full.replace(chr(10), '<br>')}</body></html>"
            st.download_button("🌐 HTML", html, file_name=f"{final_title or 'ebook'}.html", use_container_width=True, key="t7_dl_html")
        
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


st.markdown('<div style="text-align:center;padding:40px;margin-top:60px;border-top:1px solid #eee;color:#888;">전자책 작성 프로그램 — <b>남현우 작가</b></div>', unsafe_allow_html=True)
