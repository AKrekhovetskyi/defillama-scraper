import logging
from collections.abc import AsyncGenerator, AsyncIterator
from datetime import datetime
from secrets import choice
from typing import TYPE_CHECKING, ClassVar
from zoneinfo import ZoneInfo

import scrapy
from fake_useragent import UserAgent
from lxml import etree  # pyright: ignore[reportAttributeAccessIssue]
from scrapy.http import Request, Response

from defillama_scraper.items import DefillamaScraperItem

if TYPE_CHECKING:
    from playwright.async_api import Page

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ua = UserAgent()
default_request_headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9,uk;q=0.8,ru;q=0.7",
    "cache-control": "no-cache",
    "origin": "https://defillama.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://defillama.com/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": ua.chrome,
}

SCROLL_STEP_MULTIPLIER = 1.7
"""Approximate value obtained by trial and error method. `2` is too big (some values could be missing)."""


class DefillamaSpider(scrapy.Spider):
    name = "defillama"
    allowed_domains: ClassVar[list[str]] = ["defillama.com"]
    start_urls: ClassVar[list[str]] = ["https://defillama.com/chain"]  # pyright: ignore[reportIncompatibleVariableOverride]

    async def start(self) -> AsyncIterator[Request]:
        for url in self.start_urls:
            yield Request(
                url,
                headers=default_request_headers,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "proxy": f"https://{choice(self.settings['PROXY_LIST'])}" if self.settings["PROXY_LIST"] else None,
                },
            )

    async def parse(self, response: Response) -> AsyncGenerator[DefillamaScraperItem]:
        page: Page = response.meta["playwright_page"]
        # The website's frontend in based on the AJAX technology. Moreover, the data also disappear
        # when they are out of the viewport. The only solution to scape such a website is to scroll
        # the webpage incrementally and load the data on each iteration.
        scroll_height = await page.evaluate("document.body.scrollHeight;")
        inner_height = await page.evaluate("window.innerHeight;")
        top_viewport_position = await page.evaluate("window.scrollY;")

        while True:
            dom = etree.HTML(await page.content())
            for row in dom.xpath('//*[@id="table-wrapper"]/div[3]/div'):
                name = row.xpath(".//div[1]/span/a")[0].text
                protocol = row.xpath(".//div[2]")[0].text
                defi_tvl = row.xpath(".//div[3]")[0].text

                if not (name and protocol and defi_tvl):
                    logger.warning("name=%s; protocol=%s; defi_tvl=%s.", name, protocol, defi_tvl)
                    continue

                yield DefillamaScraperItem(
                    name=name.strip(),
                    protocol=int(protocol),
                    defi_tvl=defi_tvl.strip(),
                    created_at=datetime.now(ZoneInfo("Europe/Kyiv")),
                )

            await page.evaluate(f"window.scrollTo({top_viewport_position}, {top_viewport_position + inner_height});")
            if (top_viewport_position + inner_height) >= scroll_height:
                break
            top_viewport_position += round(inner_height * SCROLL_STEP_MULTIPLIER)
