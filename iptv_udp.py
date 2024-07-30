import argparse
import asyncio
import base64
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import List

import cv2
import requests
from playwright.async_api import Playwright, async_playwright
from pypinyin import lazy_pinyin

logger = logging.getLogger(__name__)

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
}

ISP_DICT = {
    "中国电信": "Chinanet",
    "中国联通": "CHINA UNICOM China169 Backbone",
    "中国移动": "China Mobile Communications Corporation",
}

IP_DIR = "ip/udp"
OUTPUT_DIR = "txt/udp"
RTP_DIR = "rtp"

os.makedirs(IP_DIR, exist_ok=True)

playwright: Playwright = None

async def get_playwright():
    global playwright
    if playwright is None:
        try:
            playwright = await async_playwright().start()
        except Exception as e:
            logging.error(f"Error starting Playwright: {e}")
            raise
    return playwright

def is_ip_accessible(ip: str) -> bool:
    try:
        logging.info(f"Checking accessibility for IP: {ip}")
        response = requests.get(f"http://{ip}/status", timeout=5)
        if response.status_code == 200:
            logging.info(f"IP {ip} is accessible. Status code: {response.status_code}")
            return True
        else:
            logging.warning(f"IP {ip} is not accessible. Status code: {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"Error checking IP {ip}: {e}")
        return False

def is_video_stream_valid(url: str, mcast: str) -> bool:
    video_url = f"{url}/rtp/{mcast}"
    logging.info(f"Checking video URL: {video_url}")

    try:
        cap = cv2.VideoCapture(video_url)
        if cap.isOpened():
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if width > 0 and height > 0:
                logging.info(f"Valid video stream found (width={width}, height={height}) at {video_url}")
                cap.release()
                return True
            else:
                logging.info(f"Invalid video stream (width={width}, height={height}) at {video_url}")
        else:
            logging.info(f"Failed to open video stream at {video_url}")
        cap.release()
    except Exception as e:
        logging.error(f"Error checking video stream {video_url}: {e}")

    return False

async def fetch_page_content(url, region):
    logging.info(f"Fetching content from {url} for region {region}")
    playwright = await get_playwright()
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    await context.add_init_script("Object.defineProperties(navigator, {webdriver:{get:()=>false}});")
    page = await context.new_page()

    try:
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        content = await page.content()
        logging.info(f"Finished fetching content from {url} for region {region}")
        return content
    except Exception as e:
        logging.error(f"Error fetching page content for {region}: {e}")
        return None
    finally:
        await browser.close()

def construct_search_url(region, isp_name, org_name):
    pinyin_name = "".join(lazy_pinyin(region, errors=lambda x: x))
    search_txt = f'"udpxy" && country="CN" && region="{pinyin_name}" && org="{org_name}"'
    encoded_search_txt = base64.b64encode(search_txt.encode("utf-8")).decode("utf-8")
    return f"https://fofa.info/result?qbase64={encoded_search_txt}"

async def extract_ips_from_content(page_content, region_name):
    logging.info(f"Extracting IPs from page content for {region_name}")
    pattern = r"http://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+)"
    ip_ports_all = re.findall(pattern, page_content)
    unique_ip_ports = list(set(ip_ports_all))
    logging.info(f"Found {len(unique_ip_ports)} unique IPs and ports for {region_name}")

    return unique_ip_ports

def extract_mcast_from_file(file_path):
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

async def validate_ips(valid_ips: List[str], mcast: str) -> List[str]:
    if not valid_ips:
        logging.warning("No valid IPs to validate.")
        return []

    validated_ips = []

    with ThreadPoolExecutor() as pool:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(pool, lambda ip: is_ip_accessible(ip) and is_video_stream_valid(ip, mcast), ip)
            for ip in valid_ips
        ]
        for ip, valid in zip(valid_ips, await asyncio.gather(*futures)):
            if valid:
                validated_ips.append(ip)

    logging.info(f"Validated {len(valid_ips)} IPs. Found {len(validated_ips)} valid IPs.")
    return validated_ips

def save_ips(isp: str, region: str, validated_ips: List[str]):
    if not validated_ips:
        logging.warning(f"No validated IPs to save for {region}.")
        return

    output_dir = os.path.join(IP_DIR, isp)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{region}.txt")

    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as file:
            existing_ips = set(file.read().splitlines())
    else:
        existing_ips = set()

    all_ips = sorted(existing_ips.union(validated_ips))
    with open(output_path, "w", encoding="utf-8") as file:
        file.write("\n".join(all_ips))
    logging.info(f"Saved validated IPs to: {output_path}")

async def fetch_ip():
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

            mcast = extract_mcast_from_file(file_path)
            if not mcast:
                logging.warning(f"No rtp:// URL found in {filename}. Skipping...")
                continue

            url = construct_search_url(region, isp, org_name)
            content = await fetch_page_content(url, region)

            if not content:
                logging.warning(f"Empty content for region {region}. Skipping...")
                continue

            ips = await extract_ips_from_content(content, region)

            validated_ips = await validate_ips(ips, mcast)
            save_ips(isp, region, validated_ips)

def generate_playlist(isp, region, ip):
    file_path = os.path.join(RTP_DIR, isp, f"{region}.txt")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return content.replace("rtp://", f"http://{ip}/rtp/")

async def get_valid_ip(isp, region, mcast):
    ip_file_path = os.path.join(IP_DIR, isp, f"{region}.txt")

    if not os.path.exists(ip_file_path):
        logging.warning(f"IP file not found: {ip_file_path}. Skipping...")
        return None

    with open(ip_file_path, "r", encoding="utf-8") as f:
        valid_ips = f.read().splitlines()

    if not valid_ips:
        logging.warning(f"No valid IP found in file: {ip_file_path}.")
        return None

    for ip in valid_ips:
        if is_ip_accessible(ip) and is_video_stream_valid(ip, mcast):
            return ip

    logging.warning(f"No valid IP found after re-validation for {region}.")
    return None


async def create_playlist():
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
            mcast = extract_mcast_from_file(mcast_file_path)

            if not mcast:
                logging.warning(f"No mcast information found for {region}. Skipping...")
                continue

            ip = await get_valid_ip(isp, region, mcast)

            if not ip:
                logging.warning(f"No valid IP available for {region}. Skipping...")
                continue

            playlists = generate_playlist(isp, region, ip)

            output_dir = os.path.join(OUTPUT_DIR, isp)
            os.makedirs(output_dir, exist_ok=True)

            output_path = os.path.join(output_dir, f"{region}.m3u8")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"{isp}-{region}-组播,#genre#\n")
                f.write(playlists)

            logging.info(f"Created playlist file: {output_path}")

async def main():
    parser = argparse.ArgumentParser(description="IP fetching and playlist generation script")
    parser.add_argument('--ip', action='store_true', help="Fetch valid IPs")
    parser.add_argument('--playlist', action='store_true', help="Generate playlists from valid IPs")
    args = parser.parse_args()

    if args.ip:
        await fetch_ip()
    elif args.playlist:
        await create_playlist()
    else:
        logging.error("You must specify an action: --ip or --playlist.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    asyncio.run(main())
