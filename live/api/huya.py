import logging
from typing import Optional
from .base import BaseChannel
from util.http import get_json, post_json, get_text
import json
import base64
import hashlib
import random
import re
import time
from html import unescape
from urllib.parse import urljoin, urlencode, parse_qsl
from util.match import match1


class Huya(BaseChannel):
    def get_url(self, vStreamInfo, vBitRateInfo, screenType, liveSourceType):
        sStreamName = vStreamInfo["sStreamName"]
        sUrl = vStreamInfo["sFlvUrl"]
        sUrlSuffix = vStreamInfo["sFlvUrlSuffix"]
        sAntiCode = vStreamInfo["sFlvAntiCode"]

        # sUrl = vStreamInfo["sHlsUrl"]
        # sUrlSuffix = vStreamInfo["sHlsUrlSuffix"]
        # sAntiCode = vStreamInfo["sHlsAntiCode"]

        base_url = f"{sUrl}/{sStreamName}.{sUrlSuffix}?"
        params = dict(parse_qsl(unescape(sAntiCode)))

        params.setdefault("t", "100")  # 102
        ct = int((int(params["wsTime"], 16) + random.random()) * 1000)
        lPresenterUid = vStreamInfo["lPresenterUid"]
        if liveSourceType and not sStreamName.startswith(str(lPresenterUid)):
            uid = int(lPresenterUid)
        else:
            uid = int(ct % 1e10 * 1e3 % 0xFFFFFFFF)
        u1 = uid & 0xFFFFFFFF00000000
        u2 = uid & 0xFFFFFFFF
        u3 = uid & 0xFFFFFF
        u = u1 | u2 >> 24 | u3 << 8
        params.update(
            {
                "ctype": "tars_mp",  # !!!!
                "u": str(u),
                "seqid": str(ct + uid),
                "ver": "1",
                "uuid": int((ct % 1e10 + random.random()) * 1e3 % 0xFFFFFFFF),
            }
        )
        fm = base64.b64decode(params["fm"]).decode().split("_", 1)[0]
        ss = hashlib.md5("|".join([params["seqid"], params["ctype"], params["t"]]).encode("utf-8")).hexdigest()
        params["wsSecret"] = hashlib.md5(
            "_".join([fm, params["u"], sStreamName, ss, params["wsTime"]]).encode("utf-8")
        ).hexdigest()

        url = base_url + urlencode(params, safe="*")

        url = url.replace("http://", "https://")

        return url

    async def get_play_url(self, video_id):
        headers = {
            "referer": "https://www.huya.com/",
        }

        html = await get_text(f"https://www.huya.com/{video_id}", headers=headers)

        stream = match1(html, "stream: ({.+)\n.*?};")
        if not stream:
            return None
        try:
            data = json.loads(stream)
        except:
            data = json.loads(base64.b64decode(stream).decode())

        vMultiStreamInfo = data["vMultiStreamInfo"]
        data = data["data"][0]
        gameLiveInfo = data["gameLiveInfo"]
        screenType = gameLiveInfo["screenType"]
        liveSourceType = gameLiveInfo["liveSourceType"]
        gameStreamInfoList = data["gameStreamInfoList"]

        print(gameStreamInfoList)

        # gameStreamInfo = next((stream for stream in gameStreamInfoList if stream["sCdnType"] == "HS"), None)

        return self.get_url(gameStreamInfoList[-1], vMultiStreamInfo, screenType, liveSourceType)


site = Huya()
