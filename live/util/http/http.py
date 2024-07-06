from typing import Any, Dict

from bs4 import BeautifulSoup
from lxml import etree

from live.util.http.http_client import HTTPClient


async def get(url: str, *, params: dict[str, str] = {}, headers: dict[str, str] = {}, **kwargs: Any):
    async with HTTPClient() as http:
        resp = await http.get(url, params=params, headers=headers, **kwargs)
        return resp


async def get_json(url: str, *, params: dict[str, str] = {}, headers: dict[str, str] = {}, **kwargs: Any):
    async with HTTPClient() as http:
        resp = await http.get(url, params=params, headers=headers, **kwargs)
        print(resp.request_info.headers)
        return await resp.json(content_type=None)


async def post(url: str, *, data: Any = None, headers: dict[str, str] = {}, **kwargs: Any):
    async with HTTPClient() as http:
        resp = await http.post(url, data=data, headers=headers, **kwargs)
        return resp


async def post_json(url: str, *, data: Any = None, headers: dict[str, str] = {}, **kwargs: Any):
    async with HTTPClient() as http:
        resp = await http.post(url, data=data, headers=headers, **kwargs)
        return await resp.json(content_type=None)


async def get_text(url: str, *, params: dict[str, str] = {}, headers: dict[str, str] = {}, **kwargs: Any):
    async with HTTPClient() as http:
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
