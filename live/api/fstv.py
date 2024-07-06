import logging
from typing import Optional
from .base import BaseChannel
import json
from urllib.parse import urljoin
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
from live.util.http import get_json, post_json

logger = logging.getLogger(__name__)

CHANNEL_MAPPING = {
    "fszh": 3,  # 佛山综合
    "fsys": 4,  # 佛山影视
    "fsgg": 2,  # 佛山公共
    "fsnh": 5,  # 佛山南海
    "fssd": 6,  # 佛山顺德
    "fsgm": 7,  # 佛山高明
    "fsss": 8,  # 佛山三水
}


class FSTV(BaseChannel):
    def __init__(self):
        self.key = b"ptfcaxhmslc4Kyrnj$lWwmkcvdze2cub"
        self.iv = b"352e7f4773ef5c30"

    def decrypt_data(self, encrypted_data):
        decipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        decrypted_data = unpad(decipher.decrypt(base64.b64decode(encrypted_data)), AES.block_size)
        return decrypted_data.decode()

    async def get_play_url(self, video_id: str) -> Optional[str]:
        if video_id not in CHANNEL_MAPPING:
            logger.error(f"Invalid Video ID: {video_id}")
            return None

        headers = {
            "APPKEY": "xinmem3.0",
            "VERSION": "4.0.9",
            "PLATFORM": "ANDROID",
            "SIGN": "b2350fe63e26fbf872b424dece22bd1b",
        }

        json_data = await post_json("https://xmapi.fstv.com.cn/appapi/tv/indexaes", headers=headers)

        for channel in json_data["data"]["channel"]:
            print(channel)
            if CHANNEL_MAPPING[video_id] == int(channel["id"]):
                encrypted_stream = channel["stream"]
                play_url = self.decrypt_data(encrypted_stream)
                return play_url

        return None


site = FSTV()
