import base64
import json
import logging
import struct
from typing import Optional

from live.util.http.http import get_text

from .base import BaseChannel

logger = logging.getLogger(__name__)

CHANNEL_MAPPING = {
    "jlws": 1531,  # 吉林卫视
    "jlds": 1532,  # 吉林都市
    "jlsh": 1534,  # 吉林生活
    "jlys": 1535,  # 吉林影视
    "jlxc": 1536,  # 吉林乡村
    "jlggxw": 1537,  # 吉林公共新闻
    "jlzywh": 1538,  # 吉视综艺文化
    "dbxq": 1539,  # 东北戏曲
}

def str2long(s, w):
    n = len(s)
    m = (4 - (n & 3) & 3) + n
    s = s.ljust(m)
    v = list(struct.unpack("<%dL" % (m >> 2), s))
    if w:
        v.append(n)
    return v

def long2str(v, w):
    n = (len(v) - 1) << 2
    if w:
        m = v[-1]
        if m < n - 3 or m > n:
            return ""
        n = m
    s = struct.pack("<%dL" % len(v), *v)
    return s[:n] if w else s

def xxtea_encrypt(data, key, delta):
    if data == "":
        return ""
    v = str2long(data.encode(), True)
    k = str2long(key.encode(), False)
    if len(k) < 4:
        k.extend([0] * (4 - len(k)))
    n = len(v) - 1
    z = v[n]
    y = v[0]
    q = 6 + 52 // (n + 1)
    sum = 0
    while q > 0:
        sum = (sum + delta) & 0xffffffff
        e = (sum >> 2) & 3
        for p in range(n):
            y = v[p + 1]
            v[p] = (v[p] + (((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4)) ^ ((sum ^ y) + (k[p & 3 ^ e] ^ z)))) & 0xffffffff
            z = v[p]
        y = v[0]
        v[n] = (v[n] + (((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4)) ^ ((sum ^ y) + (k[n & 3 ^ e] ^ z)))) & 0xffffffff
        z = v[n]
        q -= 1
    encrypted_data = long2str(v, False)
    return base64.b64encode(encrypted_data).decode()

def xxtea_decrypt(data, key, delta):
    if data == "":
        return ""
    v = str2long(base64.b64decode(data), False)
    k = str2long(key.encode(), False)
    if len(k) < 4:
        k.extend([0] * (4 - len(k)))
    n = len(v) - 1
    z = v[n]
    y = v[0]
    q = 6 + 52 // (n + 1)
    sum = (q * delta) & 0xffffffff
    while sum != 0:
        e = (sum >> 2) & 3
        for p in range(n, 0, -1):
            z = v[p - 1]
            v[p] = (v[p] - (((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4)) ^ ((sum ^ y) + (k[p & 3 ^ e] ^ z)))) & 0xffffffff
            y = v[p]
        z = v[n]
        v[0] = (v[0] - (((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4)) ^ ((sum ^ y) + (k[0 & 3 ^ e] ^ z)))) & 0xffffffff
        y = v[0]
        sum = (sum - delta) & 0xffffffff
    decrypted_data = long2str(v, True)
    return decrypted_data.decode()


class JLNTV(BaseChannel):

    KEY = "5b28bae827e651b3"
    DELTA = 0x9E3779B9

    async def get_play_url(self, video_id: str) -> Optional[str]:
        if video_id not in CHANNEL_MAPPING:
            logger.error(f"Invalid Video ID: {video_id}")
            return None

        params = {"page": 1, "size": 1000, "type": 1}

        headers = {
            "Client-Type": "web",
            "DNT": "1",
            "Host": "clientapi.jlntv.cn",
            "Origin": "https://www.jlntv.cn",
            "Referer": "https://www.jlntv.cn/",
        }

        text = await get_text("https://clientapi.jlntv.cn/broadcast/list", params=params, headers=headers)

        text = text.replace('"', "")


        decrypt_data = xxtea_decrypt(text, self.KEY, self.DELTA)

        json_data = json.loads(decrypt_data)

        data = json_data.get('data', [])

        for item in data:
            item_data = item.get('data', {})
            if item_data.get('indexId') == CHANNEL_MAPPING[video_id]:
                url = item_data.get('streamUrl')
                return url

        return None


site = JLNTV()
