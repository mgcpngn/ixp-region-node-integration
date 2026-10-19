import base64
import unittest

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from ixp_region_node import crypto

SECRET = "0123456789abcdef0123456789abcdefEXTRA"


class CryptoTest(unittest.TestCase):
    def test_roundtrip(self):
        key = crypto.key_from_secret(SECRET)
        token = crypto.encrypt_password("Aa@123456", SECRET)
        self.assertEqual(crypto.decrypt(token, key), "Aa@123456")

    def test_iv_is_random(self):
        self.assertNotEqual(
            crypto.encrypt_password("x", SECRET), crypto.encrypt_password("x", SECRET)
        )

    def test_layout_matches_doc_sample(self):
        # 按文档 Go/Python 示例的方式独立解密：前 16 字节为 IV
        token = crypto.encrypt_password("Aa@123456", SECRET)
        raw = base64.b64decode(token)
        dec = Cipher(algorithms.AES(SECRET[:32].encode()), modes.CBC(raw[:16])).decryptor()
        data = dec.update(raw[16:]) + dec.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        self.assertEqual(unpadder.update(data) + unpadder.finalize(), b"Aa@123456")

    def test_short_secret_rejected(self):
        with self.assertRaises(ValueError):
            crypto.key_from_secret("too-short")


if __name__ == "__main__":
    unittest.main()
