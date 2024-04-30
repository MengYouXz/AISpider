from . import BaseItem
from scrapy import Field


class MoiraItem(BaseItem):
    app_number = Field()
    description = Field()
    app_name=Field()
    lodged = Field()
    address = Field()
    documents = Field()

    class Meta:
        table = 'moira'
        unique_fields = ['app_number', ]
