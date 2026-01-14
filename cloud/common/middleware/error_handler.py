"""
错误处理器
"""

import logging
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from ..utils.response import error_response

logger = logging.getLogger(__name__)


def register_error_handlers(app: Flask):
    """
    注册全局错误处理器

    用法:
        app = Flask(__name__)
        register_error_handlers(app)
    """

    @app.errorhandler(400)
    def bad_request(error):
        """400 错误请求"""
        logger.warning(f"Bad request: {error}")
        return error_response(code=400, message="Bad request"), 400

    @app.errorhandler(401)
    def unauthorized(error):
        """401 未授权"""
        logger.warning(f"Unauthorized: {error}")
        return error_response(code=401, message="Unauthorized"), 401

    @app.errorhandler(403)
    def forbidden(error):
        """403 禁止访问"""
        logger.warning(f"Forbidden: {error}")
        return error_response(code=403, message="Forbidden"), 403

    @app.errorhandler(404)
    def not_found(error):
        """404 未找到"""
        logger.info(f"Not found: {error}")
        return error_response(code=404, message="Resource not found"), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """405 方法不允许"""
        logger.warning(f"Method not allowed: {error}")
        return error_response(code=405, message="Method not allowed"), 405

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """429 请求过多"""
        logger.warning(f"Rate limit exceeded: {error}")
        return error_response(code=429, message="Rate limit exceeded"), 429

    @app.errorhandler(500)
    def internal_server_error(error):
        """500 服务器内部错误"""
        logger.error(f"Internal server error: {error}", exc_info=True)
        return error_response(code=500, message="Internal server error"), 500

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """处理所有HTTP异常"""
        logger.warning(f"HTTP exception: {error}")
        return (
            error_response(
                code=error.code, message=error.description or "HTTP error"
            ),
            error.code,
        )

    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error):
        """处理数据库错误"""
        logger.error(f"Database error: {error}", exc_info=True)
        return error_response(code=500, message="Database error"), 500

    @app.errorhandler(ValueError)
    def handle_value_error(error):
        """处理值错误"""
        logger.warning(f"Value error: {error}")
        return error_response(code=400, message=str(error)), 400

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """处理所有未预期的异常"""
        logger.error(f"Unexpected error: {error}", exc_info=True)
        return error_response(code=500, message="An unexpected error occurred"), 500


class APIException(Exception):
    """自定义API异常基类"""

    def __init__(self, message: str, code: int = 400, data=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.data = data

    def to_dict(self):
        return error_response(code=self.code, message=self.message, data=self.data)


class ValidationError(APIException):
    """验证错误"""

    def __init__(self, message: str, data=None):
        super().__init__(message, code=400, data=data)


class AuthenticationError(APIException):
    """认证错误"""

    def __init__(self, message: str = "Authentication failed", data=None):
        super().__init__(message, code=401, data=data)


class AuthorizationError(APIException):
    """授权错误"""

    def __init__(self, message: str = "Permission denied", data=None):
        super().__init__(message, code=403, data=data)


class NotFoundError(APIException):
    """资源未找到错误"""

    def __init__(self, message: str = "Resource not found", data=None):
        super().__init__(message, code=404, data=data)


class ConflictError(APIException):
    """冲突错误"""

    def __init__(self, message: str = "Resource conflict", data=None):
        super().__init__(message, code=409, data=data)
