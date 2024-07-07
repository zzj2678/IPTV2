import logging
from typing import Optional

from live.util.m3u8 import update_m3u8_content

from .base import BaseChannel
from live.util.http import get_json, post_json, get_text
import base64
import hashlib
import time
from datetime import datetime
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

logger = logging.getLogger(__name__)


def rsa_decrypt(encrypted_data: str, public_key_pem: str) -> str:
    ciphertext = base64.b64decode(encrypted_data)
    public_key = RSA.import_key(public_key_pem)
    n, e = public_key.n, public_key.e
    key_length = (n.bit_length() + 7) // 8

    decrypted_bytes = b""
    for i in range(0, len(ciphertext), key_length):
        block = ciphertext[i:i + key_length]
        decrypted_int = pow(int.from_bytes(block, byteorder='big'), e, n)
        decrypted_block = decrypted_int.to_bytes((decrypted_int.bit_length() + 7) // 8, byteorder='big')
        padding_index = decrypted_block.find(b'\x00', 2)
        decrypted_bytes += decrypted_block[padding_index + 1:]

    return decrypted_bytes.decode('utf-8')

CHANNEL_MAPPING = {
    'dfws': 1,  # 东方卫视
    'shxwzh': 2,  # 上海新闻综合
    'shics': 3,  # 上海ics
    'shds': 4,  # 上海都市
    'dycj': 5,  # 第1财经
    'jsrw': 6,  # 上海纪实人文
    'hhxd': 9,  # 哈哈炫动
}

def get_nonce(length):
    base36 = base64.b32encode(bytearray(str(time.time()), 'utf-8')).decode('utf-8').lower().replace('=', '')
    return base36[:length]

def get_signature(params, secret_key):
    sign_str = '&'.join([f"{k}={v}" for k, v in sorted(params.items())]) + f"&{secret_key}"
    return hashlib.md5(hashlib.md5(sign_str.encode('utf-8')).hexdigest().encode('utf-8')).hexdigest()

class KankanNews(BaseChannel):
    secret_key = "28c8edde3d61a0411511d3b1866f0636"

    public_key = """-----BEGIN PUBLIC KEY-----
    MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDP5hzPUW5RFeE2xBT1ERB3hHZI
    Votn/qatWhgc1eZof09qKjElFN6Nma461ZAwGpX4aezKP8Adh4WJj4u2O54xCXDt
    wzKRqZO2oNZkuNmF2Va8kLgiEQAAcxYc8JgTN+uQQNpsep4n/o1sArTJooZIF17E
    tSqSgXDcJ7yDj5rc7wIDAQAB
    -----END PUBLIC KEY-----"""

    headers = {
            "referer": "https://live.kankanews.com/",
    }

    async def get_programs(self, channel_id):
        tm = str(time.time())
        date =  datetime.now().strftime('%Y-%m-%d')
        nonce = get_nonce(8)
        params = {
            'Api-Version': 'v1',
            'channel_id': channel_id,
            'date': date,
            'nonce': nonce,
            'platform': 'pc',
            'timestamp': tm,
            'version': 'v2.9.4',
        }

        sign = get_signature(params, self.secret_key)
        headers = {
            "api-version": "v1",
            "nonce": nonce,
            "m-uuid": "p8SxKgKBySMALI6mGICre",
            "platform": "pc",
            "version": "v2.9.4",
            "timestamp": tm,
            "referer": "https://live.kankanews.com/",
            "sign": sign,
        }

        url = f"https://kapi.kankanews.com/content/pc/tv/programs?channel_id={channel_id}&date={date}"
        json_data = await get_json(url, params=params, headers=headers)

        return json_data['result']['programs']

    def get_current_program_id(self, programs):
        current_time = time.time()
        for program in programs:
            if program['start_time'] < current_time < program['end_time']:
                return program['id']
            
        return None

    async def get_program_detail(self, channel_id, channel_program_id):
        tm = str(time.time())
        nonce = get_nonce(8)
        params = {
            'Api-Version': 'v1',
            'channel_id': channel_id,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'nonce': nonce,
            'platform': 'pc',
            'timestamp': tm,
            'version': 'v2.9.4',
            'channel_program_id': channel_program_id
        }

        sign = get_signature(params, self.secret_key)
        headers = {
            "api-version": "v1",
            "nonce": nonce,
            "m-uuid": "p8SxKgKBySMALI6mGICre",
            "platform": "pc",
            "version": "v2.9.4",
            "timestamp": tm,
            "referer": "https://live.kankanews.com/",
            "sign": sign,
        }

        url = f"https://kapi.kankanews.com/content/pc/tv/program/detail?channel_program_id={channel_program_id}"
        json_data = await get_json(url, params=params, headers=headers)
        return json_data

    async def get_play_url(self, video_id: str) -> Optional[str]:
        channel_id = CHANNEL_MAPPING.get(video_id)
        if not channel_id:
            logger.error(f"Invalid video_id: {video_id}")
            return None

        programs = await self.get_programs(channel_id)
        if not programs:
            logger.error(f"No programs found for channel_id: {channel_id}")
            return None

        channel_program_id = self.get_current_program_id(programs)
        if channel_program_id is None:
            logger.error("No current program found")
            return None

        data = await self.get_program_detail(channel_id, channel_program_id)
        live_address = data['result']['channel_info']['live_address']

        url = rsa_decrypt(live_address, self.public_key)
        m3u8_content = await get_text(url, headers=self.headers)
        modified_m3u8_content = update_m3u8_content(url, m3u8_content)

        return modified_m3u8_content

site = KankanNews()
