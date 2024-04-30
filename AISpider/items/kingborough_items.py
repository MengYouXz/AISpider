from . import BaseItem
from scrapy import Field


class KingboroughItem(BaseItem):

    app_num = Field()
    app_address = Field()
    advertised_date = Field()
    closing_date = Field()
    purpose = Field()
    documents = Field()

    class Meta:
        table = 'kingborough'
        unique_fields = ['app_num']
