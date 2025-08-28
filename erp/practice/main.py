
import streamlit as st
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
import urllib.parse
import requests

# ---------------------------
# 환경 변수 로드
# ---------------------------
load_dotenv()

AWS_COGNITO_CLIENT_ID = os.getenv('AWS_COGNITO_CLIENT_ID')
AWS_COGNITO_USER_POOL_ID = os.getenv('AWS_COGNITO_USER_POOL_ID')
AWS_REGION = os.getenv('AWS_REGION', 'ap-northeast-2')
COGNITO_DOMAIN = f"lunchlab-admin.auth.{AWS_REGION}.amazoncognito.com"
REDIRECT_URI = "http://localhost:8501"  # Streamlit 로컬 URL

# ---------------------------
# Cognito 인증 클래스
# ---------------------------
class CognitoAuth:
    def __init__(self):
        self.client = boto3.client('cognito-idp', region_name=AWS_REGION)
        self.client_id = AWS_COGNITO_CLIENT_ID
        self.user_pool_id = AWS_COGNITO_USER_POOL_ID
        self.domain = COGNITO_DOMAIN
        self.redirect_uri = REDIRECT_URI

    def get_login_url(self):
        """Hosted UI 로그인 URL 생성 (회원가입도 로그인 화면에서 가능)"""
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': 'aws.cognito.signin.user.admin email openid phone profile',
            'redirect_uri': self.redirect_uri
        }
        return f"https://{self.domain}/login?{urllib.parse.urlencode(params)}"

    def exchange_code_for_tokens(self, code):
        """Authorization Code를 Access Token으로 교환"""
        token_url = f"https://{self.domain}/oauth2/token"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        try:
            resp = requests.post(token_url, headers=headers, data=data)
            if resp.status_code == 200:
                tokens = resp.json()
                return {
                    'success': True,
                    'access_token': tokens.get('access_token'),
                    'id_token': tokens.get('id_token'),
                    'refresh_token': tokens.get('refresh_token')
                }
            else:
                return {'success': False, 'message': resp.text}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def get_user_info(self, access_token):
        """사용자 정보 조회"""
        try:
            resp = self.client.get_user(AccessToken=access_token)
            return {
                'success': True,
                'user_attributes': {attr['Name']: attr['Value'] for attr in resp['UserAttributes']}
            }
        except ClientError as e:
            return {'success': False, 'message': e.response["Error"]["Message"]}

    def get_logout_url(self):
        """Hosted UI 로그아웃 URL 생성"""
        params = {'client_id': self.client_id, 'logout_uri': self.redirect_uri}
        return f"https://{self.domain}/logout?{urllib.parse.urlencode(params)}"


# ---------------------------
# Streamlit 세션 초기화
# ---------------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

auth = CognitoAuth()


# ---------------------------
# 콜백 처리
# ---------------------------
def handle_callback():
    query_params = st.query_params
    if 'code' in query_params:
        code = query_params['code']
        with st.spinner("인증 처리 중..."):
            token_result = auth.exchange_code_for_tokens(code)
            if token_result['success']:
                st.session_state.access_token = token_result['access_token']
                user_info_result = auth.get_user_info(token_result['access_token'])
                if user_info_result['success']:
                    st.session_state.user_info = user_info_result['user_attributes']
                    st.session_state.authenticated = True
                    st.query_params.clear()
                    st.rerun()
                else:
                    st.error(f"사용자 정보 조회 실패: {user_info_result['message']}")
            else:
                st.error(f"토큰 교환 실패: {token_result['message']}")
    elif 'error' in query_params:
        st.error(f"인증 오류: {query_params.get('error')} - {query_params.get('error_description', '')}")


# ---------------------------
# 로그인 페이지
# ---------------------------
def login_page():
    st.title("🔐 AWS Cognito 로그인")
    st.markdown("---")
    st.write("Hosted UI를 통해 로그인이 가능합니다.")
    login_url = auth.get_login_url()
    st.link_button("🔑 로그인", login_url, use_container_width=True)
    st.markdown("---")


# ---------------------------
# 메인 페이지
# ---------------------------
def main_page():
    st.title("🎉 메인 대시보드")
    col1, col2 = st.columns([3, 1])
    with col1:
        username = st.session_state.user_info.get('preferred_username',
                     st.session_state.user_info.get('email', '사용자'))
        st.write(f"안녕하세요, **{username}**님! 👋")
    with col2:
        if st.button("로그아웃"):
            st.session_state.authenticated = False
            st.session_state.access_token = None
            st.session_state.user_info = None
            st.write(f"[Hosted UI 로그아웃]({auth.get_logout_url()})")
            st.rerun()

    st.divider()
    # 사용자 정보 표시
    if st.session_state.user_info:
        st.subheader("📋 사용자 정보")
        for k, v in st.session_state.user_info.items():
            st.info(f"{k}: {v}")

    st.divider()
    st.subheader("🚀 대시보드 예시")
    import pandas as pd, numpy as np
    data = pd.DataFrame({
        '날짜': pd.date_range('2024-01-01', periods=30),
        '방문자': np.random.randint(100, 1000, 30),
        '페이지뷰': np.random.randint(200, 2000, 30)
    }).set_index('날짜')
    st.line_chart(data)


# ---------------------------
# 메인 함수
# ---------------------------
def main():
    if not AWS_COGNITO_CLIENT_ID or not AWS_COGNITO_USER_POOL_ID:
        st.error("AWS Cognito 설정이 필요합니다. .env 확인")
        return

    handle_callback()
    if st.session_state.authenticated:
        main_page()
    else:
        login_page()


if __name__ == "__main__":
    main()