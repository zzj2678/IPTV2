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

    def sign(*args):
        from node_vm2 import NodeVM
        with NodeVM.code(js_source) as module:
            return module.call_member("sign", *args)

    # def sign(url):
    #     import dukpy
    #     context = {
    #         "url": url
    #     }
    #     signature = dukpy.evaljs(js_source, context)
    #     return signature


    return sign

class DouYin(BaseChannel):
    headers = {
        'Referer': 'https://live.douyin.com/'
    }

    async def get_cookie(self, url):
        cookies = await get_cookies(url)

        __ac_nonce = cookies["__ac_nonce"].value
        # __ac_signature = get_signature(url)("", __ac_nonce)

        return {
            "__ac_nonce": __ac_nonce,
            # "__ac_signature": __ac_signature,
            # "__ac_referer": "__ac_blank",
        }

    async def get_play_url(self, video_id: str) -> Optional[str]:
        url = f"https://live.douyin.com/{video_id}"

        cookies = await self.get_cookie(url)

        print(cookies)

        # html = await get_text(
        #     url,
        #     headers={"refer": url},
        #     cookies=cookies,
        # )
        # data = match1(
        #     html,
        #     'id="RENDER_DATA" type="application/json">(.+?)</script>',
        #     "__INIT_PROPS__ = (.+?)</script>",
        # )

        # data = json.loads(unquote(data))
        # data = data["app"]

        # print(data)

        url = f"https://live.douyin.com/webcast/room/web/enter/?aid=6383&app_name=douyin_web&live_id=1&device_platform=web&language=zh-CN&enter_from=web_live&cookie_enabled=true&screen_width=1728&screen_height=1117&browser_language=zh-CN&browser_platform=MacIntel&browser_name=Chrome&browser_version=116.0.0.0&web_rid={video_id}"
        # url = f"https://live.douyin.com/webcast/room/web/enter/?aid=6383&app_name=douyin_web&live_id=1&device_platform=web&language=zh-CN&enter_from=web_live&cookie_enabled=true&screen_width=1728&screen_height=1117&browser_language=zh-CN&browser_platform=MacIntel&browser_name=Chrome&browser_version=126.0.0.0&web_rid={video_id}&room_id_str=7388500915256380186&enter_source=&is_need_double_stream=false&insert_task_id=&live_reason=&a_bogus=mX8M%2FfwkdDgBDf6D5f9LfY3q6Ar3YQjI0tLVMD2fkn3WQ639HMYd9exLZNGvbRmjNs%2FDIb6jy4hSYNHMicIjA3v6HSRKl2Ck-g00t-P2so0j5ZhjCfuDrURF-vzWt-Bd-Jd3ic4Qy7dbFuRplnAJ5k1cthMeafE%3D"
        
        json_data = await get_json(url, headers=self.headers, cookies=cookies)

        print(json_data)

        # status = json_data.get("data", {}).get("data", [])[0].get("status")
        # if status != 2:
        #     return None

        # stream_data = json_data.get("data", {}).get("data", [])[0].get("stream_url", {}).get("live_core_sdk_data", {}).get("pull_data", {}).get("stream_data", [])
        # for stream in stream_data:
        #     if "data" in stream and "origin" in stream["data"]:
        #         return stream["data"]["origin"]["main"]["flv"]

        return None



site = DouYin()
