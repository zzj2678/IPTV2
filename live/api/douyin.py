import json
import logging
from typing import Optional
from urllib.parse import unquote

from live.util.match import match1
from .base import BaseChannel
from live.util.http import get_json, get_cookies, fake_headers, get_text
import os


logger = logging.getLogger(__name__)

js_dom = """
var window = this,
    document = {{referrer: '{url}'}},
    location = {{href: '{url}', protocol: 'https'}},
    navigator = {{userAgent: '{ua}'}};
"""


def get_signature(url):
    path = os.path.join(os.path.dirname(__file__), "_byted_acrawler.js")
    with open(path, "r", encoding="utf-8") as f:
        js_source = f.read()

    js_source = f"""{js_dom.format(url=url, ua=fake_headers["User-Agent"])}
                {js_source}
                exports.sign = window.byted_acrawler.sign
                """

    from node_vm2 import NodeVM

    def sign(*args):
        with NodeVM.code(js_source) as module:
            return module.call_member("sign", *args)

    return sign

class DouYin(BaseChannel):

    async def get_cookie(self, url):
        cookies = await get_cookies(url)

        __ac_nonce = cookies["__ac_nonce"].value
        __ac_signature = get_signature(url)("", __ac_nonce)

        return {
            "__ac_nonce": __ac_nonce,
            "__ac_signature": __ac_signature,
            "__ac_referer": "__ac_blank",
        }

    async def get_play_url(self, video_id: str) -> Optional[str]:
        url = f"https://live.douyin.com/{video_id}"

        cookies = await self.get_cookie(url)

        html = await get_text(
            url,
            headers={"refer": url},
            cookies=cookies,
        )
        data = match1(
            html,
            'id="RENDER_DATA" type="application/json">(.+?)</script>',
            "__INIT_PROPS__ = (.+?)</script>",
        )

        data = json.loads(unquote(data))
        data = data["app"]

        print(data)

        # url = f"https://live.douyin.com/webcast/room/web/enter/?aid=6383&app_name=douyin_web&live_id=1&device_platform=web&language=zh-CN&enter_from=web_live&cookie_enabled=true&screen_width=1728&screen_height=1117&browser_language=zh-CN&browser_platform=MacIntel&browser_name=Chrome&browser_version=116.0.0.0&web_rid={video_id}"
        
        # json_data = await get_json(url, cookies=cookies)

        # print(json_data)

        # status = json_data.get("data", {}).get("data", [])[0].get("status")
        # if status != 2:
        #     return None

        # stream_data = json_data.get("data", {}).get("data", [])[0].get("stream_url", {}).get("live_core_sdk_data", {}).get("pull_data", {}).get("stream_data", [])
        # for stream in stream_data:
        #     if "data" in stream and "origin" in stream["data"]:
        #         return stream["data"]["origin"]["main"]["flv"]

        return None



site = DouYin()
