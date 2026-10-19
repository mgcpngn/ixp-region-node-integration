"""实名认证接口的密码加密（对接文档"密码加密"一节）。

AES-CBC + PKCS#7，密钥为 client_secret 前 32 位，每次随机 16 字节 IV，
输出 base64(IV || 密文)。
"""

import base64
import os

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

_BLOCK = 16


def key_from_secret(client_secret: str) -> bytes:
    key = client_secret[:32].encode()
    if len(key) != 32:
        raise ValueError("client_secret 不足 32 位，无法作为 AES-256 密钥")
    return key


def encrypt(plaintext: str, key: bytes) -> str:
    if len(key) not in (16, 24, 32):
        raise ValueError("密钥长度必须为 16、24 或 32 字节")
    iv = os.urandom(_BLOCK)
    padder = padding.PKCS7(_BLOCK * 8).padder()
    data = padder.update(plaintext.encode()) + padder.finalize()
    enc = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    return base64.b64encode(iv + enc.update(data) + enc.finalize()).decode()


def decrypt(token: str, key: bytes) -> str:
    if len(key) not in (16, 24, 32):
        raise ValueError("密钥长度必须为 16、24 或 32 字节")
    raw = base64.b64decode(token)
    iv, body = raw[:_BLOCK], raw[_BLOCK:]
    dec = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    data = dec.update(body) + dec.finalize()
    unpadder = padding.PKCS7(_BLOCK * 8).unpadder()
    return (unpadder.update(data) + unpadder.finalize()).decode()


def encrypt_password(password: str, client_secret: str) -> str:
    return encrypt(password, key_from_secret(client_secret))
