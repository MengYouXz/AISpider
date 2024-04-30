import scrapy
from . import BaseItem
class WollongongItem(BaseItem):
    app_number = scrapy.Field()
    ApplicationType = scrapy.Field()
    SiteName = scrapy.Field()
    Description = scrapy.Field()
    Lodged = scrapy.Field()    #time
    Accepted = scrapy.Field()  #time
    Determined = scrapy.Field()
    Effective = scrapy.Field()  #time
    ModificationCategory = scrapy.Field()  #Modification Category
    development = scrapy.Field()        # Is the development Integrated Development?
    NSWPlanningPortal = scrapy.Field()  #Enter the NSW Planning Portal Reference number.
    notification = scrapy.Field()    #Is notification of the Review required?
    dwellinghouse = scrapy.Field() #Does the development involve the erection of a dwelling house with Cost of Works of less than $100,000
    Lapsed = scrapy.Field()  #time
    Completed = scrapy.Field()  #time
    Progress = scrapy.Field()
    People = scrapy.Field()
    Associations = scrapy.Field()
    documents = scrapy.Field()

    class Meta:
        table = 'wollongong'
        unique_fields = ['app_number']