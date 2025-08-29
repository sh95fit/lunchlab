import boto3
import streamlit as st
from botocore.exceptions import ClientError
from typing import Dict, Any
from src.utils.session import SessionManager

class CognitoAuth:
    """AWS Cognito 인증 관리 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = boto3.client('cognito-idp', region_name=config['aws']['region'])
        self.session_mgr = SessionManager()
        
        self.client_id = config['aws']['cognito_client_id']
        self.user_pool_id = config['aws']['cognito_user_pool_id']
   
        # 초기화 시 세션 확인
        self._check_existing_session()
    
    def _check_existing_session(self):
        """기존 세션 확인 및 검증"""
        if self.session_mgr.is_authenticated():
            # 토큰 유효성 검사
            access_token = self.session_mgr.get_access_token()
            if access_token:
                user_info_result = self.get_user_info(access_token)
                if not user_info_result['success']:
                    # 토큰이 유효하지 않으면 세션 클리어
                    self.session_mgr.clear_auth_data()
                    st.warning("세션이 만료되어 다시 로그인이 필요합니다.")
    
    def sign_in(self, username: str, password: str) -> Dict[str, Any]:
        """로그인"""
        try:
            params = {
                'ClientId': self.client_id,
                'AuthFlow': 'USER_PASSWORD_AUTH',
                'AuthParameters': {
                    'USERNAME': username.strip(),
                    'PASSWORD': password
                }
            }
            
            response = self.client.initiate_auth(**params)
            
            if 'AuthenticationResult' in response:
                access_token = response['AuthenticationResult']['AccessToken']
                refresh_token = response['AuthenticationResult'].get('RefreshToken')
                expires_in = response['AuthenticationResult'].get('ExpiresIn', 3600)
                
                return {
                    'success': True, 
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'expires_in': expires_in,
                    'message': '로그인이 완료되었습니다.'
                }
            else:
                return {'success': False, 'message': '로그인에 실패했습니다.'}
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_messages = {
                'NotAuthorizedException': '사용자명 또는 비밀번호가 올바르지 않습니다.',
                'UserNotConfirmedException': '이메일 인증이 필요합니다.',
                'UserNotFoundException': '존재하지 않는 사용자입니다.',
                'TooManyRequestsException': '너무 많은 요청이 발생했습니다. 잠시 후 다시 시도해주세요.',
                'InvalidParameterException': '입력 정보가 올바르지 않습니다.',
                'PasswordResetRequiredException': '비밀번호 재설정이 필요합니다.',
                'UserNotAuthorizedException': '사용자가 승인되지 않았습니다.',
                'InvalidUserPoolConfigurationException': 'User Pool 설정에 오류가 있습니다.'
            }
            
            message = error_messages.get(error_code, f'로그인 실패: {e.response["Error"]["Message"]}')
            return {'success': False, 'message': message, 'error_code': error_code}
        except Exception as e:
            return {'success': False, 'message': f'예상치 못한 오류가 발생했습니다: {str(e)}'}
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """사용자 정보 조회"""
        try:
            response = self.client.get_user(AccessToken=access_token)
            user_attributes = {
                attr['Name']: attr['Value'] 
                for attr in response['UserAttributes']
            }
            
            # 추가 메타데이터
            user_info = {
                'user_attributes': user_attributes,
                'username': response.get('Username'),
                'user_status': 'CONFIRMED',  # get_user 성공시 항상 CONFIRMED
                'mfa_enabled': len(response.get('MFAOptions', [])) > 0
            }
            
            return {
                'success': True,
                'user_attributes': user_attributes,
                'user_info': user_info
            }
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_messages = {
                'NotAuthorizedException': '인증이 만료되었습니다. 다시 로그인해주세요.',
                'UserNotFoundException': '사용자를 찾을 수 없습니다.',
                'InvalidParameterException': '잘못된 토큰입니다.',
                'TokenRefreshRequiredException': '토큰 갱신이 필요합니다.'
            }
            
            message = error_messages.get(error_code, f'사용자 정보 조회 실패: {e.response["Error"]["Message"]}')
            
            return {'success': False, 'message': message, 'error_code': error_code}
        except Exception as e:
            return {'success': False, 'message': f'예상치 못한 오류가 발생했습니다: {str(e)}'}
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """토큰 갱신"""
        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='REFRESH_TOKEN_AUTH',
                AuthParameters={
                    'REFRESH_TOKEN': refresh_token
                }
            )
            
            if 'AuthenticationResult' in response:
                access_token = response['AuthenticationResult']['AccessToken']
                expires_in = response['AuthenticationResult'].get('ExpiresIn', 3600)
                
                return {
                    'success': True,
                    'access_token': access_token,
                    'expires_in': expires_in,
                    'message': '토큰이 갱신되었습니다.'
                }
            else:
                return {'success': False, 'message': '토큰 갱신에 실패했습니다.'}
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_messages = {
                'NotAuthorizedException': '리프레시 토큰이 유효하지 않습니다.',
                'InvalidParameterException': '잘못된 토큰입니다.',
                'TokenRefreshRequiredException': '리프레시 토큰이 만료되었습니다.'
            }
            
            message = error_messages.get(error_code, f'토큰 갱신 실패: {e.response["Error"]["Message"]}')
            return {'success': False, 'message': message, 'error_code': error_code}
        except Exception as e:
            return {'success': False, 'message': f'토큰 갱신 중 오류 발생: {str(e)}'}
    
    def validate_session(self) -> bool:
        """현재 세션 유효성 검증"""
        if not self.session_mgr.is_authenticated():
            return False
        
        access_token = self.session_mgr.get_access_token()
        if not access_token:
            return False
        
        # 토큰 유효성 확인
        user_info_result = self.get_user_info(access_token)
        return user_info_result['success']    
    
    def logout(self):
        """로그아웃"""
        try:
            access_token = self.session_mgr.get_access_token()
            
            # AWS Cognito에서 로그아웃 (선택적)
            if access_token:
                try:
                    self.client.global_sign_out(AccessToken=access_token)
                except ClientError:
                    # 토큰이 이미 만료된 경우 등 무시
                    pass
            
            # 로컬 세션 클리어
            self.session_mgr.clear_auth_data()
            
            st.success("로그아웃이 완료되었습니다.")
            
        except Exception as e:
            # 오류가 발생해도 로컬 세션은 클리어
            self.session_mgr.clear_auth_data()
            st.warning(f"로그아웃 처리 중 일부 오류가 발생했지만 세션이 종료되었습니다: {str(e)}")
        
        finally:
            st.rerun()
    
    def get_session_status(self) -> Dict[str, Any]:
        """세션 상태 정보 반환"""
        session_info = self.session_mgr.get_session_info()
        
        return {
            'is_authenticated': session_info['is_authenticated'],
            'session_valid': self.validate_session() if session_info['is_authenticated'] else False,
            'login_time': session_info.get('login_time'),
            'expires_in_minutes': session_info.get('expires_in_minutes', 0),
            'user_info': self.session_mgr.get_user_info()
        }
    
    def extend_session_if_needed(self) -> bool:
        """필요시 세션 연장"""
        if not self.session_mgr.is_authenticated():
            return False
        
        session_info = self.session_mgr.get_session_info()
        remaining_minutes = session_info.get('expires_in_minutes', 0)
        
        # 30분 미만 남았을 때 자동 연장
        if remaining_minutes < 30 and remaining_minutes > 0:
            return self.session_mgr.extend_session()
        
        return True            
            