import asyncio
import base64
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor

import cv2
import requests
from playwright.async_api import Playwright, async_playwright
from pypinyin import lazy_pinyin

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
}

ISP_DICT = {
    "中国电信": "Chinanet",
    "中国联通": "CHINA UNICOM China169 Backbone",
    "中国移动": "China Mobile Communications Corporation",
}

RTP_DIR = "rtp"
UDP_DIR = "txt/udp"

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
        return region, content
    except Exception as e:
        logging.error(f"Error fetching page content for {region}: {e}")
        return region, None
    finally:
        await browser.close()


def generate_search_url(region, isp_name, org_name):
    pinyin_name = "".join(lazy_pinyin(region, errors=lambda x: x))
    search_txt = f'"udpxy" && country="CN" && region="{pinyin_name}" && org="{org_name}"'
    encoded_search_txt = base64.b64encode(search_txt.encode("utf-8")).decode("utf-8")
    return f"https://fofa.info/result?qbase64={encoded_search_txt}"


def check_url_status(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logging.error(f"Error checking URL {url}: {e}")
        return False


async def process_urls(page_content, region_name, mcast):
    logging.info(f"Processing URLs from page content for {region_name}")
    pattern = r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"
    urls_all = re.findall(pattern, page_content)
    unique_urls = list(set(urls_all))
    logging.info(f"Found {len(unique_urls)} unique URLs for {region_name}")

    async def check_status(url):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            status = await loop.run_in_executor(pool, check_url_status, url + "/status")
            logging.info(f"URL: {url}, Accessible: {status}")
            return url, status

    results = await asyncio.gather(*(check_status(url) for url in unique_urls))
    accessible_urls = [url for url, status in results if status]
    logging.info(f"Found {len(accessible_urls)} accessible URLs for {region_name}")

    valid_urls = []
    for url in accessible_urls:
        video_url = f"{url}/rtp/{mcast}"
        logging.info(f"Checking video URL: {video_url}")

        cap = cv2.VideoCapture(video_url)
        if cap.isOpened():
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if width > 0 and height > 0:
                logging.info(f"Valid video stream found (width={width}, height={height}) at {video_url}")
                valid_urls.append((url, width, height))
            else:
                logging.info(f"Invalid video stream (width={width}, height={height}) at {video_url}")
            cap.release()

    # Sort URLs by resolution (width and height), descending order
    valid_urls.sort(key=lambda x: (x[1], x[2]), reverse=True)

    # Extract sorted URLs
    sorted_urls = [url for url, _, _ in valid_urls]

    logging.info(f"Total valid URLs for {region_name}: {len(sorted_urls)}")
    return sorted_urls

def merge_files(output_dir, merged_file_path):
    try:
        with open(merged_file_path, "w", encoding="utf-8") as outfile:
            for filename in os.listdir(output_dir):
                file_path = os.path.join(output_dir, filename)
                if os.path.isfile(file_path):
                    with open(file_path, "r", encoding="utf-8") as infile:
                        outfile.write(infile.read() + "\n")
        logging.info(f"All files merged into {merged_file_path}")
    except Exception as e:
        logging.error(f"Error merging files: {e}")


async def main():
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

            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()
                rtp_match = re.search(r"rtp://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+)", file_content)
                mcast = rtp_match.group(1) if rtp_match else None

            if not mcast:
                logging.warning(f"No rtp:// URL found in {filename}. Skipping...")
                continue

            url = generate_search_url(region, isp, org_name)
            region, content = await fetch_page_content(url, region)

            if not content:
                logging.warning(f"Empty content for region {region}. Skipping...")
                continue

            valid_urls = await process_urls(content, region, mcast)

            if not valid_urls:
                continue

            new_data = file_content.replace("rtp://", f"{valid_urls[0]}/rtp/")
            output_dir = os.path.join(UDP_DIR, isp)
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{region}.txt")

            with open(output_path, "w", encoding="utf-8") as new_file:
                new_file.write(new_data)
            logging.info(f"Processed and saved: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
