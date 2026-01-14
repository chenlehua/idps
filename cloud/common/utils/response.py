"""
统一响应格式
"""

from typing import Any, Optional, Dict
from flask import jsonify


def success_response(
    data: Any = None, message: str = "Success", code: int = 200
) -> Dict:
    """
    成功响应格式

    Args:
        data: 响应数据
        message: 响应消息
        code: 业务状态码

    Returns:
        统一格式的响应字典
    """
    response = {"code": code, "message": message, "data": data, "success": True}
    return response


def error_response(
    message: str = "Error", code: int = 500, data: Any = None
) -> Dict:
    """
    错误响应格式

    Args:
        message: 错误消息
        code: 错误码
        data: 附加数据

    Returns:
        统一格式的错误响应字典
    """
    response = {"code": code, "message": message, "data": data, "success": False}
    return response


def paginate_response(
    items: list,
    total: int,
    page: int,
    page_size: int,
    message: str = "Success",
) -> Dict:
    """
    分页响应格式

    Args:
        items: 当前页的数据列表
        total: 总记录数
        page: 当前页码
        page_size: 每页记录数
        message: 响应消息

    Returns:
        包含分页信息的响应字典
    """
    total_pages = (total + page_size - 1) // page_size

    return success_response(
        data={
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        },
        message=message,
    )
