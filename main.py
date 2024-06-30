from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse, StreamingResponse
from starlette.requests import Request
from importlib import import_module
import logging
import time
from utils.proxy import get_proxy
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

app = FastAPI()

CHANNEL_MAPPINGS = {
    # Define your channel mappings here if needed
}

@app.get("/")
async def root():
    return {"hello": "world"}

@app.get("/{channel_id}/{video_id}")
async def get_play_url(channel_id: str, video_id: str):
    logger.info(f"Received request for channel ID: {channel_id} and video ID: {video_id}")

    try:
        channel = CHANNEL_MAPPINGS.get(channel_id, channel_id)
        channel_module = import_module(".".join(["api", channel]))

        play_url = await channel_module.site.get_play_url(video_id)
        
        if play_url is None:
            logger.warning(f"Play URL not found for video ID: {video_id}")
            raise HTTPException(status_code=404, detail="Play URL not found")
        
        if isinstance(play_url, str):
            if play_url.startswith("#EXTM3U"):
                headers = {
                    "Content-Type": "application/vnd.apple.mpegurl",
                    "Content-Disposition": f'attachment; filename="{int(time.time())}.m3u8"'
                }
                return StreamingResponse(iter([play_url.encode()]), headers=headers)
            else:
                logger.info(f"Redirecting to Play URL: {play_url}")
                return RedirectResponse(url=play_url, status_code=302)
        elif isinstance(play_url, bytes):
            headers = {
                "Content-Type": "video/MP2T",
                "Content-Disposition": f'attachment; filename="{int(time.time())}.ts"'
            }
            logger.info(f"Returning TS content for video ID: {video_id}")
            return StreamingResponse(iter([play_url]), headers=headers)
        else:
            logger.error(f"Unexpected response type for video ID: {video_id}")
            raise HTTPException(status_code=500, detail="Unexpected response type")

    except ModuleNotFoundError as e:
        logger.error(f"Module {channel} not found: {e}")
        raise HTTPException(status_code=404, detail="Channel not found")

@app.get("/{channel_id}/{video_id}/data/{path:path}")
async def proxy(request: Request, channel_id: str, video_id: str, path: str):
    logger.info(f"Received proxy request for channel ID: {channel_id}, video ID: {video_id}, path: {path}")
    type_to_headers = {
        'sztv':  {
            'referer': 'https://www.sztv.com.cn/',
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36}",
        },
    }

    headers = type_to_headers[channel_id]

    parsed_url = urlparse(path)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    path = parsed_url.path
    if request.url.query:
        path += "?" + request.url.query

    return await get_proxy(request, base_url, path, headers)

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8080)
