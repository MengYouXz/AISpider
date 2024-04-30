import re
from datetime import datetime
import scrapy

from scrapy.http import Response

from AISpider.items.kingborough_items import KingboroughItem
from common._string import except_blank


class KingboroughSpider(scrapy.Spider):
    """
    gave up retrying
    """
    name = "kingborough"
    allowed_domains = ["apply.hobartcity.com.au"]
    start_urls = ["https://www.kingborough.tas.gov.au/development/planning-notices/",]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'menu_Sub': 'hide',

    }

    custom_settings = {
        # 'ITEM_PIPELINES': {
        #     "AISpider.pipelines.AispiderPipeline": None,
        # }
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'LOG_STDOUT': True,
        # 'LOG_FILE': 'scrapy_tweed.log',
        'DOWNLOAD_TIMEOUT': 1200
    }

    index = 1

    def __init__(self, *args, **kwargs):
        super(KingboroughSpider, self).__init__(*args, **kwargs)
        self.cookie = None

    def start_requests(self):
        """
        添加请求负载
        """

        for url in self.start_urls:
            yield scrapy.Request(url, method="GET", dont_filter=True, headers=self.headers, )

    def parse(self, response: Response, **kwargs: any):
        data={}
        detail_title=except_blank(response.css('#list thead tr th::text').extract())
        detail_data=except_blank(response.xpath('//table[@id="list"]/tbody/tr/td').getall())
        for i in range(1,len(detail_data)+1):
            if i % 6 != 0:
                detail_data[i-1]=detail_data[i-1].replace('<td>','').replace('</td>','')
                data[detail_title[(i-1)%6]]=detail_data[i-1]
            else:
                matches = re.findall('href="(.*?)" class=', detail_data[i-1], re.DOTALL)
                detail_data[i-1]=''.join([item+'@@' for item in matches])
                data[detail_title[(i-1)%6]]=detail_data[i-1]

                item = KingboroughItem()
                item["app_num"] = data['Reference Number']
                item["app_address"] = data['Address']
                item["advertised_date"] =datetime.strptime(data['Submission Closing Date'], '%d %b %Y').timestamp()
                item["closing_date"] =datetime.strptime(data['Submission Closing Date'], '%d %b %Y').timestamp()
                item["purpose"] = data['Purpose']
                item["documents"] = data['More Info']

                yield item
# date_obj = datetime.strptime(data['Submission Closing Date'], '%d %b %Y').timestamp()
#
# timestamp = date_obj.timestamp()