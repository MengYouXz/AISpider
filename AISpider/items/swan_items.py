from . import BaseItem
from scrapy import Field


class SwanItem(BaseItem):
    app_number = Field()

    app_type = Field()
    app_description = Field()
    status = Field()
    lodged = Field()
    app_location = Field()

    decision = Field()
    determined_date = Field()

    pro_adderss = Field()
    pro_type = Field()
    pro_ward = Field()
    land_area = Field()

    class Meta:
        table = 'swan'
        unique_fields = ['app_number', ]
