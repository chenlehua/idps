#!/usr/bin/env python3
"""
IDPS数据库初始化脚本

功能：
- 初始化MySQL数据库表结构
- 初始化ClickHouse数据库表结构
- 创建默认管理员用户
- 验证数据库连接

使用方法:
    python init_db.py [--reset]

选项:
    --reset    删除现有数据库并重新创建（谨慎使用！）
"""

import sys
import os
import argparse
from pathlib import Path
from sqlalchemy import text

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "cloud"))

from common.database import (
    init_mysql,
    init_clickhouse,
    init_redis,
    create_tables,
    drop_tables,
)
from common.config import config
from common.utils.logger import setup_logger

logger = setup_logger("init_db")

# Global database connections
engine = None
clickhouse_client = None
redis_client = None


def check_mysql_connection():
    """检查MySQL连接"""
    global engine
    try:
        engine = init_mysql()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("✓ MySQL连接成功")
            return True
    except Exception as e:
        logger.error(f"✗ MySQL连接失败: {e}")
        return False


def check_clickhouse_connection():
    """检查ClickHouse连接"""
    global clickhouse_client
    try:
        clickhouse_client = init_clickhouse()
        result = clickhouse_client.execute("SELECT 1")
        logger.info("✓ ClickHouse连接成功")
        return True
    except Exception as e:
        logger.error(f"✗ ClickHouse连接失败: {e}")
        return False


def check_redis_connection():
    """检查Redis连接"""
    global redis_client
    try:
        redis_client = init_redis()
        redis_client.ping()
        logger.info("✓ Redis连接成功")
        return True
    except Exception as e:
        logger.error(f"✗ Redis连接失败: {e}")
        return False


def execute_sql_file(file_path: Path, is_clickhouse: bool = False):
    """执行SQL文件"""
    try:
        logger.info(f"执行SQL文件: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        if is_clickhouse:
            # ClickHouse: 按语句分割执行
            statements = [
                stmt.strip()
                for stmt in sql_content.split(";")
                if stmt.strip() and not stmt.strip().startswith("--")
            ]

            for stmt in statements:
                if stmt:
                    try:
                        clickhouse_client.execute(stmt)
                    except Exception as e:
                        logger.warning(f"执行语句失败（可能已存在）: {e}")

        else:
            # MySQL: 直接执行
            with engine.connect() as conn:
                # 分割多个语句
                statements = [
                    stmt.strip()
                    for stmt in sql_content.split(";")
                    if stmt.strip()
                ]

                for stmt in statements:
                    if stmt and not stmt.startswith("--"):
                        try:
                            conn.execute(text(stmt))
                            conn.commit()
                        except Exception as e:
                            logger.warning(f"执行语句失败（可能已存在）: {e}")

        logger.info(f"✓ SQL文件执行完成: {file_path}")
        return True

    except Exception as e:
        logger.error(f"✗ SQL文件执行失败: {e}")
        return False


def init_mysql_schema(reset: bool = False):
    """初始化MySQL数据库"""
    logger.info("=" * 60)
    logger.info("初始化MySQL数据库...")
    logger.info("=" * 60)

    if reset:
        logger.warning("⚠ 正在删除现有表...")
        drop_tables()

    # 执行初始化SQL
    sql_file = Path(__file__).parent.parent / "docker" / "mysql" / "init" / "01-init.sql"

    if sql_file.exists():
        return execute_sql_file(sql_file, is_clickhouse=False)
    else:
        logger.error(f"找不到SQL文件: {sql_file}")
        return False


def init_clickhouse_schema():
    """初始化ClickHouse数据库"""
    logger.info("=" * 60)
    logger.info("初始化ClickHouse数据库...")
    logger.info("=" * 60)

    sql_file = (
        Path(__file__).parent.parent / "docker" / "clickhouse" / "init" / "01-init.sql"
    )

    if sql_file.exists():
        return execute_sql_file(sql_file, is_clickhouse=True)
    else:
        logger.error(f"找不到SQL文件: {sql_file}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="IDPS数据库初始化脚本")
    parser.add_argument(
        "--reset", action="store_true", help="删除现有数据库并重新创建（谨慎使用！）"
    )
    args = parser.parse_args()

    if args.reset:
        logger.warning("=" * 60)
        logger.warning("⚠ 警告：将删除所有现有数据！")
        logger.warning("=" * 60)
        confirm = input("确定要继续吗? (yes/no): ")
        if confirm.lower() != "yes":
            logger.info("操作已取消")
            return

    logger.info("=" * 60)
    logger.info("IDPS数据库初始化")
    logger.info("=" * 60)

    # 1. 检查数据库连接
    logger.info("\n步骤 1/4: 检查数据库连接...")
    mysql_ok = check_mysql_connection()
    clickhouse_ok = check_clickhouse_connection()
    redis_ok = check_redis_connection()

    if not mysql_ok:
        logger.error("\n✗ MySQL连接失败，无法继续")
        logger.error("提示: 确保已启动数据库服务 (docker compose up -d)")
        sys.exit(1)

    if not redis_ok:
        logger.error("\n✗ Redis连接失败，无法继续")
        logger.error("提示: 确保已启动数据库服务 (docker compose up -d)")
        sys.exit(1)

    if not clickhouse_ok:
        logger.warning("\n⚠ ClickHouse连接失败，将跳过ClickHouse初始化")
        logger.warning("提示: ClickHouse配置可能需要调整，请查看文档")
        logger.warning("      数据库服务基本功能仍可正常使用")

    # 2. 初始化MySQL
    logger.info("\n步骤 2/4: 初始化MySQL数据库...")
    if not init_mysql_schema(reset=args.reset):
        logger.error("✗ MySQL初始化失败")
        sys.exit(1)

    # 3. 初始化ClickHouse
    if clickhouse_ok:
        logger.info("\n步骤 3/4: 初始化ClickHouse数据库...")
        if not init_clickhouse_schema():
            logger.error("✗ ClickHouse初始化失败")
            sys.exit(1)
    else:
        logger.info("\n步骤 3/4: 跳过ClickHouse初始化...")

    # 4. 验证
    logger.info("\n步骤 4/4: 验证数据库...")
    try:
        # 验证MySQL表
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = :schema"
                ),
                {"schema": config.MYSQL_DATABASE},
            )
            tables = [row[0] for row in result]
            logger.info(f"✓ MySQL表: {', '.join(tables)}")

        # 验证ClickHouse表（如果连接成功）
        if clickhouse_ok:
            result = clickhouse_client.execute(
                "SELECT name FROM system.tables WHERE database = 'idps'"
            )
            tables = [row[0] for row in result]
            logger.info(f"✓ ClickHouse表: {', '.join(tables)}")

    except Exception as e:
        logger.error(f"✗ 验证失败: {e}")
        sys.exit(1)

    logger.info("\n" + "=" * 60)
    logger.info("✓ 数据库初始化完成！")
    logger.info("=" * 60)
    logger.info("\n默认管理员账号:")
    logger.info("  用户名: admin")
    logger.info("  密码: Admin@123456")
    logger.info("\n⚠ 请在生产环境中修改默认密码！")


if __name__ == "__main__":
    main()
