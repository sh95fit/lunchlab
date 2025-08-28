import re
from typing import Dict, Optional

class ValidationResult:
    """검증 결과 클래스"""
    def __init__(self, is_valid: bool, message: Optional[str] = None):
        self.is_valid = is_valid
        self.message = message

class InputValidator:
    """입력 검증 유틸리티"""
    
    @staticmethod
    def validate_username(username: str) -> ValidationResult:
        """사용자명 검증"""
        if not username or not username.strip():
            return ValidationResult(False, "사용자명을 입력해주세요.")
        
        username = username.strip()
        
        if len(username) < 3:
            return ValidationResult(False, "사용자명은 3자 이상이어야 합니다.")
        
        if len(username) > 50:
            return ValidationResult(False, "사용자명은 50자 이하여야 합니다.")
        
        return ValidationResult(True)
    
    @staticmethod
    def validate_password(password: str) -> ValidationResult:
        """비밀번호 검증"""
        if not password:
            return ValidationResult(False, "비밀번호를 입력해주세요.")
        
        if len(password) < 8:
            return ValidationResult(False, "비밀번호는 8자 이상이어야 합니다.")
        
        return ValidationResult(True)
    
    @staticmethod
    def validate_email(email: str) -> ValidationResult:
        """이메일 검증"""
        if not email or not email.strip():
            return ValidationResult(False, "이메일을 입력해주세요.")
        
        email = email.strip()
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            return ValidationResult(False, "올바른 이메일 형식이 아닙니다.")
        
        return ValidationResult(True)

def validate_login_form(username: str, password: str) -> Dict[str, ValidationResult]:
    """로그인 폼 전체 검증"""
    return {
        'username': InputValidator.validate_username(username),
        'password': InputValidator.validate_password(password)
    }