import logging
import random
import time
from typing import Optional

from live.util.crypto import md5

from .base import BaseChannel

logger = logging.getLogger(__name__)

CHANNEL_MAPPING = {
    'zjws' : '01',  #浙江卫视
    'zjqj' : '02',  #浙江钱江都市
    'zjjjsh' : '03',  #浙江经济生活
    'zjjkys' : '04',  #浙江教科影视
    'zjmsxx' : '06',  #浙江民生休闲
    'zjxw' : '07',  #浙江公共新闻
    'zjse' : '08',  #浙江少儿
    'zjgj' : '10',  #浙江国际
    'zjhyg' : '11',  #浙江好易购
    'zjzjjl' : '12',  #浙江之江纪录
}


class CZTV(BaseChannel):
    def __init__(self):
        pass

    async def get_play_url(self, video_id: str) -> Optional[str]:
        if video_id not in CHANNEL_MAPPING:
            logger.error(f"Invalid Video ID: {video_id}")
            return None

        video_id = CHANNEL_MAPPING[video_id]
        pathname = f"/channel{video_id}/1080p.m3u8"
        tm = int(time.time())
        rand = md5(str(random.randint(0, 1000000)))
        key = '9T08yiAoqM4eeCwV'
        r = md5(f"{pathname}-{tm}-{rand}-0-{key}")
        auth_key = f"{tm}-{rand}-0-{r}"
        url = f"https://zhfivel02.cztv.com/channel{video_id}/1080p.m3u8?auth_key={auth_key}"

        return url

site = CZTV()
