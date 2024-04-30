from . import BaseItem
from scrapy import Field

# {app_id}--{app_num}--{app_type}--{date_received}--{proposal}--{status}--{location_ward}--{people}
class StirlingItem(BaseItem):

    app_num = Field()
    description = Field()
    primary_group = Field()
    group_ = Field()
    primary_category = Field()
    category = Field()
    sub_category = Field()
    stage_decision = Field()
    estimated_cost = Field()
    formatted_address = Field()
    suburb = Field()
    street = Field()
    initial_target = Field()
    current_target = Field()
    status = Field()
    year = Field()
    charge_balance = Field()
    house_No = Field()
    property_name = Field()


    class Meta:
        table = 'city_of_stirling'
        unique_fields = ['app_num']
