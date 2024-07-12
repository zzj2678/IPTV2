import logging
import time
from importlib import import_module

import tldextract
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from starlette.requests import Request

from live.util.proxy import get_proxy

logger = logging.getLogger(__name__)

app = FastAPI()

CHANNEL_MAPPINGS = {
    # Define your channel mappings here if needed
}


@app.get("/")
async def hello_world():
    return {"hello": "world"}


@app.get("/{channel_id}/{video_id}")
async def get_play_url(channel_id: str, video_id: str):
    logger.info(f"Received request for channel ID: {channel_id} and video ID: {video_id}")

    extension = ""
    if "." in video_id:
        video_id, extension = video_id.rsplit(".", 1)

    if not extension:
        extension = "m3u8"
        if channel_id in ["mytvsuper"]:
            extension = "mpd"
        if channel_id in ["huya", "douyu", "yy", "douyin"]:
            extension = "flv"

        play_url = f"/{channel_id}/{video_id}.{extension}"

        player_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="referrer" content="no-referrer">
            <title>Video Player</title>
            <style>
                html, body {{
                    height: 100%;
                    margin: 0;
                }}
                #player {{
                    width: 100%;
                    height: 100%;
                }}
            </style>
        </head>
        <body>
            <div id="player"></div>
            <script src="https://unpkg.com/artplayer/dist/artplayer.js"></script>
            <script src="https://lf9-cdn-tos.bytecdntp.com/cdn/expire-1-M/hls.js/8.0.0-beta.3/hls.min.js" type="application/javascript"></script>
            <script src="https://lf3-cdn-tos.bytecdntp.com/cdn/expire-1-M/flv.js/1.6.2/flv.min.js" type="application/javascript"></script>
            <script src="https://lf3-cdn-tos.bytecdntp.com/cdn/expire-1-M/dashjs/4.3.0/dash.all.min.js" type="application/javascript"></script>
            <script>
                const playUrl = '{play_url}';
                const art = new Artplayer({{
                    container: '#player',
                    autoplay: true,
                    isLive: true,
                    autoSize: true,
                    setting: true,
                    fullscreen: true,
                    fullscreenWeb: true
                }});

                if (playUrl.endsWith('.m3u8')) {{
                    if (Hls.isSupported()) {{
                        const hls = new Hls();
                        hls.loadSource(playUrl);
                        hls.attachMedia(art.video);
                    }} else if (art.video.canPlayType('application/vnd.apple.mpegurl')) {{
                        art.video.src = playUrl;
                    }}
                }} else if (playUrl.endsWith('.flv')) {{
                    if (flvjs.isSupported()) {{
                        const flvPlayer = flvjs.createPlayer({{
                            type: 'flv',
                            url: playUrl,
                        }});
                        flvPlayer.attachMediaElement(art.video);
                        flvPlayer.load();
                    }}
                }} else if (playUrl.endsWith('.mpd')) {{
                    const dashPlayer = dashjs.MediaPlayer().create();
                    dashPlayer.initialize(art.video, playUrl, true);
                }} else {{
                    art.video.src = playUrl;
                }}
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=player_html)

    try:
        channel = CHANNEL_MAPPINGS.get(channel_id, channel_id)
        channel_module = import_module(".".join(["live", "api", channel]))

        play_url = await channel_module.site.get_play_url(video_id)

        if play_url is None:
            logger.warning(f"Play URL not found for video ID: {video_id}")
            raise HTTPException(status_code=404, detail="Play URL not found")

        if isinstance(play_url, str):
            if play_url.startswith("#EXTM3U"):
                headers = {
                    "Content-Type": "application/vnd.apple.mpegurl",
                    "Content-Disposition": f'attachment; filename="{int(time.time())}.m3u8"',
                }
                return StreamingResponse(iter([play_url.encode()]), headers=headers)
            else:
                logger.info(f"Redirecting to Play URL: {play_url}")
                return RedirectResponse(url=play_url, status_code=302)
        elif isinstance(play_url, bytes):
            headers = {
                "Content-Type": "video/MP2T",
                "Content-Disposition": f'attachment; filename="{int(time.time())}.ts"',
            }
            logger.info(f"Returning TS content for video ID: {video_id}")
            return StreamingResponse(iter([play_url]), headers=headers)
        else:
            logger.error(f"Unexpected response type for video ID: {video_id}")
            raise HTTPException(status_code=500, detail="Unexpected response type")

    except ModuleNotFoundError as e:
        logger.error(f"Module {channel} not found: {e}")
        raise HTTPException(status_code=404, detail="Channel not found")

    parts = domain.split(".")
    if len(parts) > 2:
        return ".".join(parts[-2:])
    return domain


def get_top_level_domain(domain):
    extracted = tldextract.extract(domain)
    return f"{extracted.domain}.{extracted.suffix}"


@app.get("/data/{domain_port}/{path:path}")
async def proxy(request: Request, domain_port: str, path: str):
    logger.info(f"Received proxy request for path: {path}")

    domain, port = domain_port.split(":")
    scheme = "https" if port == "443" else "http"
    base_url = f"{scheme}://{domain}:{port}"

    top_level_domain = get_top_level_domain(domain)
    referer = f"{scheme}://{top_level_domain}/"

    if domain == "sztv-live.sztv.com.cn":
        referer = "https://www.sztv.com.cn/"

    if "ahtv.cn" in domain:
        referer = "https://www.ahtv.cn/"

    if domain == "live-hls.jstv.com":
        referer = "https://live.jstv.com/"

    headers = {
        "referer": referer,
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36}",
    }

    if base_url == "http://198.16.100.186:8278":
        headers.update({"CLIENT-IP": "127.0.0.1", "X-FORWARDED-FOR": "127.0.0.1"})

    path = "/" + path
    if request.url.query:
        path += "?" + request.url.query

    print(f"Proxying to URL: {base_url} ------- {path}")
    print(headers)

    logger.info(f"Proxying to URL: {base_url} ------- {path}")

    return await get_proxy(request, base_url, path, headers)


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8080)
