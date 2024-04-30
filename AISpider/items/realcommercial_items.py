from . import BaseItem
from scrapy import Field

# {app_id}--{app_num}--{app_type}--{date_received}--{proposal}--{status}--{location_ward}--{people}
class RealcommercialItem(BaseItem):
    app_model=Field()
    app_id=Field()
    location = Field()
    purpose_to = Field()
    price_information = Field()

    land_area = Field()
    floor_area = Field()
    property_extent = Field()
    tenure_type = Field()
    car_spaces = Field()
    parking_info = Field()
    municipality = Field()
    sold_on = Field()
    zoning_ = Field()


    description = Field()
    people_name = Field()
    people_address = Field()
    # page = Field()


    class Meta:
        table = 'realcommercial'
        unique_fields = ['app_id']
