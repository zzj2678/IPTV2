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
SALT = os.getenv("SALT", "")
PROXY_URL = os.getenv("PROXY_URL", "")


def read_file_content(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""


def write_to_file(file_path, content):
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")


def extract_ids(url):
    match = re.search(r"/([^/]+)/([^/]+)\.[^/]+$", url)
    return match.groups() if match else (None, None)


def get_sign_url(url):
    if PROXY_URL:
        url = url.replace("127.0.0.1:8080", PROXY_URL)

    channel_id, video_id = extract_ids(url)
    if not channel_id or not video_id:
        raise ValueError("Invalid URL format")

    timestamp = str(int(time.time()))
    key = md5(f"{channel_id}{video_id}{timestamp}{SALT}".encode("utf-8")).hexdigest()

    parsed_url = urlparse(url)
    query = dict(parse_qsl(parsed_url.query))
    query.update({"t": timestamp, "key": key})

    return urlunparse(parsed_url._replace(query=urlencode(query)))


def txt_to_m3u(content):
    result = ""
    genre = ""

    for line in content.split("\n"):
        line = line.strip()
        if "," not in line:
            continue

        channel_name, channel_url = line.split(",", 1)
        if channel_url == "#genre#":
            genre = channel_name
        else:
            if "127.0.0.1:8080" in channel_url:
                channel_url = get_sign_url(channel_url)

            result += (
                f'#EXTINF:-1 tvg-logo="https://mirror.ghproxy.com/https://raw.githubusercontent.com/linitfor/epg/main/logo/{channel_name}.png" '
                f'group-title="{genre}",{channel_name}\n{channel_url}\n'
            )

    return result


def m3u_to_txt(m3u_content):
    lines = m3u_content.strip().split("\n")[1:]
    output_dict = {}
    group_name = ""

    for line in lines:
        if line.startswith("#EXTINF"):
            group_name = line.split('group-title="')[1].split('"')[0]
            channel_name = line.split(",")[-1]
        elif line.startswith("http"):
            channel_link = line
            output_dict.setdefault(group_name, []).append(f"{channel_name},{channel_link}")

    output_lines = [f"{group},#genre#\n" + "\n".join(links) for group, links in output_dict.items()]
    return "\n".join(output_lines)


def main():
    os.makedirs(M3U_DIR, exist_ok=True)
    os.makedirs(TXT_DIR, exist_ok=True)

    iptv_response = requests.get(IPTV_URL)
    m3u_content = iptv_response.text

    write_to_file(os.path.join(M3U_DIR, "ipv6.m3u"), m3u_content)

    m3u_content = read_file_content(os.path.join(M3U_DIR, "ipv6.m3u"))
    playlists = {
        "Hot": file_to_m3u("Hot.txt"),
        "CCTV": file_to_m3u("CCTV.txt"),
        "CNTV": file_to_m3u("CNTV.txt"),
        "Shuzi": file_to_m3u("Shuzi.txt"),
        "NewTV": file_to_m3u("NewTV.txt"),
        "iHOT": file_to_m3u("iHOT.txt"),
        "SITV": file_to_m3u("SITV.txt"),
        "Movie": file_to_m3u("Movie.txt"),
        "Sport": file_to_m3u("Sport.txt"),
        "MiGu": file_to_m3u("MiGu.txt"),
        "Maiduidui": file_to_m3u("maiduidui.txt"),
        "lunbo.txt": file_to_m3u("lunbo.txt"),
        "HK": file_to_m3u("hk.txt"),
        "TW": file_to_m3u("tw.txt"),
        "YouTube": file_to_m3u("YouTube.txt"),
        "Local": file_to_m3u("Local.txt"),
        "LiveChina": file_to_m3u("LiveChina.txt"),
        "Panda": file_to_m3u("Panda.txt"),
        "Documentary": file_to_m3u("Documentary.txt"),
        "Chunwan": file_to_m3u("Chunwan.txt"),
        "fm": file_to_m3u("fm.txt"),
        "Animated": file_to_m3u("Animated.txt"),
        "About": file_to_m3u("About.txt"),
    }

    iptv_m3u = "".join(playlists.values())
    update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    update_m3u = txt_to_m3u(f"更新时间,#genre#\n{update_time},\n")

    write_m3u_to_file(os.path.join(M3U_DIR, "IPTV.m3u"), iptv_m3u + update_m3u)

    iptv_txt = m3u_to_txt(read_file_content(os.path.join(M3U_DIR, "IPTV.m3u")))
    write_to_file(os.path.join(TXT_DIR, "IPTV.txt"), iptv_txt)


def file_to_m3u(file_name):
    file_path = os.path.join(TXT_DIR, file_name)
    content = read_file_content(file_path)
    return txt_to_m3u(content)


def write_m3u_to_file(file_path, content):
    header = (
        '#EXTM3U x-tvg-url="https://mirror.ghproxy.com/https://raw.githubusercontent.com/lalifeier/IPTV/main/e.xml"\n'
    )
    write_to_file(file_path, header + content.strip())


if __name__ == "__main__":
    main()
