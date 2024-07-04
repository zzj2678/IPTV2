import logging
from typing import Optional
from .base import BaseChannel
from utils.http import get_json, post_json, get_text
from urllib.parse import urlparse
import os

logger = logging.getLogger(__name__)

class AfreecaTv(BaseChannel):
    def __init__(self):
        self.cookie = os.getenv('AFREECATV_COOKIE', 'AbroadChk=OK; AbroadVod=OK; _au=f0b701c93182b6fe93430d2ac51c303f; _ausb=0x346c7023; VodNonLoginCkCnt=0; bjStationHistory=%0217041065; TempCook=.A32.7bbT56vyHM9fKZk.jruLK6BmiT4nvyXJbbkfAA; _ausa=0x708a7a2c; LIN=path_key%3Df0b701c93182b6fe93430d2ac51c303f_243400415_1667293877505%26path1%3Detc')

        self.headers = {
            'Cookie': self.cookie,
            'Referer': 'https://play.afreecatv.com',
        }

    async def get_play_live(self, bid: str, bno: str, type: str):
        url = f'https://live.afreecatv.com/afreeca/player_live_api.php?bjid={bid}'
        data = {
            'bid': bid,
            'bno': bno,
            'type': type,
            'pwd': '',
            'player_type': 'html5',
            'stream_type': 'common',
            'quality': 'original',
            'mode': 'landing',
            'from_api': 0
        }
        logger.debug(f"Requesting play live with data: {data}")
        return await post_json(url, data=data, headers=self.headers)

    async def get_live(self, bid: str):
        logger.debug(f"Getting live stream for bid: {bid}")
        return await self.get_play_live(bid, '', 'live')

    async def get_aid(self, bid: str, bno: str):
        logger.debug(f"Getting aid for bid: {bid} and bno: {bno}")
        return await self.get_play_live(bid, bno, 'aid')

    async def get_stream(self, broad_key: str):
        url = 'https://livestream-manager.afreecatv.com/broad_stream_assign.html'
        params = {
            'return_type': 'gcp_cdn',
            'use_cors': 'true',
            'cors_origin_url': 'play.afreecatv.com',
            'broad_key': f'{broad_key}-common-original-hls',
            'time': ''
        }
        logger.debug(f"Requesting stream with params: {params}")
        return await get_json(url, params=params, headers=self.headers)

    def get_m3u8_content(self, play_url: str, m3u8_content: str) -> str:
        logger.debug("Modifying m3u8 content")

        parsed_url = urlparse(play_url)
        port = parsed_url.port if parsed_url.port else (443 if parsed_url.scheme == 'https' else 80)
        domain_port = f"{parsed_url.hostname}:{port}"
        path = "/".join(parsed_url.path.split('/')[:-1])

        lines = m3u8_content.strip().splitlines()
        modified_lines = []

        for line in lines:
            if line and not line.startswith("#") and not urlparse(line).netloc:
                modified_line = f"/data/{domain_port}{path}/{line}"
                modified_lines.append(modified_line)
            else:
                modified_lines.append(line)

        logger.debug(f"Modified m3u8 content: {modified_lines}")
        return "\n".join(modified_lines)

    async def get_play_url(self, video_id: str) -> Optional[str]:
        logger.info(f"Processing request for video ID: {video_id}")

        live_data = await self.get_live(video_id)
        print(live_data)
        if 'CHANNEL' not in live_data or 'BNO' not in live_data['CHANNEL']:
            logger.warning(f"BNO not found for video ID: {video_id}")
            return None

        bno = live_data['CHANNEL']['BNO']
        logger.debug(f"Retrieved BNO: {bno}")

        aid_data = await self.get_aid(video_id, bno)
        if 'CHANNEL' not in aid_data or 'AID' not in aid_data['CHANNEL']:
            logger.warning(f"AID not found for video ID: {video_id} with BNO: {bno}")
            return None

        aid = aid_data['CHANNEL']['AID']
        logger.debug(f"Retrieved AID: {aid}")

        stream_data = await self.get_stream(bno)
        if 'view_url' not in stream_data:
            logger.warning(f"Stream URL not found for BNO: {bno}")
            return None


        play_url = stream_data['view_url'].replace('https://pc-web.stream.afreecatv.com', 'https://live-global-cdn-v02.afreecatv.com')
        play_url = f'{play_url}?aid={aid}'
        logger.debug(f"Play URL: {play_url}")

        headers = {"Referer": 'https://play.afreecatv.com/'}
        m3u8_content = await get_text(play_url, headers=headers)

        if not m3u8_content:
            logger.warning(f"No content retrieved from {play_url}")
            return None

        m3u8_content = self.get_m3u8_content(play_url, m3u8_content)
        logger.debug(f"Modified m3u8 content: {m3u8_content}")

        return m3u8_content

site = AfreecaTv()
