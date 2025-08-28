import streamlit as st
from typing import Optional, Dict, Any

class SessionManager:
    """Streamlit 세션 상태 관리 클래스"""
    
    def __init__(self):
        self._init_session()
    
    def _init_session(self):
        """세션 초기화"""
        defaults = {
            'authenticated': False,
            'access_token': None,
            'user_info': None,
            'login_attempts': 0,
            'last_login_time': None
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def is_authenticated(self) -> bool:
        """인증 상태 확인"""
        return st.session_state.get('authenticated', False)
    
    def set_auth_data(self, access_token: str, user_info: Dict[str, Any]):
        """인증 데이터 설정"""
        import datetime
        
        st.session_state.authenticated = True
        st.session_state.access_token = access_token
        st.session_state.user_info = user_info
        st.session_state.last_login_time = datetime.datetime.now()
        st.session_state.login_attempts = 0  # 성공 시 초기화
    
    def clear_auth_data(self):
        """인증 데이터 클리어"""
        st.session_state.authenticated = False
        st.session_state.access_token = None
        st.session_state.user_info = None
        st.session_state.last_login_time = None
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """사용자 정보 반환"""
        return st.session_state.get('user_info')
    
    def get_access_token(self) -> Optional[str]:
        """액세스 토큰 반환"""
        return st.session_state.get('access_token')
    
    def increment_login_attempts(self):
        """로그인 시도 횟수 증가"""
        st.session_state.login_attempts = st.session_state.get('login_attempts', 0) + 1
    
    def get_login_attempts(self) -> int:
        """로그인 시도 횟수 반환"""
        return st.session_state.get('login_attempts', 0)
    
    def get_last_login_time(self):
        """마지막 로그인 시간 반환"""
        return st.session_state.get('last_login_time')