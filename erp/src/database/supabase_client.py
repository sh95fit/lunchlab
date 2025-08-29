import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# .env 불러오기
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


# SQLAlchemy 엔진 생성 (세션 풀 포함)
engine = create_engine(
    DATABASE_URL,
    pool_size=10,        # 최소 10개 커넥션 유지
    max_overflow=20,     # 최대 20개 추가 커넥션
    echo=True            # SQL 로그 출력
)

# 세션 생성기
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 모델 선언
Base = declarative_base()