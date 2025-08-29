import streamlit as st
from src.auth.cognito_auth import CognitoAuth
from src.utils.validators import validate_login_form

def show_page(auth: CognitoAuth):
    """로그인 페이지 렌더링"""
    
    # 헤더
    st.markdown("""
    <div class="login-header">
        <h1>🔐 관리자 로그인</h1>
        <p>AWS Cognito를 통한 안전한 인증</p>
        <small>✨ 새로고침해도 로그인 상태가 유지됩니다!</small>
    </div>
    """, unsafe_allow_html=True)
    
        
    # 세션 복원 상태 확인
    _check_session_restore_status(auth)
    
    # 로그인 폼
    _render_login_form(auth)
    
    # 로그인 도움말
    _render_login_help()

def _check_session_restore_status(auth: CognitoAuth):
    """세션 복원 상태 확인 및 표시"""
    session_info = auth.session_mgr.get_session_info()
    
    if session_info['is_authenticated']:
        st.success("""
        🎉 **세션이 자동으로 복원되었습니다!**
        
        브라우저를 새로고침하거나 새 탭에서 열어도 로그인 상태가 유지됩니다.
        """)
        
        if st.button("🚀 대시보드로 이동", type="primary", use_container_width=True):
            st.rerun()
        
        st.divider()

def _render_login_form(auth: CognitoAuth):
    """로그인 폼 렌더링"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔑 로그인")
        
        # 세션 지속성 안내
        st.info("""
            🛡️ **향상된 세션 관리**
            - 브라우저 새로고침 시 로그인 유지
            - 8시간 동안 자동 세션 유지
            - 안전한 토큰 관리
        """)
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "사용자명",
                placeholder="사용자명을 입력하세요",
                help="등록된 사용자명을 입력해주세요"
            )
            
            password = st.text_input(
                "비밀번호",
                type="password",
                placeholder="비밀번호를 입력하세요",
                help="8자 이상의 비밀번호를 입력해주세요"
            )
            
            # 세션 유지 옵션 (항상 활성화되어 있음을 표시)
            col_check, col_info = st.columns([1, 3])
            with col_check:
                st.checkbox("로그인 상태 유지", value=True, disabled=True)
            with col_info:
                st.caption("🔒 보안을 위해 8시간 후 자동 만료됩니다")
            
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                login_button = st.form_submit_button(
                    "🚀 로그인", 
                    width='stretch',
                    type="primary"
                )
            
            with col_btn2:
                clear_button = st.form_submit_button(
                    "🧹 초기화", 
                    width='stretch',
                )
            
            # 폼 처리
            if login_button:
                _handle_login(auth, username, password)
            
            if clear_button:
                st.rerun()

def _handle_login(auth: CognitoAuth, username: str, password: str):
    """로그인 처리"""
    # 입력 검증
    validation_results = validate_login_form(username, password)
    
    errors = []
    for field, result in validation_results.items():
        if not result.is_valid:
            errors.append(result.message)
    
    if errors:
        for error in errors:
            st.error(error)
        return
    
    # 로그인 시도 횟수 확인
    session_mgr = auth.session_mgr
    if session_mgr.get_login_attempts() >= 5:
        st.error("로그인 시도 횟수가 초과되었습니다. 잠시 후 다시 시도해주세요.")
        return
    
    # 로그인 시도
    with st.spinner("로그인 중..."):
        result = auth.sign_in(username, password)
    
    if result['success']:
        # 사용자 정보 조회
        with st.spinner("사용자 정보 로딩 중..."):
            user_info_result = auth.get_user_info(result['access_token'])
        
        if user_info_result['success']:
            # 세션 데이터 설정 (브라우저 저장소 포함)
            with st.spinner("세션 설정 중..."):
                session_mgr.set_auth_data(
                    result['access_token'],
                    user_info_result['user_attributes']
                )
            
            st.success("""
            🎉 **로그인 완료!**
            
            - ✅ 인증 성공
            - 🔐 보안 토큰 생성
            - 💾 세션 데이터 저장 (브라우저)
            - ⏰ 8시간 동안 유효
            """)
            
            # 잠시 후 자동으로 대시보드로 이동
            import time
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"사용자 정보 조회 실패: {user_info_result['message']}")
    else:
        session_mgr.increment_login_attempts()
        remaining_attempts = 5 - session_mgr.get_login_attempts()
        
        st.error(result['message'])
        
        if remaining_attempts > 0:
            st.warning(f"남은 로그인 시도 횟수: {remaining_attempts}회")
        else:
            st.error("로그인 시도 횟수가 초과되었습니다.")

def _render_login_help():
    """로그인 도움말 렌더링"""
    with st.expander("❓ 로그인에 문제가 있으신가요?", expanded=False):
        st.markdown("""
        **자주 발생하는 문제들:**
        
        🔹 **사용자명 또는 비밀번호 오류**
           - 대소문자를 정확히 입력했는지 확인해주세요
           - 공백이 없는지 확인해주세요
        
        🔹 **이메일 인증 필요**
           - 회원가입 시 받은 이메일에서 인증을 완료해주세요
           - 인증 메일이 스팸함에 있을 수 있습니다
        
        🔹 **계정 잠금**
           - 여러 번 로그인에 실패하면 일시적으로 잠길 수 있습니다
           - 몇 분 후 다시 시도해주세요
        
        🔹 **세션 관련 문제**
           - 브라우저가 JavaScript를 차단하고 있는지 확인해주세요
           - 브라우저의 저장소(sessionStorage) 기능이 활성화되어야 합니다
           - 시크릿/프라이빗 모드에서는 일부 기능이 제한될 수 있습니다
        
        🔹 **기술적 문제**
           - 브라우저를 새로고침해보세요
           - 다른 브라우저를 사용해보세요
           - 브라우저 캐시를 삭제해보세요
        """)
        
        st.markdown("""
        **🔐 보안 및 세션 정보:**
        
        - **세션 유지**: 로그인 후 8시간 동안 브라우저를 새로고침해도 로그인 상태가 유지됩니다
        - **자동 만료**: 보안을 위해 8시간 후 자동으로 로그아웃됩니다
        - **데이터 저장**: 브라우저의 sessionStorage에 암호화된 토큰이 저장됩니다
        - **프라이버시**: 브라우저를 완전히 닫으면 모든 세션 데이터가 삭제됩니다
        """)
    
    # 추가 기능 테스트
    with st.expander("🧪 세션 기능 테스트", expanded=False):
        st.markdown("""
        **세션 유지 기능을 테스트해보세요:**
        
        1. **로그인 테스트**: 위의 폼으로 로그인하기
        2. **새로고침 테스트**: 로그인 후 브라우저 새로고침 (F5)
        3. **새 탭 테스트**: 로그인 후 새 탭에서 같은 URL 열기
        4. **시간 테스트**: 로그인 후 잠시 기다렸다가 페이지 새로고침
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 페이지 새로고침", help="현재 페이지를 새로고침합니다"):
                st.rerun()
        
        with col2:
            if st.button("🌐 새 창에서 열기", help="새 창에서 현재 페이지를 엽니다"):
                st.markdown("""
                <script>
                window.open(window.location.href, '_blank');
                </script>
                """, unsafe_allow_html=True)
        
        # 현재 브라우저 정보
        st.markdown("**🔍 현재 브라우저 환경:**")
        st.code("""
            JavaScript: 활성화 필요
            sessionStorage: 지원 필요
            Cookie: 선택사항
            브라우저: 모던 브라우저 권장 (Chrome, Firefox, Safari, Edge)
        """)
        
        # 세션 스토리지 지원 확인
        st.components.v1.html("""
            <script>
                function checkSessionStorage() {
                    try {
                        if (typeof(Storage) !== "undefined") {
                            // 세션 스토리지 테스트
                            sessionStorage.setItem('test', 'test');
                            sessionStorage.removeItem('test');
                            
                            document.write('<div style="color: green; font-weight: bold;">✅ sessionStorage 지원됨</div>');
                        } else {
                            document.write('<div style="color: red; font-weight: bold;">❌ sessionStorage 지원되지 않음</div>');
                        }
                    } catch (e) {
                        document.write('<div style="color: red; font-weight: bold;">❌ sessionStorage 접근 불가</div>');
                    }
                }
                
                checkSessionStorage();
            </script>
        """, height=50)