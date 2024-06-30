import logging
from typing import Optional
from .base import BaseChannel
from utils.http import get_json
import re

logger = logging.getLogger(__name__)

CHANNEL_MAPPING = {
    'inews': 'C', # 無綫新聞台 港澳原版
    # 'inews': 'I-NEWS', # 無綫新聞台 海外版
    'finance': 'A', # 財經資訊台 港澳原版
    # 'finance': 'I-FINA', # 無綫財經體育資訊台 海外版
    'nevt1': 'NEVT1', # RTHK 31
    'nevt2': 'NEVT2' # RTHK 32
}

class TVB(BaseChannel):
    async def get_live(self, channel_code):
        # https://inews-api.tvb.com/news/live
        # url = f'https://inews-api.tvb.com/news/checkout/live/hd/ott_{channel_code}_h264?profile=chrome'
        url = f'https://inews-api.tvb.com/news/checkout/live/hd/ott_{channel_code}_h264?profile=safari'

        headers = {
            'CLIENT-IP': '127.0.0.1',
            'X-FORWARDED-FOR': '127.0.0.1'
        }
        return await get_json(url, headers=headers)

    async def get_play_url(self, video_id: str) -> Optional[str]:
        if video_id not in CHANNEL_MAPPING:
            logger.error(f"Invalid Video ID: {video_id}")
            return None

        channel_code = CHANNEL_MAPPING[video_id]

        data = await self.get_live(channel_code)

        stream_url = data['content']['url']

        hd_url = stream_url['hd']


        # if channel_id in ['nevt1', 'nevt2']:
            # hd_url = re.sub(r'&p=(.*?)$', '', hd_url)

        # hd_url = re.sub(r'&p=(.*?)$', '&p=3000', hd_url)

        return hd_url
            

site = TVB()
