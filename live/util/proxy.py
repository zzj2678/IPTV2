from aiohttp import ClientSession
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import StreamingResponse


async def get_proxy(request: Request, base_url, path, headers=None):
    client = ClientSession(base_url, auto_decompress=False)
    resp = await client._request(
        method=request.method,
        headers=headers,
        str_or_url=path,
        data=request.stream(),
        allow_redirects=False,
    )

    response_headers = dict(resp.headers)

    return StreamingResponse(
        content=resp.content.iter_any(),
        status_code=resp.status,
        headers=response_headers,
        background=BackgroundTask(client.close),
    )