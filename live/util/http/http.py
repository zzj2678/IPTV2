import asyncio
import os
import random
from typing import Any, Dict

from bs4 import BeautifulSoup
from lxml import etree

from live.util.http.http_client import HTTPClient


async def get_proxy():
    if not os.getenv('USE_CN_PROXY'):
        return None

    CN_PROXY = os.getenv('CN_PROXY')
    if CN_PROXY:
        return CN_PROXY

    urls = [
        "https://raw.githubusercontent.com/lalifeier/proxy-scraper/main/proxies/http.txt",
        "https://raw.githubusercontent.com/lalifeier/proxy-scraper/main/proxies/https.txt"
    ]

    proxies = await asyncio.gather(*(get_text(url) for url in urls))
    proxy_list = [proxy.strip().split() for proxy in proxies]
    proxy_list = [item for sublist in proxy_list for item in sublist]

    if not proxy_list:
        return None

    random_proxy = random.choice(proxy_list)

    return "http://" + random_proxy

async def get(url: str, *, params: dict[str, str] = {}, headers: dict[str, str] = {}, **kwargs: Any):
    async with HTTPClient() as http:
        resp = await http.get(url, params=params, headers=headers, **kwargs)
        return resp


async def get_json(url: str, *, params: dict[str, str] = {}, headers: dict[str, str] = {}, use_proxy: bool = False, **kwargs: Any):
    async with HTTPClient() as http:
        if use_proxy:
            proxy = await get_proxy()
            resp = await http.get(url, params=params, headers=headers, proxy=proxy, **kwargs)
        else:
            resp = await http.get(url, params=params, headers=headers, **kwargs)

        return await resp.json(content_type=None)


async def post(url: str, *, data: Any = None, headers: dict[str, str] = {}, **kwargs: Any):
    async with HTTPClient() as http:
        resp = await http.post(url, data=data, headers=headers, **kwargs)
        return resp


async def post_json(url: str, *, data: Any = None, headers: dict[str, str] = {}, **kwargs: Any):
    async with HTTPClient() as http:
        resp = await http.post(url, data=data, headers=headers, **kwargs)
        return await resp.json(content_type=None)


async def get_text(url: str, *, params: dict[str, str] = {}, headers: dict[str, str] = {}, use_proxy: bool = False, **kwargs: Any):
    async with HTTPClient() as http:
        if use_proxy:
            proxy = await get_proxy()
            resp = await http.get(url, params=params, headers=headers, proxy=proxy, **kwargs)
        else:
            resp = await http.get(url, params=params, headers=headers, **kwargs)

        return await resp.text()


async def get_soup(
    url: str, *, params: Dict[str, str] = {}, headers: Dict[str, str] = {}, **kwargs: Any
) -> BeautifulSoup:

    text = await get_text(url, params=params, headers=headers, **kwargs)
    soup = BeautifulSoup(markup=text, features="lxml")
    return soup


async def get_dom(url: str, *, params: Dict[str, str] = {}, headers: Dict[str, str] = {}, **kwargs: Any) -> Any:
    soup = await get_soup(url, params=params, headers=headers, **kwargs)
    dom = etree.HTML(str(soup))
    return dom


async def get_raw(url, *, params: dict[str, str] = {}, headers: dict[str, str] = {}, **kwargs: Any):
    async with HTTPClient() as http:
        resp = await http.get(url, params=params, headers=headers, **kwargs)
        return await resp.read()


async def get_status(url, *, params: dict[str, str] = {}, headers: dict[str, str] = {}, **kwargs: Any):
    async with HTTPClient() as http:
        resp = await http.get(url, params=params, headers=headers, **kwargs)
        return resp.status


async def get_location(url: str, *, params: dict[str, str] = {}, headers: dict[str, str] = {}, **kwargs: Any):
    async with HTTPClient() as http:
        resp = await http.head(url, params=params, headers=headers, **kwargs)
        return resp.url


async def get_cookies(url, *, params: dict[str, str] = {}, headers: dict[str, str] = {}, **kwargs: Any):
    async with HTTPClient() as http:
        resp = await http.get(url, params=params, headers=headers, **kwargs)
        # print(resp.cookies.items())
        # print(resp.headers)
        return resp.cookies


async def head(url: str, params: dict[str, str] = {}, headers: dict[str, str] = {}, **kwargs: Any):
    async with HTTPClient() as http:
        resp = await http.head(url, params=params, headers=headers, **kwargs)
        return resp
