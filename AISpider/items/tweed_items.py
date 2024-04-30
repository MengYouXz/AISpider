from . import BaseItem
from scrapy import Field


class TweedItem(BaseItem):

    app_id = Field()
    app_num = Field()
    detail_text = Field()

    detail_Lodged_data = Field()
    detail_Determined_data = Field()

    detail_cost = Field()
    detail_officer = Field()
    location = Field()

    people_Applicant = Field()
    documents_url = Field()


    class Meta:
        table = 'tweed_shire_council'
        unique_fields = ['app_id','app_num']
