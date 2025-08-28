import os
from typing import Dict, Any
from dotenv import load_dotenv
import streamlit as st

@st.cache_data
def load_app_config() -> Dict[str, Any]:
    """앱 설정을 로드하고 캐싱"""
    load_dotenv()
    
    config = {
        'aws': {
            'cognito_client_id': os.getenv('AWS_COGNITO_CLIENT_ID'),
            'cognito_user_pool_id': os.getenv('AWS_COGNITO_USER_POOL_ID'),
            'region': os.getenv('AWS_REGION', 'ap-northeast-2'),
        }
    }
    
    # 필수 설정 검증
    required_keys = [
        ('aws.cognito_client_id', 'AWS_COGNITO_CLIENT_ID'),
        ('aws.cognito_user_pool_id', 'AWS_COGNITO_USER_POOL_ID')
    ]
    
    missing_configs = []
    
    for config_path, env_name in required_keys:
        keys = config_path.split('.')
        value = config
        for k in keys:
            value = value.get(k)
        
        if not value:
            missing_configs.append(env_name)
    
    if missing_configs:
        st.error(f"필수 환경변수가 누락되었습니다: {', '.join(missing_configs)}")
        st.code("""
# .env 파일 예시
AWS_COGNITO_CLIENT_ID=your_client_id_here
AWS_COGNITO_USER_POOL_ID=your_user_pool_id_here
AWS_REGION=ap-northeast-2
        """, language="bash")
        st.stop()
    
    return config

def get_config_value(config: Dict[str, Any], key_path: str, default=None):
    """중첩된 딕셔너리에서 값을 안전하게 가져오기"""
    keys = key_path.split('.')
    value = config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value