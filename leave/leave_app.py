import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar
import plotly.express as px
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(
    page_title="연월차 관리 시스템",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 추가
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .vacation-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .status-approved { background-color: #d4edda; color: #155724; }
    .status-pending { background-color: #fff3cd; color: #856404; }
    .status-rejected { background-color: #f8d7da; color: #721c24; }
    .status-cancelled { background-color: #f8f9fa; color: #6c757d; }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'applications' not in st.session_state:
    st.session_state.applications = []
if 'current_user' not in st.session_state:
    st.session_state.current_user = {
        'id': 1,
        'name': '김직원',
        'join_date': date(2020, 3, 15),
        'position': '대리',
        'department': '개발팀'
    }
if 'employees' not in st.session_state:
    st.session_state.employees = [
        {'id': 1, 'name': '김직원', 'position': '대리', 'department': '개발팀'},
        {'id': 2, 'name': '박팀장', 'position': '팀장', 'department': '개발팀'},
        {'id': 3, 'name': '이부장', 'position': '부장', 'department': '개발팀'},
        {'id': 4, 'name': '최차장', 'position': '차장', 'department': '인사팀'},
        {'id': 5, 'name': '정대리', 'position': '대리', 'department': '마케팅팀'}
    ]
if 'selected_vacation_dates' not in st.session_state:
    st.session_state.selected_vacation_dates = set()
if 'current_calendar_month' not in st.session_state:
    st.session_state.current_calendar_month = date.today().month
if 'current_calendar_year' not in st.session_state:
    st.session_state.current_calendar_year = date.today().year

# 유틸리티 함수들
def calculate_annual_leave(join_date):
    today = date.today()
    work_years = (today - join_date).days // 365
    
    if work_years < 1:
        return 11
    elif work_years < 3:
        return 15
    else:
        return min(15 + (work_years - 2), 25)

def calculate_vacation_balance():
    total = calculate_annual_leave(st.session_state.current_user['join_date'])
    used = sum([app['days'] for app in st.session_state.applications 
                if app['applicant_id'] == st.session_state.current_user['id'] 
                and app['status'] == '승인완료'])
    return {'total': total, 'used': used, 'remaining': total - used}

def calculate_days(start_date, end_date, vacation_type):
    if vacation_type in ['오전반차', '오후반차']:
        return 0.5
    return (end_date - start_date).days + 1

def can_cancel(application, current_user_name):
    today = date.today()
    start_date = datetime.strptime(application['start_date'], '%Y-%m-%d').date()
    day_before = start_date - timedelta(days=1)
    
    if application['status'] != '승인완료':
        return False, None
    
    if today <= day_before and application['applicant_name'] == current_user_name:
        return True, 'self'
    
    if today > day_before and (application['approver'] == current_user_name or 
                               application.get('middle_approver') == current_user_name):
        return True, 'approver'
    
    return False, None

# 사이드바 - 시스템 정보
with st.sidebar:
    st.markdown("## 시스템 정보")
    
    user = st.session_state.current_user
    st.markdown(f"**현재 사용자**: {user['name']}")
    st.markdown(f"**입사일**: {user['join_date']}")
    
    work_years = (date.today() - user['join_date']).days // 365
    st.markdown(f"**근속연수**: {work_years}년")
    
    st.divider()
    
    # 빠른 통계
    st.markdown("## 빠른 통계")
    
    balance = calculate_vacation_balance()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("총 신청 건수", len([app for app in st.session_state.applications 
                                  if app['applicant_id'] == user['id']]))
    with col2:
        st.metric("승인된 신청", len([app for app in st.session_state.applications 
                                  if app['applicant_id'] == user['id'] 
                                  and app['status'] == '승인완료']))
    
    st.divider()
    
    # 데모 데이터
    st.markdown("## 데모 데이터")
    if st.button("📝 샘플 신청 추가", use_container_width=True):
        demo_app = {
            'id': len(st.session_state.applications) + 1,
            'applicant_id': 1,
            'applicant_name': '김직원',
            'type': '연차',
            'start_date': '2025-08-25',
            'end_date': '2025-08-25',
            'days': 1,
            'reason': '개인 사유',
            'middle_approver': None,
            'approver': '박팀장',
            'status': '승인완료',
            'applied_at': '2025-08-20 09:00:00',
            'processed_at': '2025-08-21 14:30:00'
        }
        st.session_state.applications.append(demo_app)
        st.success("샘플 데이터 추가됨!")
        st.rerun()

# 메인 컨텐츠
st.markdown('<div class="main-header"><h1>📅 연월차 관리 시스템</h1></div>', unsafe_allow_html=True)

# 사용자 정보와 연차 현황
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"### {user['name']} ({user['position']}) | {user['department']}")

with col2:
    balance = calculate_vacation_balance()
    st.markdown("### 잔여 연차")
    st.markdown(f"## **{balance['remaining']}일**")
    st.caption(f"총 {balance['total']}일 중 {balance['used']}일 사용")

st.divider()

# 메인 탭
tab1, tab2, tab3, tab4 = st.tabs(["📝 연차 신청", "📋 신청 내역", "✅ 결재 대기", "📊 연차 현황"])

# 탭 1: 연차 신청
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 휴가 종류")
        vacation_type = st.selectbox(
            "휴가 종류 선택",
            ["연차", "오전반차", "오후반차"],
            label_visibility="collapsed"
        )
        
        st.markdown("### 📅 날짜 선택")
        
        if vacation_type == "연차":
            date_selection_method = st.radio(
                "날짜 선택 방식",
                ["단일 날짜", "기간 선택", "개별 날짜 선택"],
                horizontal=True
            )
            
            if date_selection_method == "단일 날짜":
                selected_date = st.date_input(
                    "날짜", 
                    min_value=date.today(),
                    value=date.today()
                )
                start_date = end_date = selected_date
                
            elif date_selection_method == "기간 선택":
                date_range = st.date_input(
                    "기간 선택",
                    value=[date.today(), date.today()],
                    min_value=date.today()
                )
                if isinstance(date_range, tuple) and len(date_range) == 2:
                    start_date, end_date = date_range
                else:
                    start_date = end_date = date_range if isinstance(date_range, date) else date.today()
                    
            else:  # 개별 날짜 선택
                st.markdown("**🗓️ 개별 날짜 선택**")
                
                # 월/년 선택
                col_month, col_year, col_clear = st.columns([1, 1, 1])
                
                with col_month:
                    new_month = st.selectbox(
                        "월", 
                        range(1, 13), 
                        index=st.session_state.current_calendar_month - 1,
                        format_func=lambda x: f"{x}월"
                    )
                
                with col_year:
                    new_year = st.selectbox(
                        "년", 
                        [date.today().year, date.today().year + 1],
                        index=0 if st.session_state.current_calendar_year == date.today().year else 1
                    )
                
                with col_clear:
                    st.markdown("　")  # 공백으로 정렬
                    if st.button("🗑️ 선택 초기화", help="선택된 모든 날짜를 초기화합니다"):
                        st.session_state.selected_vacation_dates.clear()
                        st.rerun()
                
                # 월/년 변경 감지
                if (new_month != st.session_state.current_calendar_month or 
                    new_year != st.session_state.current_calendar_year):
                    st.session_state.current_calendar_month = new_month
                    st.session_state.current_calendar_year = new_year
                
                # 선택된 날짜 요약 표시
                if st.session_state.selected_vacation_dates:
                    selected_count = len(st.session_state.selected_vacation_dates)
                    st.success(f"✅ **{selected_count}일** 선택됨")
                    
                    # 선택된 날짜들을 월별로 그룹화하여 표시
                    sorted_dates = sorted(list(st.session_state.selected_vacation_dates))
                    grouped_by_month = {}
                    for d in sorted_dates:
                        month_key = d.strftime('%Y-%m')
                        if month_key not in grouped_by_month:
                            grouped_by_month[month_key] = []
                        grouped_by_month[month_key].append(d)
                    
                    with st.expander("📋 선택된 날짜 목록", expanded=False):
                        for month_key, dates in grouped_by_month.items():
                            st.markdown(f"**{month_key}**")
                            for d in dates:
                                col_date, col_remove = st.columns([3, 1])
                                with col_date:
                                    weekday = ['월', '화', '수', '목', '금', '토', '일'][d.weekday()]
                                    st.markdown(f"• {d.strftime('%m/%d')} ({weekday})")
                                with col_remove:
                                    if st.button("❌", key=f"remove_{d}", help=f"{d} 제거"):
                                        st.session_state.selected_vacation_dates.discard(d)
                                        st.rerun()
                
                # 개선된 달력 UI
                st.markdown(f"### 📅 {new_year}년 {new_month}월")
                
                # 달력 생성
                cal = calendar.monthcalendar(new_year, new_month)
                weekdays = ['월', '화', '수', '목', '금', '토', '일']
                
                # 달력 헤더 (스타일링)
                header_cols = st.columns(7)
                for i, day in enumerate(weekdays):
                    header_cols[i].markdown(f"<div style='text-align: center; font-weight: bold; color: #666; padding: 5px;'>{day}</div>", unsafe_allow_html=True)
                
                # 달력 본체
                for week_idx, week in enumerate(cal):
                    cols = st.columns(7)
                    for day_idx, day in enumerate(week):
                        with cols[day_idx]:
                            if day == 0:
                                st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
                            else:
                                day_date = date(new_year, new_month, day)
                                
                                # 오늘 이전 날짜는 비활성화
                                if day_date < date.today():
                                    st.markdown(
                                        f"<div style='text-align: center; color: #ccc; padding: 8px; height: 40px; line-height: 24px;'>{day}</div>", 
                                        unsafe_allow_html=True
                                    )
                                else:
                                    # 선택 상태 확인
                                    is_selected = day_date in st.session_state.selected_vacation_dates
                                    
                                    # 버튼 스타일
                                    if is_selected:
                                        button_style = "background-color: #4CAF50; color: white; border: 2px solid #45a049;"
                                    else:
                                        button_style = "background-color: #f8f9fa; color: #333; border: 1px solid #dee2e6;"
                                    
                                    # 토요일, 일요일 구분
                                    if day_idx == 5:  # 토요일
                                        button_style += "border-left: 3px solid #007bff;"
                                    elif day_idx == 6:  # 일요일
                                        button_style += "border-left: 3px solid #dc3545;"
                                    
                                    if st.button(
                                        f"{day}",
                                        key=f"date_btn_{new_year}_{new_month}_{day}",
                                        help=f"{day_date.strftime('%Y-%m-%d (%A)')}",
                                        use_container_width=True
                                    ):
                                        if is_selected:
                                            st.session_state.selected_vacation_dates.discard(day_date)
                                        else:
                                            st.session_state.selected_vacation_dates.add(day_date)
                                        st.rerun()
                
                # 선택된 날짜로 start_date, end_date 설정
                if st.session_state.selected_vacation_dates:
                    sorted_dates = sorted(list(st.session_state.selected_vacation_dates))
                    start_date = min(sorted_dates)
                    end_date = max(sorted_dates)
                else:
                    start_date = end_date = date.today()
                    
        else:  # 반차
            selected_date = st.date_input(
                "날짜", 
                min_value=date.today(),
                value=date.today()
            )
            start_date = end_date = selected_date
    
    with col2:
        st.markdown("### 사유")
        reason = st.text_area(
            "휴가 사유를 입력하세요", 
            height=100,
            placeholder="휴가 사유를 자세히 입력해주세요"
        )
        
        st.markdown("### 중간 결재자 (선택사항)")
        other_employees = [emp for emp in st.session_state.employees 
                         if emp['id'] != st.session_state.current_user['id']]
        
        middle_approver_options = ["선택 안함"] + [f"{emp['name']} ({emp['position']})" for emp in other_employees]
        middle_approver = st.selectbox(
            "중간 결재자",
            middle_approver_options,
            label_visibility="collapsed"
        )
        
        st.markdown("### 최종 결재자")
        approver = st.selectbox(
            "최종 결재자",
            [f"{emp['name']} ({emp['position']})" for emp in other_employees],
            label_visibility="collapsed"
        )
    
    # 신청 정보 요약
    st.markdown("---")
    if 'start_date' in locals() and 'end_date' in locals():
        # 신청 일수 계산 로직 개선
        if vacation_type == "연차" and 'date_selection_method' in locals() and date_selection_method == "개별 날짜 선택":
            days_requested = len(st.session_state.selected_vacation_dates)
        else:
            days_requested = calculate_days(start_date, end_date, vacation_type)
        
        balance = calculate_vacation_balance()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("신청 일수", f"{days_requested}일")
        with col2:
            st.metric("잔여 연차", f"{balance['remaining']}일")
        with col3:
            if days_requested <= balance['remaining']:
                st.success("✅ 신청 가능")
            else:
                st.error("❌ 연차 부족")
        
        # 신청 버튼
        st.markdown("### ")
        if st.button("🚀 신청하기", use_container_width=True, type="primary"):
            if not reason or not approver:
                st.error("⚠️ 모든 필수 항목을 입력해주세요.")
            elif days_requested <= 0:
                st.error("⚠️ 날짜를 선택해주세요.")
            elif days_requested > balance['remaining']:
                st.error("⚠️ 잔여 연차가 부족합니다.")
            else:
                # 개별 날짜 선택의 경우 실제 선택된 날짜 개수로 계산
                final_days = days_requested
                
                application = {
                    'id': len(st.session_state.applications) + 1,
                    'applicant_id': st.session_state.current_user['id'],
                    'applicant_name': st.session_state.current_user['name'],
                    'type': vacation_type,
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'days': final_days,
                    'reason': reason,
                    'middle_approver': middle_approver.split(' (')[0] if middle_approver != "선택 안함" else None,
                    'approver': approver.split(' (')[0],
                    'status': '승인대기',
                    'applied_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'processed_at': None,
                    'selected_dates': list(st.session_state.selected_vacation_dates) if vacation_type == "연차" and 'date_selection_method' in locals() and date_selection_method == "개별 날짜 선택" else None
                }
                st.session_state.applications.append(application)
                
                # 개별 날짜 선택의 경우 선택된 날짜들 초기화
                if vacation_type == "연차" and 'date_selection_method' in locals() and date_selection_method == "개별 날짜 선택":
                    st.session_state.selected_vacation_dates.clear()
                
                st.success("✅ 연차 신청이 완료되었습니다!")
                st.balloons()
                st.rerun()

# 탭 2: 신청 내역
with tab2:
    st.markdown("### 📋 신청 내역")
    
    user_applications = [app for app in st.session_state.applications 
                        if app['applicant_id'] == st.session_state.current_user['id']]
    
    if user_applications:
        for app in sorted(user_applications, key=lambda x: x['applied_at'], reverse=True):
            # 상태별 색상
            status_colors = {
                '승인완료': 'success',
                '승인대기': 'warning', 
                '반려': 'error',
                '취소됨': 'info'
            }
            
            with st.expander(f"{app['type']} | {app['start_date']} ~ {app['end_date']} | {app['status']}", 
                           expanded=False):
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**휴가 종류**: {app['type']}")
                    if app.get('selected_dates'):
                        # 개별 날짜 선택인 경우
                        selected_dates_str = ", ".join([d.strftime('%m/%d') for d in sorted(app['selected_dates'])])
                        st.markdown(f"**선택된 날짜**: {selected_dates_str}")
                    else:
                        # 기간 선택인 경우
                        st.markdown(f"**기간**: {app['start_date']} ~ {app['end_date']}")
                    st.markdown(f"**일수**: {app['days']}일")
                    st.markdown(f"**사유**: {app['reason']}")
                    
                with col2:
                    st.markdown(f"**결재자**: {app['approver']}")
                    if app['middle_approver']:
                        st.markdown(f"**중간결재자**: {app['middle_approver']}")
                    st.markdown(f"**신청일**: {app['applied_at'][:10]}")
                    
                with col3:
                    # 상태 표시
                    if app['status'] == '승인완료':
                        st.success(f"✅ {app['status']}")
                    elif app['status'] == '승인대기':
                        st.warning(f"⏳ {app['status']}")
                    elif app['status'] == '반려':
                        st.error(f"❌ {app['status']}")
                    else:
                        st.info(f"🔄 {app['status']}")
                    
                    # 취소 버튼
                    can_cancel_result, cancel_type = can_cancel(app, st.session_state.current_user['name'])
                    if can_cancel_result:
                        if st.button("🗑️ 취소", key=f"cancel_{app['id']}"):
                            for i, application in enumerate(st.session_state.applications):
                                if application['id'] == app['id']:
                                    st.session_state.applications[i]['status'] = '취소됨'
                                    st.session_state.applications[i]['processed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    break
                            st.success("신청이 취소되었습니다.")
                            st.rerun()
    else:
        st.info("📝 신청 내역이 없습니다.")

# 탭 3: 결재 대기
with tab3:
    st.markdown("### ✅ 결재 대기")
    
    current_user_name = st.session_state.current_user['name']
    pending_applications = [app for app in st.session_state.applications 
                           if (app['approver'] == current_user_name or 
                               app.get('middle_approver') == current_user_name) 
                           and app['status'] == '승인대기']
    
    if pending_applications:
        for app in pending_applications:
            with st.container():
                st.markdown(f"#### {app['applicant_name']} - {app['type']} ({app['days']}일)")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**📅 기간**: {app['start_date']} ~ {app['end_date']}")
                    st.markdown(f"**💬 사유**: {app['reason']}")
                    st.markdown(f"**🕐 신청일**: {app['applied_at']}")
                
                with col2:
                    col_approve, col_reject = st.columns(2)
                    
                    with col_approve:
                        if st.button("✅ 승인", key=f"approve_{app['id']}", use_container_width=True):
                            for i, application in enumerate(st.session_state.applications):
                                if application['id'] == app['id']:
                                    st.session_state.applications[i]['status'] = '승인완료'
                                    st.session_state.applications[i]['processed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    break
                            st.success("✅ 승인 처리되었습니다.")
                            st.rerun()
                    
                    with col_reject:
                        if st.button("❌ 반려", key=f"reject_{app['id']}", use_container_width=True):
                            for i, application in enumerate(st.session_state.applications):
                                if application['id'] == app['id']:
                                    st.session_state.applications[i]['status'] = '반려'
                                    st.session_state.applications[i]['processed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    break
                            st.error("❌ 반려 처리되었습니다.")
                            st.rerun()
                
                st.divider()
    else:
        st.info("🔍 결재 대기 중인 신청이 없습니다.")

# 탭 4: 연차 현황
with tab4:
    st.markdown("### 📊 연차 현황")
    
    balance = calculate_vacation_balance()
    
    # 연차 사용 현황 도넛 차트
    fig = go.Figure(data=[go.Pie(
        labels=['사용', '잔여'], 
        values=[balance['used'], balance['remaining']],
        hole=.3,
        marker_colors=['#ff6b6b', '#4ecdc4']
    )])
    
    fig.update_layout(
        title_text="연차 사용 현황",
        annotations=[dict(text=f"{balance['remaining']}일<br>잔여", x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 월별 사용 현황
    if st.session_state.applications:
        monthly_data = {}
        for app in st.session_state.applications:
            if app['status'] == '승인완료' and app['applicant_id'] == st.session_state.current_user['id']:
                month = app['start_date'][:7]  # YYYY-MM
                if month not in monthly_data:
                    monthly_data[month] = 0
                monthly_data[month] += app['days']
        
        if monthly_data:
            df_monthly = pd.DataFrame(list(monthly_data.items()), columns=['월', '사용일수'])
            fig2 = px.bar(df_monthly, x='월', y='사용일수', title='월별 연차 사용 현황')
            fig2.update_traces(marker_color='lightblue')
            st.plotly_chart(fig2, use_container_width=True)
    
    # 연차 정책 안내
    with st.expander("📋 연차 정책 안내", expanded=False):
        st.markdown("""
        **📌 연차 일수 기준 (근로기준법)**
        - 근속 1년 미만: 11일
        - 근속 1년 이상 3년 미만: 15일  
        - 근속 3년 이상: 15일 + (근속연수-2년) × 1일 (최대 25일)
        
        **📌 반차 규정**
        - 오전반차/오후반차: 0.5일로 계산
        
        **📌 취소 정책**  
        - 휴가 전날까지: 본인이 직접 취소 가능
        - 휴가 당일부터: 결재자만 취소 가능
        
        **📌 결재 프로세스**
        - 중간 결재자 → 최종 결재자 순서로 진행
        - 승인 시 자동으로 연차 일수 차감
        """)

# 하단 정보
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"**총 연차**: {balance['total']}일")
with col2:
    st.warning(f"**사용 연차**: {balance['used']}일")
with col3:
    st.success(f"**잔여 연차**: {balance['remaining']}일")