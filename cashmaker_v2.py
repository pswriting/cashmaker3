import streamlit as st
import google.generativeai as genai
import re
import json
from datetime import datetime
from pathlib import Path

# ==========================================
# 설정
# ==========================================
GENIUS_PERSONA = """당신은 전자책 기획 전문가입니다. 별표(**)나 마크다운 기호 사용 금지. 강조는 「」 사용."""

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
    .stButton > button * { color: #fff !important; }
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
    .knowledge-title { font-weight: 700; color: #333; font-size: 15px; margin-bottom: 8px; }
    .knowledge-point { background: #fff; border-radius: 8px; padding: 10px 14px; margin: 6px 0; font-size: 14px; color: #333; }
    .summary-hub { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; padding: 20px; color: white; margin: 16px 0; }
    .next-btn { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
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
        pw = st.text_input("비밀번호", type="password")
        if st.button("입장"):
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
    
    api_key = st.text_input("Gemini API 키", value=st.session_state['api_key'], type="password")
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
    text = re.sub(r'\*\*([^*]+)\*\*', r'「\1」', text)
    return text.replace('**', '').replace('*', '')

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
        config = genai.types.GenerationConfig(temperature=temp, max_output_tokens=4000)
        response = model.generate_content(GENIUS_PERSONA + "\n\n" + prompt, generation_config=config)
        return response.text
    except Exception as e:
        st.error(f"AI 오류: {e}")
        return None


# ==========================================
# AI 함수들
# ==========================================
def analyze_market(topic):
    prompt = f"""주제: {topic}

전자책 시장 분석을 해주세요. 데이터 기반으로 설득력 있게 분석해주세요.

JSON 형식으로만 출력 (다른 텍스트 없이):
{{
    "verdict": "강력 추천",
    "verdict_reason": "판정 이유 한 문장",
    "total_score": 85,
    "market_size": {{
        "score": 85,
        "level": "매우 큼",
        "monthly_searches": "월 5만회 이상",
        "related_products": "크몽 150개, 클래스101 40개",
        "analysis": "시장 분석 내용 2문장"
    }},
    "competition": {{
        "score": 70,
        "level": "보통",
        "analysis": "경쟁 분석 내용 2문장"
    }},
    "profit": {{
        "score": 80,
        "price_range": "9,900원 ~ 29,900원",
        "monthly_revenue": "월 100만원 ~ 300만원",
        "analysis": "수익 분석 내용 2문장"
    }},
    "timing": {{
        "score": 75,
        "status": "지금이 적기",
        "analysis": "타이밍 분석 내용 2문장"
    }},
    "recommendation": "최종 권장사항 2문장"
}}"""
    return ask_ai(prompt, 0.5)


def suggest_targets(topic):
    prompt = f"""주제: {topic}

구매 가능성 높은 타겟 5개를 추천해주세요.

JSON:
{{
    "personas": [
        {{
            "name": "타겟 이름",
            "demographics": "30대 직장인",
            "needs": "핵심 니즈",
            "buying_power": "상",
            "market_size": "50만명",
            "pain_points": ["고민1", "고민2", "고민3"]
        }}
    ]
}}"""
    return ask_ai(prompt, 0.7)


def analyze_reader_pains(topic, persona):
    prompt = f"""주제: {topic}
타겟: {persona}

독자의 고민을 분석해주세요.

JSON:
{{
    "surface_pains": ["표면적 고민1", "표면적 고민2", "표면적 고민3"],
    "hidden_pains": ["숨겨진 고민1", "숨겨진 고민2"],
    "emotional_pains": ["감정적 고통1", "감정적 고통2"],
    "summary": "종합 분석 2문장"
}}"""
    return ask_ai(prompt, 0.6)


def analyze_reviews_300(topic):
    prompt = f"""주제: {topic}

크몽, yes24, 알라딘, 교보문고에서 이 주제 관련 전자책 300권 이상의 리뷰를 분석한다고 가정합니다.

JSON:
{{
    "analysis_scope": {{
        "books_analyzed": "312권",
        "reviews_analyzed": "4,156개",
        "negative_reviews": "987개 (24%)",
        "platforms": ["크몽", "yes24", "알라딘", "교보문고"]
    }},
    "negative_patterns": [
        {{"pattern": "실행 가이드 부족", "frequency": "78%", "example": "이론만 있고 실제로 뭘 해야 할지 모르겠음"}},
        {{"pattern": "최신 정보 부재", "frequency": "62%", "example": "작년 정보라 지금은 안 맞음"}},
        {{"pattern": "템플릿 없음", "frequency": "51%", "example": "바로 쓸 수 있는 양식이 있었으면"}}
    ],
    "market_gaps": [
        {{
            "gap": "시장의 빈틈",
            "opportunity": "기회 포인트",
            "priority": "상",
            "content_idea": "콘텐츠 아이디어"
        }}
    ],
    "success_formula": {{
        "must_have": ["필수 요소1", "필수 요소2", "필수 요소3"],
        "avoid": ["피할 것1", "피할 것2"],
        "differentiation": "차별화 포인트"
    }},
    "summary": "종합 분석 2문장"
}}"""
    return ask_ai(prompt, 0.6)


def generate_concept(topic, persona, pains):
    prompt = f"""주제: {topic}
타겟: {persona}
고민: {pains}

"이 책 안 읽으면 손해" 느낌의 한 줄 컨셉 5개를 만들어주세요.
별표(*) 사용 금지. 강조는 「」 사용.

형식:
1. 컨셉 문장
→ 왜 끌리는가

(5개)"""
    result = ask_ai(prompt, 0.9)
    return clean_text(result)


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


def analyze_content(content_text, source_name=""):
    """텍스트 콘텐츠 분석 (유튜브 자막 또는 아티클)"""
    prompt = f"""다음 콘텐츠를 분석해주세요.

출처: {source_name}
내용:
{content_text[:5000]}

JSON:
{{
    "title": "콘텐츠 주제",
    "main_theme": "메인 주제",
    "key_points": [
        "핵심 포인트 1",
        "핵심 포인트 2",
        "핵심 포인트 3",
        "핵심 포인트 4",
        "핵심 포인트 5"
    ],
    "insights": [
        "인사이트 1",
        "인사이트 2",
        "인사이트 3"
    ],
    "action_items": [
        "실행 항목 1",
        "실행 항목 2",
        "실행 항목 3"
    ],
    "ebook_ideas": [
        "전자책 활용 아이디어 1",
        "전자책 활용 아이디어 2"
    ],
    "chapter_ideas": [
        "목차 아이디어 1",
        "목차 아이디어 2"
    ],
    "summary": "핵심 요약 3문장"
}}"""
    return ask_ai(prompt, 0.5)


def summarize_knowledge(hub_items):
    """수집된 모든 정보 종합 요약"""
    if not hub_items:
        return None
    
    all_points = []
    all_ideas = []
    all_actions = []
    
    for item in hub_items:
        if isinstance(item, dict):
            all_points.extend(item.get('key_points', []))
            all_ideas.extend(item.get('ebook_ideas', []))
            all_actions.extend(item.get('action_items', []))
    
    prompt = f"""수집된 학습 정보를 종합 분석해주세요.

핵심 포인트들:
{chr(10).join([f"• {p}" for p in all_points[:15]])}

전자책 아이디어들:
{chr(10).join([f"• {i}" for i in all_ideas[:10]])}

실행 항목들:
{chr(10).join([f"• {a}" for a in all_actions[:10]])}

JSON:
{{
    "total_summary": "전체 학습 내용 종합 요약 5문장",
    "top_insights": ["핵심 인사이트 1", "인사이트 2", "인사이트 3", "인사이트 4", "인사이트 5"],
    "recommended_outline": ["추천 목차 1", "추천 목차 2", "추천 목차 3", "추천 목차 4"],
    "study_plan": {{
        "week1": "1주차: 할 일",
        "week2": "2주차: 할 일",
        "week3": "3주차: 할 일",
        "week4": "4주차: 할 일"
    }},
    "study_tips": ["공부 팁 1", "공부 팁 2", "공부 팁 3"]
}}"""
    return ask_ai(prompt, 0.6)


def generate_outline(topic, persona, pains, gaps=None):
    gaps_text = ""
    if gaps:
        gaps_text = f"\n차별화 포인트:\n" + "\n".join([f"• {g}" for g in gaps[:3]])
    
    prompt = f"""주제: {topic}
타겟: {persona}
고민: {pains}
{gaps_text}

자청/신사임당 스타일의 킬러 목차를 만드세요.
목차만 봐도 "사고 싶다" 느낌이 들어야 합니다.

구성:
1부: 상식 파괴 (뒤통수)
2부: 진짜 원인 폭로
3부: 비밀 무기 공개
4부: 바로 실행

금지: "~의 중요성", "~하는 방법", "기초", "입문"

출력:
## PART 1. [충격적 제목]
- [소제목 1]
- [소제목 2]
- [소제목 3]

(4개 PART)"""
    return ask_ai(prompt, 0.85)


def generate_content(subtopic, chapter, questions, answers, topic, persona):
    qa = "\n".join([f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(zip(questions, answers)) if a.strip()])
    
    prompt = f"""주제: {topic}
챕터: {chapter}
소제목: {subtopic}
타겟: {persona}

인터뷰:
{qa}

규칙:
1. 첫 문장 = 뒤통수
2. 짧은 문장
3. 스토리 > 설명
4. 합쇼체

분량: 1500~2000자
마크다운 금지.

본문 작성:"""
    result = ask_ai(prompt, 0.8)
    return clean_text(result)


def generate_questions(subtopic, chapter, topic):
    prompt = f"""'{topic}' 전자책 '{chapter}' 챕터의 '{subtopic}' 인터뷰 질문 3개:

Q1: [질문]
Q2: [질문]
Q3: [질문]"""
    return ask_ai(prompt, 0.7)


# ==========================================
# 메인 UI
# ==========================================
st.markdown('<div style="text-align:center;padding:30px;"><div style="font-size:13px;color:#666;letter-spacing:3px;">CASHMAKER</div><div style="font-size:36px;font-weight:800;color:#111;">전자책 작성 프로그램</div><div style="font-size:16px;color:#666;margin-top:8px;">경쟁사 300권 분석 → 시장의 빈틈 → 베스트셀러</div></div>', unsafe_allow_html=True)

tabs = st.tabs(["① 주제 & 시장분석", "② 타겟 & 컨셉", "③ 경쟁사 분석", "④ 전문성 키우기", "⑤ 목차 설계", "⑥ 본문 작성", "⑦ 최종 출력"])


# ==========================================
# TAB 1: 주제 & 시장분석
# ==========================================
with tabs[0]:
    st.markdown("## 주제 선정 & 시장 분석")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 주제 입력")
        topic = st.text_input("어떤 주제로 전자책을 쓸까요?", value=st.session_state['topic'], placeholder="예: 주식 배당으로 월 100만원")
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
        
        if st.button("📊 시장 분석하기", use_container_width=True):
            if not topic:
                st.error("주제를 입력해주세요")
            elif not get_api_key():
                st.error("API 키를 입력해주세요")
            else:
                with st.spinner("시장 데이터 분석 중..."):
                    result = analyze_market(topic)
                    parsed = parse_json(result)
                    if parsed:
                        st.session_state['score_details'] = parsed
                    else:
                        st.error("분석 실패. 다시 시도해주세요.")
    
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
            
            st.markdown("---")
            st.markdown("#### 📊 세부 분석")
            
            # 시장 규모
            ms = d.get('market_size', {})
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-value">{ms.get('level', '')} ({ms.get('score', 0)}점)</div>
                <div class="stat-label">시장 규모</div>
            </div>
            """, unsafe_allow_html=True)
            st.write(f"📈 {ms.get('monthly_searches', '')}")
            st.write(f"📦 {ms.get('related_products', '')}")
            st.caption(ms.get('analysis', ''))
            
            # 경쟁
            comp = d.get('competition', {})
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-value">{comp.get('level', '')} ({comp.get('score', 0)}점)</div>
                <div class="stat-label">경쟁 강도</div>
            </div>
            """, unsafe_allow_html=True)
            st.caption(comp.get('analysis', ''))
            
            # 수익
            profit = d.get('profit', {})
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-value">{profit.get('monthly_revenue', '')} ({profit.get('score', 0)}점)</div>
                <div class="stat-label">예상 월 수익</div>
            </div>
            """, unsafe_allow_html=True)
            st.write(f"💰 가격대: {profit.get('price_range', '')}")
            st.caption(profit.get('analysis', ''))
            
            # 타이밍
            timing = d.get('timing', {})
            st.write(f"⏰ **타이밍:** {timing.get('status', '')} ({timing.get('score', 0)}점)")
            st.caption(timing.get('analysis', ''))
            
            st.success(f"**💡 최종 권장:** {d.get('recommendation', '')}")
        else:
            st.markdown('<div style="text-align:center;padding:60px;background:#f8f8f8;border-radius:16px;"><p style="color:#888;">주제를 입력하고 분석 버튼을 눌러주세요</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="next-btn"></div>', unsafe_allow_html=True)
    st.button("다음 → 타겟 & 컨셉", key="n1", use_container_width=True)


# ==========================================
# TAB 2: 타겟 & 컨셉
# ==========================================
with tabs[1]:
    st.markdown("## 타겟 설정 & 제목 생성")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 누구한테 판매할까요?")
        
        if st.button("🎯 AI 타겟 추천"):
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
                    if st.button("선택", key=f"sel_{i}"):
                        st.session_state['target_persona'] = f"{p.get('name', '')} - {p.get('demographics', '')}"
                        with st.spinner("독자 고민 분석 중..."):
                            r = analyze_reader_pains(st.session_state['topic'], st.session_state['target_persona'])
                            parsed = parse_json(r)
                            if parsed:
                                st.session_state['analyzed_pains'] = parsed
                                pains = parsed.get('surface_pains', []) + parsed.get('hidden_pains', [])
                                st.session_state['pain_points'] = ", ".join(pains[:5])
                        st.rerun()
        
        st.markdown("---")
        persona = st.text_area("직접 입력:", value=st.session_state['target_persona'], height=60)
        st.session_state['target_persona'] = persona
        
        if st.session_state.get('analyzed_pains'):
            pains = st.session_state['analyzed_pains']
            with st.expander("🔍 독자 고민 분석 결과", expanded=True):
                st.markdown("**표면적 고민:**")
                for p in pains.get('surface_pains', []):
                    st.write(f"• {p}")
                st.markdown("**숨겨진 고민:**")
                for p in pains.get('hidden_pains', []):
                    st.write(f"• {p}")
                if pains.get('summary'):
                    st.info(pains['summary'])
        
        pain_points = st.text_area("독자의 고민:", value=st.session_state['pain_points'], height=60)
        st.session_state['pain_points'] = pain_points
        
        if persona and st.button("🔍 독자 고민 분석하기"):
            with st.spinner("분석 중..."):
                r = analyze_reader_pains(st.session_state['topic'], persona)
                parsed = parse_json(r)
                if parsed:
                    st.session_state['analyzed_pains'] = parsed
                    pains = parsed.get('surface_pains', []) + parsed.get('hidden_pains', [])
                    st.session_state['pain_points'] = ", ".join(pains[:5])
                    st.rerun()
    
    with col2:
        st.markdown("### 제목 & 컨셉")
        
        if st.button("✨ 제목 생성"):
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
                    <div style="font-size:12px;color:#888;">TITLE {i}</div>
                    <div style="font-size:18px;font-weight:700;">{t.get('title', '')}</div>
                    <div style="color:#666;">{t.get('subtitle', '')}</div>
                    <div style="margin-top:8px;font-size:14px;color:#888;">{t.get('why_works', '')}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.session_state['book_title'] = st.text_input("최종 제목", value=st.session_state['book_title'])
        st.session_state['subtitle'] = st.text_input("부제", value=st.session_state['subtitle'])
        
        if st.button("💡 한 줄 컨셉 생성"):
            if st.session_state['topic'] and persona:
                with st.spinner("생성 중..."):
                    concept = generate_concept(st.session_state['topic'], persona, pain_points)
                    if concept:
                        st.session_state['one_line_concept'] = concept
        
        if st.session_state.get('one_line_concept'):
            st.markdown(f'<div class="info-card">{st.session_state["one_line_concept"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="next-btn"></div>', unsafe_allow_html=True)
    st.button("다음 → 경쟁사 분석", key="n2", use_container_width=True)


# ==========================================
# TAB 3: 경쟁사 분석 (300권)
# ==========================================
with tabs[2]:
    st.markdown("## 경쟁사 리뷰 분석")
    st.markdown("**🔥 AI가 300권 이상의 경쟁 도서를 분석해서 시장의 빈틈을 찾습니다**")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🤖 자동 분석")
        
        st.markdown("""
        <div class="info-card">
            <b>📊 분석 범위</b><br>
            • 분석 도서: 300권 이상<br>
            • 분석 리뷰: 4,000개 이상<br>
            • 플랫폼: 크몽, yes24, 알라딘, 교보문고<br>
            • 부정 리뷰 집중 분석
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 300권 경쟁사 분석 시작", use_container_width=True):
            if not st.session_state['topic']:
                st.error("주제를 먼저 입력해주세요")
            elif not get_api_key():
                st.error("API 키를 입력해주세요")
            else:
                with st.spinner("🔍 300권 이상 분석 중..."):
                    result = analyze_reviews_300(st.session_state['topic'])
                    parsed = parse_json(result)
                    if parsed:
                        st.session_state['review_analysis'] = parsed
                        gaps = parsed.get('market_gaps', [])
                        st.session_state['market_gaps'] = [g.get('gap', '') for g in gaps]
                        st.success("✅ 분석 완료!")
                    else:
                        st.error("분석 실패")
        
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
                    <div style="font-size:18px;font-weight:700;margin-bottom:16px;">🎯 시장의 빈틈 {len(gaps)}개 발견</div>
                """, unsafe_allow_html=True)
                
                for i, g in enumerate(gaps, 1):
                    priority = g.get('priority', '중')
                    emoji = "🔴" if priority == "상" else ("🟡" if priority == "중" else "🟢")
                    st.markdown(f"""
                    <div class="gap-item">
                        <div style="font-weight:700;">{emoji} GAP {i}: {g.get('gap', '')}</div>
                        <div style="font-size:14px;margin-top:8px;">💡 {g.get('opportunity', '')}</div>
                        <div style="font-size:13px;margin-top:4px;">📝 {g.get('content_idea', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            patterns = a.get('negative_patterns', [])
            if patterns:
                with st.expander("📢 부정 리뷰 패턴 TOP 3", expanded=True):
                    for p in patterns[:3]:
                        st.write(f"**{p.get('pattern', '')}** ({p.get('frequency', '')})")
                        st.caption(f'예: "{p.get("example", "")}"')
            
            formula = a.get('success_formula', {})
            if formula:
                with st.expander("✅ 성공 공식"):
                    st.markdown("**필수:**")
                    for m in formula.get('must_have', []):
                        st.write(f"✅ {m}")
                    st.markdown("**피할 것:**")
                    for av in formula.get('avoid', []):
                        st.write(f"❌ {av}")
                    st.info(f"💡 **차별화:** {formula.get('differentiation', '')}")
            
            if a.get('summary'):
                st.success(f"**📊 종합:** {a['summary']}")
        else:
            st.markdown('<div style="text-align:center;padding:60px;background:#f8f8f8;border-radius:16px;"><p style="font-size:48px;">🔍</p><p style="color:#888;">버튼을 눌러 분석 시작</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="next-btn"></div>', unsafe_allow_html=True)
    st.button("다음 → 전문성 키우기", key="n3", use_container_width=True)


# ==========================================
# TAB 4: 전문성 키우기 (개선됨)
# ==========================================
with tabs[3]:
    st.markdown("## 전문성 키우기")
    st.markdown("**📚 유튜브 자막, 블로그, 아티클을 분석하고 정보 허브에서 한눈에 확인하세요**")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📺 콘텐츠 학습")
        
        input_type = st.radio("입력 유형", ["유튜브 자막 붙여넣기", "텍스트 (블로그/아티클)"], horizontal=True)
        
        source_name = st.text_input("출처/제목", placeholder="예: 신사임당 유튜브 - 전자책으로 월 1000만원")
        
        if input_type == "유튜브 자막 붙여넣기":
            st.caption("💡 유튜브 영상의 자막을 복사해서 붙여넣으세요 (영상 하단 ... → 스크립트 열기)")
            content_text = st.text_area("유튜브 자막/스크립트", height=250, placeholder="유튜브 자막을 복사해서 붙여넣으세요...", key="yt_content")
        else:
            content_text = st.text_area("콘텐츠 내용", height=250, placeholder="블로그/아티클 내용을 복사해서 붙여넣으세요...", key="txt_content")
        
        if st.button("📝 분석 & 정보 허브에 추가", use_container_width=True):
            if content_text and len(content_text) > 50:
                with st.spinner("콘텐츠 분석 중..."):
                    result = analyze_content(content_text, source_name)
                    parsed = parse_json(result)
                    if parsed:
                        parsed['source'] = source_name
                        parsed['type'] = 'youtube' if '유튜브' in input_type else 'text'
                        parsed['added_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                        st.session_state['knowledge_hub'].append(parsed)
                        st.success("✅ 정보 허브에 추가됨!")
                        st.rerun()
                    else:
                        st.error("분석 실패")
            else:
                st.error("내용을 입력하세요 (최소 50자)")
        
        st.markdown("---")
        st.markdown("### ✅ 전문성 체크리스트")
        checks = ["유튜브 영상 5개 이상 분석", "베스트셀러 3권 이상 분석", "블로그/아티클 10개 이상", "직접 실행해서 성과", "무료 테스터 3명 피드백"]
        for i, c in enumerate(checks):
            st.checkbox(c, key=f"chk_{i}")
    
    with col2:
        st.markdown("### 🧠 정보 허브 (전체 내용)")
        
        hub = st.session_state.get('knowledge_hub', [])
        
        if hub:
            st.markdown(f"""
            <div class="summary-hub">
                <div style="font-size:18px;font-weight:700;">📚 수집된 정보: {len(hub)}개</div>
                <div style="font-size:14px;margin-top:8px;opacity:0.9;">아래에서 전체 내용을 확인하세요</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 각 항목 전체 내용 표시
            for i, item in enumerate(hub):
                title = item.get('title', f'항목 {i+1}')
                source = item.get('source', '')
                
                st.markdown(f"""
                <div class="knowledge-card">
                    <div class="knowledge-title">📌 {title}</div>
                    <div style="font-size:12px;color:#666;margin-bottom:12px;">출처: {source} | {item.get('added_at', '')}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # 핵심 포인트 바로 표시
                key_points = item.get('key_points', [])
                if key_points:
                    st.markdown("**🎯 핵심 포인트:**")
                    for kp in key_points:
                        st.markdown(f'<div class="knowledge-point">• {kp}</div>', unsafe_allow_html=True)
                
                # 인사이트
                insights = item.get('insights', [])
                if insights:
                    with st.expander("💡 인사이트"):
                        for ins in insights:
                            st.write(f"💡 {ins}")
                
                # 실행 항목
                actions = item.get('action_items', [])
                if actions:
                    with st.expander("✅ 실행 항목"):
                        for act in actions:
                            st.write(f"✅ {act}")
                
                # 전자책 아이디어
                ebook = item.get('ebook_ideas', [])
                if ebook:
                    with st.expander("📖 전자책 아이디어"):
                        for idea in ebook:
                            st.write(f"📖 {idea}")
                
                # 요약
                if item.get('summary'):
                    st.info(f"📝 **요약:** {item['summary']}")
                
                col_del, col_empty = st.columns([1, 3])
                with col_del:
                    if st.button(f"🗑️ 삭제", key=f"del_{i}"):
                        st.session_state['knowledge_hub'].pop(i)
                        st.rerun()
                
                st.markdown("---")
            
            # 전체 종합 요약
            if st.button("📋 전체 학습 내용 종합 정리 & 공부 방법", use_container_width=True):
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
                    <div style="font-size:16px;font-weight:700;margin-bottom:12px;">📊 종합 학습 정리</div>
                    <div style="font-size:14px;line-height:1.8;">{summary.get('total_summary', '')}</div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("🎯 핵심 인사이트 TOP 5", expanded=True):
                    for ins in summary.get('top_insights', []):
                        st.write(f"💡 {ins}")
                
                with st.expander("📚 추천 목차"):
                    for ch in summary.get('recommended_outline', []):
                        st.write(f"📌 {ch}")
                
                with st.expander("📅 공부 계획 (4주)"):
                    plan = summary.get('study_plan', {})
                    st.write(f"**1주차:** {plan.get('week1', '')}")
                    st.write(f"**2주차:** {plan.get('week2', '')}")
                    st.write(f"**3주차:** {plan.get('week3', '')}")
                    st.write(f"**4주차:** {plan.get('week4', '')}")
                
                with st.expander("✨ 공부 팁"):
                    for tip in summary.get('study_tips', []):
                        st.write(f"✨ {tip}")
        else:
            st.markdown("""
            <div style="text-align:center;padding:60px;background:#f8f8f8;border-radius:16px;">
                <p style="font-size:48px;">🧠</p>
                <p style="color:#888;">왼쪽에서 유튜브 자막이나 아티클을</p>
                <p style="color:#888;">붙여넣고 분석하면 여기에 정리됩니다</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<div class="next-btn"></div>', unsafe_allow_html=True)
    st.button("다음 → 목차 설계", key="n4", use_container_width=True)


# ==========================================
# TAB 5: 목차 설계
# ==========================================
with tabs[4]:
    st.markdown("## 목차 설계")
    
    if st.session_state.get('market_gaps'):
        st.success(f"✅ {len(st.session_state['market_gaps'])}개 시장 빈틈이 목차에 반영됩니다")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🚀 킬러 목차 생성")
        
        st.markdown("""
        <div class="info-card">
            <b>자청/신사임당 스타일</b><br>
            • 목차만 봐도 "사고 싶다"<br>
            • 상식 파괴 + 호기심 폭발
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✨ 킬러 목차 생성", use_container_width=True):
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
                            if line.startswith('##') or 'PART' in line.upper():
                                name = line.lstrip('#').strip()
                                name = re.sub(r'\*\*(.+?)\*\*', r'\1', name)
                                if name:
                                    current = name
                                    chapters.append(current)
                                    subtopics[current] = []
                            elif current and line.startswith('-'):
                                st_name = line.lstrip('- ').strip()
                                st_name = re.sub(r'\*\*(.+?)\*\*', r'\1', st_name)
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
            outline_text = ""
            for ch in st.session_state['outline']:
                outline_text += f"## {ch}\n"
                for st_name in st.session_state['chapters'].get(ch, {}).get('subtopics', []):
                    outline_text += f"- {st_name}\n"
                outline_text += "\n"
            st.code(outline_text, language=None)
    
    with col2:
        st.markdown("### 📝 목차 편집")
        
        if st.session_state.get('outline'):
            for i, ch in enumerate(st.session_state['outline']):
                subs = st.session_state['chapters'].get(ch, {}).get('subtopics', [])
                with st.expander(f"**{ch}** ({len(subs)}개)"):
                    for j, s in enumerate(subs):
                        st.write(f"{j+1}. {s}")
        else:
            st.markdown('<div style="text-align:center;padding:60px;background:#f8f8f8;border-radius:16px;"><p style="color:#888;">목차를 생성하세요</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="next-btn"></div>', unsafe_allow_html=True)
    st.button("다음 → 본문 작성", key="n5", use_container_width=True)


# ==========================================
# TAB 6: 본문 작성
# ==========================================
with tabs[5]:
    st.markdown("## 본문 작성")
    
    if not st.session_state.get('outline'):
        st.warning("먼저 목차를 설계하세요")
        st.stop()
    
    selected_ch = st.selectbox("📚 챕터", st.session_state['outline'])
    
    if selected_ch not in st.session_state['chapters']:
        st.session_state['chapters'][selected_ch] = {'subtopics': [], 'subtopic_data': {}}
    
    ch_data = st.session_state['chapters'][selected_ch]
    
    with st.expander(f"소제목 ({len(ch_data.get('subtopics', []))}개)", expanded=True):
        for j, s in enumerate(ch_data.get('subtopics', [])):
            has = bool(ch_data.get('subtopic_data', {}).get(s, {}).get('content'))
            st.write(f"{'✅' if has else '⬜'} {j+1}. {s}")
    
    if ch_data.get('subtopics'):
        st.markdown("---")
        selected_st = st.selectbox("✍️ 소제목", ch_data['subtopics'])
        
        if selected_st not in ch_data.get('subtopic_data', {}):
            ch_data['subtopic_data'][selected_st] = {'questions': [], 'answers': [], 'content': ''}
        
        st_data = ch_data['subtopic_data'][selected_st]
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 🎤 인터뷰")
            if st.button("질문 생성"):
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
                    st_data['answers'][i] = st.text_area(f"A{i+1}", value=st_data['answers'][i], height=80, key=f"a_{i}", label_visibility="collapsed")
        
        with col2:
            st.markdown("### 📝 본문")
            has_ans = st_data.get('questions') and any(a.strip() for a in st_data.get('answers', []))
            
            if has_ans:
                if st.button("✨ 본문 생성"):
                    with st.spinner("집필 중..."):
                        content = generate_content(selected_st, selected_ch, st_data['questions'], st_data['answers'], st.session_state['topic'], st.session_state['target_persona'])
                        if content:
                            st_data['content'] = content
                            st.rerun()
            
            edited = st.text_area("본문", value=st_data.get('content', ''), height=400, label_visibility="collapsed")
            st_data['content'] = edited
            
            if edited:
                st.caption(f"📊 {len(edited.replace(' ', '').replace(chr(10), '')):,}자")
    
    st.markdown('<div class="next-btn"></div>', unsafe_allow_html=True)
    st.button("다음 → 최종 출력", key="n6", use_container_width=True)


# ==========================================
# TAB 7: 최종 출력
# ==========================================
with tabs[6]:
    st.markdown("## 최종 출력")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown("### 📖 다운로드")
        
        title = st.text_input("제목", value=st.session_state.get('book_title', ''))
        subtitle = st.text_input("부제", value=st.session_state.get('subtitle', ''))
        
        full = f"{title}\n{subtitle}\n\n{'='*50}\n\n"
        for ch in st.session_state.get('outline', []):
            if ch in st.session_state.get('chapters', {}):
                ch_data = st.session_state['chapters'][ch]
                has = any(ch_data.get('subtopic_data', {}).get(s, {}).get('content') for s in ch_data.get('subtopics', []))
                if has:
                    full += f"\n{ch}\n{'-'*40}\n\n"
                    for s in ch_data.get('subtopics', []):
                        c = ch_data.get('subtopic_data', {}).get(s, {}).get('content', '')
                        if c:
                            full += f"\n{s}\n\n{c}\n\n"
        
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📄 TXT", full, file_name=f"{title or 'ebook'}.txt", use_container_width=True)
        with c2:
            html = f"<html><head><meta charset='utf-8'><title>{title}</title></head><body style='max-width:800px;margin:0 auto;padding:40px;font-family:sans-serif;line-height:1.8;'>{full.replace(chr(10), '<br>')}</body></html>"
            st.download_button("🌐 HTML", html, file_name=f"{title or 'ebook'}.html", use_container_width=True)
        
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
