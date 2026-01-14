"""
配置管理模块
支持从环境变量和.env文件加载配置
"""

import os
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """应用配置类"""

    # Flask配置
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    TESTING = os.getenv("TESTING", "False").lower() == "true"

    # MySQL配置
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "idps")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "idps123456")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "idps")

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            f"?charset=utf8mb4"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = int(os.getenv("SQLALCHEMY_POOL_SIZE", "10"))
    SQLALCHEMY_POOL_TIMEOUT = int(os.getenv("SQLALCHEMY_POOL_TIMEOUT", "30"))
    SQLALCHEMY_POOL_RECYCLE = int(os.getenv("SQLALCHEMY_POOL_RECYCLE", "3600"))
    SQLALCHEMY_MAX_OVERFLOW = int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", "20"))

    # ClickHouse配置
    CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
    CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "9000"))
    CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
    CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")
    CLICKHOUSE_DATABASE = os.getenv("CLICKHOUSE_DATABASE", "idps")

    # Redis配置
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_DECODE_RESPONSES = True

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # JWT配置
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "86400"))  # 24小时
    JWT_REFRESH_TOKEN_EXPIRES = int(
        os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "2592000")
    )  # 30天

    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
    LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", "104857600"))  # 100MB
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "10"))

    # CORS配置
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

    # 限流配置
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "1000 per hour")

    # SSL/TLS配置
    SSL_CA_CERT = os.getenv("SSL_CA_CERT", "/etc/idps/certs/ca.pem")
    SSL_SERVER_CERT = os.getenv("SSL_SERVER_CERT", "/etc/idps/certs/server.pem")
    SSL_SERVER_KEY = os.getenv("SSL_SERVER_KEY", "/etc/idps/certs/server.key")
    SSL_VERIFY_CLIENT = os.getenv("SSL_VERIFY_CLIENT", "True").lower() == "true"

    # 规则文件存储配置
    RULE_STORAGE_TYPE = os.getenv("RULE_STORAGE_TYPE", "local")  # local, s3, minio
    RULE_STORAGE_PATH = os.getenv("RULE_STORAGE_PATH", "/var/lib/idps/rules")

    # MinIO/S3配置（可选）
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "")
    MINIO_BUCKET = os.getenv("MINIO_BUCKET", "idps-rules")
    MINIO_SECURE = os.getenv("MINIO_SECURE", "True").lower() == "true"

    @classmethod
    def validate(cls):
        """验证配置有效性"""
        required_vars = [
            "SECRET_KEY",
            "MYSQL_HOST",
            "MYSQL_USER",
            "MYSQL_PASSWORD",
        ]
        missing = [var for var in required_vars if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Missing required config variables: {', '.join(missing)}")


# 导出单例配置对象
config = Config()
