import uuid
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Interval, Text
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.sql import func
from .supabase_client import Base

# ---------------------------
# 1. 사용자 세션 테이블
# ---------------------------
class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), unique=True, nullable=False)
    user_id = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    email = Column(String(255))
    access_token = Column(Text)
    refresh_token = Column(Text)
    user_attributes = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    user_agent = Column(Text)
    ip_address = Column(INET)
    login_method = Column(String(50), default="cognito")


# ---------------------------
# 2. 로그인 이력 테이블
# ---------------------------
class LoginHistory(Base):
    __tablename__ = "login_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    login_time = Column(DateTime(timezone=True), server_default=func.now())
    logout_time = Column(DateTime(timezone=True))
    success = Column(Boolean, default=True, nullable=False)
    failure_reason = Column(String(500))
    ip_address = Column(INET)
    user_agent = Column(Text)
    session_duration = Column(Interval)
    location_country = Column(String(100))
    location_city = Column(String(100))


# ---------------------------
# 3. 사용자 활동 테이블
# ---------------------------
class UserActivity(Base):
    __tablename__ = "user_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), nullable=False)
    user_id = Column(String(255), nullable=False)
    activity_type = Column(String(100), nullable=False)
    activity_detail = Column(JSON, default={})
    page_path = Column(String(500))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(INET)
    user_agent = Column(Text)


# ---------------------------
# 4. 시스템 설정 테이블
# ---------------------------
class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    setting_key = Column(String(255), unique=True, nullable=False)
    setting_value = Column(JSON, nullable=False)
    description = Column(Text)
    category = Column(String(100), default="general")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(String(255))