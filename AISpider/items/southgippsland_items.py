from . import BaseItem
from scrapy import Field


class Southgippsland(BaseItem):
    app_number = Field()
    app_date = Field()
    app_location = Field()
    app_type = Field()
    app_decision = Field()
    status = Field()
    property_address = Field()

    app_task_type = Field()
    actual_started_date = Field()
    actual_completed_date = Field()
    
    
    app_proposal = Field()
    responsible_officer = Field()
    alternate_property_address = Field()
    document = Field()
  
    class Meta:
        table = 'southgippsland'
        unique_fields = ['app_number', ]
