import streamlit as st

# 페이지 설정
st.set_page_config(page_title="CASHMAKER", page_icon="✨", layout="wide")

# CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800;900&display=swap');
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    * { 
        font-family: 'Pretendard', sans-serif; 
        transition: all 0.6s ease;
    }
    
    .stApp { 
        background: linear-gradient(180deg, #000 0%, #0a0e27 50%, #1a1f3a 100%);
    }
    
    .main .block-container { 
        background: rgba(255, 255, 255, 0.01);
        backdrop-filter: blur(40px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 32px;
        padding: 3rem 4rem; 
        animation: fadeInUp 0.8s ease-out;
    }
    
    h1 { 
        background: linear-gradient(135deg, #FFD700, #FFA500, #FFD700);
        background-size: 300% 100%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900 !important; 
        font-size: 3.5rem !important;
        animation: shimmer 6s ease-in-out infinite;
    }
    
    .stButton > button { 
        background: linear-gradient(135deg, #FFD700, #FFA500) !important;
        color: #000 !important;
        border: none !important;
        padding: 18px 36px;
        border-radius: 16px;
        font-weight: 700;
        box-shadow: 0 8px 32px rgba(255, 215, 0, 0.4);
    }
    
    .stButton > button:hover { 
        transform: translateY(-4px);
        box-shadow: 0 16px 48px rgba(255, 215, 0, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# 메인 화면
st.markdown("<h1>CASHMAKER 전자책 프로그램</h1>", unsafe_allow_html=True)
st.write("### 🎨 프리미엄 디자인 적용됨")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("✨ 애플 스타일")
    
with col2:
    st.success("🎯 3D 애니메이션")
    
with col3:
    st.warning("💎 프리미엄 효과")

if st.button("시작하기"):
    st.balloons()
    st.success("✅ 디자인이 정상적으로 작동합니다!")

st.markdown("---")
st.write("현우님의 전자책 제작 프로그램 - 프리미엄 버전")
