import logging
from typing import Optional

from live.util.http import get_json
from live.util.http.http import get_text
from live.util.m3u8 import update_m3u8_content

from .base import BaseChannel

logger = logging.getLogger(__name__)

CHANNEL_MAPPING = {
    "ynws": "yunnanweishi",  # 云南卫视
    "ynds": "yunnandushi",   # 云南都市
    "ynyl": "yunnanyule",     # 云南娱乐
    "ynkl": "yunnangonggong", # 康旅频道
    "yngj": "yunnanguoji",    # 澜湄国际
    "ynse": "yunnanshaoer"    # 云南少儿
}

class YNTV(BaseChannel):
  headers = {
        'Referer': 'https://www.yntv.cn/'
  }

  async def get_play_url(self, video_id: str) -> Optional[str]:
    if video_id not in CHANNEL_MAPPING:
        logger.error(f"Invalid Video ID: {video_id}")
        return None

    params = {
        "name": CHANNEL_MAPPING[video_id],
    }

    json_data = await get_json(
        'https://api.yntv.ynradio.com/index/jmd/getRq',
        params=params,
        headers=self.headers
    )

    url = f"https://tvlive.yntv.cn{json_data['url']}?wsSecret={json_data['string']}&wsTime={json_data['time']}"

    m3u8_content = await get_text(url, headers=self.headers)

    modified_m3u8_content = update_m3u8_content(url, m3u8_content, True)

    return modified_m3u8_content


site = YNTV()
