"""
加密工具
"""

import os
import hashlib
import hmac
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


def generate_random_key(length: int = 32) -> bytes:
    """
    生成随机密钥

    Args:
        length: 密钥长度（字节）

    Returns:
        随机密钥字节串
    """
    return os.urandom(length)


def hash_sha256(data: str) -> str:
    """
    SHA256哈希

    Args:
        data: 要哈希的字符串

    Returns:
        16进制哈希字符串
    """
    return hashlib.sha256(data.encode()).hexdigest()


def hmac_sha256(key: str, data: str) -> str:
    """
    HMAC-SHA256签名

    Args:
        key: 密钥
        data: 要签名的数据

    Returns:
        16进制签名字符串
    """
    return hmac.new(key.encode(), data.encode(), hashlib.sha256).hexdigest()


def verify_hmac_sha256(key: str, data: str, signature: str) -> bool:
    """
    验证HMAC-SHA256签名

    Args:
        key: 密钥
        data: 原始数据
        signature: 签名

    Returns:
        签名是否有效
    """
    expected = hmac_sha256(key, data)
    return hmac.compare_digest(expected, signature)


class AESCipher:
    """
    AES-256-GCM加密解密类
    """

    def __init__(self, key: bytes = None):
        """
        初始化AES加密器

        Args:
            key: 32字节的密钥，如果为None则自动生成
        """
        if key is None:
            key = generate_random_key(32)
        elif len(key) != 32:
            raise ValueError("Key must be 32 bytes for AES-256")

        self.key = key
        self.aesgcm = AESGCM(key)

    def encrypt(self, plaintext: str, associated_data: str = None) -> str:
        """
        加密字符串

        Args:
            plaintext: 明文字符串
            associated_data: 关联数据（可选）

        Returns:
            Base64编码的密文（包含nonce）
        """
        # 生成随机nonce（12字节）
        nonce = os.urandom(12)

        # 加密
        ciphertext = self.aesgcm.encrypt(
            nonce,
            plaintext.encode(),
            associated_data.encode() if associated_data else None,
        )

        # 将nonce和密文组合并Base64编码
        combined = nonce + ciphertext
        return base64.b64encode(combined).decode()

    def decrypt(self, ciphertext_b64: str, associated_data: str = None) -> str:
        """
        解密字符串

        Args:
            ciphertext_b64: Base64编码的密文（包含nonce）
            associated_data: 关联数据（可选，必须与加密时一致）

        Returns:
            明文字符串

        Raises:
            Exception: 解密失败
        """
        try:
            # Base64解码
            combined = base64.b64decode(ciphertext_b64)

            # 分离nonce和密文
            nonce = combined[:12]
            ciphertext = combined[12:]

            # 解密
            plaintext = self.aesgcm.decrypt(
                nonce,
                ciphertext,
                associated_data.encode() if associated_data else None,
            )

            return plaintext.decode()

        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")

    @staticmethod
    def from_base64_key(key_b64: str) -> "AESCipher":
        """
        从Base64编码的密钥创建AESCipher实例

        Args:
            key_b64: Base64编码的密钥

        Returns:
            AESCipher实例
        """
        key = base64.b64decode(key_b64)
        return AESCipher(key)

    def get_key_base64(self) -> str:
        """
        获取Base64编码的密钥

        Returns:
            Base64编码的密钥字符串
        """
        return base64.b64encode(self.key).decode()


def hash_password(password: str) -> str:
    """
    哈希密码（使用bcrypt）

    Args:
        password: 明文密码

    Returns:
        哈希后的密码
    """
    import bcrypt

    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """
    验证密码

    Args:
        password: 明文密码
        hashed: 哈希后的密码

    Returns:
        密码是否正确
    """
    import bcrypt

    return bcrypt.checkpw(password.encode(), hashed.encode())
