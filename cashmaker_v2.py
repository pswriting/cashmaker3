import streamlit as st
import google.generativeai as genai
import re
import json
import io
import os
from datetime import datetime
from pathlib import Path

# ==========================================
# API 키 저장/불러오기 (로컬 파일)
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

st.set_page_config(page_title="전자책 작성 프로그램", layout="wide", page_icon="◆")

st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif; }
    .stDeployButton {display:none;} 
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    [data-testid="collapsedControl"] { display: flex !important; visibility: visible !important; }
    .stApp { background: #ffffff; }
    .main .block-container { background: #ffffff; padding: 2rem 3rem; max-width: 1200px; }
    [data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #eeeeee; }
    [data-testid="stSidebar"] * { color: #222222 !important; }
    .stMarkdown, .stText, p, span, label, .stMarkdown p { color: #222222 !important; line-height: 1.7; }
    h1 { color: #111111 !important; font-weight: 700 !important; font-size: 2rem !important; }
    h2 { color: #111111 !important; font-weight: 700 !important; font-size: 1.4rem !important; }
    h3 { color: #222222 !important; font-weight: 600 !important; font-size: 1.1rem !important; }
    .stTabs [data-baseweb="tab-list"] { background: transparent; gap: 0; border-bottom: 2px solid #eeeeee; }
    .stTabs [data-baseweb="tab"] { background: transparent; color: #888888 !important; font-weight: 500; padding: 16px 24px; border-bottom: 2px solid transparent; margin-bottom: -2px; }
    .stTabs [aria-selected="true"] { background: transparent !important; color: #111111 !important; font-weight: 700 !important; border-bottom: 2px solid #111111 !important; }
    .stButton > button { width: 100%; border-radius: 30px; font-weight: 600; background: #111111 !important; color: #ffffff !important; border: none !important; padding: 14px 32px; }
    .stButton > button:hover { background: #333333 !important; }
    .stButton > button * { color: #ffffff !important; }
    .stDownloadButton > button { background: #2d5a27 !important; color: #ffffff !important; border-radius: 30px; }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea { background: #ffffff !important; border: 1px solid #dddddd !important; border-radius: 8px !important; color: #222222 !important; }
    .hero-section { text-align: center; padding: 60px 20px; margin-bottom: 40px; }
    .hero-label { font-size: 13px; font-weight: 600; color: #666666; letter-spacing: 3px; margin-bottom: 16px; }
    .hero-title { font-size: 42px; font-weight: 800; color: #111111; margin-bottom: 16px; }
    .hero-subtitle { font-size: 18px; color: #666666; }
    .section-label { font-size: 12px; font-weight: 600; color: #888888; letter-spacing: 2px; margin-bottom: 8px; }
    .score-card { background: #f8f8f8; border-radius: 20px; padding: 50px 40px; text-align: center; }
    .score-number { font-size: 80px; font-weight: 800; color: #111111; line-height: 1; margin-bottom: 8px; }
    .score-label { color: #888888; font-size: 14px; }
    .status-badge { display: inline-block; padding: 8px 20px; border-radius: 20px; font-weight: 600; font-size: 13px; margin-top: 20px; }
    .status-excellent { background: #111111; color: #ffffff; }
    .status-good { background: #f0f0f0; color: #333333; }
    .status-warning { background: #fff3e0; color: #e65100; }
    .info-card { background: #f8f8f8; border-radius: 16px; padding: 24px; margin: 16px 0; }
    .info-card-title { font-size: 12px; font-weight: 700; color: #888888; letter-spacing: 1px; margin-bottom: 12px; }
    .info-card p { color: #333333 !important; font-size: 15px; line-height: 1.8; margin: 8px 0; }
    .title-card { background: #ffffff; border: 1px solid #eeeeee; border-radius: 16px; padding: 24px; margin: 12px 0; }
    .title-card .card-number { font-size: 12px; font-weight: 600; color: #aaaaaa; margin-bottom: 8px; }
    .title-card .main-title { color: #111111; font-size: 18px; font-weight: 700; margin-bottom: 6px; }
    .title-card .sub-title { color: #666666; font-size: 14px; margin-bottom: 16px; }
    .title-card .reason { color: #444444; font-size: 14px; padding: 14px 16px; background: #f8f8f8; border-radius: 10px; }
    .score-item { background: #ffffff; border: 1px solid #eeeeee; border-radius: 12px; padding: 16px 20px; margin: 10px 0; display: flex; justify-content: space-between; }
    .score-item-label { color: #333333; font-weight: 500; }
    .score-item-value { color: #111111; font-weight: 700; font-size: 20px; }
    .score-item-reason { color: #666666; font-size: 14px; margin-top: 4px; }
    .summary-box { background: #f8f8f8; border-radius: 12px; padding: 20px; margin-top: 20px; }
    .empty-state { text-align: center; padding: 60px 20px; background: #f8f8f8; border-radius: 16px; }
    .empty-state p { color: #888888 !important; }
    .quick-action-box { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border: 1px dashed #dee2e6; border-radius: 16px; padding: 24px; margin: 16px 0; text-align: center; }
    .premium-footer { text-align: center; padding: 40px 20px; margin-top: 60px; border-top: 1px solid #eeeeee; }
    .premium-footer-text { color: #888888; font-size: 14px; }
    .premium-footer-author { color: #222222; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

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

default_states = {
    'topic': '', 'target_persona': '', 'pain_points': '', 'one_line_concept': '',
    'outline': [], 'chapters': {}, 'current_step': 1, 'market_analysis': '',
    'book_title': '', 'subtitle': '', 'topic_score': None, 'topic_verdict': None,
    'score_details': None, 'generated_titles': None, 'outline_mode': 'ai',
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
        any(ch.get('content') for ch in st.session_state['chapters'].values()) if st.session_state['chapters'] else False
    ]
    progress = sum(progress_items) / len(progress_items) * 100
    st.progress(progress / 100)
    st.caption(f"{progress:.0f}% 완료")
    
    st.markdown("---")
    st.markdown("### Info")
    if st.session_state['topic']:
        st.caption(f"주제: {st.session_state['topic']}")
    if st.session_state['book_title']:
        st.caption(f"제목: {st.session_state['book_title']}")
    if st.session_state['outline']:
        st.caption(f"목차: {len(st.session_state['outline'])}개")
    
    st.markdown("---")
    st.markdown("### 💾 저장/불러오기")
    save_data = {k: st.session_state.get(k, '') for k in ['topic', 'target_persona', 'pain_points', 'one_line_concept', 'outline', 'chapters', 'book_title', 'subtitle', 'market_analysis', 'topic_score', 'topic_verdict', 'score_details', 'generated_titles']}
    save_json = json.dumps(save_data, ensure_ascii=False, indent=2)
    file_name = re.sub(r'[^\w\s가-힣-]', '', st.session_state.get('book_title', '전자책') or '전자책')[:20]
    st.download_button("📥 작업 저장하기", save_json, file_name=f"{file_name}_{datetime.now().strftime('%m%d_%H%M')}.json", mime="application/json", use_container_width=True)
    
    uploaded_file = st.file_uploader("📤 작업 불러오기", type=['json'], label_visibility="collapsed")
    if uploaded_file is not None:
        try:
            loaded_data = json.loads(uploaded_file.read().decode('utf-8'))
            if st.button("불러오기 적용", use_container_width=True):
                for key in save_data.keys():
                    if key in loaded_data:
                        st.session_state[key] = loaded_data[key]
                st.success("불러오기 완료!")
                st.rerun()
        except Exception as e:
            st.error(f"파일 오류: {e}")
    
    st.markdown("---")
    st.markdown("### API 설정")
    if 'api_key' not in st.session_state:
        st.session_state['api_key'] = load_saved_api_key()
    
    api_key_input = st.text_input("Gemini API 키", value=st.session_state['api_key'], type="password", placeholder="AIza...")
    if api_key_input and api_key_input != st.session_state['api_key']:
        st.session_state['api_key'] = api_key_input
        save_api_key(api_key_input)
        st.toast("✅ API 키가 저장되었습니다!")
    elif api_key_input:
        st.session_state['api_key'] = api_key_input
    
    with st.expander("API 키 발급 방법 (무료)"):
        st.markdown("1. [Google AI Studio](https://aistudio.google.com/apikey) 접속\n2. Google 계정 로그인\n3. **API 키 만들기** 클릭\n4. 키 복사 후 붙여넣기")
    
    if not st.session_state.get('api_key'):
        st.caption("⚠️ API 키를 입력하세요")
    else:
        st.caption("✅ API 키 입력됨")

# --- AI 함수 ---
def get_api_key():
    return st.session_state.get('api_key', '')

def sync_full_outline():
    if not st.session_state.get('outline'):
        return
    new_full_outline = ""
    for ch in st.session_state['outline']:
        new_full_outline += f"## {ch}\n"
        if ch in st.session_state.get('chapters', {}):
            for st_name in st.session_state['chapters'][ch].get('subtopics', []):
                new_full_outline += f"- {st_name}\n"
        new_full_outline += "\n"
    st.session_state['full_outline'] = new_full_outline.strip()

def trigger_auto_save():
    sync_full_outline()
    st.session_state['auto_save_trigger'] = True

def ask_ai(system_role, prompt, temperature=0.7):
    api_key = get_api_key()
    if not api_key:
        return "⚠️ API 키를 먼저 입력해주세요."
    try:
        genai.configure(api_key=api_key)
        ai_model = genai.GenerativeModel('models/gemini-2.0-flash')
        generation_config = genai.types.GenerationConfig(temperature=temperature)
        full_prompt = f"당신은 {system_role}입니다.\n\n{prompt}\n\n반드시 한국어로만 답변하세요."
        response = ai_model.generate_content(full_prompt, generation_config=generation_config)
        return response.text
    except Exception as e:
        return f"오류 발생: {str(e)}"

# ==========================================
# 🔥 개선된 주제 분석 함수
# ==========================================
def analyze_topic_score(topic):
    prompt = f"""'{topic}' 주제의 전자책 적합도를 분석해주세요.

5가지 항목을 0~100점으로 채점:
1. 시장성 2. 수익성 3. 차별화 가능성 4. 작성 난이도 5. 지속성

JSON 형식으로만 답변:
{{"market": {{"score": 85, "reason": "이유"}}, "profit": {{"score": 80, "reason": "이유"}}, "differentiation": {{"score": 75, "reason": "이유"}}, "difficulty": {{"score": 90, "reason": "이유"}}, "sustainability": {{"score": 70, "reason": "이유"}}, "total_score": 80, "verdict": "적합", "summary": "종합 의견"}}"""
    return ask_ai("전자책 시장 분석가", prompt, temperature=0.3)

# ==========================================
# 🔥 개선된 제목 생성 함수
# ==========================================
def generate_titles_advanced(topic, persona, pain_points):
    prompt = f"""'{topic}' 전자책의 베스트셀러급 제목 5개를 만드세요.

타겟: {persona}
고민: {pain_points}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ 망하는 제목 → ✅ 40만부 팔리는 제목
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"부자 되는 방법" → "역행자"
"투자 노하우" → "부의 추월차선"
"돈 버는 비결" → "돈의 속성"
"성공 전략 가이드" → "타이탄의 도구들"
"시간 관리 비법" → "아침형 인간"

💀 절대 금지: ~하는 방법, ~하는 법, 노하우, 비결, 가이드, 비법

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 제목 공식
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【역설】 상식을 뒤집는 한 단어/문장
【도발】 불편하지만 끌리는 표현
【상징】 개념을 상징하는 새로운 단어
【숫자】 구체적 결과가 보이는 숫자
【비밀】 감춰진 진실을 암시

JSON 형식으로만:
{{"titles": [
  {{"title": "제목", "subtitle": "부제", "concept": "컨셉", "why_works": "왜 끌리는지"}}
]}}"""
    return ask_ai("베스트셀러 작가", prompt, temperature=0.95)

def generate_concept(topic, persona, pain_points):
    prompt = f"""주제: {topic}
타겟: {persona}
고민: {pain_points}

"이 책 안 읽으면 손해"라는 한 줄 컨셉 5개:

1. [컨셉] → 왜 끌리는가
2. [컨셉] → 왜 끌리는가
3. [컨셉] → 왜 끌리는가
4. [컨셉] → 왜 끌리는가
5. [컨셉] → 왜 끌리는가"""
    return ask_ai("카피라이터", prompt, temperature=0.9)

# ==========================================
# 🔥 핵심 개선: 목차 생성 함수 (베스트셀러 분석 기반)
# ==========================================
def generate_outline(topic, persona, pain_points):
    prompt = f"""당신은 40만부 베스트셀러 작가입니다.

'{topic}' 주제로 목차를 만드세요.
타겟: {persona}
고민: {pain_points}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 [핵심] 같은 내용도 제목에 따라 클릭률이 10배 차이남
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ 망하는 제목 → ✅ 팔리는 제목

"시간 관리의 중요성" → "새벽 4시, 나는 왜 일어나는가"
"부업 시작하기" → "월급 외 첫 100만원이 들어오던 날"
"마인드셋 바꾸기" → "모방하는 한심한 인생에 대하여"
"성공하는 습관" → "왜 열심히 할수록 가난해지는가"
"투자 기초" → "삼성전자 주식을 삼성증권에서 사는 사람"
"목표 설정법" → "3년 뒤에도 지금과 똑같다면"
"실패 극복하기" → "나는 '운 좋게' 최악의 인생을 살았다"
"재테크 전략" → "통장에 47만원, 그날 깨달은 것"
"자기계발 필요성" → "당신이 노예인 줄도 모르는 이유"
"전문성 키우기" → "업계 사람들이 절대 안 알려주는 것"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💀 절대 금지 단어 (쓰면 아무도 안 읽음)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

~하는 방법, ~하는 법, ~의 중요성, ~의 필요성
효과적인, 성공적인, 완벽한, 핵심, 비결, 비법
노하우, 마인드셋, 가이드, 전략, 팁
첫 번째, 두 번째, STEP 1, Part 1
시작하기, 기초, 입문, 이해하기

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 베스트셀러에서 직접 뽑은 6가지 공식
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【공식1: 역설】 상식의 반대를 말해서 "엥?" 하게
"빨리 부자가 되려면, 빨리 부자가 되려 하면 안 된다"
"리스크가 클 때가 리스크가 가장 작을 때다"
"전문분야? 오히려 없는 게 더 낫다"

【공식2: 도발】 독자를 직접 찔러서 "뜨끔" 하게
"모방하는 한심한 인생에 대하여"
"평범하다는 것은 현대판 노예라는 뜻이다"
"당신이 부의 길이라고 믿었던 것들의 함정"

【공식3: 질문】 당연한 걸 뒤집어서 "왜지?" 궁금하게
"달걀을 한 바구니에 담지 않았는데 왜 모두 깨질까?"
"왜 배운 사람일수록 가난에서 못 벗어날까"
"절약만으로는 절대 부자가 될 수 없는 이유"

【공식4: 숫자+장면】 구체적이어서 "진짜네" 신뢰하게
"10페이지로 1천만 원을 벌다"
"통장에 47만원, 그날 나는 깨달았다"
"월급 250만원으로 3년 만에 1억 만든 공식"

【공식5: 비밀】 숨겨진 정보를 암시해서 "나만 모르나?" 불안하게
"업계 사람들은 가르쳐주지 않는 것"
"그들의 언어 패턴을 걸러내는 법"
"아무도 말 안 하는 진짜 게임의 룰"

【공식6: 시나리오】 상상하게 만들어서 "나라면?" 몰입하게
"내가 청년으로 다시 돌아가 부자가 되려 한다면"
"만약 3년 후에도 지금과 똑같다면"
"100억을 상속받았는데 절대 잃지 말라는 유언이 붙었다면"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 출력 형식 (정확히 이 형식만, 설명 없이)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 챕터1: [도발/역설 - 독자가 "내 얘기다" 느끼게]
- [역설 또는 도발 공식 사용]
- [숫자+장면 공식 사용]
- [질문 공식 사용]

## 챕터2: [질문/비밀 - "이래서 안 됐구나" 깨닫게]
- [비밀 공식 사용]
- [역설 공식 사용]
- [도발 공식 사용]

## 챕터3: [숫자+장면/역설 - "나도 할 수 있겠다" 희망주기]
- [숫자+장면 공식 사용]
- [시나리오 공식 사용]
- [역설 공식 사용]

## 챕터4: [시나리오/비밀 - "당장 해야겠다" 행동 촉구]
- [시나리오 공식 사용]
- [비밀 공식 사용]
- [숫자+장면 공식 사용]

'{topic}' 주제로 위 공식들을 적용해서 목차를 작성하세요.
각 제목은 독자가 "이건 꼭 읽어봐야겠다"고 느끼게 만드세요."""
    return ask_ai("40만부 베스트셀러 작가", prompt, temperature=0.95)

def regenerate_chapter_outline(chapter_number, topic, persona, existing_chapters):
    prompt = f"""'{topic}' 전자책의 {chapter_number}번째 챕터를 새로 작성하세요.

기존 챕터들: {existing_chapters}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ 망하는 챕터 제목 → ✅ 팔리는 챕터 제목
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"성공을 위한 마인드셋" → "모방하는 한심한 인생에 대하여"
"효과적인 시간 관리" → "당신이 노예인 줄도 모르는 이유"
"수익 창출 전략" → "10페이지로 1천만 원을 벌다"
"실패를 통한 교훈" → "나는 '운 좋게' 최악의 인생을 살았다"
"목표 달성 가이드" → "3년 뒤에도 지금과 똑같다면"
"기초부터 배우기" → "업계 사람들이 절대 안 알려주는 것"

💀 금지: ~하는 방법, ~의 중요성, 노하우, 전략, 마인드셋

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 출력 (정확히 이 형식만)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 챕터{chapter_number}: [도발/역설/질문/숫자+장면 중 하나]
- [역설 또는 도발 형태]
- [숫자+구체적 상황]
- [비밀 또는 시나리오 형태]"""
    return ask_ai("베스트셀러 작가", prompt, temperature=0.95)

def regenerate_single_subtopic(chapter_title, subtopic_index, topic, existing_subtopics):
    prompt = f"""'{topic}' 전자책의 '{chapter_title}' 챕터에서 {subtopic_index}번 소제목을 새로 작성하세요.

기존: {existing_subtopics}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ 망하는 제목 → ✅ 팔리는 제목
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"시간 관리" → "새벽 4시, 나는 왜 일어나는가"
"수익 창출" → "월급 외 첫 100만원이 들어오던 날"
"마인드 변화" → "모방하는 한심한 인생에 대하여"
"성공 습관" → "왜 열심히 할수록 가난해지는가"
"기초 배우기" → "업계 사람들이 절대 안 알려주는 것"

💀 금지: ~하는 방법, ~의 중요성, 노하우, 전략, 마인드셋

소제목 하나만 출력 (설명 없이):"""
    result = ask_ai("베스트셀러 작가", prompt, temperature=0.95)
    result = result.strip().strip('[]').strip('-').strip()
    if '\n' in result:
        result = result.split('\n')[0].strip()
    return result

def generate_subtopics(chapter_title, topic, persona, num_subtopics=3):
    prompt = f"""'{topic}' 전자책의 '{chapter_title}' 챕터 소제목 {num_subtopics}개를 작성하세요.

타겟: {persona}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ 망하는 제목 → ✅ 팔리는 제목
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"목표 설정" → "3년 뒤에도 지금과 똑같다면"
"실패 극복" → "나는 '운 좋게' 최악의 인생을 살았다"
"재테크 기초" → "통장에 47만원, 그날 깨달은 것"
"자기계발" → "당신이 노예인 줄도 모르는 이유"
"전문성 향상" → "업계 사람들이 절대 안 알려주는 것"
"첫 시작" → "10페이지로 1천만 원을 벌다"

💀 금지: ~하는 방법, ~의 중요성, 노하우, 전략, 마인드셋, 비결

숫자와 소제목만:
1. [소제목]
2. [소제목]
3. [소제목]"""
    return ask_ai("베스트셀러 작가", prompt, temperature=0.95)

# ==========================================
# 🔥 핵심 개선: 인터뷰 질문 생성
# ==========================================
def generate_interview_questions(subtopic_title, chapter_title, topic):
    prompt = f"""'{topic}' 전자책의 '{chapter_title}' 챕터 중 '{subtopic_title}' 부분을 작성하려 합니다.

작가의 진짜 경험과 통찰을 끌어내는 질문 3개:

🔥 좋은 질문:
1. 구체적 장면: "그 순간 어디에 있었고, 무엇을 보고 있었나요?"
2. 감정과 숫자: "그때 통장 잔고가 얼마였고, 어떤 기분이었나요?"
3. 반전/깨달음: "모든 게 바뀐 결정적 순간은 언제였나요?"

❌ 피해야 할 질문:
- "~에 대해 설명해주세요" (추상적)
- "~가 중요한 이유는?" (설교 유발)

형식:
Q1: [구체적 장면/감정 질문]
Q2: [숫자/데이터 질문]
Q3: [반전/깨달음 질문]"""
    return ask_ai("베스트셀러 고스트라이터", prompt, temperature=0.7)

# ==========================================
# 🔥 핵심 개선: 자청 스타일 본문 생성
# ==========================================
def generate_subtopic_content(subtopic_title, chapter_title, questions, answers, topic, persona):
    qa_pairs = ""
    for i, (q, a) in enumerate(zip(questions, answers), 1):
        if a.strip():
            qa_pairs += f"\n질문{i}: {q}\n답변{i}: {a}\n"
    
    prompt = f"""당신은 '자청', '프드프'처럼 독자를 사로잡는 베스트셀러 작가입니다.

주제: {topic}
챕터: {chapter_title}
소제목: {subtopic_title}
타겟: {persona}

[작가 인터뷰]
{qa_pairs}

===================================
🔥 자청 스타일 글쓰기 공식
===================================

[1. 첫 문장 = 후킹]
❌ "오늘은 ~에 대해 이야기해보겠습니다"
✅ "저는 그날 회사를 그만뒀습니다."
✅ "통장 잔고 47만원. 그게 전부였습니다."

[2. 구체적 장면]
❌ "힘든 시간이었습니다"
✅ "새벽 4시, 원룸 책상 앞. 손이 떨렸습니다."

❌ "경제적으로 어려웠습니다"
✅ "편의점 삼각김밥 하나가 하루 식사였습니다."

[3. 감정 + 숫자 = 신뢰]
- 시간: "새벽 4시", "퇴근 후 11시"
- 금액: "47만원", "월 300만원"
- 기간: "3개월", "1년 6개월"
- 감정: "손이 떨렸습니다", "눈물이 났습니다"

[4. 스토리 구조]
평범한 일상 → 문제/위기 → 고민과 시도 → 깨달음 → 변화

💡 교훈을 말하지 말고 이야기로 보여주세요
❌ "포기하지 않는 것이 중요합니다"
✅ "57번째 거절을 받고 나서야 깨달았습니다. 문제는 제안서가 아니었습니다."

[5. 독자 공감]
- "당신도 그런 적 있지 않나요?"
- "솔직히 말씀드릴게요."
- "저도 처음엔 몰랐습니다."

===================================
📝 문단 구성 (매우 중요!)
===================================

✅ 올바른 예시:
저는 그날 새벽 4시에 눈을 떴습니다. 통장 잔고는 47만원. 다음 달 월세를 내면 남는 건 없었습니다. 천장을 바라보며 생각했습니다. 이대로는 안 되겠다고.

그때 우연히 본 영상 하나가 제 인생을 바꿨습니다. 별거 아닌 내용이었습니다. 하지만 그 안에 제가 몰랐던 진실이 있었습니다.

❌ 잘못된 예시 (한 문장씩 띄어쓰기):
저는 그날 새벽 4시에 눈을 떴습니다.

통장 잔고는 47만원.

===================================
🚫 절대 금지
===================================
- "~하는 것이 중요합니다" (설교)
- "첫째, 둘째, 셋째" (나열)
- 번호, 불릿, 마크다운
- 한 문장씩 띄어쓰기

[분량] 1500~2000자
[문체] 존댓말 (~입니다, ~습니다)

'{subtopic_title}' 본문을 작성하세요."""

    return ask_ai("베스트셀러 작가", prompt, temperature=0.75)

def refine_content(content, style="친근한"):
    style_map = {
        "친근한": "존댓말, 독자에게 직접 말하듯, 공감 표현",
        "전문적": "존댓말, 데이터와 논리 강조",
        "직설적": "존댓말, 핵심만 간결하게",
        "스토리텔링": "존댓말, 구체적 장면, 감정과 숫자"
    }
    prompt = f"""글을 다듬어주세요.

[원본]
{content}

[수정사항]
1. 한 문단 = 3~5문장 붙여서
2. 한 문장씩 띄어쓰기 금지
3. 존댓말 통일
4. 구조화 표현 제거
5. 마크다운 제거

[스타일] {style_map.get(style, style_map["친근한"])}

다듬어진 글만 출력:"""
    return ask_ai("에디터", prompt, temperature=0.7)

def check_quality(content):
    prompt = f"""베스트셀러 수준 평가:

{content[:4000]}

[평가 기준] 각 10점
1. 첫 문장 후킹
2. 몰입도
3. 공감력
4. 구체성 (장면/숫자)
5. 문단 구성 (3~5문장 묶음)
6. AI 티 (-점)

출력:
📊 종합: __/60점

📌 항목별 점수

✍️ 수정 제안 TOP 3

🎯 총평"""
    return ask_ai("베스트셀러 편집자", prompt, temperature=0.6)

def generate_marketing_copy(title, subtitle, topic, persona):
    prompt = f"""제목: {title}
부제: {subtitle}
주제: {topic}
타겟: {persona}

마케팅 카피:
1. 크몽 상품 제목 (40자 이내)
2. 헤드라인 3개
3. CTA 3개
4. 인스타 홍보 문구
5. 블로그 제목 3개"""
    return ask_ai("크몽 탑셀러 마케터", prompt, temperature=0.85)

# 헬퍼 함수들
def calculate_char_count(text):
    if not text:
        return 0
    return len(text.replace('\n', '').replace(' ', ''))

def clean_content_for_display(content, subtopic_title=None, chapter_title=None):
    if not content:
        return ""
    content = re.sub(r'<[^>]+>', '', content)
    lines = content.split('\n')
    cleaned_lines = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            if idx > 3 or len(cleaned_lines) > 0:
                cleaned_lines.append(line)
            continue
        if stripped.startswith('#'):
            continue
        if stripped.startswith('챕터') and ':' in stripped[:15]:
            continue
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines).strip()

def get_all_content_text():
    pure_content = ""
    for ch in st.session_state.get('outline', []):
        if ch in st.session_state.get('chapters', {}):
            ch_data = st.session_state['chapters'][ch]
            if 'subtopic_data' in ch_data:
                subtopic_list = ch_data.get('subtopics', [])
                if not subtopic_list and ch in ch_data['subtopic_data']:
                    subtopic_list = [ch]
                for st_name in subtopic_list:
                    st_data = ch_data['subtopic_data'].get(st_name, {})
                    if st_data.get('content'):
                        pure_content += st_data['content']
    return pure_content

# --- 메인 UI ---
st.markdown("""
<div class="hero-section">
    <div class="hero-label">CASHMAKER</div>
    <div class="hero-title">전자책 작성 프로그램</div>
    <div class="hero-subtitle">쉽고, 빠른 전자책 수익화</div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["① 주제 선정", "② 타겟 & 컨셉", "③ 목차 설계", "④ 본문 작성", "⑤ 문체 다듬기", "⑥ 최종 출력"])

# === TAB 1: 주제 선정 ===
with tabs[0]:
    st.markdown("## 주제 선정 & 적합도 분석")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<p class="section-label">Step 01</p>', unsafe_allow_html=True)
        st.markdown("### 주제 입력")
        topic_input = st.text_input("어떤 주제로 전자책을 쓰고 싶으세요?", value=st.session_state['topic'], placeholder="예: 크몽으로 월 500만원 벌기")
        if topic_input != st.session_state['topic']:
            st.session_state['topic'] = topic_input
            st.session_state['topic_score'] = None
        
        st.markdown("""<div class="info-card"><div class="info-card-title">좋은 주제의 조건</div>
        <p>• 내가 직접 경험하고 성과를 낸 것</p>
        <p>• 사람들이 돈 주고 배우고 싶어하는 것</p>
        <p>• 구체적인 결과를 약속할 수 있는 것</p></div>""", unsafe_allow_html=True)
        
        if st.button("📊 적합도 분석하기 (선택)", key="analyze_btn"):
            if not topic_input:
                st.error("주제를 입력해주세요.")
            else:
                with st.spinner("분석 중..."):
                    result = analyze_topic_score(topic_input)
                    try:
                        json_match = re.search(r'\{[\s\S]*\}', result)
                        if json_match:
                            score_data = json.loads(json_match.group())
                            st.session_state['topic_score'] = score_data.get('total_score', 0)
                            st.session_state['topic_verdict'] = score_data.get('verdict', '분석 실패')
                            st.session_state['score_details'] = score_data
                    except:
                        st.error("분석 오류. 다시 시도해주세요.")
    
    with col2:
        st.markdown('<p class="section-label">Step 02</p>', unsafe_allow_html=True)
        st.markdown("### 분석 결과")
        if st.session_state['topic_score'] is not None:
            score = st.session_state['topic_score']
            verdict = st.session_state['topic_verdict']
            details = st.session_state['score_details']
            verdict_class = "status-excellent" if verdict == "적합" else ("status-good" if verdict == "보통" else "status-warning")
            st.markdown(f"""<div class="score-card"><div class="score-number">{score}</div><div class="score-label">종합 점수</div><span class="status-badge {verdict_class}">{verdict}</span></div>""", unsafe_allow_html=True)
            if details:
                for name, key in [("시장성", "market"), ("수익성", "profit"), ("차별화", "differentiation"), ("작성 난이도", "difficulty"), ("지속성", "sustainability")]:
                    st.markdown(f"""<div class="score-item"><span class="score-item-label">{name}</span><span class="score-item-value">{details.get(key, {}).get('score', 0)}</span></div><p class="score-item-reason">{details.get(key, {}).get('reason', '')}</p>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state"><p>분석은 선택사항입니다.</p></div>', unsafe_allow_html=True)

# === TAB 2: 타겟 & 컨셉 ===
with tabs[1]:
    st.markdown("## 타겟 설정 & 제목 생성")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<p class="section-label">Step 01</p>', unsafe_allow_html=True)
        st.markdown("### 타겟 정의")
        if not st.session_state['topic']:
            topic_here = st.text_input("주제", value=st.session_state['topic'], placeholder="예: 크몽으로 월 500만원 벌기", key="topic_tab2")
            if topic_here:
                st.session_state['topic'] = topic_here
        
        persona = st.text_area("누가 이 책을 읽나요?", value=st.session_state['target_persona'], placeholder="예: 30대 직장인, 부업으로 월 100만원 원하는 사람", height=100)
        st.session_state['target_persona'] = persona
        
        pain_points = st.text_area("타겟의 가장 큰 고민은?", value=st.session_state['pain_points'], placeholder="예: 시간이 없다, 뭘 해야 할지 모르겠다", height=100)
        st.session_state['pain_points'] = pain_points
        
        st.markdown("---")
        st.markdown("### 한 줄 컨셉")
        if st.button("컨셉 생성하기", key="concept_btn"):
            if not st.session_state['topic'] or not persona:
                st.error("주제와 타겟을 먼저 입력해주세요.")
            else:
                with st.spinner("생성 중..."):
                    st.session_state['one_line_concept'] = generate_concept(st.session_state['topic'], persona, pain_points)
        if st.session_state['one_line_concept']:
            st.markdown(f'<div class="info-card">{st.session_state["one_line_concept"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<p class="section-label">Step 02</p>', unsafe_allow_html=True)
        st.markdown("### 제목 생성")
        if st.button("제목 생성하기", key="title_btn"):
            if not st.session_state['topic']:
                st.error("주제를 먼저 입력해주세요.")
            else:
                with st.spinner("생성 중..."):
                    titles_result = generate_titles_advanced(st.session_state['topic'], st.session_state['target_persona'], st.session_state['pain_points'])
                    try:
                        json_match = re.search(r'\{[\s\S]*\}', titles_result)
                        if json_match:
                            st.session_state['generated_titles'] = json.loads(json_match.group())
                    except:
                        st.session_state['generated_titles'] = None
        
        if st.session_state.get('generated_titles') and 'titles' in st.session_state['generated_titles']:
            for i, t in enumerate(st.session_state['generated_titles']['titles'], 1):
                st.markdown(f"""<div class="title-card"><div class="card-number">TITLE 0{i}</div><div class="main-title">{t.get('title', '')}</div><div class="sub-title">{t.get('subtitle', '')}</div><div class="reason">{t.get('why_works', '')}</div></div>""", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 최종 선택")
        st.session_state['book_title'] = st.text_input("제목", value=st.session_state['book_title'], placeholder="최종 제목")
        st.session_state['subtitle'] = st.text_input("부제", value=st.session_state['subtitle'], placeholder="부제")

# === TAB 3: 목차 설계 ===
with tabs[2]:
    st.markdown("## 목차 설계")
    outline_mode = st.radio("목차를 어떻게 만드시겠어요?", ["🤖 자동으로 목차 생성", "✍️ 내가 직접 입력"], horizontal=True, key="outline_mode_radio")
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if outline_mode == "🤖 자동으로 목차 생성":
            st.markdown("### 목차를 자동으로 설계합니다")
            if not st.session_state['topic']:
                st.warning("💡 주제를 먼저 입력해주세요")
                topic_here = st.text_input("주제", value=st.session_state['topic'], placeholder="예: 크몽으로 월 500만원 벌기", key="topic_tab3")
                if topic_here:
                    st.session_state['topic'] = topic_here
            
            if st.button("🚀 목차 생성하기", key="outline_btn"):
                if not st.session_state['topic']:
                    st.error("주제를 먼저 입력해주세요.")
                else:
                    with st.spinner("베스트셀러급 목차 설계 중..."):
                        outline_text = generate_outline(st.session_state['topic'], st.session_state['target_persona'], st.session_state['pain_points'])
                        lines = outline_text.split('\n')
                        chapters = []
                        current_chapter = None
                        chapter_subtopics = {}
                        
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                            line_lower = line.lower()
                            is_chapter = line.startswith('##') or any(line_lower.startswith(kw) for kw in ['챕터', 'chapter'])
                            if not is_chapter and len(line) > 1 and line[0].isdigit():
                                rest = line[1:].lstrip('0123456789')
                                if rest and rest[0] in '부장.:':
                                    is_chapter = True
                            
                            if is_chapter:
                                chapter_name = line.lstrip('#').strip()
                                current_chapter = chapter_name
                                chapters.append(current_chapter)
                                chapter_subtopics[current_chapter] = []
                            elif current_chapter and (line.startswith('-') or (line[0].isdigit() and ')' in line[:5])):
                                subtopic = line.lstrip('-·• ')
                                subtopic = re.sub(r'^\d+\)\s*', '', subtopic)
                                if subtopic:
                                    chapter_subtopics[current_chapter].append(subtopic)
                        
                        st.session_state['outline'] = chapters
                        st.session_state['full_outline'] = outline_text
                        for ch in chapters:
                            subtopics = chapter_subtopics.get(ch, [])
                            st.session_state['chapters'][ch] = {'subtopics': subtopics, 'subtopic_data': {st: {'questions': [], 'answers': [], 'content': ''} for st in subtopics}}
                        
                        st.success(f"✅ {len(chapters)}개 챕터, {sum(len(chapter_subtopics.get(ch, [])) for ch in chapters)}개 소제목 생성됨!")
                        st.rerun()
            
            if st.session_state.get('full_outline'):
                st.markdown("**📋 현재 목차**")
                st.code(st.session_state['full_outline'], language=None)
        else:
            st.markdown("### 목차를 직접 입력하세요")
            existing_outline = ""
            if st.session_state['outline']:
                for ch in st.session_state['outline']:
                    existing_outline += f"{ch}\n"
                    if ch in st.session_state['chapters']:
                        for i, st_name in enumerate(st.session_state['chapters'][ch].get('subtopics', []), 1):
                            existing_outline += f"{i}) {st_name}\n"
            
            manual_outline = st.text_area("목차 입력", value=existing_outline, height=350, placeholder="챕터1: 제목\n1) 소제목\n2) 소제목\n...")
            
            if st.button("✅ 목차 저장하기", key="save_manual"):
                if manual_outline.strip():
                    lines = manual_outline.strip().split('\n')
                    chapters = []
                    current_chapter = None
                    chapter_subtopics = {}
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        is_chapter = any(line.lower().startswith(kw) for kw in ['챕터', 'chapter', '에필로그', '프롤로그'])
                        if not is_chapter and len(line) > 2 and line[0].isdigit():
                            rest = line[1:].lstrip('0123456789')
                            if rest and rest[0] in '부장.:':
                                is_chapter = True
                        
                        if is_chapter:
                            current_chapter = line
                            chapters.append(current_chapter)
                            chapter_subtopics[current_chapter] = []
                        elif current_chapter:
                            subtopic = line.lstrip('-·• ')
                            subtopic = re.sub(r'^\d+\)\s*', '', subtopic).strip()
                            if subtopic and len(subtopic) > 2:
                                chapter_subtopics[current_chapter].append(subtopic)
                    
                    st.session_state['outline'] = chapters
                    st.session_state['full_outline'] = manual_outline
                    for ch in chapters:
                        subtopics = chapter_subtopics.get(ch, [])
                        st.session_state['chapters'][ch] = {'subtopics': subtopics, 'subtopic_data': {st_name: {'questions': [], 'answers': [], 'content': ''} for st_name in subtopics}}
                    st.success(f"✅ {len(chapters)}개 챕터 저장됨!")
                    st.rerun()
    
    with col2:
        st.markdown("### 📋 현재 목차")
        if st.session_state['outline']:
            for i, chapter in enumerate(st.session_state['outline']):
                subtopic_count = len(st.session_state['chapters'].get(chapter, {}).get('subtopics', []))
                with st.expander(f"**{chapter}** ({subtopic_count}개)", expanded=False):
                    col_edit, col_actions = st.columns([3, 2])
                    with col_edit:
                        new_title = st.text_input("챕터 제목", value=chapter, key=f"edit_ch_{i}", label_visibility="collapsed")
                    with col_actions:
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("🔄", key=f"regen_ch_{i}", help="재생성"):
                                with st.spinner("재생성 중..."):
                                    new_text = regenerate_chapter_outline(i+1, st.session_state['topic'], st.session_state['target_persona'], st.session_state['outline'])
                                    lines = new_text.split('\n')
                                    new_ch_title = None
                                    new_sts = []
                                    for line in lines:
                                        line = line.strip()
                                        if line.startswith('##'):
                                            new_ch_title = line.lstrip('#').strip()
                                        elif line.startswith('-'):
                                            st_name = line.lstrip('- ').strip()
                                            if st_name:
                                                new_sts.append(st_name)
                                    if new_ch_title:
                                        old_ch = st.session_state['outline'][i]
                                        st.session_state['outline'][i] = new_ch_title
                                        if old_ch in st.session_state['chapters']:
                                            del st.session_state['chapters'][old_ch]
                                        st.session_state['chapters'][new_ch_title] = {'subtopics': new_sts, 'subtopic_data': {st: {'questions': [], 'answers': [], 'content': ''} for st in new_sts}}
                                        st.rerun()
                        with c2:
                            if st.button("🗑️", key=f"del_ch_{i}", help="삭제"):
                                old_ch = st.session_state['outline'].pop(i)
                                if old_ch in st.session_state['chapters']:
                                    del st.session_state['chapters'][old_ch]
                                st.rerun()
                    
                    if new_title != chapter and new_title.strip():
                        if st.button("💾 저장", key=f"save_ch_{i}"):
                            st.session_state['outline'][i] = new_title
                            if chapter in st.session_state['chapters']:
                                st.session_state['chapters'][new_title] = st.session_state['chapters'].pop(chapter)
                            st.rerun()
                    
                    st.markdown("---")
                    st.markdown("**소제목:**")
                    if chapter in st.session_state['chapters']:
                        for j, st_name in enumerate(st.session_state['chapters'][chapter].get('subtopics', [])):
                            c1, c2 = st.columns([4, 1])
                            with c1:
                                new_st = st.text_input(f"소제목 {j+1}", value=st_name, key=f"st_{i}_{j}", label_visibility="collapsed")
                            with c2:
                                if st.button("🔄", key=f"regen_st_{i}_{j}"):
                                    with st.spinner("재생성 중..."):
                                        new_st_title = regenerate_single_subtopic(chapter, j+1, st.session_state['topic'], st.session_state['chapters'][chapter].get('subtopics', []))
                                        if new_st_title:
                                            old_st = st.session_state['chapters'][chapter]['subtopics'][j]
                                            st.session_state['chapters'][chapter]['subtopics'][j] = new_st_title
                                            if old_st in st.session_state['chapters'][chapter].get('subtopic_data', {}):
                                                st.session_state['chapters'][chapter]['subtopic_data'][new_st_title] = st.session_state['chapters'][chapter]['subtopic_data'].pop(old_st)
                                            else:
                                                st.session_state['chapters'][chapter]['subtopic_data'][new_st_title] = {'questions': [], 'answers': [], 'content': ''}
                                            st.rerun()
                            if new_st != st_name and new_st.strip():
                                if st.button("💾", key=f"save_st_{i}_{j}"):
                                    st.session_state['chapters'][chapter]['subtopics'][j] = new_st
                                    if st_name in st.session_state['chapters'][chapter].get('subtopic_data', {}):
                                        st.session_state['chapters'][chapter]['subtopic_data'][new_st] = st.session_state['chapters'][chapter]['subtopic_data'].pop(st_name)
                                    st.rerun()
            
            if st.button("➕ 새 챕터 추가"):
                new_ch = f"챕터{len(st.session_state['outline'])+1}: 새 챕터"
                st.session_state['outline'].append(new_ch)
                st.session_state['chapters'][new_ch] = {'subtopics': [], 'subtopic_data': {}}
                st.rerun()
        else:
            st.markdown('<div class="empty-state"><p>왼쪽에서 목차를 생성하세요</p></div>', unsafe_allow_html=True)

# === TAB 4: 본문 작성 ===
with tabs[3]:
    st.markdown("## 본문 작성")
    
    if not st.session_state['outline']:
        st.warning("⚠️ 먼저 '③ 목차 설계' 탭에서 목차를 작성해주세요.")
        st.stop()
    
    chapter_list = [item for item in st.session_state['outline'] if not item.strip().startswith('-')]
    if not chapter_list:
        st.warning("⚠️ 챕터가 없습니다.")
        st.stop()
    
    selected_chapter = st.selectbox("📚 챕터 선택", chapter_list, key="chapter_select")
    
    if selected_chapter not in st.session_state['chapters']:
        st.session_state['chapters'][selected_chapter] = {'subtopics': [], 'subtopic_data': {}}
    
    chapter_data = st.session_state['chapters'][selected_chapter]
    if 'subtopics' not in chapter_data:
        chapter_data['subtopics'] = []
    if 'subtopic_data' not in chapter_data:
        chapter_data['subtopic_data'] = {}
    
    for st_name in chapter_data['subtopics']:
        if st_name not in chapter_data['subtopic_data']:
            chapter_data['subtopic_data'][st_name] = {'questions': [], 'answers': [], 'content': ''}
    
    st.markdown("---")
    
    if chapter_data['subtopics']:
        st.markdown("### ✍️ 소제목 선택 → 본문 작성")
        selected_subtopic = st.selectbox("작성할 소제목", chapter_data['subtopics'], key="subtopic_select",
            format_func=lambda x: f"{'✅' if chapter_data['subtopic_data'].get(x, {}).get('content') else '⬜'} {x}")
        
        completed = sum(1 for s in chapter_data['subtopics'] if chapter_data['subtopic_data'].get(s, {}).get('content'))
        st.progress(completed / len(chapter_data['subtopics']) if chapter_data['subtopics'] else 0)
        st.caption(f"진행: {completed}/{len(chapter_data['subtopics'])} 완료")
        
        st.markdown("---")
        
        if selected_subtopic:
            if selected_subtopic not in chapter_data['subtopic_data']:
                chapter_data['subtopic_data'][selected_subtopic] = {'questions': [], 'answers': [], 'content': ''}
            
            subtopic_data = chapter_data['subtopic_data'][selected_subtopic]
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown(f"### 🎤 인터뷰: {selected_subtopic}")
                if st.button("🎤 질문 생성하기", key="gen_q"):
                    with st.spinner("질문 생성 중..."):
                        questions_text = generate_interview_questions(selected_subtopic, selected_chapter, st.session_state['topic'])
                        questions = re.findall(r'Q\d+:\s*(.+)', questions_text)
                        if not questions:
                            questions = [q.strip() for q in questions_text.split('\n') if q.strip() and '?' in q][:3]
                        subtopic_data['questions'] = questions
                        subtopic_data['answers'] = [''] * len(questions)
                        st.rerun()
                
                if subtopic_data['questions']:
                    for i, q in enumerate(subtopic_data['questions']):
                        st.markdown(f"**Q{i+1}.** {q}")
                        if i >= len(subtopic_data['answers']):
                            subtopic_data['answers'].append('')
                        subtopic_data['answers'][i] = st.text_area(f"A{i+1}", value=subtopic_data['answers'][i], key=f"ans_{selected_chapter}_{selected_subtopic}_{i}", height=80, label_visibility="collapsed")
                else:
                    st.info("👆 '질문 생성하기'를 눌러 인터뷰를 시작하세요.")
            
            with col2:
                st.markdown(f"### 📝 본문: {selected_subtopic}")
                has_answers = subtopic_data.get('questions') and any(a.strip() for a in subtopic_data.get('answers', []))
                content_key = f"content_{selected_chapter}_{selected_subtopic}"
                
                if has_answers:
                    if st.button("✨ 본문 생성하기", key="gen_content"):
                        with st.spinner("자청 스타일로 집필 중... (30초~1분)"):
                            content = generate_subtopic_content(selected_subtopic, selected_chapter, subtopic_data['questions'], subtopic_data['answers'], st.session_state['topic'], st.session_state['target_persona'])
                            st.session_state['chapters'][selected_chapter]['subtopic_data'][selected_subtopic]['content'] = content
                            st.session_state[content_key] = content
                            st.rerun()
                else:
                    st.info("👈 먼저 인터뷰 질문에 답변해주세요.")
                
                stored_content = st.session_state['chapters'][selected_chapter]['subtopic_data'][selected_subtopic].get('content', '')
                if content_key not in st.session_state:
                    st.session_state[content_key] = stored_content
                
                edited = st.text_area("본문", height=400, key=content_key, label_visibility="collapsed")
                if content_key in st.session_state:
                    st.session_state['chapters'][selected_chapter]['subtopic_data'][selected_subtopic]['content'] = st.session_state[content_key]
                
                final_content = st.session_state['chapters'][selected_chapter]['subtopic_data'][selected_subtopic].get('content', '')
                if final_content:
                    st.caption(f"📊 {calculate_char_count(final_content):,}자")
                    st.success(f"✅ '{selected_subtopic}' 작성 완료!")
        
        with st.expander("⚙️ 소제목 관리"):
            col_gen, col_add = st.columns(2)
            with col_gen:
                num_st = st.number_input("생성 개수", min_value=1, max_value=10, value=3, key="num_st")
                if st.button("✨ 소제목 자동 생성", key="gen_st"):
                    with st.spinner("생성 중..."):
                        text = generate_subtopics(selected_chapter, st.session_state['topic'], st.session_state['target_persona'], num_st)
                        new_sts = []
                        for line in text.split('\n'):
                            line = line.strip()
                            if line and (line[0].isdigit() or line.startswith('-')):
                                cleaned = re.sub(r'^[\d\.\-\s]+', '', line).strip()
                                if cleaned:
                                    new_sts.append(cleaned)
                        if new_sts:
                            chapter_data['subtopics'] = new_sts[:num_st]
                            for st_name in new_sts[:num_st]:
                                if st_name not in chapter_data['subtopic_data']:
                                    chapter_data['subtopic_data'][st_name] = {'questions': [], 'answers': [], 'content': ''}
                            st.success(f"✅ {len(new_sts[:num_st])}개 생성!")
                            st.rerun()
            with col_add:
                new_name = st.text_input("새 소제목", placeholder="직접 입력", key="new_st_name")
                if st.button("➕ 추가", key="add_st"):
                    if new_name.strip() and new_name not in chapter_data['subtopics']:
                        chapter_data['subtopics'].append(new_name)
                        chapter_data['subtopic_data'][new_name] = {'questions': [], 'answers': [], 'content': ''}
                        st.rerun()
    else:
        st.warning("⚠️ 이 챕터에 소제목이 없습니다.")
        col_gen, col_add = st.columns(2)
        with col_gen:
            if st.button("✨ 소제목 자동 생성", key="gen_st_empty"):
                with st.spinner("생성 중..."):
                    text = generate_subtopics(selected_chapter, st.session_state['topic'], st.session_state['target_persona'], 3)
                    new_sts = []
                    for line in text.split('\n'):
                        line = line.strip()
                        if line and (line[0].isdigit() or line.startswith('-')):
                            cleaned = re.sub(r'^[\d\.\-\s]+', '', line).strip()
                            if cleaned:
                                new_sts.append(cleaned)
                    if new_sts:
                        chapter_data['subtopics'] = new_sts[:3]
                        for st_name in new_sts[:3]:
                            chapter_data['subtopic_data'][st_name] = {'questions': [], 'answers': [], 'content': ''}
                        st.success(f"✅ {len(new_sts[:3])}개 생성!")
                        st.rerun()
        with col_add:
            new_st_name = st.text_input("소제목 이름", placeholder="직접 입력", key="new_st_empty")
            if st.button("➕ 추가", key="add_st_empty"):
                if new_st_name.strip():
                    chapter_data['subtopics'].append(new_st_name)
                    chapter_data['subtopic_data'][new_st_name] = {'questions': [], 'answers': [], 'content': ''}
                    st.rerun()
    
    st.markdown("---")
    st.markdown("### 📖 작성된 본문")
    pure_content = get_all_content_text()
    if pure_content:
        content_count = sum(1 for ch in st.session_state['outline'] for st_name in st.session_state['chapters'].get(ch, {}).get('subtopics', []) if st.session_state['chapters'].get(ch, {}).get('subtopic_data', {}).get(st_name, {}).get('content'))
        st.success(f"✅ 총 {content_count}개 소제목 | {calculate_char_count(pure_content):,}자")
        with st.expander("📖 전체 본문 보기"):
            for ch in st.session_state['outline']:
                if ch in st.session_state['chapters']:
                    ch_data = st.session_state['chapters'][ch]
                    if 'subtopic_data' in ch_data:
                        for st_name in ch_data.get('subtopics', []):
                            st_data = ch_data['subtopic_data'].get(st_name, {})
                            if st_data.get('content'):
                                st.markdown(f"## {ch}")
                                st.markdown(f"**{st_name}**")
                                st.markdown(clean_content_for_display(st_data['content']))
                                st.markdown("---")
    else:
        st.info("💡 아직 작성된 본문이 없습니다.")

# === TAB 5: 문체 다듬기 ===
with tabs[4]:
    st.markdown("## 문체 다듬기 & 품질 검사")
    
    content_options = []
    for ch in st.session_state['outline']:
        if ch in st.session_state['chapters']:
            ch_data = st.session_state['chapters'][ch]
            if 'subtopic_data' in ch_data:
                for st_name, st_data in ch_data['subtopic_data'].items():
                    if st_data.get('content'):
                        content_options.append(f"{ch} > {st_name}")
    
    if not content_options:
        st.info("💡 먼저 본문을 작성해주세요.")
        direct_content = st.text_area("다듬을 텍스트 직접 입력", height=300, placeholder="텍스트를 붙여넣으세요...")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 문체 다듬기")
        if content_options:
            selected_content = st.selectbox("다듬을 콘텐츠", content_options, key="refine_select")
        style = st.selectbox("목표 스타일", ["친근한", "전문적", "직설적", "스토리텔링"], key="style_select")
        
        if st.button("✨ 문체 다듬기", key="refine_btn"):
            content_to_refine = ""
            if content_options:
                parts = selected_content.split(" > ")
                if len(parts) == 2:
                    ch, st_name = parts
                    content_to_refine = st.session_state['chapters'][ch]['subtopic_data'][st_name]['content']
            elif 'direct_content' in dir() and direct_content:
                content_to_refine = direct_content
            
            if content_to_refine:
                with st.spinner("다듬는 중..."):
                    st.session_state['refined_content'] = refine_content(content_to_refine, style)
        
        if st.session_state.get('refined_content'):
            st.text_area("다듬어진 본문", value=st.session_state['refined_content'], height=400)
            if content_options and st.button("원본에 적용", key="apply_refined"):
                parts = selected_content.split(" > ")
                if len(parts) == 2:
                    ch, st_name = parts
                    st.session_state['chapters'][ch]['subtopic_data'][st_name]['content'] = st.session_state['refined_content']
                    st.success("적용됨!")
                    st.rerun()
    
    with col2:
        st.markdown("### 품질 검사")
        if st.button("🔍 베스트셀러 체크", key="quality_btn"):
            content_to_check = ""
            if content_options:
                parts = selected_content.split(" > ")
                if len(parts) == 2:
                    ch, st_name = parts
                    content_to_check = st.session_state['chapters'][ch]['subtopic_data'][st_name]['content']
            elif 'direct_content' in dir() and direct_content:
                content_to_check = direct_content
            
            if content_to_check:
                with st.spinner("분석 중..."):
                    st.session_state['quality_result'] = check_quality(content_to_check)
        
        if st.session_state.get('quality_result'):
            st.markdown(f'<div class="info-card">{st.session_state["quality_result"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

# === TAB 6: 최종 출력 ===
with tabs[5]:
    st.markdown("## 최종 출력 & 마케팅")
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown("### 전자책 다운로드")
        book_title = st.text_input("전자책 제목", value=st.session_state.get('book_title', ''), key="final_title")
        subtitle = st.text_input("부제", value=st.session_state.get('subtitle', ''), key="final_subtitle")
        st.session_state['book_title'] = book_title
        st.session_state['subtitle'] = subtitle
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            font_family = st.selectbox("폰트", ["Pretendard", "Noto Sans KR"], key="font")
            font_size = st.selectbox("크기", ["16px", "17px", "18px"], key="fontsize")
        with col_s2:
            line_height = st.selectbox("줄간격", ["1.8", "1.9", "2.0"], key="lineheight")
        
        # 본문 생성
        full_book_txt = f"{book_title}\n{subtitle}\n\n{'='*50}\n\n" if book_title else ""
        full_book_html = f"<h1>{book_title}</h1><p style='color:#666;'>{subtitle}</p><hr>" if book_title else ""
        
        for chapter in st.session_state['outline']:
            if chapter in st.session_state['chapters']:
                ch_data = st.session_state['chapters'][chapter]
                if 'subtopic_data' in ch_data:
                    has_content = any(ch_data['subtopic_data'].get(st_name, {}).get('content') for st_name in ch_data.get('subtopics', []))
                    if has_content:
                        full_book_txt += f"\n{chapter}\n{'-'*40}\n\n"
                        full_book_html += f"<h2>{chapter}</h2>"
                        for st_name in ch_data.get('subtopics', []):
                            st_data = ch_data['subtopic_data'].get(st_name, {})
                            if st_data.get('content'):
                                full_book_txt += f"\n{st_name}\n\n{st_data['content']}\n\n"
                                full_book_html += f"<h3>{st_name}</h3>"
                                for para in st_data['content'].split('\n\n'):
                                    if para.strip():
                                        full_book_html += f"<p style='font-size:{font_size};line-height:{line_height};'>{para}</p>"
        
        html_content = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><title>{book_title or '전자책'}</title>
        <link href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css" rel="stylesheet">
        <style>body{{font-family:'{font_family}',sans-serif;max-width:800px;margin:0 auto;padding:60px 20px;}}
        h1{{font-size:36px;font-weight:700;}}h2{{font-size:24px;margin-top:50px;}}h3{{font-size:18px;margin-top:30px;}}</style>
        </head><body>{full_book_html}</body></html>"""
        
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button("📄 TXT 다운로드", full_book_txt, file_name=f"{book_title or 'ebook'}_{datetime.now().strftime('%Y%m%d')}.txt", mime="text/plain", use_container_width=True)
        with col_dl2:
            st.download_button("🌐 HTML 다운로드", html_content, file_name=f"{book_title or 'ebook'}_{datetime.now().strftime('%Y%m%d')}.html", mime="text/html", use_container_width=True)
        
        # DOCX 생성
        try:
            from docx import Document
            from docx.shared import Pt
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            
            doc = Document()
            if book_title:
                p = doc.add_paragraph()
                r = p.add_run(book_title)
                r.font.size = Pt(28)
                r.font.bold = True
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if subtitle:
                p = doc.add_paragraph()
                r = p.add_run(subtitle)
                r.font.size = Pt(14)
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            for chapter in st.session_state['outline']:
                if chapter in st.session_state['chapters']:
                    ch_data = st.session_state['chapters'][chapter]
                    if 'subtopic_data' in ch_data:
                        has_content = any(ch_data['subtopic_data'].get(st_name, {}).get('content') for st_name in ch_data.get('subtopics', []))
                        if has_content:
                            p = doc.add_paragraph()
                            r = p.add_run(chapter)
                            r.font.size = Pt(20)
                            r.font.bold = True
                            for st_name in ch_data.get('subtopics', []):
                                st_data = ch_data['subtopic_data'].get(st_name, {})
                                if st_data.get('content'):
                                    p = doc.add_paragraph()
                                    r = p.add_run(st_name)
                                    r.font.size = Pt(14)
                                    r.font.bold = True
                                    for para in st_data['content'].split('\n\n'):
                                        if para.strip():
                                            p = doc.add_paragraph()
                                            r = p.add_run(para)
                                            r.font.size = Pt(11)
            
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            st.download_button("📘 DOCX 다운로드", buffer.getvalue(), file_name=f"{book_title or 'ebook'}_{datetime.now().strftime('%Y%m%d')}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
        except ImportError:
            st.info("DOCX: python-docx 설치 필요")
        
        st.markdown("---")
        pure_content = get_all_content_text()
        if pure_content:
            total_chars = calculate_char_count(pure_content)
            st.success(f"📊 총 {total_chars:,}자 / 약 {total_chars//500}페이지")
    
    with col2:
        st.markdown("### 마케팅 카피")
        if st.button("카피 생성하기", key="marketing_btn"):
            with st.spinner("생성 중..."):
                st.session_state['marketing_copy'] = generate_marketing_copy(st.session_state.get('book_title', st.session_state['topic']), st.session_state.get('subtitle', ''), st.session_state['topic'], st.session_state['target_persona'])
        
        if st.session_state.get('marketing_copy'):
            st.markdown(f'<div class="info-card">{st.session_state["marketing_copy"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

# --- 푸터 ---
st.markdown("""
<div class="premium-footer">
    <span class="premium-footer-text">전자책 작성 프로그램 — </span><span class="premium-footer-author">남현우 작가</span>
</div>
""", unsafe_allow_html=True)
