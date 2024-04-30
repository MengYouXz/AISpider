from . import BaseItem
from scrapy import Field


class PenrithItem(BaseItem):
    app_number = Field()
    description = Field()
    category = Field()
    status = Field()
    lodged = Field()
    estimated_cost = Field()
    officer = Field()
    decision = Field()
    location = Field()
    documents = Field()

    class Meta:
        table = 'penrith'
        unique_fields = ['app_number', ]
