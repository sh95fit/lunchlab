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
    </div>
    """, unsafe_allow_html=True)
    
    # 로그인 폼
    _render_login_form(auth)
    
    # 로그인 도움말
    _render_login_help()

def _render_login_form(auth: CognitoAuth):
    """로그인 폼 렌더링"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔑 로그인")
        
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
        user_info_result = auth.get_user_info(result['access_token'])
        
        if user_info_result['success']:
            session_mgr.set_auth_data(
                result['access_token'],
                user_info_result['user_attributes']
            )
            st.success(result['message'])
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
        
        🔹 **기술적 문제**
           - 브라우저를 새로고침해보세요
           - 다른 브라우저를 사용해보세요
        """)