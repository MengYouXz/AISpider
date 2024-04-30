from . import BaseItem
from scrapy import Field


class kyogle_villageItem(BaseItem):

    app_id = Field()
    detail_txt = Field()
    detail_Lodged = Field()
    detail_Determined = Field()
    detail_status = Field()
    detail_cost = Field()
    detail_officer = Field()
    location = Field()
    people = Field()


    class Meta:
        table = 'kyogle_village'
        unique_fields = ['app_id']
