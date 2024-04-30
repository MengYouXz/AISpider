import scrapy
from scrapy.http import Response



from AISpider.items.maribyrnong_items import  MaribyrnongItem
from common._string import except_blank


class maribyrnong_city_council_spider(scrapy.Spider):
    """
    gave up retrying
    """
    name = "maribyrnong"
    allowed_domains = ["maribyrnong.vic.gov.au.com"]
    start_urls = ["https://www.maribyrnong.vic.gov.au/Advertised-Planning-Applications"]


    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        # 'menu_Sub': 'hide',

    }

    custom_settings = {
        # 'ITEM_PIPELINES': {
        #     "AISpider.pipelines.AispiderPipeline": None,
        # }
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'LOG_STDOUT': True,
        # 'LOG_FILE': 'scrapy_kyogle.log',
        'DOWNLOAD_TIMEOUT': 1200
    }

    index = 1

    def __init__(self, *args, **kwargs):
        super(maribyrnong_city_council_spider, self).__init__(*args, **kwargs)
        self.cookie = None

    def start_requests(self):

        for url in self.start_urls:
            yield scrapy.Request(url, method="GET", dont_filter=True, headers=self.headers )

    def parse(self, response: Response, **kwargs: any):
        url_list=response.xpath('//div[@class="list-item-container"]/article/a/@href').getall()

        for item in url_list:

            yield scrapy.Request(url=item, method="GET", dont_filter=True,
                                  callback=self.parse_detail
                                 )

    def parse_detail(self, response: Response, **kwargs: any):
        app_tittle =''.join(response.xpath('//div[@class="col-xs-12 col-m-8"]/h1/text()').getall())
        appdetails_src = response.xpath('//div[@class="col-xs-12 col-m-8"]/ul/li/span/text()').getall()

        details = {}
        for  i in range(len(appdetails_src)) :
            if  i%2==0 :
                details[appdetails_src[i].strip()] =appdetails_src[i+1].strip()
            i+=1
        location =except_blank(response.xpath('//div[@class="col-xs-12 col-m-8"]/p/text()').getall())
        location=''.join([''.join(item.replace('\xa0','')) for item in location])

        related_information =response.xpath('//ul[@class="related-information-list"]/li/a/@href').getall()or None
        for i in range(0, len(related_information)):
            related_information[i] = related_information[i].strip()

            if (related_information[i])[0] == '/' and related_information != None:

                related_information[i] = 'https://www.maribyrnong.vic.gov.au' + related_information[i]

        related_information= '@@'.join([item.strip() for item in related_information ])


        app_num=details["Application number"] if "Application number" in list(details.keys()) else None
        proposal=details["Proposal"] if "Proposal" in list(details.keys()) else None
        notes=details["Notes"] if "Notes" in list(details.keys()) else None

        
        item = MaribyrnongItem()
        item["app_num"] = app_num or  None
        item["app_tittle"] = app_tittle or  None
        item["proposal"] = proposal or  None
        item["notes"] = notes or  None
        item["location"] = location or  None
        item["related_information"] = related_information or  None
        yield item