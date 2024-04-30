from . import BaseItem
from scrapy import Field


class MoyneItem(BaseItem):

    app_number = Field()
    description = Field()
    address = Field()
    documents = Field()

    class Meta:
        table = 'moyne'
        unique_fields = ['app_number', ]
