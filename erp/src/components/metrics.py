import streamlit as st
import random
from datetime import datetime, timedelta

def render_metrics():
    """메트릭스 렌더링"""
    st.markdown("### 📊 주요 지표")
    
    # 실시간 데이터 시뮬레이션
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_users = _get_random_metric(1000, 1500)
        user_change = _get_random_change(-5, 15)
        st.metric(
            "총 사용자", 
            f"{total_users:,}", 
            f"{user_change:+d}",
            help="플랫폼에 등록된 총 사용자 수"
        )
    
    with col2:
        daily_visitors = _get_random_metric(200, 800)
        visitor_change = _get_random_change(-10, 20)
        st.metric(
            "오늘 방문자", 
            f"{daily_visitors:,}", 
            f"{visitor_change:+d}",
            help="오늘 플랫폼에 접속한 순 방문자 수"
        )
    
    with col3:
        active_sessions = _get_random_metric(50, 150)
        session_change = _get_random_change(-5, 10)
        st.metric(
            "활성 세션", 
            f"{active_sessions:,}", 
            f"{session_change:+d}",
            help="현재 활성화된 사용자 세션 수"
        )
    
    with col4:
        response_time = _get_random_metric(150, 350) / 100
        time_change = _get_random_change(-50, 30) / 100
        st.metric(
            "평균 응답시간", 
            f"{response_time:.2f}s", 
            f"{time_change:+.2f}s",
            help="시스템의 평균 응답 시간"
        )
    
    # 추가 통계 정보
    _render_additional_stats()

def _render_additional_stats():
    """추가 통계 정보 렌더링"""
    st.markdown("### 📈 상세 통계")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 성과 지표**")
        
        # 성공률
        success_rate = random.uniform(95, 99.5)
        st.progress(success_rate / 100)
        st.caption(f"API 성공률: {success_rate:.1f}%")
        
        # 만족도
        satisfaction = random.uniform(4.0, 4.8)
        star_rating = "⭐" * int(satisfaction)
        st.caption(f"사용자 만족도: {star_rating} ({satisfaction:.1f}/5.0)")
    
    with col2:
        st.markdown("**💻 시스템 상태**")
        
        # CPU 사용률
        cpu_usage = random.uniform(20, 80)
        st.progress(cpu_usage / 100)
        st.caption(f"CPU 사용률: {cpu_usage:.1f}%")
        
        # 메모리 사용률
        memory_usage = random.uniform(40, 85)
        st.progress(memory_usage / 100)
        st.caption(f"메모리 사용률: {memory_usage:.1f}%")

def _get_random_metric(min_val: int, max_val: int) -> int:
    """랜덤 메트릭 값 생성"""
    return random.randint(min_val, max_val)

def _get_random_change(min_change: int, max_change: int) -> int:
    """랜덤 변화량 생성"""
    return random.randint(min_change, max_change)