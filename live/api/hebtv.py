import hashlib
import logging
import time
from typing import Optional

from live.api.base import BaseChannel
from live.util.http.http import get_json

logger = logging.getLogger(__name__)

CHANNEL_MAPPING = {
    'hbws': 0,   # 河北卫视
    'hbjj': 1,   # 河北经济
    'hbnm': 2,   # 河北农民
    'hbds': 3,   # 河北都市
    'hbys': 4,   # 河北影视
    'hbsekj': 5,   # 少儿科教
    'hbgg': 6,   # 河北公共
    'hbsjgw': 7,   # 三佳购物
}

class HeBTV(BaseChannel):
    async def get_play_url(self, video_id: str) -> Optional[str]:
        if video_id not in CHANNEL_MAPPING:
            logger.error(f"Invalid Video ID: {video_id}")
            return None

        data = await get_json("https://api.cmc.hebtv.com/scms/api/com/article/getArticleList?catalogId=32557&siteId=1")
        live_data = data['returnData']['news'][CHANNEL_MAPPING[video_id]]
        m3u8 = live_data['liveVideo'][0]['formats'][0]['liveStream']
        live_key = live_data['appCustomParams']['movie']['liveKey']
        live_uri = live_data['appCustomParams']['movie']['liveUri']

        t = int(time.time()) + 7200
        k = hashlib.md5(f"{live_uri}{live_key}{t}".encode()).hexdigest()
        play_url = f"{m3u8}?t={t}&k={k}"

        return play_url

site = HeBTV()
