import logging
from typing import Optional

from live.util.http import get_json

from .base import BaseChannel

logger = logging.getLogger(__name__)

CHANNEL_MAPPING = {
   "sxws"  : 'q8RVWgs', #山西卫视
   "sxjj"  : '4j01KWX', #山西经济
   "sxys"  : 'Md571Kv', #山西影视
   "sxshfz"  : 'p4y5do9', #山西社会与法治
   "sxwtsh"  : 'Y00Xezi', #山西文体生活
   "sxhh"  : 'ce1mC4', #山西黄河
}

class SXTV(BaseChannel):

  async def get_play_url(self, video_id: str) -> Optional[str]:
    if video_id not in CHANNEL_MAPPING:
        logger.error(f"Invalid Video ID: {video_id}")
        return None

    params = {
        "channelid": CHANNEL_MAPPING[video_id],
    }

    json_data = await get_json(
        'http://dyhhplus.sxrtv.com/apiv3.8/m3u8_notoken.php',
        params=params,
    )

    stream_url = json_data["address"]

    return stream_url


site = SXTV()
