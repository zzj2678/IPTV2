import argparse
import asyncio
import base64
import concurrent.futures
import json
import logging
import os
import random
import re
import shutil
from typing import List

import aiohttp
import cv2
import requests
from playwright.async_api import Playwright, async_playwright
from pypinyin import lazy_pinyin

# from fofa_hack import fofa

logger = logging.getLogger(__name__)

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
}

regions = [
    "北京",
    "天津",
    "河北",
    "山西",
    "内蒙古",
    "辽宁",
    "吉林",
    "黑龙江",
    "上海",
    "江苏",
    "浙江",
    "安徽",
    "福建",
    "江西",
    "山东",
    "河南",
    "湖北",
    "湖南",
    "广东",
    "广西",
    "海南",
    "重庆",
    "四川",
    "贵州",
    "云南",
    "西藏",
    "陕西",
    "甘肃",
    "青海",
    "宁夏",
    "新疆",
]

isp_dict = {
    "中国电信": "Chinanet",
    "中国联通": "CHINA UNICOM China169 Backbone",
    # "中国移动": "China Mobile Communications Corporation"
}

OUTPUT_DIR = "txt/jiudian"
os.makedirs(OUTPUT_DIR, exist_ok=True)

IP_DIR = "ip/jiudian"


def clean_name(name):
    # 清洗名称的函数，根据需要自行添加清洗规则
    name = name.replace("中央", "CCTV")
    name = name.replace("高清", "")
    name = name.replace("超清", "")
    name = name.replace("HD", "")
    name = name.replace("标清", "")
    name = name.replace("超高", "")
    name = name.replace("频道", "")
    name = name.replace("-", "")
    name = name.replace(" ", "")
    name = name.replace("PLUS", "+")
    name = name.replace("＋", "+")
    name = name.replace("(", "")
    name = name.replace(")", "")
    name = name.replace("L", "")
    name = name.replace("CMIPTV", "")
    name = name.replace("cctv", "CCTV")
    name = re.sub(r"CCTV(\d+)台", r"CCTV\1", name)
    name = name.replace("CCTV1综合", "CCTV1")
    name = name.replace("CCTV2财经", "CCTV2")
    name = name.replace("CCTV3综艺", "CCTV3")
    name = name.replace("CCTV4国际", "CCTV4")
    name = name.replace("CCTV4中文国际", "CCTV4")
    name = name.replace("CCTV4欧洲", "CCTV4")
    name = name.replace("CCTV5体育", "CCTV5")
    name = name.replace("CCTV5+体育", "CCTV5+")
    name = name.replace("CCTV6电影", "CCTV6")
    name = name.replace("CCTV7军事", "CCTV7")
    name = name.replace("CCTV7军农", "CCTV7")
    name = name.replace("CCTV7农业", "CCTV7")
    name = name.replace("CCTV7国防军事", "CCTV7")
    name = name.replace("CCTV8电视剧", "CCTV8")
    name = name.replace("CCTV8纪录", "CCTV9")
    name = name.replace("CCTV9记录", "CCTV9")
    name = name.replace("CCTV9纪录", "CCTV9")
    name = name.replace("CCTV10科教", "CCTV10")
    name = name.replace("CCTV11戏曲", "CCTV11")
    name = name.replace("CCTV12社会与法", "CCTV12")
    name = name.replace("CCTV13新闻", "CCTV13")
    name = name.replace("CCTV新闻", "CCTV13")
    name = name.replace("CCTV14少儿", "CCTV14")
    name = name.replace("央视14少儿", "CCTV14")
    name = name.replace("CCTV少儿超", "CCTV14")
    name = name.replace("CCTV15音乐", "CCTV15")
    name = name.replace("CCTV音乐", "CCTV15")
    name = name.replace("CCTV16奥林匹克", "CCTV16")
    name = name.replace("CCTV17农业农村", "CCTV17")
    name = name.replace("CCTV17军农", "CCTV17")
    name = name.replace("CCTV17农业", "CCTV17")
    name = name.replace("CCTV5+体育赛视", "CCTV5+")
    name = name.replace("CCTV5+赛视", "CCTV5+")
    name = name.replace("CCTV5+体育赛事", "CCTV5+")
    name = name.replace("CCTV5+赛事", "CCTV5+")
    name = name.replace("CCTV5+体育", "CCTV5+")
    name = name.replace("CCTV5赛事", "CCTV5+")
    name = name.replace("凤凰中文台", "凤凰中文")
    name = name.replace("凤凰资讯台", "凤凰资讯")
    name = name.replace("CCTV4K测试）", "CCTV4")
    name = name.replace("CCTV164K", "CCTV16")
    name = name.replace("上海东方卫视", "上海卫视")
    name = name.replace("东方卫视", "上海卫视")
    name = name.replace("内蒙卫视", "内蒙古卫视")
    name = name.replace("福建东南卫视", "东南卫视")
    name = name.replace("广东南方卫视", "南方卫视")
    name = name.replace("金鹰卡通卫视", "金鹰卡通")
    name = name.replace("湖南金鹰卡通", "金鹰卡通")
    name = name.replace("炫动卡通", "哈哈炫动")
    name = name.replace("卡酷卡通", "卡酷少儿")
    name = name.replace("卡酷动画", "卡酷少儿")
    name = name.replace("BRTVKAKU少儿", "卡酷少儿")
    name = name.replace("优曼卡通", "优漫卡通")
    name = name.replace("优曼卡通", "优漫卡通")
    name = name.replace("嘉佳卡通", "佳嘉卡通")
    name = name.replace("世界地理", "地理世界")
    name = name.replace("CCTV世界地理", "地理世界")
    name = name.replace("BTV北京卫视", "北京卫视")
    name = name.replace("BTV冬奥纪实", "冬奥纪实")
    name = name.replace("东奥纪实", "冬奥纪实")
    name = name.replace("卫视台", "卫视")
    name = name.replace("湖南电视台", "湖南卫视")
    name = name.replace("2金鹰卡通", "金鹰卡通")
    name = name.replace("湖南教育台", "湖南教育")
    name = name.replace("湖南金鹰纪实", "金鹰纪实")
    name = name.replace("少儿科教", "少儿")
    name = name.replace("影视剧", "影视")
    return name


def is_province(region):
    provinces = [
        "北京",
        "天津",
        "河北",
        "山西",
        "内蒙古",
        "辽宁",
        "吉林",
        "黑龙江",
        "上海",
        "江苏",
        "浙江",
        "安徽",
        "福建",
        "江西",
        "山东",
        "河南",
        "湖北",
        "湖南",
        "广东",
        "广西",
        "海南",
        "重庆",
        "四川",
        "贵州",
        "云南",
        "西藏",
        "陕西",
        "甘肃",
        "青海",
        "宁夏",
        "新疆",
    ]
    return region in provinces


def is_city(region):
    return not is_province(region)


playwright: Playwright = None


async def get_playwright():
    global playwright
    if playwright is None:
        try:
            playwright = await async_playwright().start()
        except Exception as e:
            raise e

    return playwright


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


def generate_search_url(region, isp_name, org_name):
    pinyin_name = "".join(lazy_pinyin(region, errors=lambda x: x))
    if is_province(region):
        search_txt = f'"iptv/live/zh_cn.js" && country="CN" && region="{pinyin_name}" && org="{org_name}"'
    elif not is_province(region):
        search_txt = f'"iptv/live/zh_cn.js" && country="CN" && city="{pinyin_name}" && org="{org_name}"'
    else:
        return None

    bytes_string = search_txt.encode("utf-8")
    encoded_search_txt = base64.b64encode(bytes_string).decode("utf-8")
    return f"https://fofa.info/result?qbase64={encoded_search_txt}"


def generate_region_urls(regions, isp_dict):
    url_dict = {}
    for region in regions:
        for isp_name, org_name in isp_dict.items():
            url = generate_search_url(region, isp_name, org_name)
            if url:
                key = f"{region}-{isp_name}"
                url_dict[key] = url
    return url_dict


def get_province_name(region):
    return region.split("-")[0]


def merge_files(output_dir, merged_file_path):
    try:
        with open(merged_file_path, "w", encoding="utf-8") as outfile:
            for subdir in os.listdir(output_dir):
                subdir_path = os.path.join(output_dir, subdir)
                if os.path.isdir(subdir_path):
                    logging.info(f"Processing directory: {subdir_path}")
                    for filename in os.listdir(subdir_path):
                        file_path = os.path.join(subdir_path, filename)
                        if os.path.isfile(file_path):
                            logging.info(f"Reading file: {file_path}")
                            with open(file_path, "r", encoding="utf-8") as infile:
                                outfile.write(infile.read() + "\n")
        print(f"All files merged into {merged_file_path}")
    except Exception as e:
        print(f"Error merging files: {e}")


async def extract_ips_from_content(page_content, region_name):
    logging.info(f"Extracting IPs from page content for {region_name}")
    pattern = r"http://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+)"
    ip_ports_all = re.findall(pattern, page_content)
    unique_ip_ports = list(set(ip_ports_all))
    logging.info(f"Found {len(unique_ip_ports)} unique IPs and ports for {region_name}")

    ip_ports = set()
    for ip_port in unique_ip_ports:
        ip_address, port = ip_port.split(":")
        for i in range(1, 256):  # 第四位从1到255
            ip_ports.add(f"{ip_address.rsplit('.', 1)[0]}.{i}:{port}")

    return unique_ip_ports


async def fetch_ip():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    region_urls = generate_region_urls(regions, isp_dict)

    for region, url in region_urls.items():
        content = await fetch_page_content(url, region)
        if not content:
            logging.warning(f"Empty content for region {region}. Skipping...")
            continue

        province_name = get_province_name(region)
        isp_name = region.split("-")[1]

        ips = await extract_ips_from_content(content, region)

        validated_ips = await validate_ips(ips)
        save_ips(isp_name, province_name, validated_ips)


def is_ip_accessible(ip: str) -> bool:
    try:
        logging.info(f"Checking accessibility for IP: {ip}")
        response = requests.get(f"http://{ip}/iptv/live/1000.json?key=txiptv", timeout=5)
        if response.status_code == 200:
            logging.info(f"IP {ip} is accessible. Status code: {response.status_code}")
            return True
        else:
            logging.warning(f"IP {ip} is not accessible. Status code: {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"Error checking IP {ip}: {e}")
        return False


async def validate_ips(valid_ips: List[str]) -> List[str]:
    if not valid_ips:
        logging.warning("No valid IPs to validate.")
        return []

    validated_ips = []

    with concurrent.futures.ThreadPoolExecutor() as pool:
        loop = asyncio.get_event_loop()
        futures = [loop.run_in_executor(pool, lambda ip: is_ip_accessible(ip), ip) for ip in valid_ips]
        for ip, valid in zip(valid_ips, await asyncio.gather(*futures)):
            if valid:
                validated_ips.append(ip)

    logging.info(f"Validated {len(valid_ips)} IPs. Found {len(validated_ips)} valid IPs.")
    return validated_ips


def save_ips(isp, province, ips):
    output_dir = os.path.join(IP_DIR, isp)
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"{province}.txt")

    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as file:
            existing_ips = set(file.read().splitlines())
    else:
        existing_ips = set()

    all_ips = sorted(existing_ips.union(ips))
    with open(output_path, "w", encoding="utf-8") as file:
        file.write("\n".join(all_ips))
    logging.info(f"Saved validated IPs to: {output_path}")


def get_valid_ips(isp: str, region: str) -> list:
    ip_file_path = os.path.join(IP_DIR, isp, f"{region}.txt")

    if not os.path.exists(ip_file_path):
        logging.warning(f"IP file not found: {ip_file_path}. Skipping...")
        return []

    with open(ip_file_path, "r", encoding="utf-8") as f:
        valid_ips = f.read().splitlines()

    return valid_ips


async def is_video_stream_valid(video_url: str) -> bool:
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


async def generate_playlist(isp: str, region: str) -> str:
    valid_ips = get_valid_ips(isp, region)
    ip_playlists = {}

    if not valid_ips:
        return ""

    async with aiohttp.ClientSession() as session:
        for ip in valid_ips:
            url = f"http://{ip}/iptv/live/1000.json?key=txiptv"
            try:
                async with session.get(url, headers=headers, timeout=3) as response:
                    if response.status == 200:
                        json_data = await response.json()
                        programs = []

                        for item in json_data.get("data", []):
                            if isinstance(item, dict):
                                name = item.get("name", "")
                                chid = str(item.get("chid")).zfill(4)
                                srcid = item.get("srcid")
                                if name and chid and srcid:
                                    name = clean_name(name)
                                    m3u8_url = f"http://{ip}/tsfile/live/{chid}_{srcid}.m3u8"
                                    programs.append((name, m3u8_url))

                        ip_playlists[ip] = programs
                        logging.info(f"Processed {len(programs)} programs from IP {ip}")

            except aiohttp.ClientError as e:
                logging.error(f"Failed to fetch data from {url}. Error: {e}")
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse JSON from {url}. Error: {e}")
            except Exception as e:
                logging.error(f"Unexpected error occurred for URL {url}. Error: {e}")

    if not ip_playlists:
        return ""

    async def check_random_urls(urls):
        for url in urls:
            if await is_video_stream_valid(url):
                return True
        return False

    best_ip = None
    best_count = 0

    for ip, programs in ip_playlists.items():
        # Randomly sample up to 5 URLs for validation
        sampled_urls = [url for _, url in random.sample(programs, min(len(programs), 5))]

        # Check if any sampled URL is valid
        if await check_random_urls(sampled_urls):
            if len(programs) > best_count:
                best_ip = ip
                best_count = len(programs)

    if best_ip:
        best_playlist = "\n".join(f"{name},{url}" for name, url in ip_playlists[best_ip])
        return best_playlist

    return ""


async def create_playlist():
    for region in regions:
        for isp_name, org_name in isp_dict.items():
            playlists = await generate_playlist(isp_name, region)

            if not playlists:
                continue

            output_dir = os.path.join(OUTPUT_DIR, isp_name)
            os.makedirs(output_dir, exist_ok=True)

            output_path = os.path.join(output_dir, f"{region}.m3u8")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"{isp_name}-{region}-酒店,#genre#\n")

                f.write(playlists)

            logging.info(f"Created playlist file: {output_path}")

    merge_files(OUTPUT_DIR, os.path.join(OUTPUT_DIR, "全国.txt"))


async def main():
    parser = argparse.ArgumentParser(description="IP fetching and playlist generation script")
    parser.add_argument("--ip", action="store_true", help="Fetch valid IPs")
    parser.add_argument("--playlist", action="store_true", help="Generate playlists from valid IPs")
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
