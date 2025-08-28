import streamlit as st
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# AWS Cognito 설정
AWS_COGNITO_CLIENT_ID = os.getenv('AWS_COGNITO_CLIENT_ID')
AWS_COGNITO_USER_POOL_ID = os.getenv('AWS_COGNITO_USER_POOL_ID')
AWS_REGION = os.getenv('AWS_REGION', 'ap-northeast-2')  # 기본값 설정

class CognitoAuth:
    def __init__(self):
        self.client = boto3.client('cognito-idp', region_name=AWS_REGION)
        self.client_id = AWS_COGNITO_CLIENT_ID
        self.user_pool_id = AWS_COGNITO_USER_POOL_ID
    
    def sign_up(self, username, password, email, phone_number=None, given_name=None, family_name=None):
        """회원가입"""
        try:
            # 기본 필수 속성
            user_attributes = [
                {'Name': 'email', 'Value': email}
            ]
            
            # 선택적 속성 추가
            if phone_number and phone_number.strip():
                # 전화번호 형식 검증 (간단한 검사)
                if not phone_number.startswith('+'):
                    phone_number = '+82' + phone_number.lstrip('0')
                user_attributes.append({'Name': 'phone_number', 'Value': phone_number})
            
            if given_name and given_name.strip():
                user_attributes.append({'Name': 'given_name', 'Value': given_name.strip()})
            
            if family_name and family_name.strip():
                user_attributes.append({'Name': 'family_name', 'Value': family_name.strip()})
            
            params = {
                'ClientId': self.client_id,
                'Username': username,
                'Password': password,
                'UserAttributes': user_attributes
            }
            
            response = self.client.sign_up(**params)
            return {'success': True, 'message': '회원가입이 완료되었습니다. 이메일 인증을 확인해주세요.'}
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UsernameExistsException':
                return {'success': False, 'message': '이미 존재하는 사용자명입니다.'}
            elif error_code == 'InvalidPasswordException':
                return {'success': False, 'message': '비밀번호가 정책에 맞지 않습니다.'}
            elif error_code == 'InvalidParameterException':
                return {'success': False, 'message': '입력 정보가 올바르지 않습니다. (전화번호 형식 확인)'}
            else:
                return {'success': False, 'message': f'회원가입 실패: {e.response["Error"]["Message"]}'}
    
    def confirm_sign_up(self, username, confirmation_code):
        """이메일 인증 확인"""
        try:
            params = {
                'ClientId': self.client_id,
                'Username': username,
                'ConfirmationCode': confirmation_code
            }
            
            self.client.confirm_sign_up(**params)
            return {'success': True, 'message': '이메일 인증이 완료되었습니다.'}
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'CodeMismatchException':
                return {'success': False, 'message': '인증 코드가 일치하지 않습니다.'}
            elif error_code == 'ExpiredCodeException':
                return {'success': False, 'message': '인증 코드가 만료되었습니다.'}
            elif error_code == 'UserNotFoundException':
                return {'success': False, 'message': '사용자를 찾을 수 없습니다.'}
            else:
                return {'success': False, 'message': f'인증 실패: {e.response["Error"]["Message"]}'}
    
    def sign_in(self, username, password):
        """로그인"""
        try:
            params = {
                'ClientId': self.client_id,
                'AuthFlow': 'USER_PASSWORD_AUTH',
                'AuthParameters': {
                    'USERNAME': username,
                    'PASSWORD': password
                }
            }
            
            response = self.client.initiate_auth(**params)
            
            if 'AuthenticationResult' in response:
                access_token = response['AuthenticationResult']['AccessToken']
                return {'success': True, 'access_token': access_token, 'message': '로그인 성공'}
            else:
                return {'success': False, 'message': '로그인 실패'}
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NotAuthorizedException':
                return {'success': False, 'message': '잘못된 사용자명 또는 비밀번호입니다.'}
            elif error_code == 'UserNotConfirmedException':
                return {'success': False, 'message': '이메일 인증이 필요합니다.'}
            elif error_code == 'UserNotFoundException':
                return {'success': False, 'message': '사용자를 찾을 수 없습니다.'}
            else:
                return {'success': False, 'message': f'로그인 실패: {e.response["Error"]["Message"]}'}
    
    def get_user_info(self, access_token):
        """사용자 정보 조회"""
        try:
            response = self.client.get_user(AccessToken=access_token)
            user_attributes = {}
            for attr in response['UserAttributes']:
                user_attributes[attr['Name']] = attr['Value']
            return {'success': True, 'user_attributes': user_attributes}
        except ClientError as e:
            return {'success': False, 'message': f'사용자 정보 조회 실패: {e.response["Error"]["Message"]}'}
    
    def resend_confirmation_code(self, username):
        """인증 코드 재전송"""
        try:
            params = {
                'ClientId': self.client_id,
                'Username': username
            }
            
            self.client.resend_confirmation_code(**params)
            return {'success': True, 'message': '인증 코드를 재전송했습니다.'}
            
        except ClientError as e:
            return {'success': False, 'message': f'인증 코드 재전송 실패: {e.response["Error"]["Message"]}'}

# Streamlit 앱 설정
st.set_page_config(page_title="AWS Cognito 인증", page_icon="🔐", layout="wide")

# 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

# Cognito 인스턴스 생성
auth = CognitoAuth()

def login_page():
    """로그인/회원가입 페이지"""
    st.title("🔐 로그인 / 회원가입")
    
    # 탭으로 로그인/회원가입 구분
    tab1, tab2, tab3 = st.tabs(["로그인", "회원가입", "이메일 인증"])
    
    with tab1:
        st.subheader("로그인")
        with st.form("login_form"):
            username = st.text_input("사용자명")
            password = st.text_input("비밀번호", type="password")
            login_button = st.form_submit_button("로그인")
            
            if login_button:
                if username and password:
                    with st.spinner("로그인 중..."):
                        result = auth.sign_in(username, password)
                    
                    if result['success']:
                        st.session_state.authenticated = True
                        st.session_state.access_token = result['access_token']
                        
                        # 사용자 정보 조회
                        user_info_result = auth.get_user_info(result['access_token'])
                        if user_info_result['success']:
                            st.session_state.user_info = user_info_result['user_attributes']
                        
                        st.success(result['message'])
                        st.rerun()
                    else:
                        st.error(result['message'])
                else:
                    st.error("모든 필드를 입력해주세요.")
    
    with tab2:
        st.subheader("회원가입")
        with st.form("signup_form"):
            new_username = st.text_input("사용자명 (신규)")
            new_email = st.text_input("이메일 *")
            new_phone = st.text_input("전화번호 (예: 01012345678)")
            new_given_name = st.text_input("이름")
            new_family_name = st.text_input("성")
            new_password = st.text_input("비밀번호 (신규) *", type="password")
            confirm_password = st.text_input("비밀번호 확인 *", type="password")
            signup_button = st.form_submit_button("회원가입")
            
            if signup_button:
                if new_username and new_email and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("비밀번호가 일치하지 않습니다.")
                    else:
                        with st.spinner("회원가입 중..."):
                            result = auth.sign_up(
                                username=new_username, 
                                password=new_password, 
                                email=new_email,
                                phone_number=new_phone,
                                given_name=new_given_name,
                                family_name=new_family_name
                            )
                        
                        if result['success']:
                            st.success(result['message'])
                            st.info("이메일 인증 탭으로 이동해서 인증 코드를 입력해주세요.")
                        else:
                            st.error(result['message'])
                else:
                    st.error("필수 필드(*)를 모두 입력해주세요.")
    
    with tab3:
        st.subheader("이메일 인증")
        st.info("📧 회원가입 후 이메일로 전송된 6자리 인증 코드를 입력해주세요.")
        
        with st.form("confirm_form"):
            confirm_username = st.text_input("사용자명 (인증용)")
            confirmation_code = st.text_input("인증 코드 (6자리)")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                confirm_button = st.form_submit_button("인증 확인")
            with col2:
                resend_button = st.form_submit_button("코드 재전송")
            
            if confirm_button:
                if confirm_username and confirmation_code:
                    with st.spinner("인증 중..."):
                        result = auth.confirm_sign_up(confirm_username, confirmation_code)
                    
                    if result['success']:
                        st.success(result['message'])
                        st.info("이제 로그인 탭에서 로그인할 수 있습니다.")
                    else:
                        st.error(result['message'])
                else:
                    st.error("모든 필드를 입력해주세요.")
            
            if resend_button:
                if confirm_username:
                    with st.spinner("코드 재전송 중..."):
                        result = auth.resend_confirmation_code(confirm_username)
                    
                    if result['success']:
                        st.success(result['message'])
                    else:
                        st.error(result['message'])
                else:
                    st.error("사용자명을 입력해주세요.")

def main_page():
    """메인 페이지 (인증 후)"""
    st.title("🎉 메인 대시보드")
    
    # 헤더 영역
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.session_state.user_info:
            username = st.session_state.user_info.get('preferred_username', 
                      st.session_state.user_info.get('email', '사용자'))
            st.write(f"안녕하세요, **{username}**님! 👋")
        else:
            st.write("환영합니다! 👋")
    
    with col2:
        if st.button("로그아웃", type="secondary"):
            st.session_state.authenticated = False
            st.session_state.access_token = None
            st.session_state.user_info = None
            st.rerun()
    
    st.divider()
    
    # 사용자 정보 표시
    if st.session_state.user_info:
        st.subheader("📋 사용자 정보")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**이메일:** {st.session_state.user_info.get('email', 'N/A')}")
            st.info(f"**이메일 인증:** {'✅' if st.session_state.user_info.get('email_verified') == 'true' else '❌'}")
            
            # 이름 정보 표시
            given_name = st.session_state.user_info.get('given_name', '')
            family_name = st.session_state.user_info.get('family_name', '')
            if given_name or family_name:
                full_name = f"{family_name} {given_name}".strip()
                st.info(f"**이름:** {full_name}")
        
        with col2:
            st.info(f"**사용자 ID:** {st.session_state.user_info.get('sub', 'N/A')}")
            
            # 전화번호 정보 표시
            phone_number = st.session_state.user_info.get('phone_number', '')
            if phone_number:
                phone_verified = st.session_state.user_info.get('phone_number_verified', 'false')
                st.info(f"**전화번호:** {phone_number}")
                st.info(f"**전화번호 인증:** {'✅' if phone_verified == 'true' else '❌'}")
            else:
                st.info(f"**전화번호:** 등록되지 않음")
            
            # 업데이트 시간 표시
            updated_at = st.session_state.user_info.get('updated_at', 'N/A')
            if updated_at != 'N/A':
                import datetime
                try:
                    # Unix 타임스탬프를 날짜로 변환
                    dt = datetime.datetime.fromtimestamp(int(updated_at))
                    updated_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                    st.info(f"**최근 업데이트:** {updated_str}")
                except:
                    st.info(f"**최근 업데이트:** {updated_at}")
            else:
                st.info(f"**최근 업데이트:** N/A")
    
    st.divider()
    
    # 메인 컨텐츠 영역
    st.subheader("🚀 대시보드")
    
    # 예시 컨텐츠
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("총 사용자", "1,234", "12")
    
    with col2:
        st.metric("오늘 방문자", "567", "5")
    
    with col3:
        st.metric("활성 세션", "89", "-2")
    
    # 차트 예시
    st.subheader("📊 통계")
    
    import pandas as pd
    import numpy as np
    
    # 예시 데이터
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    data = pd.DataFrame({
        '날짜': dates,
        '방문자': np.random.randint(100, 1000, 30),
        '페이지뷰': np.random.randint(200, 2000, 30)
    })
    
    st.line_chart(data.set_index('날짜'))
    
    # 기능 메뉴
    st.subheader("🛠️ 기능")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📁 파일 관리", use_container_width=True):
            st.info("파일 관리 기능")
    
    with col2:
        if st.button("👥 사용자 관리", use_container_width=True):
            st.info("사용자 관리 기능")
    
    with col3:
        if st.button("📈 분석 도구", use_container_width=True):
            st.info("분석 도구 기능")
    
    with col4:
        if st.button("⚙️ 설정", use_container_width=True):
            st.info("설정 기능")

# 메인 앱 로직
def main():
    # AWS 설정 확인
    if not AWS_COGNITO_CLIENT_ID or not AWS_COGNITO_USER_POOL_ID:
        st.error("AWS Cognito 설정이 누락되었습니다. .env 파일을 확인해주세요.")
        st.code("""
# .env 파일 예시
AWS_COGNITO_CLIENT_ID=your_client_id_here
AWS_COGNITO_USER_POOL_ID=your_user_pool_id_here
AWS_REGION=ap-northeast-2
        """, language="bash")
        return
    
    # 인증 상태에 따라 페이지 렌더링
    if st.session_state.authenticated:
        main_page()
    else:
        login_page()

if __name__ == "__main__":
    main()