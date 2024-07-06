import random
import ssl
from copy import deepcopy

ORIGIN_CIPHERS = "ECDHE-ECDSA-AES256-CCM:ECDHE-ECDSA-AES128-CCM8:ECDHE-ECDSA-AES256-CCM8:DHE-RSA-AES128-CCM:DHE-RSA-AES256-CCM:AES128-CCM8:AES256-CCM8:DHE-RSA-AES128-CCM8:DHE-RSA-AES256-CCM8:ADH-AES128-SHA256:ADH-AES256-SHA256:ADH-AES128-GCM-SHA256:ADH-AES256-GCM-SHA384:AES128-CCM:AES256-CCM:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES256-SHA256:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-DSS-AES128-SHA256:DHE-DSS-AES256-SHA256:DHE-DSS-AES128-GCM-SHA256:DHE-DSS-AES256-GCM-SHA384:DHE-RSA-AES128-SHA256:AES256-GCM-SHA384:AES128-GCM-SHA256:AES256-SHA256:AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:RSA+AES128:ALL:!ADH:@STRENGTH:HIGH:DEFAULT:!DH:!aNULL:!eNULL:!LOW:!ADH:!RC4:!3DES:!MD5:!EXP:!PSK:!SRP:!DSS"


class _SSLMethod(object):
    ssl_method = {
        "SSLv23": ssl.PROTOCOL_SSLv23,
        "TLSv1": ssl.PROTOCOL_TLSv1,
        "TLSv1_1": ssl.PROTOCOL_TLSv1_1,
        "TLSv1_2": ssl.PROTOCOL_TLSv1_2,
        "TLS": ssl.PROTOCOL_TLS,
        "TLS_CLIENT": ssl.PROTOCOL_TLS_CLIENT,
        "TLS_SERVER": ssl.PROTOCOL_TLS_SERVER,
    }

    ssl_context = {
        "SSLv2": ssl.OP_NO_SSLv2,
        "SSLv3": ssl.OP_NO_SSLv3,
        "TLSv1": ssl.OP_NO_TLSv1,
        "TLSv1_1": ssl.OP_NO_TLSv1_1,
        "TLSv1_2": ssl.OP_NO_TLSv1_2,
        "TLSv1_3": ssl.OP_NO_TLSv1_3,
    }

    def __init__(self, version=None):
        self.version: str = version or "TLSv1_2"

    @property
    def gen(self):
        return self.ssl_method[self.version]

    @property
    def context(self):
        _ssl_context = deepcopy(self.ssl_context)
        del _ssl_context[self.version]
        return _ssl_context


class CipherFactory:
    def __init__(self, cipher: str = None):
        if cipher is None:
            cipher = ORIGIN_CIPHERS
        self.cipher = cipher

    @classmethod
    def setter_cipher(cls, val: str = None):
        return cls(val)

    def __call__(self) -> str:
        ciphers_list = self.cipher.split(":")
        random.shuffle(ciphers_list)
        ciphers_real = ":".join(ciphers_list)
        return ciphers_real


generate_cipher = CipherFactory()


class SSLFactory:
    cipers = generate_cipher

    def __call__(self, _ssl: str = "TLSv1_2") -> ssl.SSLContext:
        _verion_set = _SSLMethod(_ssl).context
        ciphers = self.cipers() + ":!aNULL:!eNULL:!MD5"

        context = ssl.create_default_context()
        for ssl_option in _verion_set.values():
            context.options |= ssl_option
        context.set_ciphers(ciphers)
        return context


sslgen = SSLFactory()


__all__ = [sslgen, generate_cipher]
