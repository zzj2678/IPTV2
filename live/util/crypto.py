import base64
import binascii
import hashlib

from Crypto import Random
from Crypto.Cipher import AES, DES, DES3, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad


def md5(s: str):
    return hashlib.md5(s.encode("utf8")).hexdigest()


def sha1(s: str):
    return hashlib.sha1(s.encode("utf8")).hexdigest()


def sha256(s: str):
    return hashlib.sha256(s.encode("utf8")).hexdigest()


def des_encrypt(text, key, iv):
    print(text, key, iv)
    key = binascii.a2b_hex(key.encode("utf-8"))
    iv = binascii.a2b_hex(iv.encode("utf-8"))

    padding_text = pad(text.encode("utf-8"), DES3.block_size, style="pkcs7")
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    encrypt_bytes = cipher.encrypt(padding_text)
    return base64.b64encode(encrypt_bytes).decode("utf-8")


def rsa_encrypt(text, pub_key):
    key = RSA.importKey(pub_key)
    cipher = PKCS1_v1_5.new(key)
    cipher_text = base64.b64encode(cipher.encrypt(text.encode("utf-8")))
    return cipher_text.decode("utf-8")


def aes_decrypt(text, key):
    key = binascii.a2b_hex(key.encode("utf-8"))
    cipher = AES.new(key, AES.MODE_ECB)
    text = binascii.a2b_hex(text)
    decrypt_key = cipher.decrypt(text)
    return binascii.b2a_hex(decrypt_key).decode()


# class AES:
#     def __init__(self, key, iv):
#         self.key = key
#         self.iv = iv

#     def __pad(self, text):
#         text_length = len(text)
#         amount_to_pad = AES.block_size - (text_length % AES.block_size)
#         if amount_to_pad == 0:
#             amount_to_pad = AES.block_size
#         pad = chr(amount_to_pad)
#         return text + pad * amount_to_pad

#     def __unpad(self, text):
#         pad = ord(text[-1])
#         return text[:-pad]

#     def encrypt(self, raw):
#         raw = self.__pad(raw)
#         cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
#         return base64.b64encode(cipher.encrypt(raw))

#     def decrypt(self, enc):
#         enc = base64.b64decode(enc)
#         cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
#         return self.__unpad(cipher.decrypt(enc).decode("utf-8"))
