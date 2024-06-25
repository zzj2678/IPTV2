import os
import requests
from datetime import datetime

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
        f.write("#EXTM3U\n")
        f.write(content.strip())

def txt_to_m3u(content):
    result = '#EXTM3U x-tvg-url="https://mirror.ghproxy.com/https://raw.githubusercontent.com/lalifeier/IPTV/main/e.xml"\n'
    
    genre = ''  # 初始化genre变量

    for line in content.split('\n'):
        line = line.strip()
        if "," not in line:
            continue

        channel_name, channel_url = line.split(',', 1)
        if channel_url == '#genre#':
            genre = channel_name
        else:
            result += f'#EXTINF:-1 tvg-logo="https://raw.githubusercontent.com/linitfor/epg/main/logo/{channel_name}.png" group-title="{genre}",{channel_name}\n'
            result += f'{channel_url}\n'

    return result

def file_to_m3u(file_path):
    return txt_to_m3u(read_file_content(file_path))

def read_file_content(file_path):
    with open(file_path, 'r') as file:
        content = file.read() 
    return content

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

    tvb_m3u = file_to_m3u(os.path.join(TXT_DIR, "TVB.txt"))

    maiduidui_m3u = file_to_m3u(os.path.join(TXT_DIR, "maiduidui.txt"))

    Sport_m3u = file_to_m3u(os.path.join(TXT_DIR, "Sport.txt"))

    live_china_m3u = file_to_m3u(os.path.join(TXT_DIR, "LiveChina.txt"))

    panda_m3u = file_to_m3u(os.path.join(TXT_DIR, "Panda.txt"))

    documentary_m3u = file_to_m3u(os.path.join(TXT_DIR, "Documentary.txt"))

    chun_wan_m3u = file_to_m3u(os.path.join(TXT_DIR, "Chunwan.txt"))

    animated_m3u = file_to_m3u(os.path.join(TXT_DIR, "Animated.txt"))

    about_m3u = file_to_m3u(os.path.join(TXT_DIR, "About.txt"))

    iptv_m3u = cctv_m3u + cntv_m3u + shu_zi_m3u + new_tv_m3u + i_hot_m3u + sitv_m3u + local_m3u + tvb_m3u + maiduidui_m3u + migu_m3u + huya_m3u + Sport_m3u + live_china_m3u + panda_m3u + documentary_m3u + chun_wan_m3u + animated_m3u + about_m3u

    write_m3u_to_file(os.path.join(M3U_DIR, "CCTV.m3u"), cctv_m3u)
    write_m3u_to_file(os.path.join(M3U_DIR, "CNTV.m3u"), cntv_m3u)
    write_m3u_to_file(os.path.join(M3U_DIR, "IPTV.m3u"), iptv_m3u)

    with open(os.path.join(M3U_DIR, "IPTV.m3u"), "a", encoding="utf-8") as f:
        update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"更新时间,#genre#\n")
        f.write(f"{update_time},\n")

if __name__ == "__main__":
    main()



