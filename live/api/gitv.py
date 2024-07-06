import logging
from typing import Optional
from .base import BaseChannel
import json
from urllib.parse import urljoin
from util.http import get_json, post_json, get_text

logger = logging.getLogger(__name__)

CHANNEL_MAPPING = {
    "cctv1": "G_CCTV-1-HQ",  # CCTV1
    "cctv2": "G_CCTV-2-HQ",  # CCTV2
    "cctv3": "G_CCTV-3-HQ",  # CCTV3
    "cctv4": "G_CCTV-4-HQ",  # CCTV4
    "cctv5": "G_CCTV-5-HQ",  # CCTV5
    "cctv6": "G_CCTV-6-HQ",  # CCTV6
    "cctv8": "G_CCTV-8-HQ",  # CCTV8
    "cctv9": "G_CCTV-9-HQ",  # CCTV9
    "cctv10": "G_CCTV-10-HQ",  # CCTV10
    "cctv11": "G_CCTV-11-HQ",  # CCTV11
    "cctv12": "G_CCTV-12-HQ",  # CCTV12
    "cctv13": "G_CCTV-13-HQ",  # CCTV13
    "cctv14": "G_CCTV-14-HQ",  # CCTV14
    "cctv15": "G_CCTV-15",  # CCTV15
    "cetv1": "G_CETV-1-HQ",  # 中国教育1
    "cetv4": "G_CETV-4-HQ",  # 中国教育4
    "bjws": "G_BEIJING-HQ",  # 北京卫视
    "dfws": "G_DONGFANG-HQ",  # 东方卫视
    "tjws": "G_TIANJIN-HQ",  # 天津卫视
    "cqws": "G_CHONGQING-HQ",  # 重庆卫视
    "hljws": "G_HEILONGJIANG-HQ",  # 黑龙江卫视
    "jlws": "G_JILIN-HQ",  # 吉林卫视
    "lnws": "G_LIAONING-HQ",  # 辽宁卫视
    "nmws": "G_NEIMENGGU",  # 内蒙古卫视
    "nxws": "G_NINGXIA",  # 宁夏卫视
    "gsws": "G_GANSU",  # 甘肃卫视
    "qhws": "G_QINGHAI",  # 青海卫视
    "sxws": "G_SHANXI",  # 陕西卫视
    "hbws": "G_HEBEI-HQ",  # 河北卫视
    "sxiws": "SXWS",  # 山西卫视
    "sdws": "G_SHANDONG-HQ",  # 山东卫视
    "ahws": "G_ANHUI-HQ",  # 安徽卫视
    "hnws": "G_HENAN-HQ",  # 河南卫视
    "hubws": "G_HUBEI-HQ",  # 湖北卫视
    "hunws": "G_HUNAN-HQ",  # 湖南卫视
    "jxws": "G_JIANGXI-HQ",  # 江西卫视
    "jsws": "G_JIANGSU-HQ",  # 江苏卫视
    "zjws": "G_ZHEJIANG-HQ",  # 浙江卫视
    "dnws": "G_DONGNAN-HQ",  # 东南卫视
    "gdws": "G_GUANGDONG-HQ",  # 广东卫视
    "szws": "G_SHENZHEN-HQ",  # 深圳卫视
    "gxws": "G_GUANGXI-HQ",  # 广西卫视
    "ynws": "G_YUNNAN",  # 云南卫视
    "gzws": "G_GUIZHOU-HQ",  # 贵州卫视
    "scws": "G_SICHUAN-HQ",  # 四川卫视
    "xjws": "G_XINJIANG",  # 新疆卫视
    "btws": "G_BINGTUAN",  # 兵团卫视
    "xzws": "G_XIZANG",  # 西藏卫视
    "hinws": "G_HAINAN-HQ",  # 海南卫视
    "xdkt": "G_XUANDONG",  # 炫动卡通
    "jyjs": "G_JINYINGJS-HQ",  # 金鹰纪实
    "jykt": "G_JINYING",  # 金鹰卡通
    "jxds": "G_JXDS",  # 江西都市
    "jxjs": "G_JXJJSH",  # 江西经济生活
    "jxys": "G_JXYSLY",  # 江西影视旅游
    "jxgg": "G_JXGGNY",  # 江西公共农业频道
    "jxse": "G_JXSE",  # 江西少儿
    "jxxw": "G_JXXW",  # 江西新闻
    "fsgw": "G_FENGSHANG",  # 风尚购物
    "jxjy": "G_JXJY",  # 江西教育
}


class GITV(BaseChannel):
    async def get_app_token(self) -> Optional[str]:
        url = "https://jx-auth-user.live.gitv.tv/v1/getAppToken"
        headers = {"checksum": "e4b13e6cb63bf456e4f42e44c238f01a"}
        data = {"partnerCode": "JXXMT", "timestamp": "1710725285"}
        json_data = await post_json(url, json=data, headers=headers)
        return json_data.get("data", {}).get("token")

    async def get_play_url(self, video_id: str) -> Optional[str]:
        if video_id not in CHANNEL_MAPPING:
            logger.error(f"Invalid Video ID: {video_id}")
            return None

        token = await self.get_app_token()
        if not token:
            logger.error("Failed to get app token")
            return None

        url = f"https://jxcbn.live.gitv.tv/gitv_live/{CHANNEL_MAPPING[video_id]}/{CHANNEL_MAPPING[video_id]}.m3u8?partnerCode=JXXMT&token={token}&gAppChannel=default&gMac=unknown"

        json_data = await get_json(url)

        play_info = json_data.get("data", {}).get("playinfo", {})
        play_url = play_info.get("playurl", "")

        # m3u8_content = await get_text(play_url)

        return play_url


site = GITV()
