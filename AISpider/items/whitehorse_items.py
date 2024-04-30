from . import BaseItem
from scrapy import Field


class WhitehorseItem(BaseItem):
    app_number = Field()
    name_details = Field()
    decision_type = Field()
    decision_date = Field()
    app_class = Field()
    app_type = Field()
    app_description = Field()
    location = Field()
    status = Field()
    current_decision = Field()
    application_date = Field()
    lodgement_date = Field()
    to_be_commenced_by_date = Field()
    expiry_date = Field()
    office = Field()
    start_date = Field()
    document = Field()
    class Meta:
        table = 'whitehorse'
        unique_fields = ['app_number', ]
