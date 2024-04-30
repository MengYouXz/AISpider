import scrapy
from . import BaseItem

class ArmadaleItem(BaseItem):
    title = scrapy.Field()
    feedback_closes = scrapy.Field()
    address = scrapy.Field()
    text = scrapy.Field()
    documents = scrapy.Field()

    class Meta:
        table = 'armadale'
        unique_fields = ['title']