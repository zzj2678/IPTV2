import json
import logging
import random
from typing import Optional
from .base import BaseChannel
from live.util.http import get_json

logger = logging.getLogger(__name__)

class BiliBili(BaseChannel):
    async def get_play_url(self, video_id: str) -> Optional[str]:
        json_data = await get_json( f"https://api.live.bilibili.com/room/v1/Room/room_init?id={video_id}")

        if json_data["msg"] == "直播间不存在":
            return None
        
        data = json_data.get("data")
        live_status = data.get("live_status")
        if live_status != 1:
            return None
        
        video_id = data["room_id"]

        params = {
            "room_id": video_id,
            "protocol": "0,1",
            "format": "0,1,2",
            "codec": "0,1",
            "qn": "10000",
            "platform": "web",
            "ptype": "8",
            'dolby': 5
        }
        json_data = await get_json("https://api.live.bilibili.com/xlive/web-room/v2/index/getRoomPlayInfo", params=params)

        streams = json_data.get("data", {}).get("playurl_info", {}).get("playurl", {}).get("stream", [])

        for stream in streams:
           for format in stream['format']:
            if format.get("format_name") == "ts":
                for codec in format['codec']:
                    url_info = random.choice(codec['url_info'])
                    return f"{url_info['host']}{codec['base_url']}{url_info['extra']}"
        return None

site = BiliBili()
