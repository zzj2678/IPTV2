import hashlib
import logging
import random
import time
import urllib.parse
import uuid
from typing import Dict, Optional

from live.api.base import BaseChannel
from live.util.http.http import post_json

logger = logging.getLogger(__name__)

CHANNEL_MAPPING = {
    "cctv6": "LIVEI56PNI726KA7A",  # CCTV6电影频道
    "1905b": "LIVE8J4LTCXPI7QJ5",  # 1905国外电影
    "1905a": "LIVENCOI8M4RGOOJ9",  # 1905国内电影
}


# (new i["default"].SHA1).hex(n + "." + t)
def generate_sign(params: Dict[str, str], salt: str) -> str:
    sorted_params = sorted(params.items())
    params_str = urllib.parse.urlencode(sorted_params)
    sign_str = f"{params_str}.{salt}"
    sign = hashlib.sha1(sign_str.encode()).hexdigest()
    return sign


class A1905(BaseChannel):
    salt = "2bcc2c6ab75dac016d20181bfcd1ee0697c78018"

    async def get_play_url(self, video_id: str) -> Optional[str]:
        if video_id not in CHANNEL_MAPPING:
            logger.error(f"Invalid Video ID: {video_id}")
            return None

        ts = int(time.time())
        playid = f"{str(ts)[6:]}{str(random.random())[-8:]}"

        params = {
            "cid": 999999,
            "expiretime": ts + 600,
            "nonce": ts,
            "page": "https%3A%2F%2Fwww.1905.com%2F",
            "playerid": playid,
            "streamname": CHANNEL_MAPPING[video_id],
            "uuid": str(uuid.uuid4()),
        }

        sign = generate_sign(params, self.salt)
        params["appid"] = "GEalPdWA"

        headers = {
            "Authorization": sign,
            "Content-Type": "application/json",
        }
        data = await post_json("https://profile.m1905.com/mvod/liveinfo.php", json=params, headers=headers)
        data = data["data"]

        play_url = data["quality"]["hd"]["host"] + data["path"]["hd"]["path"] + data["sign"]["hd"]["sign"]

        return play_url


site = A1905()
