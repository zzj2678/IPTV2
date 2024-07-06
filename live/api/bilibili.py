import logging
from typing import Optional
from .base import BaseChannel
from live.util.http import get_json

logger = logging.getLogger(__name__)

class BiliBili(BaseChannel):

    async def get_play_url(self, video_id: str) -> Optional[str]:
        params = {
            "room_id": video_id,
            "protocol": "0,1",
            "format": "0,1,2",
            "codec": "0,1",
            "qn": "10000",
            "platform": "web",
            "ptype": "8"
        }
        json_data = await get_json("https://api.live.bilibili.com/xlive/web-room/v2/index/getRoomPlayInfo", params=params)

        streams = json_data.get("data", {}).get("playurl_info", {}).get("playurl", {}).get("stream", [])
        for stream in streams:
            formats = stream.get("format", [])
            for fmt in formats:
                if fmt.get("format_name") == "ts":
                    last_fmt = fmt["codec"][-1]
                    base_url = last_fmt["base_url"]
                    url_info = last_fmt["url_info"]
                    for idx, info in enumerate(url_info):
                        if idx == 0:
                            host = info["host"]
                            extra = info["extra"]
                            return f"{host}{base_url}{extra}"
        return None

site = BiliBili()
