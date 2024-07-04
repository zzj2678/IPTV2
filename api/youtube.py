import logging
from typing import Optional
from .base import BaseChannel
import json
from urllib.parse import urljoin
from utils.http import get_json, post_json, get_text

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

    async def get_play_url(self, video_id: str) -> Optional[str]:
        data = await self.get_player(video_id)

        streaming_data = data.get('streamingData', {})

        print(streaming_data)

        hls_manifest_url = streaming_data.get('hlsManifestUrl')
        if hls_manifest_url:
            resolution_url = await get_text(hls_manifest_url)
            return resolution_url

        return None

site = Youtube()

