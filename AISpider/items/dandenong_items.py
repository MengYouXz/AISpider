import scrapy
from . import BaseItem

class DandenongItem(BaseItem):
    applicationid = scrapy.Field()
    category = scrapy.Field()
    subcategory = scrapy.Field()
    word = scrapy.Field()
    description = scrapy.Field()
    lodged = scrapy.Field()      #time
    cost = scrapy.Field()
    decision = scrapy.Field()
    required = scrapy.Field()     #int
    commenced = scrapy.Field()
    meetingdate = scrapy.Field()   #time
    authdecision = scrapy.Field()
    authdecisiondate = scrapy.Field()  #time
    vcatappeallodgeddate = scrapy.Field()   #time
    vcatdecisiondate = scrapy.Field()   #time
    vcatdecision = scrapy.Field()
    correctiondecision = scrapy.Field()
    applicationamended = scrapy.Field()
    finaloutcome = scrapy.Field()
    finaloutcomedate = scrapy.Field()  #time
    lodgedplannumber = scrapy.Field()  #int
    plancertified = scrapy.Field()    #time
    planrecertified = scrapy.Field()
    statementcompliance = scrapy.Field()
    address = scrapy.Field()
    documents = scrapy.Field()

    class Meta:
        table = 'dandenong'
        unique_fields = ['applicationid']
