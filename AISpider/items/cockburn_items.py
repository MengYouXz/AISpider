from . import BaseItem
from scrapy import Field


class CockburnTtem(BaseItem):
    app_number = Field()
    description = Field()
    group_ = Field()
    category = Field()
    sub_category = Field()
    status_ = Field()
    lodgement_date = Field()
    stage = Field()

    address = Field()

    document = Field()
    
 
    class Meta:
        table = 'cockburn'
        unique_fields = ['app_number', ]
