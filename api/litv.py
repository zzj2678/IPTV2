import logging
from typing import Optional
from .base import BaseChannel
import time
import os

logger = logging.getLogger(__name__)

CHANNEL_MAPPING = {
    '4gtv-4gtv001': [1, 6],
    '4gtv-4gtv003': [1, 6],
    '4gtv-4gtv004': [1, 8],
    '4gtv-4gtv006': [1, 9],
    '4gtv-4gtv009': [2, 7],
    '4gtv-4gtv010': [1, 2],
    '4gtv-4gtv011': [1, 6],
    '4gtv-4gtv013': [1, 2],
    '4gtv-4gtv014': [1, 5],
    '4gtv-4gtv018': [1, 10],
    '4gtv-4gtv034': [1, 6],
    '4gtv-4gtv039': [1, 7],
    '4gtv-4gtv040': [1, 6],
    '4gtv-4gtv041': [1, 6],
    '4gtv-4gtv042': [1, 6],
    '4gtv-4gtv043': [1, 6],
    '4gtv-4gtv044': [1, 8],
    '4gtv-4gtv045': [1, 6],
    '4gtv-4gtv046': [1, 8],
    '4gtv-4gtv047': [1, 8],
    '4gtv-4gtv048': [1, 2],
    '4gtv-4gtv049': [1, 8],
    '4gtv-4gtv051': [1, 6],
    '4gtv-4gtv052': [1, 8],
    '4gtv-4gtv053': [1, 8],
    '4gtv-4gtv054': [1, 8],
    '4gtv-4gtv055': [1, 8],
    '4gtv-4gtv056': [1, 2],
    '4gtv-4gtv057': [1, 8],
    '4gtv-4gtv058': [1, 8],
    '4gtv-4gtv059': [1, 6],
    '4gtv-4gtv061': [1, 7],
    '4gtv-4gtv062': [1, 8],
    '4gtv-4gtv063': [1, 6],
    '4gtv-4gtv064': [1, 8],
    '4gtv-4gtv065': [1, 8],
    '4gtv-4gtv066': [1, 2],
    '4gtv-4gtv067': [1, 8],
    '4gtv-4gtv068': [1, 7],
    '4gtv-4gtv070': [1, 7],
    '4gtv-4gtv072': [1, 2],
    '4gtv-4gtv073': [1, 8],
    '4gtv-4gtv074': [1, 8],
    '4gtv-4gtv076': [1, 2],
    '4gtv-4gtv077': [1, 7],
    '4gtv-4gtv079': [1, 2],
    '4gtv-4gtv080': [1, 5],
    '4gtv-4gtv082': [1, 7],
    '4gtv-4gtv083': [1, 6],
    '4gtv-4gtv084': [1, 6],
    '4gtv-4gtv085': [1, 5],
    '4gtv-4gtv101': [1, 6],
    '4gtv-4gtv102': [1, 6],
    '4gtv-4gtv103': [1, 6],
    '4gtv-4gtv104': [1, 7],
    '4gtv-4gtv109': [1, 7],
    '4gtv-4gtv152': [1, 6],
    '4gtv-4gtv153': [1, 6],
    '4gtv-4gtv155': [1, 6],
    'litv-ftv03': [1, 7],
    'litv-ftv07': [1, 7],
    'litv-ftv09': [1, 7],
    'litv-ftv10': [1, 7],
    'litv-ftv13': [1, 7],
    'litv-ftv15': [1, 7],
    'litv-ftv16': [1, 2],
    'litv-ftv17': [1, 2],
    'litv-longturn01': [4, 2],
    'litv-longturn03': [5, 2],
    'litv-longturn04': [5, 2],
    'litv-longturn05': [5, 2],
    'litv-longturn06': [5, 2],
    'litv-longturn07': [5, 2],
    'litv-longturn08': [5, 2],
    'litv-longturn09': [5, 2],
    'litv-longturn10': [5, 2],
    'litv-longturn11': [5, 2],
    'litv-longturn12': [5, 2],
    'litv-longturn13': [4, 2],
    'litv-longturn14': [1, 6],
    'litv-longturn15': [5, 2],
    'litv-longturn17': [5, 2],
    'litv-longturn18': [5, 2],
    'litv-longturn19': [5, 2],
    'litv-longturn20': [5, 2],
    'litv-longturn21': [5, 2],
    'litv-longturn23': [5, 2]
}

class G4TV(BaseChannel):
    def __init__(self):
        pass

    async def get_play_url(self, video_id: str) -> Optional[str]:
        timestamp = int(time.time() / 4 - 355017625)
        t = timestamp * 4

        playlist = "#EXTM3U\n"
        playlist += "#EXT-X-VERSION:3\n"
        playlist += "#EXT-X-TARGETDURATION:4\n"
        playlist += f"#EXT-X-MEDIA-SEQUENCE:{timestamp}\n"

        for i in range(3):
            playlist += "#EXTINF:4,\n"
            playlist += f"{os.getenv('PROXY_URL', '')}/data/litvpc-hichannel.cdn.hinet.net:443/live/pool/{video_id}/litv-pc/{video_id}-avc1_6000000={CHANNEL_MAPPING[video_id][0]}-mp4a_134000_zho={CHANNEL_MAPPING[video_id][1]}-begin={t}0000000-dur=40000000-seq={timestamp}.ts\n"
            timestamp += 1
            t += 4

        return playlist

site = G4TV()
