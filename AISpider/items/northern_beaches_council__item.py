from . import BaseItem
from scrapy import Field


class northern_beaches_council_Item(BaseItem):

    app_id = Field()
    app_num = Field()
    description = Field()
    applicationType = Field()
    status = Field()
    submitted = Field()
    exhibitionPeriod = Field()
    determined = Field()
    determination_level = Field()
    appeal_status = Field()
    cost = Field()
    officer = Field()
    # related = Field()
    location = Field()
    people = Field()
    docs = Field()


    class Meta:
        table = 'northern_beaches_council'
        unique_fields = ['app_id',]
