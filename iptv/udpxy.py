import asyncio
import base64
import logging
import os
import re
from typing import List, Optional

from pypinyin import lazy_pinyin

from iptv.base import Base
from iptv.config import IP_DIR, ISP_DICT, OUTPUT_DIR, RTP_DIR

logger = logging.getLogger(__name__)


class UDPxy(Base):
    def __init__(self):
        super().__init__()
        self.ip_dir = os.path.join(IP_DIR, "udpxy")
        self.output_dir = os.path.join(OUTPUT_DIR, "udpxy")

    def extract_mcast_from_file(self, file_path: str) -> Optional[str]:
        logging.info(f"Extracting mcast from file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
            rtp_match = re.search(r"rtp://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+)", file_content)
            mcast = rtp_match.group(1) if rtp_match else None
        if mcast:
            logging.info(f"Found mcast: {mcast}")
        else:
            logging.warning(f"No mcast found in file: {file_path}")
        return mcast

    def generate_search_url(self, region: str, org_name: str) -> str:
        pinyin_name = "".join(lazy_pinyin(region, errors=lambda x: x))
        search_txt = f'"udpxy" && country="CN" && region="{pinyin_name}" && org="{org_name}"'
        # search_txt = f'"udpxy" && country="CN" && region="{pinyin_name}" && org="{org_name}" && is_domain=true'
        encoded_search_txt = base64.b64encode(search_txt.encode("utf-8")).decode("utf-8")
        return f"https://fofa.info/result?qbase64={encoded_search_txt}"

    async def validate_ip(self, ip: List[str], mcast: str) -> List[str]:
        if not ip:
            logging.warning("No valid IPs to validate.")
            return []

        validated_ip = []

        async def validate_single_ip(ip_address: str) -> bool:
            url_status = f"http://{ip_address}/status"
            url_video = f"http://{ip_address}/rtp/{mcast}"
            return await self.is_url_accessible(url_status) and self.is_video_stream_valid(url_video)

        tasks = [
            validate_single_ip(ip_address)
            for ip_address in ip
        ]

        for ip_address, valid in zip(ip, await asyncio.gather(*tasks)):
            if valid:
                validated_ip.append(ip_address)

        logging.info(f"Validated {len(ip)} IPs. Found {len(validated_ip)} valid IPs.")
        return validated_ip

    async def sniff_ip(self):
        for isp in os.listdir(RTP_DIR):
            isp_dir = os.path.join(RTP_DIR, isp)
            if not os.path.isdir(isp_dir):
                continue

            if isp not in ISP_DICT:
                logging.warning(f"Unknown ISP '{isp}'. Skipping...")
                continue

            org_name = ISP_DICT[isp]

            for filename in os.listdir(isp_dir):
                if not filename.endswith(".txt"):
                    continue

                region = filename.replace(".txt", "")
                file_path = os.path.join(isp_dir, filename)

                mcast = self.extract_mcast_from_file(file_path)
                if not mcast:
                    logging.warning(f"No rtp:// URL found in {filename}. Skipping...")
                    continue

                url = self.generate_search_url(region, org_name)
                content = await self.fetch_page_content(url)

                if not content:
                    logging.warning(f"Empty content for region {region}. Skipping...")
                    continue

                ip = await self.extract_ip_from_content(content)

                validated_ips = await self.validate_ip(ip, mcast)

                self.save_ip(isp, region, validated_ips)

    async def get_valid_ip(self, isp, region, mcast):
        ip_file_path = os.path.join(self.ip_dir, isp, f"{region}.txt")

        if not os.path.exists(ip_file_path):
            logging.warning(f"IP file not found: {ip_file_path}. Skipping...")
            return None

        with open(ip_file_path, "r", encoding="utf-8") as f:
            valid_ips = f.read().splitlines()

        if not valid_ips:
            logging.warning(f"No valid IP found in file: {ip_file_path}.")
            return None

        for ip in valid_ips:
            if await self.is_url_accessible(f"http://{ip}/status") and self.is_video_stream_valid(f"http://{ip}/rtp/{mcast}"):
                return ip

        logging.warning(f"No valid IP found after re-validation for {region}.")
        return None

    async def generate_playlist(self):
        for isp in os.listdir(RTP_DIR):
            isp_dir = os.path.join(RTP_DIR, isp)
            if not os.path.isdir(isp_dir):
                logging.warning(f"Directory not found: {isp_dir}. Skipping...")
                continue

            for filename in os.listdir(isp_dir):
                if not filename.endswith(".txt"):
                    continue

                region = filename.replace(".txt", "")

                mcast_file_path = os.path.join(isp_dir, filename)
                mcast = self.extract_mcast_from_file(mcast_file_path)

                if not mcast:
                    logging.warning(f"No mcast information found for {region}. Skipping...")
                    continue

                ip = await self.get_valid_ip(isp, region, mcast)

                if not ip:
                    logging.warning(f"No valid IP available for {region}. Skipping...")
                    continue

                file_path = os.path.join(RTP_DIR, isp, f"{region}.txt")
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                playlists = content.replace("rtp://", f"http://{ip}/rtp/")

                output_dir = os.path.join(self.output_dir, isp)
                os.makedirs(output_dir, exist_ok=True)

                output_path = os.path.join(output_dir, f"{region}.txt")
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(f"{isp}-{region}-组播,#genre#\n")
                    f.write(playlists)

                logging.info(f"Created playlist file: {output_path}")

            self.merge_playlist(self.output_dir, os.path.join(self.output_dir, "全国.txt"))
