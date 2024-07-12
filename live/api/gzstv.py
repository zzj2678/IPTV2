import logging
from typing import Optional

from live.util.http import get_json

from .base import BaseChannel

logger = logging.getLogger(__name__)

CHANNEL_MAPPING = {
    "gzws" : "tv/ch01", #贵州卫视
    "gzgg" : "tv/ch02", #贵州公共
    "gzwy" : "tv/ch03", #贵州影视
    "gzsh" : "tv/ch04", #贵州生活
    "gzfz" : "tv/ch05", #贵州法制
    "gzkj" : "tv/ch06", #贵州科教
    "gzjj" : "tv/ch09", #贵州经济
    "gzjygw" : "tv/ch10", #贵州家有购物
    "gzyd" : "tv/ch13", #贵州移动
    "fm946" : "fm/94_6", #综合广播
    "fm989" : "fm/98_9", #经济广播
    "fm916" : "fm/91_6", #音乐广播
    "fm952" : "fm/95_2", #交通广播
    "fm972" : "fm/97_2", #旅游广播
    "fm900" : "fm/90_0", #故事广播
}

class GZTV(BaseChannel):

  async def get_play_url(self, video_id: str) -> Optional[str]:
    if video_id not in CHANNEL_MAPPING:
        logger.error(f"Invalid Video ID: {video_id}")
        return None

    params = {
        "fields": 'stream_url',
    }

    json_data = await get_json(
        f'https://api.gzstv.com/v1/{CHANNEL_MAPPING[video_id]}',
        params=params,
    )

    stream_url = json_data["stream_url"]

    return stream_url


site = GZTV()
