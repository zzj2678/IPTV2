import asyncio
import logging
import re
import os
from pyppeteer import launch
import requests
import json
import concurrent.futures

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# 定义各个地区的FOFA搜索链接
regions = {
    'hebei': "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iSGViZWki",
    'beijing': "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iYmVpamluZyI%3D",
    'guangdong': "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iZ3Vhbmdkb25nIg%3D%3D",
    'shanghai': "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0ic2hhbmdoYWki",
    'tianjin': "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0idGlhbmppbiI%3D",
    'chongqing': "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iY2hvbmdxaW5nIg%3D%3D",
    'shanxi': "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0ic2hhbnhpIg%3D%3D",
    'shaanxi': "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iU2hhYW54aSI%3D",
    'liaoning': "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0ibGlhb25pbmci",
    'jiangsu': "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iamlhbmdzdSI%3D",
    'zhejiang': "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iemhlamlhbmci",
    'anhui': "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5a6J5b69Ig%3D%3D",
    'fujian': "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iRnVqaWFuIg%3D%3D",
    'jiangxi': "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5rGf6KW%2FIg%3D%3D",
    'shandong': "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5bGx5LicIg%3D%3D",
    'henan': "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5rKz5Y2XIg%3D%3D",
    'hubei': "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5rmW5YyXIg%3D%3D",
    'hunan': "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5rmW5Y2XIg%3D%3D"

    # "hebei": "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22hebei%22",
    # "beijing": "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22beijing%22",
    # "guangdong": "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22guangdong%22",
    # "shanghai": "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22shanghai%22",
    # "tianjin": "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22tianjin%22",
    # "chongqing": "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22chongqing%22",
    # "shanxi": "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22shanxi%22",
    # "shaanxi": "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22shaanxi%22",
    # "liaoning": "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22liaoning%22",
    # "jiangsu": "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22jiangsu%22",
    # "zhejiang": "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22zhejiang%22",
    # "anhui": "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22anhui%22",
    # "fujian": "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22fujian%22",
    # "jiangxi": "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22jiangxi%22",
    # "shandong": "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22shandong%22",
    # "henan": "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22henan%22",
    # "hubei": "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22hubei%22",
    # "hunan": "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22hunan%22"
    # 其他地区链接可以按照需要添加
}

region_names = {
    'hebei': '河北',
    'beijing': '北京',
    'guangdong': '广东',
    'shanghai': '上海',
    'tianjin': '天津',
    'chongqing': '重庆',
    'shanxi': '山西',
    'shaanxi': '陕西',
    'liaoning': '辽宁',
    'jiangsu': '江苏',
    'zhejiang': '浙江',
    'anhui': '安徽',
    'fujian': '福建',
    'jiangxi': '江西',
    'shandong': '山东',
    'henan': '河南',
    'hubei': '湖北',
    'hunan': '湖南'
    # 其他地区的中文名称
}

OUTPUT_DIR = 'txt/jiudian'
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def fetch_page_content(url, region):
    try:
        logging.info(f"Fetching content from {url} for region {region}")
        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()
        await page.evaluateOnNewDocument('() =>{ Object.defineProperties(navigator,' '{ webdriver:{ get: () => false } }) }')   
        await page.goto(url)
        await asyncio.sleep(5)  # Adjust as necessary based on page load time
        content = await page.content()
        await browser.close()
        logging.info(f"Finished fetching content from {url} for region {region}")
        return content 
    except Exception as e:
        logging.error(f"Error fetching page content for {region}: {str(e)}")
        return None

def process_url(ip_port, results):
    url = f"http://{ip_port}/iptv/live/1000.json?key=txiptv"
    try:
        response = requests.get(url, timeout=3)
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

    results = [f"{region_name}酒店,#genre#"]

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

async def main():
    tasks = []
    for region, url in regions.items():
        tasks.append(fetch_page_content(url, region))

    try:
        html_contents = await asyncio.gather(*tasks)
    except Exception as e:
        logging.error(f"Error occurred during asyncio.gather: {str(e)}")
        html_contents = [None] * len(tasks)  # Assigning None to handle missing content

    all_results = []
    for region, content in zip(regions.keys(), html_contents):
        if not content: 
                logging.warning(f"Empty content for region {region}. Skipping...")
                continue

        region_name = region_names.get(region)
        if region_name is None:
                logging.warning(f"Region name not found for {region}. Skipping...")
                continue
        results = process_urls(content, region_name)
        file_path = os.path.join(OUTPUT_DIR, f"{region}.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(result + '\n')

            all_results.extend(results)

        logging.info(f"Results for {region_name} written to {file_path}")

    all_regions_file = os.path.join(OUTPUT_DIR, "all.txt")
    with open(all_regions_file, 'w', encoding='utf-8') as f:
        for result in all_results:
            f.write(result + '\n')

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
