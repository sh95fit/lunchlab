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

def main():
    """메인 애플리케이션 함수"""
    # 설정 및 초기화
    config = load_app_config()
    session_mgr = SessionManager()
    auth = CognitoAuth(config)
    
    # 라우팅
    if session_mgr.is_authenticated():
        dashboard.show_page(auth)
    else:
        login.show_page(auth)

if __name__ == "__main__":
    main()