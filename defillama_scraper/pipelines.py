# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from json import dumps, loads

from scrapy.utils.project import get_project_settings

from defillama_scraper.items import DefillamaScraperItem
from defillama_scraper.spiders.defillama import DefillamaSpider

settings = get_project_settings()


class DefillamaScraperPipeline:
    def __init__(self) -> None:
        self.items: list[DefillamaScraperItem] = []

    def process_item(self, item: DefillamaScraperItem, _: DefillamaSpider) -> DefillamaScraperItem:
        self.items.append(item)
        return item

    def remove_duplicate_items(self) -> None:
        unique_items = []
        names = set()
        for item in self.items:
            if item.name.lower() not in names:
                unique_items.append(item)
            names.add(item.name.lower())
        self.items = unique_items

    def close_spider(self, _: DefillamaSpider) -> None:
        protocols = loads(settings.get("BLOCKCHAIN_PROTOCOLS_FILE").read_text() or "[]")
        self.remove_duplicate_items()
        dumped_items = [item.model_dump() for item in self.items]
        protocols.extend(dumped_items)
        settings.get("BLOCKCHAIN_PROTOCOLS_FILE").write_text(dumps(protocols, indent=2))
