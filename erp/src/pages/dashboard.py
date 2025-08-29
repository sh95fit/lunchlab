import streamlit as st
from datetime import datetime
from src.auth.cognito_auth import CognitoAuth
from src.components.metrics import render_metrics
from src.components.charts import render_charts

def show_page(auth: CognitoAuth):
    """대시보드 페이지 렌더링"""
    user_info = auth.session_mgr.get_user_info()
    session_info = auth.session_mgr.get_session_info()
    
    # 헤더
    _render_header(auth, user_info, session_info)
    
    # 세션 만료 경고
    _render_session_warning(auth, session_info)
    
    # 메트릭스
    render_metrics()
    
    # 사용자 정보
    _render_user_info(user_info)
    
    # 세션 정보
    _render_session_info(session_info, auth)
    
    # 차트 및 분석
    render_charts()
    
    # 기능 메뉴
    _render_feature_menu()

def _render_header(auth: CognitoAuth, user_info, session_info):
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
                <small>세션 유지: ✅ 활성화 (새로고침해도 로그인 상태 유지)</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    
    # 상단 메뉴바
    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
    
    with col1:
        if st.button("🔄 새로고침 테스트", help="페이지를 새로고침하여 세션 유지 테스트"):
            st.rerun()
    
    with col2:
        if st.button("⏰ 세션 연장", help="세션 유효시간을 연장합니다"):
            if auth.session_mgr.extend_session():
                st.success("세션이 연장되었습니다!")
                st.rerun()
            else:
                st.error("세션 연장에 실패했습니다.")
    
    with col3:
        remaining_minutes = session_info.get('expires_in_minutes', 0)
        if remaining_minutes > 60:
            time_display = f"{remaining_minutes // 60}시간 {remaining_minutes % 60}분"
        else:
            time_display = f"{remaining_minutes}분"
        
        st.metric(
            "세션 만료까지",
            time_display,
            help="세션이 만료되면 자동으로 로그아웃됩니다"
        )
    
    with col4:
        st.metric(
            "로그인 시간",
            session_info.get('session_duration', 'N/A'),
            help="현재 세션의 지속 시간"
        )
    
    with col5:
        if st.button("🚪 로그아웃", type="primary", help="로그아웃하여 세션을 종료합니다"):
            _handle_logout(auth)
    
    # 마지막 로그인 시간 표시
    if last_login:
        st.markdown(f'<p class="last-login-time">마지막 로그인: {last_login.strftime("%Y-%m-%d %H:%M:%S")}</p>', 
                   unsafe_allow_html=True)

def _render_session_warning(auth: CognitoAuth, session_info):
    """세션 만료 경고"""
    remaining_minutes = session_info.get('expires_in_minutes', 0)
    
    if remaining_minutes <= 30 and remaining_minutes > 0:
        st.warning(
            f"⚠️ 세션이 {remaining_minutes}분 후에 만료됩니다. "
            f"계속 사용하시려면 '세션 연장' 버튼을 클릭하세요.",
            icon="⏰"
        )
    elif remaining_minutes <= 0:
        st.error(
            "🚨 세션이 만료되었습니다. 다시 로그인해주세요.",
            icon="🔒"
        )
        if st.button("다시 로그인하기", type="primary"):
            auth.logout()

def _render_session_info(session_info, auth):
    """세션 정보 표시"""
    with st.expander("🔐 세션 정보", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 세션 상태**")
            
            if session_info['is_authenticated']:
                st.success("✅ 인증됨")
            else:
                st.error("❌ 인증 안됨")
            
            if session_info['login_time']:
                st.info(f"🕒 **로그인 시간:** {session_info['login_time']}")
            
            if session_info['session_duration']:
                st.info(f"⏱️ **세션 지속 시간:** {session_info['session_duration']}")
        
        with col2:
            st.markdown("**🛡️ 보안 정보**")
            
            remaining_minutes = session_info.get('expires_in_minutes', 0)
            if remaining_minutes > 0:
                st.info(f"⏰ **세션 만료:** {session_info['expires_in']}")
                
                # 진행 바로 남은 시간 표시
                total_minutes = auth.session_mgr.SESSION_TIMEOUT_HOURS * 60
                progress = remaining_minutes / total_minutes
                
                st.progress(progress)
                st.caption(f"세션 진행률: {(1-progress)*100:.1f}%")
            else:
                st.error("🚨 **세션 상태:** 만료됨")
            
            # 세션 관리 버튼들
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("🔄 세션 새로고침", key="refresh_session"):
                    if auth.session_mgr.extend_session():
                        st.success("세션이 새로고침되었습니다!")
                        st.rerun()
            
            with col_btn2:
                if st.button("🗑️ 세션 종료", key="end_session"):
                    _handle_logout(auth)

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

    # 세션 테스트 섹션
    _render_session_test_section()
    
def _render_session_test_section():
    """세션 테스트 섹션"""
    st.markdown("### 🧪 세션 유지 테스트")
    
    st.info("""
    **세션 유지 기능 테스트:**
    1. 🔄 **새로고침 테스트**: 브라우저를 새로고침해도 로그인 상태가 유지됩니다
    2. 📱 **탭 테스트**: 새 탭에서 같은 URL을 열어도 로그인 상태가 유지됩니다
    3. ⏰ **시간 테스트**: 8시간 동안 세션이 유지됩니다 (연장 가능)
    4. 🛡️ **보안 테스트**: 브라우저를 완전히 닫으면 세션이 종료됩니다
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 강제 새로고침", help="페이지를 강제로 새로고침합니다"):
            st.rerun()
    
    with col2:
        if st.button("📋 세션 정보 복사", help="현재 세션 정보를 클립보드에 복사"):
            st.code(f"""
                세션 정보:
                - 인증 상태: ✅
                - 로그인 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                - 브라우저 저장소: sessionStorage
                - 만료 시간: 8시간
            """)
    
    with col3:
        if st.button("🆕 새 탭에서 열기", help="새 탭에서 현재 페이지를 엽니다"):
            st.markdown("""
                <script>
                    window.open(window.location.href, '_blank');
                </script>
            """, unsafe_allow_html=True)