import os
import re
import time
from datetime import datetime
from hashlib import md5
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import requests

IPTV_URL = "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u"
M3U_DIR = "m3u"
TXT_DIR = "txt"


def extract_channels(keyword, m3u_content):
    m3u_filtered_content = ""
    lines = iter(m3u_content.split("\n"))
    for line in lines:
        if keyword in line:
            m3u_filtered_content += line + "\n"
            try:
                m3u_filtered_content += next(lines) + "\n"
            except StopIteration:
                pass
    return m3u_filtered_content


def write_to_file(file_path, content):
    with open(file_path, "w") as f:
        f.write(content)


def write_m3u_to_file(file_path, content):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(
            '#EXTM3U x-tvg-url="https://mirror.ghproxy.com/https://raw.githubusercontent.com/lalifeier/IPTV/main/e.xml"\n'
        )
        f.write(content.strip())


def extract_ids(url: str):
    pattern = r'/([^/]+)/([^/]+)\.[^/]+$'
    match = re.search(pattern, url)
    if match:
        return match.group(1), match.group(2)
    return None, None


def get_sign_url(url):
    PROXY_URL = os.getenv("PROXY_URL", "")
    if PROXY_URL:
        url = url.replace('iptv.lalifeier.eu.org', PROXY_URL)

    channel_id, video_id = extract_ids(url)
    if not channel_id or not video_id:
        print(url)
        raise ValueError("Invalid URL format")

    SALT = os.getenv("SALT", "")
    t = str(int(time.time()))

    print(f"{channel_id}{video_id}{t}{SALT}")
    key = md5(f"{channel_id}{video_id}{t}{SALT}".encode('utf-8')).hexdigest()

    parsed_url = urlparse(url)
    query = dict(parse_qsl(parsed_url.query))
    query.update({'t': t, 'key': key})

    new_query = urlencode(query)
    new_url = parsed_url._replace(query=new_query)

    return urlunparse(new_url)


def txt_to_m3u(content):
    # result = '#EXTM3U x-tvg-url="https://mirror.ghproxy.com/https://raw.githubusercontent.com/lalifeier/IPTV/main/e.xml"\n'
    result = ""
    genre = ""  # 初始化genre变量

    for line in content.split("\n"):
        line = line.strip()
        if "," not in line:
            continue

        channel_name, channel_url = line.split(",", 1)
        if channel_url == "#genre#":
            genre = channel_name
        else:
            if 'lalifeier.eu.org' in channel_url:
                channel_url = get_sign_url(channel_url)

            result += f'#EXTINF:-1 tvg-logo="https://raw.githubusercontent.com/linitfor/epg/main/logo/{channel_name}.png" group-title="{genre}",{channel_name}\n'
            result += f"{channel_url}\n"

    return result


def file_to_m3u(file_path):
    return txt_to_m3u(read_file_content(file_path))


def read_file_content(file_path):
    with open(file_path, "r") as file:
        content = file.read()
    return content


def m3u_to_txt(m3u_content):
    # 移除第一行并按行分割
    lines = m3u_content.strip().split("\n")[1:]

    # 初始化变量
    output_dict = {}
    group_name = channel_name = ""

    # 逐行处理输入内容
    for line in lines:
        if line.startswith("#EXTINF"):
            # 获取 group-title 的值和频道名
            group_title_part = line.split('group-title="')[1]
            group_name = group_title_part.split('"')[0]
            channel_name = line.split(",")[-1]
        elif line.startswith("http"):
            # 获取频道链接并合并频道名
            channel_link = line
            combined_link = f"{channel_name},{channel_link}"
            # 将组名作为键，合并链接作为值存储在字典中
            output_dict.setdefault(group_name, []).append(combined_link)

    # 准备返回的字符串
    output_lines = [f"{group},#genre#\n" + "\n".join(links) for group, links in output_dict.items()]

    return "\n".join(output_lines)


def main():
    os.makedirs(M3U_DIR, exist_ok=True)

    iptv_response = requests.get(IPTV_URL)
    m3u_content = iptv_response.text

    write_to_file(os.path.join(M3U_DIR, "ipv6.m3u"), m3u_content)

    m3u_content = open(os.path.join(M3U_DIR, "ipv6.m3u")).read()

    # cctv_m3u = extract_channels("央视频道", m3u_content)
    cctv_m3u = file_to_m3u(os.path.join(TXT_DIR, "CCTV.txt"))

    # cntv_m3u = extract_channels("卫视频道", m3u_content)
    cntv_m3u = file_to_m3u(os.path.join(TXT_DIR, "CNTV.txt"))

    # shu_zi_m3u = extract_channels("数字频道", m3u_content)
    shu_zi_m3u = file_to_m3u(os.path.join(TXT_DIR, "Shuzi.txt"))

    new_tv_m3u = file_to_m3u(os.path.join(TXT_DIR, "NewTV.txt"))

    i_hot_m3u = file_to_m3u(os.path.join(TXT_DIR, "iHOT.txt"))

    sitv_m3u = file_to_m3u(os.path.join(TXT_DIR, "SITV.txt"))

    local_m3u = file_to_m3u(os.path.join(TXT_DIR, "Local.txt"))

    migu_m3u = file_to_m3u(os.path.join(TXT_DIR, "MiGu.txt"))

    huya_m3u = file_to_m3u(os.path.join(TXT_DIR, "huya.txt"))

    hk_m3u = file_to_m3u(os.path.join(TXT_DIR, "hk.txt"))

    tw_m3u = file_to_m3u(os.path.join(TXT_DIR, "tw.txt"))

    youtube_m3u = file_to_m3u(os.path.join(TXT_DIR, "YouTube.txt"))

    maiduidui_m3u = file_to_m3u(os.path.join(TXT_DIR, "maiduidui.txt"))

    Sport_m3u = file_to_m3u(os.path.join(TXT_DIR, "Sport.txt"))

    live_china_m3u = file_to_m3u(os.path.join(TXT_DIR, "LiveChina.txt"))

    panda_m3u = file_to_m3u(os.path.join(TXT_DIR, "Panda.txt"))

    documentary_m3u = file_to_m3u(os.path.join(TXT_DIR, "Documentary.txt"))

    chun_wan_m3u = file_to_m3u(os.path.join(TXT_DIR, "Chunwan.txt"))

    animated_m3u = file_to_m3u(os.path.join(TXT_DIR, "Animated.txt"))

    about_m3u = file_to_m3u(os.path.join(TXT_DIR, "About.txt"))

    update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    update_m3u = txt_to_m3u(f"更新时间,#genre#\n{update_time},\n")

    iptv_m3u = (
        about_m3u
        + cctv_m3u
        + cntv_m3u
        + shu_zi_m3u
        + new_tv_m3u
        + i_hot_m3u
        + sitv_m3u
        + local_m3u
        + hk_m3u
        + tw_m3u
        + youtube_m3u
        + maiduidui_m3u
        + migu_m3u
        + huya_m3u
        + Sport_m3u
        + live_china_m3u
        + panda_m3u
        + documentary_m3u
        + chun_wan_m3u
        + animated_m3u
        + update_m3u
    )

    write_m3u_to_file(os.path.join(M3U_DIR, "CCTV.m3u"), cctv_m3u)
    write_m3u_to_file(os.path.join(M3U_DIR, "CNTV.m3u"), cntv_m3u)
    write_m3u_to_file(os.path.join(M3U_DIR, "IPTV.m3u"), iptv_m3u)

    with open(os.path.join(M3U_DIR, "IPTV.m3u"), "r", encoding="utf-8") as file:
        m3u_content = file.read()

    iptv_txt = m3u_to_txt(m3u_content)

    with open(os.path.join(TXT_DIR, "IPTV.txt"), "w", encoding="utf-8") as file:
        file.write(iptv_txt)


if __name__ == "__main__":
    main()
