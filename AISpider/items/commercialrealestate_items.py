from . import BaseItem
from scrapy import Field


class Commercialrealestate(BaseItem):
    app_number = Field()
    description = Field()
    type_ = Field()

    floor_area = Field()
    land_area = Field()
    parking = Field()
    annual_return = Field()
    availability = Field()
    category = Field()

    address = Field()
    value = Field()
    agent_info = Field()

    closing_date = Field()
    recipient_name = Field()
    delivery_address = Field()


    class Meta:
        table = 'commercialrealestate'
        unique_fields = ['app_number', ]