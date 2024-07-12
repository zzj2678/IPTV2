import logging
from typing import Optional

from live.util.http import get_json
from live.util.http.http import get_text
from live.util.m3u8 import update_m3u8_content

from .base import BaseChannel

logger = logging.getLogger(__name__)

CHANNEL_MAPPING = {
    "ahws": "47",  # 安徽卫视
    "ahjjsh": "71",  # 安徽经济生活
    "ahzyty": "73",  # 安徽综艺体育
    "ahys": "72",  # 安徽影视
    "ahgg": "50",  # 安徽公共
    "ahnykj": "51",  # 安徽农业科教
    "ahgj": "70",  # 安徽国际
    "ahyd": "68",  # 安徽移动
}


class AHTV(BaseChannel):
    async def get_play_url(self, video_id: str) -> Optional[str]:
        if video_id not in CHANNEL_MAPPING:
            logger.error(f"Invalid Video ID: {video_id}")
            return None

        params = {
            "appid": "m2otdjzyuuu8bcccnq",
            "appkey": "5eab6b4e1969a8f9aef459699f0d9000",
            "is_audio": 0,
            "category_id": "1,2",
        }

        headers = {"Referer": "https://www.ahtv.cn/"}

        json_data = await get_json("https://mapi.ahtv.cn/api/open/ahtv/channel.php", params=params, headers=headers)

        for item in json_data:
            if item["id"] == int( CHANNEL_MAPPING[video_id]):

                url = item["m3u8"]

                base_url = '/'.join(url.split('/')[:-1]) + '/'
                text = await get_text(url, headers=headers)

                lines = text.splitlines()
                for line in lines:
                  if not line.startswith("#") and "m3u8" in line:
                    url = f'{base_url}{line}'

                    m3u8_content = await get_text(url, headers=headers)

                    modified_m3u8_content = update_m3u8_content(url, m3u8_content, True)

                    return modified_m3u8_content


site = AHTV()
