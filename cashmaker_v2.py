import streamlit as st
import google.generativeai as genai
import re
import json
from datetime import datetime
from pathlib import Path

# ==========================================
# 페이지 설정
# ==========================================
st.set_page_config(
    page_title="CASHMAKER - 전자책 작성",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CSS 스타일
# ==========================================
st.markdown("""
<style>
    /* 다크 테마 */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    /* 메인 컨테이너 */
    .main .block-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* 제목 스타일 */
    h1 {
        color: #FFD700;
        text-align: center;
        font-size: 3rem;
        margin-bottom: 1rem;
        text-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
    }
    
    h2 {
        color: #FFA500;
        margin-top: 2rem;
    }
    
    h3 {
        color: #87CEEB;
    }
    
    /* 텍스트 */
    p, span, label, .stMarkdown {
        color: rgba(255, 255, 255, 0.9);
    }
    
    /* 입력 필드 */
    .stTextInput input, .stTextArea textarea {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 215, 0, 0.3);
        border-radius: 10px;
    }
    
    /* 버튼 */
    .stButton button {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: black;
        font-weight: bold;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 215, 0, 0.4);
    }
    
    /* 사이드바 */
    [data-testid="stSidebar"] {
        background: rgba(10, 10, 20, 0.8);
        border-right: 1px solid rgba(255, 215, 0, 0.2);
    }
    
    /* 탭 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        color: rgba(255, 255, 255, 0.6);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.2), rgba(255, 165, 0, 0.2));
        color: #FFD700;
    }
    
    /* 성공/경고/에러 메시지 */
    .stSuccess {
        background: rgba(76, 175, 80, 0.1);
        border: 1px solid rgba(76, 175, 80, 0.3);
        color: #4CAF50;
    }
    
    .stWarning {
        background: rgba(255, 152, 0, 0.1);
        border: 1px solid rgba(255, 152, 0, 0.3);
        color: #FF9800;
    }
    
    .stError {
        background: rgba(244, 67, 54, 0.1);
        border: 1px solid rgba(244, 67, 54, 0.3);
        color: #F44336;
    }
    
    .stInfo {
        background: rgba(33, 150, 243, 0.1);
        border: 1px solid rgba(33, 150, 243, 0.3);
        color: #2196F3;
    }
    
    /* 숨기기 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 세션 상태 초기화
# ==========================================
def init_session_state():
    defaults = {
        'authenticated': False,
        'api_key': '',
        'topic': '',
        'target_persona': '',
        'pain_points': '',
        'book_title': '',
        'subtitle': '',
        'outline': [],
        'chapters': {},
        'generated_content': {}
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ==========================================
# AI 함수
# ==========================================
def ask_ai(prompt, temperature=0.7):
    """Gemini AI 호출"""
    api_key = st.session_state.get('api_key', '')
    
    if not api_key:
        return "⚠️ 사이드바에서 API 키를 먼저 입력해주세요."
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=4000
            )
        )
        
        return response.text
        
    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg.upper():
            return "❌ API 키가 유효하지 않습니다. 다시 확인해주세요."
        elif "QUOTA" in error_msg.upper():
            return "❌ API 사용량 한도 초과. 잠시 후 다시 시도하세요."
        else:
            return f"❌ 오류 발생: {error_msg}"

def generate_outline(topic, persona, pain_points):
    """목차 생성"""
    prompt = f"""당신은 베스트셀러 전자책 기획자입니다.

주제: {topic}
타겟: {persona}
고민: {pain_points}

4개 챕터, 각 챕터당 3개 소제목으로 구성된 전자책 목차를 만들어주세요.

규칙:
- 챕터 제목은 호기심을 자극하는 임팩트 있게
- 소제목은 구체적이고 실용적으로
- "~의 방법", "~하는 법" 같은 뻔한 표현 금지

출력 형식:
## 챕터1: [제목]
- 소제목1
- 소제목2
- 소제목3

## 챕터2: [제목]
- 소제목1
- 소제목2
- 소제목3

(총 4개 챕터)"""

    return ask_ai(prompt, 0.85)

def generate_content(subtopic, chapter, topic, persona):
    """본문 생성"""
    prompt = f"""당신은 베스트셀러 작가입니다.

전자책 주제: {topic}
타겟: {persona}
챕터: {chapter}
소제목: {subtopic}

'{subtopic}'에 대한 본문을 1500자 이상 작성해주세요.

작성 규칙:
1. 합니다체 사용
2. 첫 문장은 임팩트 있게
3. 구체적인 사례와 숫자 포함
4. 스토리텔링 방식
5. 독자가 바로 실행할 수 있는 팁 포함

본문만 작성하세요."""

    return ask_ai(prompt, 0.8)

def generate_titles(topic, persona):
    """제목 생성"""
    prompt = f"""베스트셀러 전자책 제목을 5개 만들어주세요.

주제: {topic}
타겟: {persona}

규칙:
- 7자 이내의 강력한 메인 제목
- 15자 이내의 부제
- 호기심을 자극하는 제목

형식:
1. [메인 제목] - [부제]
2. [메인 제목] - [부제]
...
"""
    return ask_ai(prompt, 0.9)

# ==========================================
# 유틸리티 함수
# ==========================================
def parse_outline(text):
    """목차 텍스트 파싱"""
    lines = text.split('\n')
    chapters = []
    current_chapter = None
    chapter_data = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('##'):
            current_chapter = line.lstrip('#').strip()
            chapters.append(current_chapter)
            chapter_data[current_chapter] = []
        elif line.startswith('-') and current_chapter:
            subtopic = line.lstrip('- ').strip()
            if subtopic:
                chapter_data[current_chapter].append(subtopic)
    
    return chapters, chapter_data

def calculate_stats():
    """통계 계산"""
    total_chapters = len(st.session_state['outline'])
    total_subtopics = sum(
        len(st.session_state['chapters'].get(ch, {}).get('subtopics', []))
        for ch in st.session_state['outline']
    )
    
    total_chars = 0
    completed = 0
    
    for ch in st.session_state['outline']:
        ch_data = st.session_state['chapters'].get(ch, {})
        for sub in ch_data.get('subtopics', []):
            content = ch_data.get('content', {}).get(sub, '')
            if content:
                completed += 1
                total_chars += len(content.replace('\n', '').replace(' ', ''))
    
    return total_chapters, total_subtopics, completed, total_chars

# ==========================================
# 비밀번호 체크
# ==========================================
CORRECT_PASSWORD = "cashmaker2024"

if not st.session_state['authenticated']:
    st.markdown("<h1>🚀 CASHMAKER</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem;'>전자책 자동 작성 프로그램</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password = st.text_input("비밀번호 입력", type="password", placeholder="cashmaker2024")
        
        if st.button("🔓 입장하기", use_container_width=True):
            if password == CORRECT_PASSWORD:
                st.session_state['authenticated'] = True
                st.success("✅ 인증 성공!")
                st.rerun()
            else:
                st.error("❌ 비밀번호가 틀렸습니다")
    
    st.stop()

# ==========================================
# 사이드바
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ 설정")
    
    # API 키 입력
    api_key = st.text_input(
        "Gemini API 키",
        value=st.session_state['api_key'],
        type="password",
        help="Google AI Studio에서 발급"
    )
    st.session_state['api_key'] = api_key
    
    if api_key:
        st.success("✅ API 키 입력됨")
    else:
        st.warning("⚠️ API 키 필요")
        with st.expander("📌 API 키 발급 방법"):
            st.markdown("""
1. [Google AI Studio](https://aistudio.google.com/apikey) 접속
2. Google 계정 로그인
3. "API 키 만들기" 클릭
4. 생성된 키 복사
5. 위에 붙여넣기

✅ 무료 ✅ 신용카드 불필요
""")
    
    st.markdown("---")
    
    # 통계
    st.markdown("### 📊 진행 상황")
    chapters, subtopics, completed, chars = calculate_stats()
    
    if chapters > 0:
        progress = completed / subtopics if subtopics > 0 else 0
        st.progress(progress)
        st.caption(f"📚 챕터: {chapters}개")
        st.caption(f"📝 소제목: {subtopics}개")
        st.caption(f"✅ 완료: {completed}개")
        if chars > 0:
            st.caption(f"📊 총 글자: {chars:,}자")
    else:
        st.info("아직 작업을 시작하지 않았습니다")
    
    st.markdown("---")
    
    # 저장/불러오기
    st.markdown("### 💾 저장")
    
    save_data = {
        'topic': st.session_state['topic'],
        'target_persona': st.session_state['target_persona'],
        'pain_points': st.session_state['pain_points'],
        'book_title': st.session_state['book_title'],
        'subtitle': st.session_state['subtitle'],
        'outline': st.session_state['outline'],
        'chapters': st.session_state['chapters'],
    }
    
    save_json = json.dumps(save_data, ensure_ascii=False, indent=2)
    
    st.download_button(
        "📥 작업 저장",
        save_json,
        file_name=f"ebook_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json",
        use_container_width=True
    )
    
    uploaded = st.file_uploader("📤 작업 불러오기", type=['json'])
    if uploaded:
        try:
            data = json.loads(uploaded.read().decode('utf-8'))
            if st.button("✅ 불러오기 적용"):
                for key in data:
                    st.session_state[key] = data[key]
                st.success("불러오기 완료!")
                st.rerun()
        except:
            st.error("파일 오류")
    
    st.markdown("---")
    
    # 로그아웃
    if st.button("🚪 로그아웃", use_container_width=True):
        st.session_state['authenticated'] = False
        st.rerun()

# ==========================================
# 메인 UI
# ==========================================
st.markdown("<h1>📚 CASHMAKER</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.8;'>AI로 전자책을 자동 작성하세요</p>", unsafe_allow_html=True)

# 탭 생성
tabs = st.tabs(["① 주제 설정", "② 제목 & 목차", "③ 본문 작성", "④ 최종 출력"])

# ==========================================
# TAB 1: 주제 설정
# ==========================================
with tabs[0]:
    st.header("📌 주제 설정")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("기본 정보")
        
        topic = st.text_input(
            "전자책 주제",
            value=st.session_state['topic'],
            placeholder="예: 크몽으로 월 500만원 버는 법"
        )
        st.session_state['topic'] = topic
        
        persona = st.text_area(
            "타겟 독자",
            value=st.session_state['target_persona'],
            placeholder="예: 30대 직장인, 부업으로 추가 수입을 원하는 사람",
            height=100
        )
        st.session_state['target_persona'] = persona
        
        pain_points = st.text_area(
            "타겟의 고민",
            value=st.session_state['pain_points'],
            placeholder="예: 시간이 없다, 뭘 해야 할지 모르겠다, 시작이 두렵다",
            height=100
        )
        st.session_state['pain_points'] = pain_points
    
    with col2:
        st.subheader("✅ 입력 확인")
        
        if topic:
            st.success(f"**주제**: {topic}")
        else:
            st.info("주제를 입력해주세요")
        
        if persona:
            st.success(f"**타겟**: {persona}")
        else:
            st.info("타겟 독자를 입력해주세요")
        
        if pain_points:
            st.success(f"**고민**: {pain_points}")
        else:
            st.info("타겟의 고민을 입력해주세요")
        
        st.markdown("---")
        
        if topic and persona:
            st.success("✅ 다음 탭으로 이동하세요")
        else:
            st.warning("⚠️ 주제와 타겟을 입력하세요")

# ==========================================
# TAB 2: 제목 & 목차
# ==========================================
with tabs[1]:
    st.header("📝 제목 & 목차 생성")
    
    if not st.session_state['topic']:
        st.warning("⚠️ 먼저 '① 주제 설정' 탭에서 주제를 입력하세요")
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📖 제목 생성")
            
            if st.button("✨ AI로 제목 생성", key="gen_title"):
                with st.spinner("제목 생성 중..."):
                    titles = generate_titles(
                        st.session_state['topic'],
                        st.session_state['target_persona']
                    )
                    st.session_state['generated_titles'] = titles
            
            if st.session_state.get('generated_titles'):
                st.markdown("**생성된 제목:**")
                st.info(st.session_state['generated_titles'])
            
            st.markdown("---")
            
            st.subheader("최종 제목 입력")
            book_title = st.text_input(
                "메인 제목",
                value=st.session_state['book_title'],
                placeholder="7자 이내"
            )
            st.session_state['book_title'] = book_title
            
            subtitle = st.text_input(
                "부제",
                value=st.session_state['subtitle'],
                placeholder="15자 이내"
            )
            st.session_state['subtitle'] = subtitle
        
        with col2:
            st.subheader("📋 목차 생성")
            
            if st.button("🚀 AI로 목차 자동 생성", key="gen_outline"):
                with st.spinner("목차 생성 중... (30초)"):
                    outline_text = generate_outline(
                        st.session_state['topic'],
                        st.session_state['target_persona'],
                        st.session_state['pain_points']
                    )
                    
                    chapters, chapter_data = parse_outline(outline_text)
                    
                    if chapters:
                        st.session_state['outline'] = chapters
                        st.session_state['chapters'] = {
                            ch: {
                                'subtopics': chapter_data.get(ch, []),
                                'content': {}
                            }
                            for ch in chapters
                        }
                        st.success(f"✅ {len(chapters)}개 챕터 생성 완료!")
                        st.rerun()
                    else:
                        st.error("목차 생성 실패. 다시 시도하세요.")
            
            # 목차 표시
            if st.session_state['outline']:
                st.markdown("**📚 현재 목차:**")
                for i, ch in enumerate(st.session_state['outline'], 1):
                    st.markdown(f"**{i}. {ch}**")
                    subs = st.session_state['chapters'][ch]['subtopics']
                    for sub in subs:
                        st.markdown(f"   - {sub}")
                    st.markdown("")

# ==========================================
# TAB 3: 본문 작성
# ==========================================
with tabs[2]:
    st.header("✍️ 본문 작성")
    
    if not st.session_state['outline']:
        st.warning("⚠️ 먼저 '② 제목 & 목차' 탭에서 목차를 생성하세요")
    else:
        # 챕터 선택
        chapter = st.selectbox(
            "📚 챕터 선택",
            st.session_state['outline'],
            format_func=lambda x: f"{st.session_state['outline'].index(x)+1}. {x}"
        )
        
        if chapter:
            st.markdown(f"### {chapter}")
            
            subs = st.session_state['chapters'][chapter]['subtopics']
            
            # 진행률
            completed = sum(
                1 for sub in subs 
                if st.session_state['chapters'][chapter]['content'].get(sub)
            )
            progress = completed / len(subs) if subs else 0
            st.progress(progress)
            st.caption(f"진행: {completed}/{len(subs)} 완료")
            
            st.markdown("---")
            
            # 소제목 선택
            subtopic = st.selectbox(
                "📝 작성할 소제목",
                subs,
                format_func=lambda x: f"{'✅' if st.session_state['chapters'][chapter]['content'].get(x) else '⬜'} {x}"
            )
            
            if subtopic:
                st.markdown(f"#### {subtopic}")
                
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    if st.button("✨ AI로 본문 작성", key=f"gen_{subtopic}"):
                        with st.spinner("본문 작성 중... (30~60초)"):
                            content = generate_content(
                                subtopic,
                                chapter,
                                st.session_state['topic'],
                                st.session_state['target_persona']
                            )
                            
                            st.session_state['chapters'][chapter]['content'][subtopic] = content
                            st.success("✅ 작성 완료!")
                            st.rerun()
                
                with col2:
                    # 본문 표시/편집
                    current_content = st.session_state['chapters'][chapter]['content'].get(subtopic, '')
                    
                    if current_content:
                        edited = st.text_area(
                            "본문 내용",
                            value=current_content,
                            height=400,
                            key=f"edit_{chapter}_{subtopic}"
                        )
                        
                        st.session_state['chapters'][chapter]['content'][subtopic] = edited
                        
                        char_count = len(edited.replace('\n', '').replace(' ', ''))
                        st.caption(f"📊 {char_count:,}자")
                    else:
                        st.info("👈 'AI로 본문 작성' 버튼을 눌러주세요")

# ==========================================
# TAB 4: 최종 출력
# ==========================================
with tabs[3]:
    st.header("📦 최종 출력")
    
    # 전체 내용 생성
    full_text = ""
    
    if st.session_state['book_title']:
        full_text += f"{st.session_state['book_title']}\n"
    if st.session_state['subtitle']:
        full_text += f"{st.session_state['subtitle']}\n"
    
    full_text += "\n" + "="*50 + "\n\n"
    
    for ch in st.session_state['outline']:
        full_text += f"\n## {ch}\n\n"
        
        ch_data = st.session_state['chapters'][ch]
        for sub in ch_data['subtopics']:
            content = ch_data['content'].get(sub, '')
            if content:
                full_text += f"### {sub}\n\n{content}\n\n"
    
    # 통계
    total_chars = len(full_text.replace('\n', '').replace(' ', ''))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("챕터", f"{len(st.session_state['outline'])}개")
    with col2:
        chapters, subtopics, completed, chars = calculate_stats()
        st.metric("완성도", f"{completed}/{subtopics}")
    with col3:
        st.metric("총 글자", f"{total_chars:,}자")
    
    st.markdown("---")
    
    # 다운로드
    if total_chars > 100:
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                "📄 TXT 다운로드",
                full_text,
                file_name=f"{st.session_state.get('book_title', 'ebook')}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            # HTML 생성
            html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>{st.session_state.get('book_title', '전자책')}</title>
    <style>
        body {{
            font-family: 'Noto Sans KR', sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            line-height: 1.8;
        }}
        h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
        h2 {{ font-size: 2rem; margin-top: 3rem; }}
        h3 {{ font-size: 1.5rem; margin-top: 2rem; }}
        p {{ margin: 1rem 0; }}
    </style>
</head>
<body>
{'<h1>' + st.session_state['book_title'] + '</h1>' if st.session_state['book_title'] else ''}
{'<p style="color: #666;">' + st.session_state['subtitle'] + '</p>' if st.session_state['subtitle'] else ''}
<hr>
{full_text.replace('\n\n', '</p><p>').replace('## ', '<h2>').replace('###', '<h3>')}
</body>
</html>"""
            
            st.download_button(
                "🌐 HTML 다운로드",
                html_content,
                file_name=f"{st.session_state.get('book_title', 'ebook')}_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True
            )
        
        st.markdown("---")
        
        # 미리보기
        st.subheader("📖 전체 내용 미리보기")
        with st.expander("펼쳐보기"):
            st.text(full_text)
    else:
        st.info("💡 먼저 본문을 작성하세요")

# ==========================================
# 푸터
# ==========================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; color: rgba(255,255,255,0.5);'>
    <p><strong>CASHMAKER</strong> | 전자책 자동 작성 프로그램</p>
    <p>Made by 남현우 작가</p>
</div>
""", unsafe_allow_html=True)
