import scrapy
from . import BaseItem


class KwinanaItem(BaseItem):
    application_id = scrapy.Field()
    address = scrapy.Field()
    text = scrapy.Field()
    key_dates = scrapy.Field()
    documents = scrapy.Field()

    class Meta:
        table = 'kwinana'
        unique_fields = ['application_id']