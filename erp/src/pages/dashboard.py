import streamlit as st
from datetime import datetime
from src.auth.cognito_auth import CognitoAuth
from src.components.metrics import render_metrics
from src.components.charts import render_charts

def show_page(auth: CognitoAuth):
    """대시보드 페이지 렌더링"""
    user_info = auth.session_mgr.get_user_info()
    
    # 헤더
    _render_header(auth, user_info)
    
    # 메트릭스
    render_metrics()
    
    # 사용자 정보
    _render_user_info(user_info)
    
    # 차트 및 분석
    render_charts()
    
    # 기능 메뉴
    _render_feature_menu()

def _render_header(auth: CognitoAuth, user_info):
    """헤더 렌더링"""
    username = _get_display_name(user_info)
    last_login = auth.session_mgr.get_last_login_time()
    
    # 헤더 전체를 하나의 컨테이너로 만들기
    st.markdown(f"""
    <div class="dashboard-header">
        <div class="header-content">
            <div class="header-text">
                <h1>👋 안녕하세요, {username}님!</h1>
                <p>관리자 대시보드에 오신 것을 환영합니다.</p>
            </div>
            <div class="header-button">
                <!-- 로그아웃 버튼은 Streamlit으로 별도 처리 -->
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 로그아웃 버튼을 헤더 위에 절대 위치로 배치
    col1, col2, col3 = st.columns([1, 8, 1])
    
    with col3:
        # 헤더 영역과 겹치도록 마진 조정
        st.markdown('<div class="logout-button-container">', unsafe_allow_html=True)
        if st.button("🚪 로그아웃", key="logout_btn", help="로그아웃하여 세션을 종료합니다"):
            _handle_logout(auth)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 마지막 로그인 시간 표시
    if last_login:
        st.markdown(f'<p class="last-login-time">마지막 로그인: {last_login.strftime("%Y-%m-%d %H:%M:%S")}</p>', 
                   unsafe_allow_html=True)

def _get_display_name(user_info):
    """표시할 사용자명 결정"""
    if not user_info:
        return "사용자"
    
    # 우선순위: preferred_username > given_name + family_name > email > sub
    if user_info.get('preferred_username'):
        return user_info['preferred_username']
    
    given_name = user_info.get('given_name', '')
    family_name = user_info.get('family_name', '')
    
    if given_name or family_name:
        return f"{family_name} {given_name}".strip()
    
    if user_info.get('email'):
        return user_info['email'].split('@')[0]
    
    return user_info.get('sub', '사용자')[:8] + "..."

def _handle_logout(auth: CognitoAuth):
    """로그아웃 처리"""
    auth.logout()

def _render_user_info(user_info):
    """사용자 정보 렌더링"""
    if not user_info:
        return
    
    with st.expander("👤 사용자 정보", expanded=False):
        col1, col2 = st.columns(2)
        
        # 기본 정보
        with col1:
            st.markdown("**🔍 기본 정보**")
            st.info(f"**이메일:** {user_info.get('email', 'N/A')}")
            
            # 이름 정보
            given_name = user_info.get('given_name', '')
            family_name = user_info.get('family_name', '')
            if given_name or family_name:
                full_name = f"{family_name} {given_name}".strip()
                st.info(f"**이름:** {full_name}")
            
            # 사용자 ID
            user_id = user_info.get('sub', 'N/A')
            if user_id != 'N/A':
                st.info(f"**사용자 ID:** {user_id[:8]}...")
            else:
                st.info(f"**사용자 ID:** {user_id}")
        
        # 인증 상태
        with col2:
            st.markdown("**✅ 인증 상태**")
            
            # 이메일 인증
            email_verified = user_info.get('email_verified', 'false') == 'true'
            st.info(f"**이메일 인증:** {'✅ 완료' if email_verified else '❌ 미완료'}")
            
            # 전화번호 정보
            phone_number = user_info.get('phone_number')
            if phone_number:
                phone_verified = user_info.get('phone_number_verified', 'false') == 'true'
                st.info(f"**전화번호:** {phone_number}")
                st.info(f"**전화번호 인증:** {'✅ 완료' if phone_verified else '❌ 미완료'}")
            else:
                st.info("**전화번호:** 등록되지 않음")
            
            # 업데이트 시간
            updated_at = user_info.get('updated_at')
            if updated_at:
                try:
                    dt = datetime.fromtimestamp(int(updated_at))
                    updated_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                    st.info(f"**최근 업데이트:** {updated_str}")
                except:
                    st.info(f"**최근 업데이트:** {updated_at}")

def _render_feature_menu():
    """기능 메뉴 렌더링"""
    st.markdown("### 🛠️ 주요 기능")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📁 파일 관리", width='stretch'):
            st.info("📁 파일 관리 기능이 선택되었습니다.")
    
    with col2:
        if st.button("👥 사용자 관리", width='stretch'):
            st.info("👥 사용자 관리 기능이 선택되었습니다.")
    
    with col3:
        if st.button("📈 분석 도구", width='stretch'):
            st.info("📈 분석 도구 기능이 선택되었습니다.")
    
    with col4:
        if st.button("⚙️ 시스템 설정", width='stretch'):
            st.info("⚙️ 시스템 설정 기능이 선택되었습니다.")