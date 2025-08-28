streamlit_cognito_app/
├── .env                          # 환경변수
├── .gitignore                    # Git 무시 파일
├── requirements.txt              # 패키지 의존성
├── README.md                     # 프로젝트 문서
├── streamlit_app.py             # 메인 앱 진입점
├── .streamlit/
│   └── config.toml              # Streamlit 설정
├── src/
│   ├── __init__.py
│   ├── auth/
│   │   ├── __init__.py
│   │   └── cognito_auth.py      # AWS Cognito 인증 로직
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── login.py             # 로그인 페이지
│   │   └── dashboard.py         # 메인 대시보드
│   ├── components/
│   │   ├── __init__.py
│   │   ├── metrics.py           # 메트릭 컴포넌트
│   │   └── charts.py            # 차트 컴포넌트
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py            # 설정 관리
│   │   ├── session.py           # 세션 상태 관리
│   │   └── validators.py        # 입력 검증 유틸리티
│   └── styles/
│       ├── __init__.py
│       └── custom.css           # 커스텀 CSS
└── tests/
    ├── __init__.py
    ├── test_auth.py             # 인증 테스트
    └── test_utils.py            # 유틸리티 테스트