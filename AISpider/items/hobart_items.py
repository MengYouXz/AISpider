from . import BaseItem
from scrapy import Field


class HobartItem(BaseItem):
    app_id = Field()
    app_num = Field()
    app_detail = Field()
    officer = Field()
    data_status = Field()
    app_related = Field()
    location = Field()
    documents = Field()

    class Meta:
        table = 'hobart_city_council'
        unique_fields = ['app_id','app_num']
