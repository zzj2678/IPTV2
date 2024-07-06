import logging
from typing import Optional
from .base import BaseChannel
import json
from urllib.parse import urljoin
import re
from utils.http import get_json, post_json, get_text
from utils.m3u8 import update_m3u8_content

logger = logging.getLogger(__name__)

class Youtube(BaseChannel):
    async def get_player(self, video_id: str) -> Optional[str]:
        url = 'https://www.youtube.com/youtubei/v1/player'
        data = {
            'context': {
                'client': {
                    'hl': 'zh',
                    'clientVersion': '2.20201021.03.00',
                    'clientName': 'WEB'
                }
            },
            'videoId': video_id
        }

        return await post_json(url, json=data)

    async def get_max_resolution_url(self, url):
        text = await get_text(url)

        lines = text.splitlines()

        max_resolution = 0
        max_resolution_url = None

        for i, line in enumerate(lines):
            if line.startswith("#") and 'RESOLUTION=' in line:
                resolution_match = re.search(r'RESOLUTION=(\d+)x(\d+)', line)
                if resolution_match:
                    width = int(resolution_match.group(1))
                    height = int(resolution_match.group(2))
                    resolution = width * height

                    if resolution > max_resolution:
                        max_resolution = resolution
                        max_resolution_url = lines[i + 1] 

        return max_resolution_url

    async def get_play_url(self, video_id: str) -> Optional[str]:
        data = await self.get_player(video_id)

        streaming_data = data.get('streamingData', {})

        # print(json.dumps(streaming_data))

        hls_manifest_url = streaming_data.get('hlsManifestUrl')
        if not hls_manifest_url:
            return None

        url = await self.get_max_resolution_url(hls_manifest_url)

        # headers = {"Referer": 'https://www.youtube.com/'}
        # m3u8_content = await get_text(url)

        # m3u8_content = update_m3u8_content(url, m3u8_content, True)

        # print(m3u8_content)

        return url

     

  

site = Youtube()

