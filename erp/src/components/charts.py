import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Literal

def render_charts():
    """차트 렌더링"""
    st.markdown("### 📊 데이터 분석")
    
    tab1, tab2, tab3 = st.tabs(["📈 방문자 통계", "💹 사용량 분석", "🎯 성과 리포트"])
    
    with tab1:
        _render_visitor_chart()
    
    with tab2:
        _render_usage_chart()
    
    with tab3:
        _render_performance_chart()

def _render_visitor_chart():
    """방문자 통계 차트"""
    st.markdown("**일일 방문자 추이**")
    
    # 데이터 생성
    chart_data = create_time_series_data("visitors")
    
    # 차트 표시
    st.line_chart(chart_data)
    
    # 요약 통계
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_visitors = chart_data['일일 방문자'].mean()
        st.metric("평균 일일 방문자", f"{avg_visitors:.0f}")
    
    with col2:
        max_visitors = chart_data['일일 방문자'].max()
        st.metric("최대 방문자", f"{max_visitors:.0f}")
    
    with col3:
        total_visitors = chart_data['일일 방문자'].sum()
        st.metric("총 방문자", f"{total_visitors:.0f}")

def _render_usage_chart():
    """사용량 분석 차트"""
    st.markdown("**시스템 사용량 분석**")
    
    chart_data = create_time_series_data("usage")
    
    # 바 차트로 표시
    st.bar_chart(chart_data)
    
    # 상세 정보
    with st.expander("📋 상세 사용량 정보", expanded=False):
        st.dataframe(
            chart_data.describe().round(2),
            width='stretch'
        )

def _render_performance_chart():
    """성과 리포트 차트"""
    st.markdown("**성과 지표 트렌드**")
    
    chart_data = create_time_series_data("performance")
    
    # 영역 차트로 표시
    st.area_chart(chart_data)
    
    # 성과 요약
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 주요 지표**")
        response_time_avg = chart_data['평균 응답시간'].mean()
        throughput_avg = chart_data['처리량'].mean()
        
        st.write(f"• 평균 응답시간: {response_time_avg:.2f}초")
        st.write(f"• 평균 처리량: {throughput_avg:.0f} req/min")
    
    with col2:
        st.markdown("**📈 개선 사항**")
        
        # 트렌드 분석
        response_trend = "📉 개선됨" if chart_data['평균 응답시간'].iloc[-1] < chart_data['평균 응답시간'].iloc[0] else "📈 증가함"
        throughput_trend = "📈 증가함" if chart_data['처리량'].iloc[-1] > chart_data['처리량'].iloc[0] else "📉 감소함"
        
        st.write(f"• 응답시간: {response_trend}")
        st.write(f"• 처리량: {throughput_trend}")

def create_time_series_data(chart_type: Literal["visitors", "usage", "performance"]) -> pd.DataFrame:
    """시계열 데이터 생성"""
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=29),
        end=datetime.now(),
        freq='D'
    )
    
    np.random.seed(42)  # 일관된 데이터를 위한 시드 설정
    
    if chart_type == "visitors":
        return pd.DataFrame({
            '일일 방문자': np.random.randint(100, 1000, len(dates)) + 
                          np.sin(np.arange(len(dates)) * 0.2) * 200,
            '신규 방문자': np.random.randint(20, 300, len(dates)) + 
                          np.sin(np.arange(len(dates)) * 0.15) * 80,
            '재방문자': np.random.randint(50, 400, len(dates)) + 
                       np.sin(np.arange(len(dates)) * 0.25) * 120
        }, index=dates)
    
    elif chart_type == "usage":
        return pd.DataFrame({
            'API 호출': np.random.randint(1000, 5000, len(dates)) + 
                       np.sin(np.arange(len(dates)) * 0.3) * 1000,
            '스토리지 사용량(GB)': np.random.randint(100, 500, len(dates)) + 
                                 np.cumsum(np.random.randn(len(dates)) * 0.1),
            '대역폭(GB)': np.random.randint(50, 200, len(dates)) + 
                        np.sin(np.arange(len(dates)) * 0.4) * 50
        }, index=dates)
    
    else:  # performance
        return pd.DataFrame({
            '평균 응답시간': np.random.uniform(0.5, 3.0, len(dates)) + 
                           np.sin(np.arange(len(dates)) * 0.1) * 0.5,
            '처리량': np.random.randint(100, 500, len(dates)) + 
                     np.sin(np.arange(len(dates)) * 0.2) * 100,
            '에러율(%)': np.random.uniform(0.1, 2.0, len(dates))
        }, index=dates)