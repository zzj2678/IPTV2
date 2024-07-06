import logging
from typing import Optional
from .base import BaseChannel
import time
import os

logger = logging.getLogger(__name__)

# 一般来说没声音调节第二个参数就行，从1-10
CHANNEL_MAPPING = {
    '4gtv-4gtv001': [1, 6],  # 民視台灣台
    '4gtv-4gtv002': [1, 10], # 民視
    '4gtv-4gtv003': [1, 6],  # 民視第一台
    '4gtv-4gtv004': [1, 8],  # 民視綜藝
    '4gtv-4gtv006': [1, 9],  # 豬哥亮歌廳秀
    '4gtv-4gtv009': [2, 7],  # 中天新聞
    '4gtv-4gtv010': [1, 2],  # 非凡新聞
    '4gtv-4gtv011': [1, 6],  # 影迷數位電影台
    '4gtv-4gtv013': [1, 2],  # 視納華仁紀實頻道
    '4gtv-4gtv014': [1, 5],  # 時尚運動X
    '4gtv-4gtv016': [1, 6],  # GLOBETROTTER
    '4gtv-4gtv017': [1, 6],  # AMC電影台
    '4gtv-4gtv018': [1, 10], # 達文西頻道
    '4gtv-4gtv034': [1, 6],  # 八大精彩台
    '4gtv-4gtv039': [1, 7],  # 八大綜藝台
    '4gtv-4gtv040': [1, 6],  # 中視
    '4gtv-4gtv041': [1, 6],  # 華視
    '4gtv-4gtv042': [1, 6],  # 公視戲劇
    '4gtv-4gtv043': [1, 6],  # 客家電視台
    '4gtv-4gtv044': [1, 8],  # 靖天卡通台
    '4gtv-4gtv045': [1, 6],  # 靖洋戲劇台
    '4gtv-4gtv046': [1, 8],  # 靖天綜合台
    '4gtv-4gtv047': [1, 8],  # 靖天日本台
    '4gtv-4gtv048': [1, 2],  # 非凡商業
    '4gtv-4gtv049': [1, 8],  # 采昌影劇
    '4gtv-4gtv051': [1, 6],  # 台視新聞
    '4gtv-4gtv052': [1, 8],  # 華視新聞
    '4gtv-4gtv053': [1, 8],  # GINX TV
    '4gtv-4gtv054': [1, 8],  # 靖天歡樂台
    '4gtv-4gtv055': [1, 8],  # 靖天映畫
    '4gtv-4gtv056': [1, 2],  # 台視財經
    '4gtv-4gtv057': [1, 8],  # 靖洋卡通台
    '4gtv-4gtv058': [1, 8],  # 靖天戲劇台
    '4gtv-4gtv059': [1, 6],  # 古典音樂台
    '4gtv-4gtv061': [1, 7],  # 靖天電影台
    '4gtv-4gtv062': [1, 8],  # 靖天育樂台
    '4gtv-4gtv063': [1, 6],  # 靖天國際台
    '4gtv-4gtv064': [1, 8],  # 中視菁采
    '4gtv-4gtv065': [1, 8],  # 靖天資訊台
    '4gtv-4gtv066': [1, 2],  # 台視
    '4gtv-4gtv067': [1, 8],  # TVBS精采台
    '4gtv-4gtv068': [1, 7],  # TVBS歡樂台
    '4gtv-4gtv070': [1, 7],  # 愛爾達娛樂
    '4gtv-4gtv072': [1, 2],  # TVBS新聞台
    '4gtv-4gtv073': [1, 8],  # TVBS
    '4gtv-4gtv074': [1, 8],  # 中視新聞
    '4gtv-4gtv075': [1, 6],  # 鏡新聞
    '4gtv-4gtv076': [1, 2],  # CATCHPLAY電影台
    '4gtv-4gtv077': [1, 7],  # TRACE SPORTS STARS
    '4gtv-4gtv079': [1, 2],  # 阿里郎
    '4gtv-4gtv080': [1, 5],  # 中視經典
    '4gtv-4gtv082': [1, 7],  # TRACE URBAN
    '4gtv-4gtv083': [1, 6],  # MEZZO LIVE
    '4gtv-4gtv084': [1, 6],  # 國會頻道1
    '4gtv-4gtv085': [1, 5],  # 國會頻道2
    '4gtv-4gtv101': [1, 6],  # 智林體育台
    '4gtv-4gtv104': [1, 7],  # 國際財經
    '4gtv-4gtv109': [1, 7],  # 第1商業台
    '4gtv-4gtv152': [1, 6],  # 東森新聞
    '4gtv-4gtv153': [1, 6],  # 東森財經新聞
    '4gtv-4gtv155': [1, 6],  # 民視
    '4gtv-4gtv156': [1, 2],  # 民視台灣台
    'litv-ftv03': [1, 7],    # 美國之音
    'litv-ftv07': [1, 7],    # 民視旅遊
    'litv-ftv09': [1, 7],    # 民視影劇
    'litv-ftv10': [1, 7],    # 半島新聞
    'litv-ftv13': [1, 7],    # 民視新聞台
    'litv-ftv15': [1, 7],    # 愛放動漫
    'litv-ftv16': [1, 2],    # 好消息
    'litv-ftv17': [1, 2],    # 好消息2台
    'litv-longturn01': [4, 2], # 龍華卡通
    'litv-longturn03': [5, 2], # 龍華電影
    'litv-longturn04': [5, 2], # 博斯魅力
    'litv-longturn05': [5, 2], # 博斯高球1
    'litv-longturn06': [5, 2], # 博斯高球2
    'litv-longturn07': [5, 2], # 博斯運動1
    'litv-longturn08': [5, 2], # 博斯運動2
    'litv-longturn09': [5, 2], # 博斯網球
    'litv-longturn10': [5, 2], # 博斯無限
    'litv-longturn11': [5, 2], # 龍華日韓
    'litv-longturn12': [5, 2], # 龍華偶像
    'litv-longturn13': [4, 2], # 博斯無限2
    'litv-longturn14': [1, 6], # 寰宇新聞台
    'litv-longturn15': [5, 2], # 寰宇新聞台灣台
    'litv-longturn17': [5, 2], # 亞洲旅遊台
    'litv-longturn18': [5, 2], # 龍華戲劇
    'litv-longturn19': [5, 2], # Smart知識台
    'litv-longturn20': [5, 2], # 生活英語台
    'litv-longturn21': [5, 2], # 龍華經典
    'litv-longturn22': [5, 2], # 台灣戲劇台
    'litv-longturn23': [5, 2], # 寰宇財經台
}

class G4TV(BaseChannel):
    def __init__(self):
        pass

    async def get_play_url(self, video_id: str) -> Optional[str]:
        if video_id not in CHANNEL_MAPPING:
            logger.error(f"Invalid Video ID: {video_id}")
            return None

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
