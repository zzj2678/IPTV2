import logging
from typing import Optional
from .base import BaseChannel
import json
from urllib.parse import urljoin
import re
import time
from live.util.http import get_json, post_json, get_text
from live.util.match import match1

logger = logging.getLogger(__name__)


class YY(BaseChannel):
    def __init__(self):
        self.headers = {
            "Referer": "https://www.yy.com/"
        }

    async def get_play_url(self, video_id: str) -> Optional[str]:
        headers = {
            "Referer": "https://wap.yy.com",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1"
        }

        html = await get_text(f"https://wap.yy.com/mobileweb/{video_id}", headers=headers)

        rid  = match1(html, r"md5Hash[\s\S]*?sid.*'(.*)'.*?getQuery")

        tm = int(time.time() * 1000)

        data = {
            "head": {
                "seq": tm,
                "appidstr": "0",
                "bidstr": "0",
                "cidstr": rid,
                "sidstr": rid,
                "uid64": 0,
                "client_type": 108,
                "client_ver": "5.14.13",
                "stream_sys_ver": 1,
                "app": "yylive_web",
                "playersdk_ver": "5.14.13",
                "thundersdk_ver": "0",
                "streamsdk_ver": "5.14.13"
            },
            "client_attribute": {
                "client": "web",
                "model": "",
                "cpu": "",
                "graphics_card": "",
                "os": "chrome",
                "osversion": "118.0.0.0",
                "vsdk_version": "",
                "app_identify": "",
                "app_version": "",
                "business": "",
                "width": "1728",
                "height": "1117",
                "scale": "",
                "client_type": 8,
                "h265": 0
            },
            "avp_parameter": {
                "version": 1,
                "client_type": 8,
                "service_type": 0,
                "imsi": 0,
                "send_time": int(time.time()),
                "line_seq": -1,
                "gear": 4,
                "ssl": 1,
                "stream_format": 0
            }
        }

        url = f"https://stream-manager.yy.com/v3/channel/streams?uid=0&cid={rid}&sid={rid}&appid=0&sequence={tm}&encode=json"

        data = await post_json(url, headers=self.headers, data=json.dumps(data))

        if "avp_info_res" in data and "stream_line_addr" in data["avp_info_res"]:
            stream_line_addr = data["avp_info_res"]["stream_line_addr"]
            if stream_line_addr:
                return list(stream_line_addr.values())[0]["cdn_info"]["url"]
            
        return None

site = YY()
