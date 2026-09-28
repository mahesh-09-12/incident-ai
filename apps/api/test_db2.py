import sys
from sqlalchemy import text
from app.db.session import SessionLocal

try:
    db = SessionLocal()
    result = db.execute(text("SELECT 1")).scalar()
    print("Database connection successful:", result)
except Exception as e:
    print("Database connection failed:", e)
    sys.exit(1)
