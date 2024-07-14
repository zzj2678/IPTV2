import logging
import time
from typing import Optional

from live.util.crypto import md5
from live.util.http import get_text
from live.util.m3u8 import update_m3u8_content

from .base import BaseChannel

logger = logging.getLogger(__name__)

CHANNEL_MAPPING = {
    'jsws': 'jsws',  # 江苏卫视
    'jscs': 'jscs',  # 江苏城市
    'jsgg': 'jsgg',  # 江苏新闻
    'jszy': 'jszy',  # 江苏综艺
    'jsys': 'jsys',  # 江苏影视
    'jsty': 'jsty',  # 江苏体育
    'jsjy': 'jsjy',  # 江苏教育
    'jsgj': 'jsgj',  # 江苏国际
    'hxgw': 'hxgw',  # 好享购物
    'ymkt': 'ymkt',  # 优漫卡通
}


class JSTV(BaseChannel):
    headers = {
        "Referer": 'https://live.jstv.com/',
        # 'Origin': 'https://live.jstv.com',
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    async def get_play_url(self, video_id: str) -> Optional[str]:
        if video_id not in CHANNEL_MAPPING:
            logger.error(f"Invalid Video ID: {video_id}")
            return None

        tm = int(time.time()) + 5

        upt = md5(f"8f6f55fb8ffbfd555aa29a9a1426a&{tm}&/livezhuzhan/{video_id}.m3u8")[12:20] + str(tm)
        url = f"https://live-hls.jstv.com/livezhuzhan/{video_id}.m3u8?upt={upt}"

        m3u8_content = await get_text(url, headers=self.headers,  proxy='http://58.52.216.91:3128')

        modified_m3u8_content = update_m3u8_content(url, m3u8_content)

        return modified_m3u8_content

site = JSTV()
