import logging
import json
import urllib.parse
from typing import Optional
from .base import BaseChannel
from util.http import get_json
import cloudscraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

logger = logging.getLogger(__name__)

CHANNEL_MAPPING = {
    "JUHD": "2c045f5adb26d391cc41cd01f00416fa:fc146771a9b096fc4cb57ffe769861be",  # 翡翠台超高清
    "J": "0958b9c657622c465a6205eb2252b8ed:2d2fd7b1661b1e28de38268872b48480",  # 翡翠台
    "B": "56603b65fa1d7383b6ef0e73b9ae69fa:5d9d8e957d2e45d8189a56fe8665aaaa",  # TVB plus
    "P": "e04facdd91354deee318c674993b74c1:8f97a629de680af93a652c3102b65898",  # 明珠台
    "CWIN": "0737b75ee8906c00bb7bb8f666da72a0:15f515458cdb5107452f943a111cbe89",  # Super Free
    "TVG": "8fe3db1a24969694ae3447f26473eb9f:5cce95833568b9e322f17c61387b306f",  # 黃金翡翠台
    "C": "90a0bd01d9f6cbb39839cd9b68fc26bc:51546d1f2af0547f0e961995b60a32a1",  # 無綫新聞台
    "CTVE": "6fa0e47750b5e2fb6adf9b9a0ac431a3:a256220e6c2beaa82f4ca5fba4ec1f95",  # 娛樂新聞台
    "PCC": "7bca0771ba9205edb5d467ce2fdf0162:eb19c7e3cea34dc90645e33f983b15ab",  # 鳳凰衛視中文台
    "PIN": "83f7d313adfc0a5b978b9efa0421ce25:ecdc8065a46287bfb58e9f765e4eec2b",  # 鳳凰衛視資訊台
    "PHK": "cde62e1056eb3615dab7a3efd83f5eb4:b8685fbecf772e64154630829cf330a3",  # 鳳凰衛視香港台
    "CC1": "e50b18fee7cab76b9f2822e2ade8773a:2e2e8602b6d835ccf10ee56a9a7d91a2",  # 中央電視台綜合頻道 (港澳版)
    "CRE": "adef00c5ba927d01642b1e6f3cedc9fb:b45d912fec43b5bbd418ea7ea1fbcb60",  # 創世電視
}


class MyTvSuper(BaseChannel):
    def __init__(self):
        self.api_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJib3NzX2lkIjoiODUwNDY0NTgwIiwiZGV2aWNlX3Rva2VuIjoiWHp6anMzYTVKTms2TFpnZmJQeFZHR2QzIiwiZGV2aWNlX2lkIjoiTldGalptSmxNREF0TkRJNU5TMDBaakV3TFRrNFl6QXRNbUkwT0RCbFpXRTJaVEV3IiwiZGV2aWNlX3R5cGUiOiJ3ZWIiLCJkZXZpY2Vfb3MiOiJicm93c2VyIiwiZHJtX2lkIjoiTldGalptSmxNREF0TkRJNU5TMDBaakV3TFRrNFl6QXRNbUkwT0RCbFpXRTJaVEV3IiwiZXh0cmEiOnsicHJvZmlsZV9pZCI6MX0sImlhdCI6MTcwOTgwNTA3NywiZXhwIjoxNzA5ODA4Njc3fQ.XG-C6gWxLgbBRQ3ttKn68AKMQLOg6SxTpbmHxXl_qI2dbjd1eFFmwB9kD1yd2N_X8HxLPBwJukD4lygIKxbBGrQQDY_1vNd76TldllaeE2BC3fUtc-kAFOU4JwbUkfFYsWVm3v2JP-YGM2GGlhFqN_3170WDAi2Gq-R0tZckeFNWk7jOSShqkE0E7L3eqJ09sDG76R-PCbdpnCIxaY_NXtoYRfIoVQZA9QysExUyO6hQGUxLaTvJDtflX_ZM3OiqTMndHp1p0cDsINnpFokD6Yby5XS18RjQ-Dn1XJznj7-sRjlaGgyIIBoJjxsR2oD5S8teA5S6x7w3Dv6uTO3bWVV9J60E6jguGVqKnSYJ4Rx8A1TgyUTT_g57key6UFIiEhkHYqk7s3H01V-lHffNp5zDo9UrCdaO6maW_ZeA85ohR6P1PMh9EakQ5A-vok60s2oqyokKHfyrQvcodsI-MTC9mKegjJzgV2-HBgyylyj6B2ewvE4icDD25UdspWgbc33NrRpe_kgPxgVKF4cgKCD-S1AT3WrOaqKnPfPvhqmlciwlpZrUqZg09BqcazWPoyWAp2nqf93H6tlDqMrtAQgvft3Nd8-cM7jYx-WvzqRrCRpZ8vRSv11UdezKzR2Jm4H64KTWbs3GxB5vboZaeypdEzQW6PipPpftqRnNMQU"  # Replace with your actual API token

    async def get_channel(self, channel_code):
        url = "https://user-api.mytvsuper.com/v1/channel/checkout"
        params = {"platform": "android_tv", "network_code": channel_code}
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + self.api_token,
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Host": "user-api.mytvsuper.com",
            "Origin": "https://www.mytvsuper.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.2 Safari/605.1.15",
            "Referer": "https://www.mytvsuper.com/",
            "X-Forwarded-For": "210.6.4.148",  # 香港原生IP  210.6.4.148
        }
        return await get_json(url, params=params, headers=headers)

    async def get_play_url(self, video_id: str) -> Optional[str]:
        logger.info(f"Processing request for video ID: {video_id}")

        if video_id not in CHANNEL_MAPPING:
            logger.error(f"Invalid Video ID: {video_id}")
            return None

        data = await self.get_channel(video_id)
        profiles = data.get("profiles", [])

        play_url = ""
        for profile in profiles:
            if profile.get("quality") == "high":
                play_url = profile.get("streaming_path", "")
                break

        play_url = play_url.split("&p=")[0]

        license_key = CHANNEL_MAPPING[video_id]

        m3u_content = f"#EXTM3U\n"
        m3u_content += f"#EXTINF:-1\n"
        m3u_content += "#KODIPROP:inputstream.adaptive.manifest_type=mpd\n"
        m3u_content += "#KODIPROP:inputstream.adaptive.license_type=clearkey\n"
        m3u_content += f"#KODIPROP:inputstream.adaptive.license_key=https://h2j.860775.xyz/{license_key}\n"
        m3u_content += f"{play_url}\n"

        return m3u_content


site = MyTvSuper()
