# debug_db.py
from sqlalchemy import create_engine, text
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(text("SHOW TABLES;"))
    print("所有表：", [row[0] for row in result])