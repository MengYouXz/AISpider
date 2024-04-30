from . import BaseItem
from scrapy import Field


class FremantleItem(BaseItem):
    app_num = Field()
    app_detail = Field()
    app_group = Field()
    app_category = Field()
    app_sub_category = Field()
    app_status = Field()
    lodgement_date = Field()
    stage_decision = Field()
    wapc_ref = Field()
    council_decision = Field()
    wapc_decision = Field()
    no_of_lots = Field()
    date_received = Field()
    council_decision_date = Field()
    wapc_decision_date = Field()
    advertisement_commence = Field()
    advertisement_closing = Field()
    decision_date = Field()
    date_issued = Field()
    detail_address = Field()
    detail_address_description = Field()



    class Meta:
        table = 'city_of_fremantle'
        unique_fields = ['app_num']
