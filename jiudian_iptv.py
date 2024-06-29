import asyncio
import logging
import re
import os
from pyppeteer import launch
import requests
import json
import concurrent.futures
from pypinyin import lazy_pinyin
import base64
import shutil
import aiohttp
# from fofa_hack import fofa
from random import randint 

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
}

regions = [
    '北京', '天津', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江',
    '上海', '江苏', '浙江', '安徽', '福建', '江西', '山东',
    '河南', '湖北', '湖南', '广东', '广西', '海南', '重庆',
    '四川', '贵州', '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆'
]

# regions = [
#     '北京',
#     # '上海', 
#     # '江苏', 
#     # '浙江',
#     '广东'
# ]

isp_dict = {
    "中国电信": "Chinanet",
    "中国联通": "CHINA UNICOM China169 Backbone",
    # "中国移动": "China Mobile Communications Corporation"
}

OUTPUT_DIR = 'txt/jiudian'
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def fetch_page_content(url, region):
    try:
        logging.info(f"Fetching content from {url} for region {region}")
        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()
        await page.evaluateOnNewDocument('() =>{ Object.defineProperties(navigator,' '{ webdriver:{ get: () => false } }) }')   
        await page.goto(url, waitUntil="domcontentloaded")
        content = await page.content()
        await browser.close()
        logging.info(f"Finished fetching content from {url} for region {region}")
        return region, content  # Return both region and content as a tuple
    except Exception as e:
        logging.error(f"Error fetching page content for {region}: {str(e)}")
        return region, None  # Return None for content in case of error

# async def fetch_page_content(url, region):
#     try:
#         logging.info(f"Fetching content from {url} for region {region}")
#         async with aiohttp.ClientSession() as session:
#             async with session.get(url, headers=headers, timeout=10) as response:
#                 content = await response.text()
#                 logging.info(f"Finished fetching content from {url} for region {region}")
#                 return region, content  # Return both region and content
#     except aiohttp.ClientError as e:
#         logging.error(f"Error fetching page content for {region}: {str(e)}")
#         return region, None  # Return None for content in case of error

def process_url(ip_port, results):
    url = f"http://{ip_port}/iptv/live/1000.json?key=txiptv"
    try:
        response = requests.get(url, headers=headers, timeout=3)
        response.raise_for_status()  # 检查请求是否成功
        json_data = response.json()

        for item in json_data.get('data', []):
            if isinstance(item, dict):
                name = item.get('name', '')
                chid = str(item.get('chid')).zfill(4)
                srcid = item.get('srcid')
                if name and chid and srcid:
                    name = clean_name(name)
                    url = f"http://{ip_port}/tsfile/live/{chid}_{srcid}.m3u8"
                    results.append(f"{name},{url}")
                    logging.info(f"Appended cleaned name and URL: {name}, {url}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to process JSON for URL {url}. Error: {str(e)}")
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON for URL {url}. Error: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error occurred for URL {url}. Error: {str(e)}")

def process_urls(page_content, region_name):
    logging.info(f"Processing URLs from page content for {region_name}")
    pattern = r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"  # 匹配的格式
    urls_all = re.findall(pattern, page_content)

    ip_ports = set()
    for url in urls_all:
        ip_port = url.replace('http://', '')
        ip_address, port = ip_port.split(':')
        for i in range(1, 256):  # 第四位从1到255
            ip_ports.add(f"{ip_address.rsplit('.', 1)[0]}.{i}:{port}")

    logging.info(f"Found {len(ip_ports)} unique URLs for region {region_name}")

    results = [f"{region_name}-酒店,#genre#"]

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(process_url, ip_port, results) for ip_port in ip_ports]

        for future in concurrent.futures.as_completed(futures):
            pass  # 在这里可以处理每个请求的结果，如果有需要的话

    logging.info(f"Finished processing URLs for region {region_name}. Total results: {len(results) - 1}")
    return results

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
    provinces = ['北京', '天津', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江',
                 '上海', '江苏', '浙江', '安徽', '福建', '江西', '山东',
                 '河南', '湖北', '湖南', '广东', '广西', '海南', '重庆',
                 '四川', '贵州', '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆']
    return region in provinces

def is_city(region):
    return not is_province(region)

def generate_search_url(region, isp_name, org_name):
    pinyin_name = "".join(lazy_pinyin(region, errors=lambda x: x))
    if is_province(region):
        search_txt = f'"iptv/live/zh_cn.js" && country="CN" && region="{pinyin_name}" && org="{org_name}"'
    elif not is_province(region):
        search_txt = f'"iptv/live/zh_cn.js" && country="CN" && city="{pinyin_name}" && org="{org_name}"'
    else:
        return None
    
    bytes_string = search_txt.encode('utf-8')
    encoded_search_txt = base64.b64encode(bytes_string).decode('utf-8')
    return f'https://fofa.info/result?qbase64={encoded_search_txt}'

def generate_region_urls(regions, isp_dict):
    url_dict = {}
    for region in regions:
        for isp_name, org_name in isp_dict.items():
            url = generate_search_url(region, isp_name, org_name)
            if url:
                key = f'{region}-{isp_name}'
                url_dict[key] = url
    return url_dict

def get_province_name(region):
    return region.split('-')[0]

def merge_files(output_dir, merged_file_path):
    try:
        with open(merged_file_path, 'w', encoding='utf-8') as outfile:
            for filename in os.listdir(output_dir):
                file_path = os.path.join(output_dir, filename)
                if os.path.isfile(file_path):
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read() + '\n')  # 读取并写入文件内容，添加换行符分隔
        print(f"All files merged into {merged_file_path}")
    except Exception as e:
        print(f"Error merging files: {e}")

async def main():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    region_urls = generate_region_urls(regions, isp_dict)

    for region, url in region_urls.items():
        try:
            result = await fetch_page_content(url, region)
            content = result[1] if result[1] is not None else None
        except Exception as e:
            logging.error(f"Error fetching page content for {region}: {str(e)}")
            content = None

        # await asyncio.sleep(randint(1, 3))  

        if not content: 
            logging.warning(f"Empty content for region {region}. Skipping...")
            continue

        region_name = get_province_name(region)
        results = process_urls(content, region)
        file_path = os.path.join(OUTPUT_DIR, f"{region_name}.txt")

        with open(file_path, 'a', encoding='utf-8') as f:
            for result in results:
                f.write(result + '\n')

        logging.info(f"Results for {region_name} written to {file_path}")

    merge_files(OUTPUT_DIR, os.path.join(OUTPUT_DIR, "全国.txt"))


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
