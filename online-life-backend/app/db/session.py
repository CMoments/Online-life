from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# MySQL异步连接URL
SQLALCHEMY_DATABASE_URL = "mysql+aiomysql://Database:Online-life2025@39.104.19.8:3306/Online"

# 创建异步引擎
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_timeout=30,  # 连接超时时间
    connect_args={
        "connect_timeout": 30  # MySQL连接超时时间
    }
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncSession:
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() 