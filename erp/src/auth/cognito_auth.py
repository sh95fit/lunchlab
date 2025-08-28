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
                return {
                    'success': True, 
                    'access_token': access_token, 
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
                'InvalidParameterException': '입력 정보가 올바르지 않습니다.'
            }
            
            message = error_messages.get(error_code, f'로그인 실패: {e.response["Error"]["Message"]}')
            return {'success': False, 'message': message}
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
            
            return {
                'success': True,
                'user_attributes': user_attributes
            }
        except ClientError as e:
            error_messages = {
                'NotAuthorizedException': '인증이 만료되었습니다. 다시 로그인해주세요.',
                'UserNotFoundException': '사용자를 찾을 수 없습니다.'
            }
            
            error_code = e.response['Error']['Code']
            message = error_messages.get(error_code, f'사용자 정보 조회 실패: {e.response["Error"]["Message"]}')
            
            return {'success': False, 'message': message}
        except Exception as e:
            return {'success': False, 'message': f'예상치 못한 오류가 발생했습니다: {str(e)}'}
    
    def logout(self):
        """로그아웃"""
        self.session_mgr.clear_auth_data()
        st.rerun()