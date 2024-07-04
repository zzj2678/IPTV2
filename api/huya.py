import logging
from typing import Optional
from .base import BaseChannel
from utils.http import get_json, post_json, get_text
import json
import base64
import hashlib
import random
import re
import time
from html import unescape
from urllib.parse import urljoin, urlencode, parse_qsl
from utils.match import match1

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

        reSecret = not screenType and liveSourceType in (0, 8, 13)
        if reSecret:
            params.setdefault("t", "100")  # 102
            ct = int(params["wsTime"], 16) + random.random()
            lPresenterUid = vStreamInfo["lPresenterUid"]
            if not sStreamName.startswith(str(lPresenterUid)):
                uid = lPresenterUid
            else:
                uid = int(ct % 1e7 * 1e6 % 0xFFFFFFFF)
            u1 = uid & 0xFFFFFFFF00000000
            u2 = uid & 0xFFFFFFFF
            u3 = uid & 0xFFFFFF
            u = u1 | u2 >> 24 | u3 << 8
            params.update(
                {
                    "u": str(u),
                    "seqid": str(int(ct * 1000) + uid),
                    "ver": "1",
                    "uuid": int(ct % 1e7 * 1e6 % 0xFFFFFFFF),
                }
            )
            fm = base64.b64decode(params["fm"]).decode().split("_", 1)[0]
            ss = hash.md5("|".join([params["seqid"], params["ctype"], params["t"]]))

        if reSecret:
            params["wsSecret"] = hash.md5("_".join([fm, params["u"], sStreamName, ss, params["wsTime"]]))

        url = base_url + urlencode(params, safe="*")

        return url

    async def get_play_url(self, video_id):
        headers = {
            "referer": "https://www.huya.com/",
        }

        html = await get_text(f'https://www.huya.com/{video_id}', headers=headers)

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

        # gameStreamInfo = next((stream for stream in gameStreamInfoList if stream["sCdnType"] == "HS"), None)

        return self.get_url(gameStreamInfoList[0], vMultiStreamInfo, screenType, liveSourceType)

site = Huya()