"""
请求日志中间件
"""

import time
import logging
from flask import request, g
from functools import wraps

logger = logging.getLogger(__name__)


def request_logger(app):
    """
    Flask应用的请求日志中间件

    记录所有HTTP请求的详细信息：
    - 请求方法和路径
    - 请求参数
    - 响应状态码
    - 响应时间

    用法:
        app = Flask(__name__)
        request_logger(app)
    """

    @app.before_request
    def before_request():
        """请求开始时记录"""
        g.start_time = time.time()

        # 记录请求信息
        log_data = {
            "method": request.method,
            "path": request.path,
            "remote_addr": request.remote_addr,
            "user_agent": request.user_agent.string,
        }

        # 记录查询参数
        if request.args:
            log_data["query_params"] = dict(request.args)

        # 记录VIN（如果已认证）
        if hasattr(request, "vin") and request.vin:
            log_data["vin"] = request.vin

        logger.info(f"Request started: {log_data}")

    @app.after_request
    def after_request(response):
        """请求结束时记录"""
        if hasattr(g, "start_time"):
            elapsed = time.time() - g.start_time

            log_data = {
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "elapsed_ms": round(elapsed * 1000, 2),
            }

            if hasattr(request, "vin") and request.vin:
                log_data["vin"] = request.vin

            # 根据状态码选择日志级别
            if response.status_code >= 500:
                logger.error(f"Request failed: {log_data}")
            elif response.status_code >= 400:
                logger.warning(f"Request error: {log_data}")
            else:
                logger.info(f"Request completed: {log_data}")

        return response

    @app.teardown_request
    def teardown_request(exception=None):
        """请求清理时记录异常"""
        if exception:
            logger.exception(f"Request exception: {exception}")


def log_function_call(f):
    """
    函数调用日志装饰器

    用法:
        @log_function_call
        def my_function(arg1, arg2):
            pass
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        func_name = f.__name__
        logger.debug(f"Calling function: {func_name}")

        start_time = time.time()
        try:
            result = f(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.debug(
                f"Function {func_name} completed in {elapsed:.3f}s"
            )
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"Function {func_name} failed after {elapsed:.3f}s: {str(e)}"
            )
            raise

    return decorated_function
