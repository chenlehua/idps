"""
数据验证工具
"""

import re
from typing import Optional


def validate_vin(vin: str) -> bool:
    """
    验证VIN码（车辆识别代码）格式

    VIN码规则：
    - 长度为17个字符
    - 只包含大写字母和数字
    - 不包含字母I、O、Q（避免与数字0、1混淆）

    Args:
        vin: VIN码字符串

    Returns:
        是否有效
    """
    if not vin or len(vin) != 17:
        return False

    # 检查字符集
    pattern = r'^[A-HJ-NPR-Z0-9]{17}$'
    return bool(re.match(pattern, vin))


def validate_ip(ip: str) -> bool:
    """
    验证IPv4地址格式

    Args:
        ip: IP地址字符串

    Returns:
        是否有效
    """
    if not ip:
        return False

    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False

    # 检查每个段是否在0-255范围内
    parts = ip.split('.')
    return all(0 <= int(part) <= 255 for part in parts)


def validate_port(port: int) -> bool:
    """
    验证端口号

    Args:
        port: 端口号

    Returns:
        是否有效（1-65535）
    """
    return isinstance(port, int) and 1 <= port <= 65535


def validate_mac(mac: str) -> bool:
    """
    验证MAC地址格式

    支持格式：
    - AA:BB:CC:DD:EE:FF
    - AA-BB-CC-DD-EE-FF
    - AABBCCDDEEFF

    Args:
        mac: MAC地址字符串

    Returns:
        是否有效
    """
    if not mac:
        return False

    # 支持多种格式
    patterns = [
        r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$',  # AA:BB:CC:DD:EE:FF
        r'^([0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}$',  # AA-BB-CC-DD-EE-FF
        r'^[0-9A-Fa-f]{12}$',  # AABBCCDDEEFF
    ]

    return any(re.match(pattern, mac) for pattern in patterns)


def validate_email(email: str) -> bool:
    """
    验证电子邮件地址格式

    Args:
        email: 邮箱地址

    Returns:
        是否有效
    """
    if not email:
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_device_fingerprint(fingerprint: str) -> bool:
    """
    验证设备指纹格式

    设备指纹应该是64个字符的16进制字符串（SHA256）

    Args:
        fingerprint: 设备指纹

    Returns:
        是否有效
    """
    if not fingerprint:
        return False

    pattern = r'^[0-9a-fA-F]{64}$'
    return bool(re.match(pattern, fingerprint))


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除不安全字符

    Args:
        filename: 原始文件名

    Returns:
        清理后的文件名
    """
    # 移除路径分隔符和其他危险字符
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')

    return filename


def validate_rule_version(version: str) -> bool:
    """
    验证规则版本号格式

    支持语义化版本号：major.minor.patch (如: 1.0.0)

    Args:
        version: 版本号字符串

    Returns:
        是否有效
    """
    if not version:
        return False

    pattern = r'^\d+\.\d+\.\d+$'
    return bool(re.match(pattern, version))
