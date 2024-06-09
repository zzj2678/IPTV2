#!/bin/bash

# Directory for m3u files
M3U_DIR=m3u

# Create m3u directory if it doesn't exist
mkdir -p "$M3U_DIR"

# 央视源
wget https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u -O "$M3U_DIR/CCTV.m3u"
sed -i -n '/央视/,+1p' "$M3U_DIR/CCTV.m3u"
sed -i '1i #EXTM3U' "$M3U_DIR/CCTV.m3u"
sed -i '/^\s*$/d' "$M3U_DIR/CCTV.m3u"

# 卫视源
touch "$M3U_DIR/CNTV.m3u"
for keyword in "卫视频道" "NewTV系列" "超清频道"; do
  wget https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u -O "$M3U_DIR/temp.m3u"
  sed -i -n "/$keyword/,+1p" "$M3U_DIR/temp.m3u"
  cat "$M3U_DIR/temp.m3u" >> "$M3U_DIR/CNTV.m3u"
  rm -f "$M3U_DIR/temp.m3u"
done
sed -i '1i #EXTM3U' "$M3U_DIR/CNTV.m3u"
sed -i '/^\s*$/d' "$M3U_DIR/CNTV.m3u"

# 整合源
cat "$M3U_DIR/CCTV.m3u" "$M3U_DIR/CNTV.m3u" > "$M3U_DIR/IPTV.m3u"
sed -i '/#EXTM3U/d' "$M3U_DIR/IPTV.m3u"
sed -i '1i #EXTM3U' "$M3U_DIR/IPTV.m3u"
sed -i '/^\s*$/d' "$M3U_DIR/IPTV.m3u"

# 节目源
# wget https://epg.112114.xyz/pp.xml -O EPG.xml
