from src.database.supabase_client import engine, Base
from src.database.models import UserSession, LoginHistory, UserActivity, SystemSetting

def init_db():
    # 모든 테이블 생성
    Base.metadata.create_all(bind=engine)
    print("✅ 모든 테이블 생성 완료")

if __name__ == "__main__":
    init_db()
