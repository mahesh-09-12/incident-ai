import sys
from sqlalchemy import create_engine, text

DATABASE_URL="postgresql+psycopg://neondb_owner:npg_xqo3egfycb7r@ep-frosty-king-az5s5rdo-pooler.c-3.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
        print("Database connection successful:", result)
except Exception as e:
    print("Database connection failed:", e)
    sys.exit(1)
