from . import BaseItem
from scrapy import Field


class MaribyrnongItem(BaseItem):
    app_num = Field()
    app_tittle = Field()
    proposal = Field()
    notes = Field()
    location = Field()
    related_information = Field()

    class Meta:
        table = 'maribyrnong_city_council'
        unique_fields = ['app_num']
