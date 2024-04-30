from . import BaseItem
from scrapy import Field


class LithgowItem(BaseItem):
    application_id = Field()
    description = Field()
    application_group = Field()
    category = Field()
    sub_category = Field()
    lodged_date = Field()
    stage = Field()
    determined_date = Field()
    name_details = Field()
    properties = Field()

    class Meta:
        table = 'lithgow'
        unique_fields = ['application_id']
