from . import BaseItem
from scrapy import Field

# {app_id}--{app_num}--{app_type}--{date_received}--{proposal}--{status}--{location_ward}--{people}
class domainItem(BaseItem):
    total_title=Field()
    total_location=Field()
    total_information=Field()
    project_highlights=Field()
    total_description=Field()

    app_model=Field()
    app_id=Field()
    location = Field()
    app_title = Field()
    app_status = Field()
    purpose_to = Field()
    property_features = Field()

    count_beds = Field()
    count_baths = Field()
    parking_info = Field()
    land_area = Field()

    description = Field()
    domain_says = Field()
    people_name = Field()
    people_address = Field()


    class Meta:
        table = 'domain'
        unique_fields = ['app_id']
