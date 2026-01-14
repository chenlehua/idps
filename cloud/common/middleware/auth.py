"""
JWT认证中间件
"""

import jwt
import time
from functools import wraps
from flask import request, jsonify
from typing import Optional, Dict, Any

from ..config import config
from ..utils.response import error_response
from ..database import redis_client


class TokenError(Exception):
    """Token错误基类"""

    pass


class TokenExpiredError(TokenError):
    """Token过期错误"""

    pass


class TokenInvalidError(TokenError):
    """Token无效错误"""

    pass


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[int] = None
) -> str:
    """
    创建访问令牌

    Args:
        data: 要编码的数据字典（通常包含vin, device_fingerprint等）
        expires_delta: 过期时间（秒），默认使用配置中的值

    Returns:
        JWT token字符串
    """
    to_encode = data.copy()

    if expires_delta is None:
        expires_delta = config.JWT_ACCESS_TOKEN_EXPIRES

    expire = int(time.time()) + expires_delta
    to_encode.update({"exp": expire, "iat": int(time.time())})

    token = jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    return token


def verify_token(token: str) -> Dict[str, Any]:
    """
    验证JWT令牌

    Args:
        token: JWT token字符串

    Returns:
        解码后的数据字典

    Raises:
        TokenExpiredError: Token已过期
        TokenInvalidError: Token无效
    """
    try:
        # 检查Token是否在黑名单中（已撤销）
        if redis_client and redis_client.exists(f"token:blacklist:{token}"):
            raise TokenInvalidError("Token has been revoked")

        payload = jwt.decode(
            token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM]
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise TokenInvalidError(f"Invalid token: {str(e)}")


def revoke_token(token: str, expires_in: int = None):
    """
    撤销Token（加入黑名单）

    Args:
        token: 要撤销的token
        expires_in: 黑名单过期时间（秒），默认使用token的剩余有效时间
    """
    if not redis_client:
        return

    if expires_in is None:
        try:
            payload = jwt.decode(
                token,
                config.JWT_SECRET_KEY,
                algorithms=[config.JWT_ALGORITHM],
                options={"verify_exp": False},
            )
            exp = payload.get("exp", 0)
            expires_in = max(0, exp - int(time.time()))
        except Exception:
            expires_in = config.JWT_ACCESS_TOKEN_EXPIRES

    redis_client.setex(f"token:blacklist:{token}", expires_in, "1")


def auth_required(f):
    """
    认证装饰器
    要求请求头中包含有效的Authorization: Bearer <token>

    用法:
        @app.route('/api/protected')
        @auth_required
        def protected_route():
            vin = request.vin  # 从token中提取的VIN
            return {'message': 'success'}
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 从请求头获取token
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return error_response(code=401, message="Missing authorization header"), 401

        # 解析Bearer token
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return error_response(code=401, message="Invalid authorization header"), 401

        token = parts[1]

        try:
            # 验证token
            payload = verify_token(token)

            # 将解码后的数据附加到request对象
            request.token_payload = payload
            request.vin = payload.get("vin")
            request.device_fingerprint = payload.get("device_fingerprint")

            return f(*args, **kwargs)

        except TokenExpiredError:
            return error_response(code=401, message="Token has expired"), 401
        except TokenInvalidError as e:
            return error_response(code=401, message=str(e)), 401
        except Exception as e:
            return error_response(code=500, message=f"Authentication error: {str(e)}"), 500

    return decorated_function


def optional_auth(f):
    """
    可选认证装饰器
    如果提供了有效token则验证，否则继续执行

    用法:
        @app.route('/api/resource')
        @optional_auth
        def resource():
            vin = getattr(request, 'vin', None)
            if vin:
                # 已认证用户的逻辑
                pass
            else:
                # 未认证用户的逻辑
                pass
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
                try:
                    payload = verify_token(token)
                    request.token_payload = payload
                    request.vin = payload.get("vin")
                    request.device_fingerprint = payload.get("device_fingerprint")
                except (TokenExpiredError, TokenInvalidError):
                    pass  # 忽略错误，继续执行

        return f(*args, **kwargs)

    return decorated_function
