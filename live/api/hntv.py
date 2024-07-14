import hashlib
import logging
import time
from typing import Optional

from live.api.base import BaseChannel
from live.util.http.http import get_json

logger = logging.getLogger(__name__)

CHANNEL_MAPPING = {
    "hnws": 145,  # 河南卫视
    "hnds": 141,  # 河南都市
    "hnms": 146,  # 河南民生
    "hmfz": 147,  # 河南法治
    "hndsj": 148,  # 河南电视剧
    "hnxw": 149,  # 河南新闻
    "htgw": 150,  # 欢腾购物
    "hngg": 151,  # 河南公共
    "hnxc": 152,  # 河南乡村
    "hngj": 153,  # 河南国际
    "hnly": 154,  # 河南梨园
    "wwbk": 155,  # 文物宝库
    "wspd": 156,  # 武术世界
    "jczy": 157,  # 睛彩中原
    "ydxj": 163,  # 移动戏曲
    "xsj": 183,  # 象视界
    "gxpd": 194,  # 国学频道
}


class HNTV(BaseChannel):
    async def get_play_url(self, video_id: str) -> Optional[str]:
        if video_id not in CHANNEL_MAPPING:
            logger.error(f"Invalid Video ID: {video_id}")
            return None

        timestamp = int(time.time())
        sign = hashlib.sha256(f"6ca114a836ac7d73{timestamp}".encode()).hexdigest()
        headers = {"timestamp": str(timestamp), "sign": sign}

        data = await get_json("https://pubmod.hntv.tv/program/getAuth/live/class/xiaobeibi/11", headers=headers)

        print(data)

        play_url = next(
            (item["video_streams"][0] for item in data if item["cid"] == CHANNEL_MAPPING[video_id]), None
        )

        return play_url


site = HNTV()
