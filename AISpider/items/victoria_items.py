from . import BaseItem
from scrapy import Field


class town_of_victoria_parkSpider_Item(BaseItem):

    app_id = Field()
    app_location = Field()
    app_data_post = Field()
    app_data_closing = Field()
    app_detail_text = Field()
    people_name = Field()
    people_office = Field()
    people_phone = Field()
    people_email = Field()
    documents = Field()


    class Meta:
        table = 'town_of_victoria_park'
        unique_fields = ['app_id']
