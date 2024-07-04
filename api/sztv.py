import logging
import hashlib
import time
from typing import Optional
from .base import BaseChannel
from utils.http import get_text
from urllib.parse import urlparse
import os
from utils.m3u8 import get_m3u8_content

logger = logging.getLogger(__name__)

# 公共基础 URL
BASE_URL = "https://sztv-live.sztv.com.cn/"

CHANNEL_MAPPING = {
    'szws': 'AxeFRth',   # 深圳卫视
    'szyl': '1q4iPng',   # 深圳娱乐
    'szse': '1SIQj6s',   # 深圳少儿
    'szgg': '2q76Sw2',   # 深圳公共
    'szcjsh': '3vlcoxP', # 深圳财经生活
    'szdsj': '4azbkoY',  # 深圳电视剧
    'yhgw': 'BJ5u5k2',   # 宜和购物
    'szds': 'ZwxzUXr',   # 深圳都市
    'szgj': 'sztvgjpd',  # 深圳国际
    'szyd': 'wDF6KJ3',   # 深圳移动
    'ba1': 'Qr45J1U',    # 宝安fm1043
    'fy': 'bPHSw12',     # 飞扬971
    'ba2': 'g0c7BL1',    # 宝安fm905
    'xf': 'ms3M6DA',     # 先锋898
    'sj': 'sf4orL8',     # 私家车广播
    'kl': '171m21B',     # 快乐106.2
}

class SZTV(BaseChannel):
    async def get_key(self, pid: str) -> str:
        t = int(time.time())
        token = hashlib.md5(f"{t}{pid}cutvLiveStream|Dream2017".encode()).hexdigest()
        url = f"http://cls2.cutv.com/getCutvHlsLiveKey?t={t}&token={token}&id={pid}"
        return await get_text(url)

    def generate_play_url(self, base_url: str, pid: str, key: str) -> str:
        segment = self.determine_segment(pid)
        return f"{base_url}{pid}{segment}{key}.m3u8"

    def determine_segment(self, pid: str) -> str:
        return '/500/' if len(pid) >= 4 else '/64/'

    async def get_play_url(self, video_id: str) -> Optional[str]:
        logger.info(f"Processing request for video ID: {video_id}")

        pid = CHANNEL_MAPPING.get(video_id)
        if not pid:
            logger.error(f"Invalid Video ID: {pid}")
            return None

        key = await self.get_key(pid)
        if not key:
            logger.warning(f"Failed to fetch key for video ID {video_id}")
            return None

        play_url = self.generate_play_url(BASE_URL, pid, key)

        logger.info(f"Returning Play URL for video ID {video_id}: {play_url}")

        headers = {"Referer": 'https://www.sztv.com.cn/'}
        m3u8_content = await get_text(play_url, headers=headers)

        if not m3u8_content:
            logger.warning(f"No content retrieved from {play_url}")
            return None

        print(m3u8_content)

        modified_m3u8_content = get_m3u8_content(play_url, m3u8_content)

        return modified_m3u8_content



site = SZTV()
