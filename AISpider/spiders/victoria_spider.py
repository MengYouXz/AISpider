import re
import scrapy
from scrapy.http import Response
from AISpider.items.victoria_items import town_of_victoria_parkSpider_Item
from common._string import except_blank
import time
from datetime import date, datetime, timedelta
from common._date import get_all_month
# from common.set_date import get_this_month

class VictoriaSpider(scrapy.Spider):
    """
    gave up retrying
    """
    name = "town_of_victoria_park"
    allowed_domains = ["victoriapark.wa.gov.au"]
    start_urls = ["https://www.victoriapark.wa.gov.au/consultations/development-applications", ]

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
        super(VictoriaSpider, self).__init__(*args, **kwargs)
        self.cookie = None

    def start_requests(self):
        """
        添加请求负载
        """

        for url in self.start_urls:
            yield scrapy.Request(url, method="GET", dont_filter=True, headers=self.headers, )

    def parse(self, response: Response, **kwargs: any):
        # print(response.text)
        url_list = except_blank(
            response.xpath('//div[@class="consultation-item panel panel-default"]/div/div/div/a/@href').getall())
        for url in url_list:
            url = 'https://www.victoriapark.wa.gov.au' + url
            yield scrapy.Request(url, method="GET", dont_filter=True, headers=self.headers, callback=self.parse_detail)

    def parse_detail(self, response: Response, **kwargs: any):

        # print(response.text)
        app_title = except_blank(response.xpath('//section[@class="main-channel col-md-8"]/h1/text()').getall())
        for item in app_title:
            if len(item.split('-', 1)) == 2:
                app_id = item.split('-', 1)[0]
                app_location = item.split('-', 1)[1]
        app_data = except_blank(
            response.xpath('//section[@class="main-channel col-md-8"]/p[@class="dateline"]/text()').getall())
        if len(app_data) == 2:
            app_data_post = datetime.strptime(app_data[0],'%d/%m/%Y').timestamp()
            app_data_closing = datetime.strptime(''.join(re.findall('(\d+/\d+/\d+)',app_data[1])),'%d/%m/%Y').timestamp()
        else:
            app_data_post = app_data_closing = None
        app_detail_text = except_blank(
            response.xpath('//section[@class="main-channel col-md-8"]/div[@class="detail"]/ul').getall())
        if app_detail_text==[]:
            app_detail_text = except_blank(
                response.xpath('//section[@class="main-channel col-md-8"]/div[@class="detail"]/ol').getall())
        app_detail_text = datawash(app_detail_text)
        app_contant_titile = except_blank(response.xpath('//div[@class="panel-body"]/p/strong/text()').getall())
        app_contant_text = except_blank(response.xpath('//div[@class="panel-body"]/p/text()').getall())
        app_contant_text_email=except_blank(response.xpath('//div[@class="panel-body"]/p/a/text()').getall())
        app_contant_text.append(app_contant_text_email[0])
        if len(app_contant_titile)==len(app_contant_text):
            detail=dict(zip(app_contant_titile,app_contant_text))

        documents=except_blank(response.xpath('//div[@class="panel-body"]/div/blockquote/p/a/@href').getall())
        documents="".join(["https://www.victoriapark.wa.gov.au" + documents[i]+ "@@" for i in range(len(documents))])
        # print(documents)

        item = town_of_victoria_parkSpider_Item()
        item["app_id"] = ''.join(app_id)
        item["app_location"] = ''.join(app_location)
        item["app_data_post"] =app_data_post
        item["app_data_closing"] =app_data_closing
        item["app_detail_text"] =''.join(app_detail_text)
        item["people_name"] = detail['Name:']if "Name:" in list(detail.keys()) else None
        item["people_office"] = detail['Job Title:']if "Job Title:" in list(detail.keys()) else None
        item["people_phone"] = detail['Phone:']if "Phone:" in list(detail.keys()) else None
        item["people_email"] = detail['Email:']if "Email:" in list(detail.keys()) else None
        item["documents"] = ''.join(documents)

        yield item


def datawash(data_list):
    for item in range(len(data_list)):
        data_list[item] =re.sub('<.*?>','',data_list[item])
        data_list[item] =re.sub(r'[^\x20-\x7E]', '', data_list[item])
        data_list[item]=data_list[item].replace('\\','')
    return data_list


