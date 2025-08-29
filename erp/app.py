import streamlit as st
from src.utils.config import load_app_config
from src.utils.session import SessionManager
from src.auth.cognito_auth import CognitoAuth
from src.pages import login, dashboard

# 페이지 설정
st.set_page_config(
    page_title="AWS Cognito Admin",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS 스타일 로드
@st.cache_data
def load_custom_css():
    try:
        with open('src/styles/custom.css', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""

css = load_custom_css()
if css:
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

def show_session_restoration_info():
    """세션 복원 정보 표시"""
    st.markdown("""
    <div style="position: fixed; top: 10px; right: 10px; z-index: 999; 
                background: rgba(0,0,0,0.8); color: white; padding: 10px; 
                border-radius: 5px; font-size: 12px; max-width: 300px;">
        <strong>🔄 세션 복원 기능</strong><br>
        브라우저 새로고침 시 자동으로 로그인 상태를 복원합니다.<br>
        <small>JavaScript와 sessionStorage를 사용합니다.</small>
    </div>
    """, unsafe_allow_html=True)

def main():
    """메인 애플리케이션 함수"""
    
    # 세션 복원 정보 표시 (개발/테스트용)
    if st.sidebar.checkbox("🔧 개발자 정보 표시", value=False):
        show_session_restoration_info()    
    
    try:
        # 설정 및 초기화
        config = load_app_config()
        auth = CognitoAuth(config)
        
        # 세션 상태 확인
        session_status = auth.get_session_status()
        
        # 디버그 정보 (사이드바)
        if st.sidebar.checkbox("🐛 디버그 정보", value=False):
            st.sidebar.markdown("### 🔍 세션 디버그 정보")
            st.sidebar.json(session_status)
            
            # 수동 세션 제어
            st.sidebar.markdown("### 🛠️ 세션 제어")
            
            if st.sidebar.button("🔄 세션 검증"):
                is_valid = auth.validate_session()
                if is_valid:
                    st.sidebar.success("✅ 세션 유효함")
                else:
                    st.sidebar.error("❌ 세션 무효함")
            
            if st.sidebar.button("⏰ 세션 연장"):
                if auth.session_mgr.extend_session():
                    st.sidebar.success("✅ 세션 연장됨")
                else:
                    st.sidebar.error("❌ 세션 연장 실패")
            
            if st.sidebar.button("🗑️ 세션 클리어"):
                auth.session_mgr.clear_auth_data()
                st.sidebar.success("✅ 세션 클리어됨")
                st.rerun()
        
        # 라우팅
        if session_status['is_authenticated'] and session_status['session_valid']:
            # 세션 자동 연장 체크
            auth.extend_session_if_needed()
            
            # 대시보드 표시
            dashboard.show_page(auth)
        else:
            # 만료된 세션이 있으면 클리어
            if session_status['is_authenticated'] and not session_status['session_valid']:
                auth.session_mgr.clear_auth_data()
                st.warning("세션이 만료되어 자동으로 로그아웃되었습니다.")
                st.rerun()
            
            # 로그인 페이지 표시
            login.show_page(auth)
        
        # 하단에 버전 정보
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="text-align: center; color: #666; font-size: 0.8em;">
                🔐 AWS Cognito Admin v2.0 | 
                🔄 세션 유지 기능 | 
                ⚡ Streamlit {streamlit_version}
            </div>
            """.format(streamlit_version=st.__version__), unsafe_allow_html=True)
    
    except Exception as e:
        st.error("애플리케이션 초기화 중 오류가 발생했습니다.")
        st.exception(e)
        
        # 복구 옵션
        st.markdown("### 🔧 복구 옵션")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 페이지 새로고침", type="primary"):
                st.rerun()
        
        with col2:
            if st.button("🧹 세션 초기화"):
                # 세션 스테이트 완전 초기화
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.success("세션이 초기화되었습니다. 페이지를 새로고침하세요.")

def add_session_restore_script():
    """세션 복원 스크립트 추가"""
    script = """
    <script>
    console.log('🔄 Streamlit 세션 복원 스크립트 로드됨');
    
    // 세션 데이터 복원 함수
    function restoreSessionData() {
        try {
            const sessionData = sessionStorage.getItem('streamlit_auth_session');
            if (sessionData) {
                const data = JSON.parse(sessionData);
                const now = new Date().getTime();
                
                if (data.expires_at && now < data.expires_at) {
                    console.log('✅ 유효한 세션 데이터 발견, 복원 중...');
                    
                    // Streamlit에 메시지 전송
                    window.parent.postMessage({
                        type: 'streamlit_session_restore',
                        data: data
                    }, '*');
                    
                    return true;
                } else {
                    console.log('⏰ 만료된 세션 데이터 삭제');
                    sessionStorage.removeItem('streamlit_auth_session');
                }
            }
        } catch (error) {
            console.error('❌ 세션 복원 중 오류:', error);
            sessionStorage.removeItem('streamlit_auth_session');
        }
        return false;
    }
    
    // 페이지 로드 시 세션 복원 시도
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(restoreSessionData, 100);
    });
    
    // 이미 로드된 경우 즉시 실행
    if (document.readyState === 'complete') {
        setTimeout(restoreSessionData, 100);
    }
    
    // 세션 저장/삭제 메시지 리스너
    window.addEventListener('message', function(event) {
        if (event.data.type === 'save_session') {
            try {
                sessionStorage.setItem('streamlit_auth_session', JSON.stringify(event.data.data));
                console.log('💾 세션 데이터 저장됨');
            } catch (error) {
                console.error('❌ 세션 저장 실패:', error);
            }
        } else if (event.data.type === 'clear_session') {
            try {
                sessionStorage.removeItem('streamlit_auth_session');
                console.log('🗑️ 세션 데이터 삭제됨');
            } catch (error) {
                console.error('❌ 세션 삭제 실패:', error);
            }
        }
    });
    
    // 주기적 세션 체크 (5분마다)
    setInterval(function() {
        const sessionData = sessionStorage.getItem('streamlit_auth_session');
        if (sessionData) {
            try {
                const data = JSON.parse(sessionData);
                const now = new Date().getTime();
                
                if (data.expires_at && now >= data.expires_at) {
                    console.log('⏰ 세션 만료로 인한 자동 삭제');
                    sessionStorage.removeItem('streamlit_auth_session');
                }
            } catch (error) {
                console.error('❌ 세션 체크 오류:', error);
            }
        }
    }, 5 * 60 * 1000); // 5분
    
    </script>
    """
    
    st.components.v1.html(script, height=0)

if __name__ == "__main__":
    main()