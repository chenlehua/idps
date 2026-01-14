"""
数据库连接管理
"""

from contextlib import contextmanager
from typing import Generator
import redis
from clickhouse_driver import Client
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, Session

from .config import config

# SQLAlchemy Base
Base = declarative_base()

# MySQL Engine and Session
engine = None
SessionLocal = None
db_session = None

# ClickHouse Client
clickhouse_client = None

# Redis Client
redis_client = None


def init_mysql():
    """初始化MySQL连接"""
    global engine, SessionLocal, db_session

    engine = create_engine(
        config.SQLALCHEMY_DATABASE_URI,
        pool_size=config.SQLALCHEMY_POOL_SIZE,
        pool_timeout=config.SQLALCHEMY_POOL_TIMEOUT,
        pool_recycle=config.SQLALCHEMY_POOL_RECYCLE,
        max_overflow=config.SQLALCHEMY_MAX_OVERFLOW,
        echo=config.DEBUG,
    )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = scoped_session(SessionLocal)

    # Bind base to engine
    Base.metadata.bind = engine

    return engine


def init_clickhouse():
    """初始化ClickHouse连接"""
    global clickhouse_client

    clickhouse_client = Client(
        host=config.CLICKHOUSE_HOST,
        port=config.CLICKHOUSE_PORT,
        user=config.CLICKHOUSE_USER,
        password=config.CLICKHOUSE_PASSWORD,
        database=config.CLICKHOUSE_DATABASE,
    )

    return clickhouse_client


def init_redis():
    """初始化Redis连接"""
    global redis_client

    redis_client = redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        password=config.REDIS_PASSWORD if config.REDIS_PASSWORD else None,
        db=config.REDIS_DB,
        decode_responses=config.REDIS_DECODE_RESPONSES,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True,
    )

    # Test connection
    redis_client.ping()

    return redis_client


def init_db():
    """初始化所有数据库连接"""
    init_mysql()
    init_clickhouse()
    init_redis()


def create_tables():
    """创建所有数据表"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """删除所有数据表（谨慎使用）"""
    Base.metadata.drop_all(bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话的上下文管理器
    用法:
        with get_db() as db:
            db.query(...)
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db_session() -> Session:
    """
    获取数据库会话（需要手动关闭）
    用法:
        db = get_db_session()
        try:
            db.query(...)
            db.commit()
        except:
            db.rollback()
        finally:
            db.close()
    """
    return SessionLocal()


def close_db():
    """关闭数据库连接"""
    if db_session:
        db_session.remove()
    if engine:
        engine.dispose()
    if clickhouse_client:
        clickhouse_client.disconnect()
    if redis_client:
        redis_client.close()


# 导出
__all__ = [
    "Base",
    "engine",
    "db_session",
    "clickhouse_client",
    "redis_client",
    "init_db",
    "init_mysql",
    "init_clickhouse",
    "init_redis",
    "create_tables",
    "drop_tables",
    "get_db",
    "get_db_session",
    "close_db",
]
