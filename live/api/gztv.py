import logging
from typing import Optional
from .base import BaseChannel
from live.util.http import get_json

logger = logging.getLogger(__name__)

CHANNEL_MAPPING = {
    "zhonghe": "31",  # 广州综合
    "xinwen": "32",  # 广州新闻
    "jingsai": "35",  # 广州竞赛
    "yingshi": "36",  # 广州影视
    "fazhi": "34",  # 广州法治
    "shenghuo": "33",  # 广州南国都市
}


class GZTV(BaseChannel):
    async def get_live_channel_list(self):
        url = "https://gzbn.gztv.com:7443/plus-cloud-manage-app/liveChannel/queryLiveChannelList?type=1"
        logger.info(f"Fetching live channel list from: {url}")
        json_data = await get_json(url)
        return json_data.get("data", [])

    async def get_play_url(self, video_id: str) -> Optional[str]:
        logger.info(f"Processing request for video ID: {video_id}")

        if video_id not in CHANNEL_MAPPING:
            logger.error(f"Invalid Video ID: {video_id}")
            return None

        station_number = CHANNEL_MAPPING[video_id]

        channel_data = await self.get_live_channel_list()

        play_url = next(
            (item.get("httpUrl") for item in channel_data if item.get("stationNumber") == station_number), None
        )

        if play_url is None:
            logger.warning(f"Play URL for video ID {video_id} not found")
            return None

        logger.info(f"Returning Play URL for video {video_id}: {play_url}")

        return play_url


site = GZTV()
