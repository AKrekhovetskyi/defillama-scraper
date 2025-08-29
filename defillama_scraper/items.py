# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from datetime import datetime

from pydantic import BaseModel, PositiveInt, field_serializer


class DefillamaScraperItem(BaseModel):
    name: str
    protocol: PositiveInt
    defi_tvl: str
    created_at: datetime

    @field_serializer("created_at")
    @staticmethod
    def serialize_created_at(created_at: datetime) -> str:
        return created_at.isoformat()
