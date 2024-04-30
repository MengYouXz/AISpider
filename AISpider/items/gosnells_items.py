from . import BaseItem
from scrapy import Field



class GosnellsItem(BaseItem):
    app_id = Field()
    app_num = Field()
    app_detail = Field()
    status = Field()
    lodged_time = Field()
    determined_time = Field()
    app_outcome = Field()
    officer = Field()
    location = Field()
    description_detail = Field()
    people = Field()
    app_related = Field()
    class Meta:
        table = 'city_of_gosnells'
        unique_fields = ['app_id','app_num']
