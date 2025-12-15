# === TAB 5: 디자인 생성 (수정됨) ===
with tabs[4]:
    st.markdown("## 🎨 전문가급 표지 디자인")
    st.info("📌 최초 생성 시 고화질 배경 이미지를 다운로드하느라 3~5초 정도 걸릴 수 있습니다.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📕 전자책 표지 설정")
        
        cover_title = st.text_input("표지 제목", value=st.session_state.get('book_title', ''), key="cover_title_v2")
        cover_subtitle = st.text_input("표지 부제목", value=st.session_state.get('subtitle', ''), key="cover_subtitle_v2")
        cover_author = st.text_input("저자명/브랜드", value="CASHMAKER", key="cover_author")
        
        # 스타일 선택 (새로운 옵션)
        cover_style = st.selectbox(
            "디자인 테마 선택", 
            ["rich_black", "ceo_white", "money_gold", "digital_blue"],
            format_func=lambda x: {
                "rich_black": "🖤 리치 블랙 (압도적 고급감)",
                "ceo_white": "🤍 CEO 화이트 (깔끔/전문성)",
                "money_gold": "👑 머니 골드 (수익/부)",
                "digital_blue": "💻 디지털 블루 (IT/테크)"
            }.get(x, x)
        )
        
        if st.button("🎨 표지 생성하기", key="gen_cover_v2"):
            if not cover_title:
                st.error("제목을 입력해주세요.")
            else:
                with st.spinner("고화질 텍스처 로딩 & 렌더링 중..."):
                    # 위에서 만든 새로운 함수 호출
                    cover_img = create_pro_book_cover(cover_title, cover_subtitle, cover_style, cover_author)
                    st.session_state['cover_image'] = cover_img
                    st.success("완료! 우측에서 확인하세요.")
    
    with col2:
        st.markdown("### 📸 미리보기")
        if st.session_state.get('cover_image'):
            st.image(st.session_state['cover_image'], caption="High-End Book Cover", use_container_width=True)
            
            # 다운로드 버튼
            buf = BytesIO()
            st.session_state['cover_image'].save(buf, format='PNG')
            st.download_button(
                label="📥 고화질 표지 다운로드 (PNG)",
                data=buf.getvalue(),
                file_name="premium_book_cover.png",
                mime="image/png"
            )
        else:
            st.markdown("""
            <div style="height: 500px; background: #f0f2f6; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #888;">
                왼쪽에서 내용을 입력하고<br>'표지 생성하기'를 눌러주세요.
            </div>
            """, unsafe_allow_html=True)
