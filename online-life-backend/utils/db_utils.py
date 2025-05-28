from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
from models import Base

# 创建数据库引擎
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=False, pool_recycle=3600)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    """获取数据库会话"""
    return SessionLocal()


def init_database():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)


class DatabaseManager:
    """数据库管理器"""

    @staticmethod
    def create_tables():
        """创建所有表"""
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def drop_tables():
        """删除所有表"""
        Base.metadata.drop_all(bind=engine)

    @staticmethod
    def get_session():
        """获取数据库会话（上下文管理器）"""

        class SessionContext:
            def __enter__(self):
                self.session = SessionLocal()
                return self.session

            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type:
                    self.session.rollback()
                else:
                    self.session.commit()
                self.session.close()

        return SessionContext()

    @staticmethod
    def execute_query(query, params=None):
        """执行原生SQL查询"""
        with DatabaseManager.get_session() as session:
            result = session.execute(query, params or {})
            return result.fetchall()

    @staticmethod
    def execute_update(query, params=None):
        """执行更新操作"""
        with DatabaseManager.get_session() as session:
            result = session.execute(query, params or {})
            session.commit()
            return result.rowcount


def paginate_query(query, page=1, per_page=10):
    """分页查询"""
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
        "has_prev": page > 1,
        "has_next": page * per_page < total,
    }
