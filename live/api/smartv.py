import logging
from typing import Optional
from .base import BaseChannel
import hashlib
import time
import json
from urllib.parse import urlparse, parse_qs
from util.http import get_text
from util.m3u8 import update_m3u8_content

logger = logging.getLogger(__name__)


class Smartv(BaseChannel):
    def __init__(self):
        pass

    async def _generate_url(self, video_id: str) -> str:
        base_url = f"http://198.16.100.186:8278/{video_id}/playlist.m3u8"
        tid = "mc42afe745533"
        t = str(int(time.time() // 150))
        tsum = hashlib.md5(f"tvata nginx auth module/{video_id}/playlist.m3u8{tid}{t}".encode()).hexdigest()
        return f"{base_url}?tid={tid}&ct={t}&tsum={tsum}"

    async def get_play_url(self, video_id: str) -> Optional[str]:
        url = await self._generate_url(video_id)
        headers = {
            "CLIENT-IP": "127.0.0.1",
            "X-FORWARDED-FOR": "127.0.0.1",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; 22101316C Build/SP1A.210812.016)",
        }

        playlist = await get_text(url, headers=headers)

        return update_m3u8_content(url, playlist)


site = Smartv()
