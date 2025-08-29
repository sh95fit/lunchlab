import streamlit as st
import json
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class SessionManager:
    """Streamlit 세션 상태 관리 클래스"""
    
    SESSION_TIMEOUT_HOURS = 8  # 세션 유효기간 (8시간)
    
    def __init__(self):
        self._init_session()
        self._restore_session_from_browser()
    
    def _init_session(self):
        """세션 초기화"""
        defaults = {
            'authenticated': False,
            'access_token': None,
            'user_info': None,
            'login_attempts': 0,
            'last_login_time': None,
            'session_restored': False
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def _restore_session_from_browser(self):
        """브라우저에서 세션 복원"""
        if st.session_state.get('session_restored', False):
            return
            
        # JavaScript를 통해 sessionStorage에서 데이터 가져오기
        session_data_js = """
        <script>
        function getSessionData() {
            const sessionData = sessionStorage.getItem('streamlit_auth_session');
            if (sessionData) {
                try {
                    const data = JSON.parse(sessionData);
                    // 만료 시간 체크
                    const now = new Date().getTime();
                    if (data.expires_at && now < data.expires_at) {
                        // 세션이 유효한 경우 Streamlit으로 전달
                        window.parent.postMessage({
                            type: 'restore_session',
                            data: data
                        }, '*');
                    } else {
                        // 만료된 세션 삭제
                        sessionStorage.removeItem('streamlit_auth_session');
                    }
                } catch (e) {
                    console.error('Session data parsing error:', e);
                    sessionStorage.removeItem('streamlit_auth_session');
                }
            }
        }
        
        // 페이지 로드 시 실행
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', getSessionData);
        } else {
            getSessionData();
        }
        
        // 메시지 리스너 추가 (Streamlit에서 세션 저장 요청 시)
        window.addEventListener('message', function(event) {
            if (event.data.type === 'save_session') {
                sessionStorage.setItem('streamlit_auth_session', JSON.stringify(event.data.data));
            } else if (event.data.type === 'clear_session') {
                sessionStorage.removeItem('streamlit_auth_session');
            }
        });
        </script>
        """
        
        # JavaScript 실행
        st.components.v1.html(session_data_js, height=0)
        
        # 세션 복원 시도
        self._check_for_restored_session()
        
        st.session_state.session_restored = True

    def _check_for_restored_session(self):
        """복원된 세션 데이터 확인"""
        # URL 파라미터를 통해 세션 복원 데이터 확인
        query_params = st.query_params
        
        if 'session_token' in query_params and 'session_user' in query_params:
            try:
                # URL에서 세션 데이터 복원 (보안을 위해 간단한 토큰만)
                token = query_params['session_token'][0]
                user_data = json.loads(query_params['session_user'][0])
                
                # 간단한 토큰 검증 (실제로는 더 복잡한 검증 필요)
                if token and user_data:
                    st.session_state.authenticated = True
                    st.session_state.access_token = token
                    st.session_state.user_info = user_data
                    st.session_state.last_login_time = datetime.now()
                    
                    # URL 파라미터 제거
                    st.experimental_set_query_params()
            except Exception as e:
                st.error(f"세션 복원 중 오류 발생: {str(e)}")    
    
    def is_authenticated(self) -> bool:
        """인증 상태 확인"""
        authenticated = st.session_state.get('authenticated', False)
        
        if authenticated:
            # 세션 만료 시간 확인
            last_login = st.session_state.get('last_login_time')
            if last_login and isinstance(last_login, datetime):
                if datetime.now() - last_login > timedelta(hours=self.SESSION_TIMEOUT_HOURS):
                    # 세션 만료
                    self.clear_auth_data()
                    return False
        
        return authenticated
    
    def set_auth_data(self, access_token: str, user_info: Dict[str, Any]):
        """인증 데이터 설정 및 브라우저에 저장"""
        current_time = datetime.now()
        expires_at = current_time + timedelta(hours=self.SESSION_TIMEOUT_HOURS)
        
        # Streamlit 세션에 저장
        st.session_state.authenticated = True
        st.session_state.access_token = access_token
        st.session_state.user_info = user_info
        st.session_state.last_login_time = current_time
        st.session_state.login_attempts = 0
        
        # 브라우저 sessionStorage에 저장할 데이터 준비
        session_data = {
            'access_token': access_token,
            'user_info': user_info,
            'login_time': current_time.timestamp(),
            'expires_at': expires_at.timestamp() * 1000  # JavaScript timestamp (ms)
        }
        
        # JavaScript를 통해 sessionStorage에 저장
        save_session_js = f"""
        <script>
        window.parent.postMessage({{
            type: 'save_session',
            data: {json.dumps(session_data)}
        }}, '*');
        </script>
        """
        
        st.components.v1.html(save_session_js, height=0)
        
        # 성공 메시지
        st.success("🎉 로그인이 완료되었습니다! 새로고침해도 로그인 상태가 유지됩니다.")
    
    def clear_auth_data(self):
        """인증 데이터 클리어 및 브라우저에서 삭제"""
        # Streamlit 세션 클리어
        st.session_state.authenticated = False
        st.session_state.access_token = None
        st.session_state.user_info = None
        st.session_state.last_login_time = None
        
        # JavaScript를 통해 sessionStorage에서 삭제
        clear_session_js = """
            <script>
            window.parent.postMessage({
                type: 'clear_session'
            }, '*');
            </script>
        """
        
        st.components.v1.html(clear_session_js, height=0)
    
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

    def get_session_info(self) -> Dict[str, Any]:
        """세션 정보 반환"""
        last_login = self.get_last_login_time()
        if last_login and isinstance(last_login, datetime):
            session_duration = datetime.now() - last_login
            expires_in = timedelta(hours=self.SESSION_TIMEOUT_HOURS) - session_duration
            
            return {
                'is_authenticated': self.is_authenticated(),
                'login_time': last_login.strftime('%Y-%m-%d %H:%M:%S'),
                'session_duration': str(session_duration).split('.')[0],  # 초 제거
                'expires_in': str(expires_in).split('.')[0] if expires_in.total_seconds() > 0 else "만료됨",
                'expires_in_minutes': int(expires_in.total_seconds() / 60) if expires_in.total_seconds() > 0 else 0
            }
        
        return {
            'is_authenticated': False,
            'login_time': None,
            'session_duration': None,
            'expires_in': None,
            'expires_in_minutes': 0
        }

    def extend_session(self):
        """세션 연장"""
        if self.is_authenticated():
            current_time = datetime.now()
            st.session_state.last_login_time = current_time
            
            # 브라우저 세션도 업데이트
            access_token = self.get_access_token()
            user_info = self.get_user_info()
            
            if access_token and user_info:
                self.set_auth_data(access_token, user_info)
                return True
        return False