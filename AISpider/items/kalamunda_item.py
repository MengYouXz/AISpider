from . import BaseItem
from scrapy import Field


class KalamundaItem(BaseItem):
    app_number = Field()
    lodgement_date = Field()
    description = Field()
    applicant = Field()

    name = Field()
    telephone = Field()
    email = Field()

    decision = Field()
    decision_date = Field()

    stage_ = Field()
    start_date = Field()
    end_date = Field()

    class Meta:
        table = 'kalamunda'
        unique_fields = ['app_number', ]
