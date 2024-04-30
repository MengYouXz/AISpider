from . import BaseItem
from scrapy import Field


class MurrindindiItem(BaseItem):

    app_number = Field()
    description = Field()
    address = Field()
    date = Field()
    documents = Field()

    class Meta:
        table = 'murrindindi'
        unique_fields = ['app_number', ]
