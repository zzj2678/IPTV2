import logging
import hashlib
import time
import re
from typing import Optional
from .base import BaseChannel
from utils.http import get_json, get_text, post_json
from urllib.parse import urlparse
import os
from utils.m3u8 import update_m3u8_content
from utils.crypto import md5
from utils.match import match1

logger = logging.getLogger(__name__)

def get_sign(rid, did, tt, js_enc):
    v = match1(js_enc, r'var vdwdae325w_64we = "(\d+)"')
    rb = md5(str(rid) + str(did) + str(tt) + v)

    from node_vm2 import VM

    js_enc = re.sub(r"eval\(strc\).*?;", "strc;", js_enc)
    with VM() as vm:
        js_enc = vm.run(js_enc + "ub98484234()")

    js_enc = re.sub(r"\(function \(", "function ub98484234(", js_enc)
    js_enc = re.sub(r"var rb=.*?;", f"var rb='{rb}';", js_enc)
    js_enc = re.sub(r"return rt;}[\s\S]*", "return rt;};", js_enc)
    with VM() as vm:
        data = vm.run(js_enc + f"ub98484234({rid}, {did}, {tt})")

    return {
        # 'v': match1(data, 'v=(\d+)'),
        "v": v,
        "did": did,
        "tt": tt,
        "sign": match1(data, "sign=(\w{32})"),
    }


async def get_h5enc(html, vid):
    js_enc = match1(html, "(var vdwdae325w_64we =[\s\S]+?)\s*</script>")
    if js_enc is None or "ub98484234(" not in js_enc:
        data = await get_json(
            "https://www.douyu.com/swf_api/homeH5Enc", params={"rids": vid}
        )

        if data["error"] != 0:
            raise InternalException(message=data["msg"])
        js_enc = data["data"]["room" + vid]

    return js_enc


async def get_sign_params(html, vid, did="10000000000000000000000000001501"):
    tt = str(int(time.time()))
    js_enc = await get_h5enc(html, vid)

    return get_sign(vid, did, tt, js_enc)

class DouYu(BaseChannel):
    headers = {"Referer": "https://www.douyu.com"}

    did = "10000000000000000000000000001501"

    async def get_play_url(self, video_id: str) -> Optional[str]:
        html = await get_text(f'https://www.douyu.com/{video_id}', headers=self.headers)

        params = await get_sign_params(html, video_id, self.did)
        params.update(
            {
                "cdn": "",
                "rate": 0,
                "ver": "Douyu_222060105",
                "iar": 0,
                "ive": 0,
                "hevc": 0,
                "fa": 0,
            }
        )

        json_data = await post_json(
            f"https://www.douyu.com/lapi/live/getH5Play/{video_id}",
            data=params,
        )

        if json_data["error"]:
            print(json_data)
            return None

        data = json_data["data"]

        rate = data["rate"]
        rtmp_url = data["rtmp_url"]
        rtmp_live = data["rtmp_live"]
        url = "/".join([rtmp_url, rtmp_live])

        return url

site = DouYu()
