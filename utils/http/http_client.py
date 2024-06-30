import logging
from logging import getLogger
from types import TracebackType
from typing import Any, Optional, Type

# import orjson
from aiohttp import ClientSession, ClientTimeout, TCPConnector

from utils.cipers import sslgen
from utils.http.trace_config import get_trace_config

# from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG)

logger = getLogger(__name__)

fake_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Charset": "UTF-8,*;q=0.5",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36",
    "X-FORWARDED-FOR": "118.120.251.92",
    "CLIENT-IP": "118.120.251.92",
}


class HTTPClient:
    session: ClientSession = None

    def __init__(self, session: Optional[ClientSession] = None):
        if session is not None:
            self.session = session
            return

        timeout = ClientTimeout(total=60)
        self.session = ClientSession(
            timeout=timeout,
            # json_serialize=lambda x: orjson.dumps(x).decode(),
            headers=fake_headers,
            trace_configs=[get_trace_config()],
            # trust_env=True,
            connector=TCPConnector(ssl=False),
        )

    async def __aenter__(self):
        await self.session.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.session.close()
        self.session = None

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        await self.session.__aexit__(exc_type, exc_val, exc_tb)

    async def request(self, url: str, method: str = "GET", **kwargs: Any):
        response = await self.session.request(method, url, **kwargs)
        return response

    async def get(self, url: str, **kwargs: Any):
        response = await self.session.get(
            url,
            # ssl=False,
            ssl=sslgen(),
            **kwargs,
        )
        return response

    async def options(self, url: str, **kwargs: Any):
        response = await self.session.options(url, **kwargs)
        return response

    async def head(self, url: str, **kwargs: Any):
        response = await self.session.head(url, **kwargs)
        return response

    async def post(self, url: str, data: Any = None, **kwargs: Any):
        response = await self.session.post(url, data=data, **kwargs)
        return response

    async def put(self, url: str, data: Any = None, **kwargs: Any):
        response = await self.session.put(url, data=data, **kwargs)
        return response

    async def patch(self, url: str, data: Any = None, **kwargs: Any):
        response = await self.session.patch(url, data=data, **kwargs)
        return response

    async def delete(self, url: str, **kwargs: Any):
        response = await self.session.delete(url, **kwargs)
        return response

    async def request_websocket(self, url: str):
        socket = await self.session.ws_connect(url)
        return socket