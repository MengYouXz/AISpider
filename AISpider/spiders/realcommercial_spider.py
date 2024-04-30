import math
import re
import scrapy
from scrapy.http import Response
from AISpider.items.realcommercial_items import RealcommercialItem
from common._string import except_blank, data_wash_tag


class RealcommercialSpider(scrapy.Spider):
    """
    gave up retrying
    """
    name = "realcommercial"
    allowed_domains = ["www.realcommercial.com.au"]
    start_urls = [
        #格式为：url,名字分类
        'https://www.realcommercial.com.au/for-sale/?includePropertiesWithin=includesurrounding&keywords=childcare,childcare for sale',#363
        'https://www.realcommercial.com.au/for-lease/?includePropertiesWithin=includesurrounding&keywords=childcare%0A,childcare for lease',#586
        'https://www.realcommercial.com.au/sold/?includePropertiesWithin=includesurrounding&keywords=childcare%0A,childcare sold',#2077
        'https://www.realcommercial.com.au/leased/?includePropertiesWithin=includesurrounding&keywords=childcare,childcare leased',#1414
        'https://www.realcommercial.com.au/for-sale/?includePropertiesWithin=includesurrounding&keywords=retirement%2Bvillage%0A,Retirement Village for sale',#755
        'https://www.realcommercial.com.au/for-sale/land-development/?includePropertiesWithin=includesurrounding,development site for sale',#3497
        'https://www.realcommercial.com.au/sold/land-development/?includePropertiesWithin=includesurrounding,development site sold'#10000
    ]
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
        # 'LOG_FILE': 'scrapy_realcommercial.log',
        'DOWNLOAD_TIMEOUT': 1200
    }

    index = 1

    def __init__(self, *args, **kwargs):
        super(RealcommercialSpider, self).__init__(*args, **kwargs)
        self.cookie = None

    def start_requests(self):
        """
        添加请求负载
        """

        for url in self.start_urls:
            url_list = url.split(',', 1)[0]
            app_model = url.split(',', 1)[1]
            yield scrapy.Request(url_list, method="GET", dont_filter=True, headers=self.headers,
                                 meta={'app_model': app_model, 'url_list': url_list})

    def parse(self, response: Response, **kwargs: any):
        url_list=response.meta.get('url_list')
        app_model = response.meta.get('app_model')
        error_text = ''.join(
            except_blank(response.xpath('//div[@class="Message_reminderBoxContainer_1K0jd"]/h3/text()').getall()))
        page_title = ''.join(
            except_blank(response.xpath('//span[@class="SearchResultsHeader_availableResults_2ahBB"]/text()').getall()))
        page_number = ''.join(re.findall("of (.*) ", page_title, re.DOTALL))

        if page_number=='4000+':
            page_number=10000
        for page in range(1,(math.ceil(int(page_number) / 10)+1)):#(math.ceil(int(page_number) / 10)+1)
            if error_text != "We couldn't find anything that quite matches your search.":
                url = url_list + f'&page={page}'
                yield scrapy.Request(url, method="GET", headers=self.headers, callback=self.parse_list,
                                     meta={'app_model': app_model,'page': page})
    def parse_list(self, response):
        app_model = response.meta.get('app_model')
        page = response.meta.get('page')
        detail_url = response.xpath('//a[@class="Address_link_1aaSW"]/@href').getall()
        for url in detail_url:

            if re.findall("https://www.realcommercial.com.au", url):
                app_id = re.findall("#(\d+)", url, re.DOTALL)[-1]
                yield scrapy.Request(url, method="GET", headers=self.headers,
                                     callback=self.parse_detail1,
                                     meta={'app_model': app_model, 'app_id': app_id, 'page': page})
            else:
                url = 'https://www.realcommercial.com.au' + url
                app_id = re.findall("-(\d+)", url, re.DOTALL)[-1]
                yield scrapy.Request(url, method="GET", headers=self.headers,
                                 callback=self.parse_detail, meta={'app_model': app_model, 'app_id': app_id,'page':page})

    def parse_detail(self, response):

        location = ''.join(except_blank(
            response.xpath('//div[@class="PrimaryDetailsTop_addressWrapper_30LL5"]/h1/span/text()').getall()))
        purpose_to = ''.join(
            except_blank(response.xpath('//div[@class="PrimaryDetailsTop_propertyTypes_1mGFK"]/text()').getall()))
        key_information={}
        price_information = ''.join(
            except_blank(response.xpath('//div[@class="Price_priceLabel_18amG"]/text()').getall()))
        key_information_title = except_blank(
            response.xpath('//div[@class="AttributesPanel_main_Tn4u3"]/div/div/p/text()').getall())
        key_information_data = except_blank(
            response.xpath('//div[@class="AttributesPanel_main_Tn4u3"]/div/button/p/text()').getall())
        if len(key_information_title) == len(key_information_data):
            key_information = dict(zip(key_information_title, key_information_data))
            if "Leased on" in list(key_information.keys()):
                price_information = key_information["Leased on"]

        description = ''.join(data_wash_tag(
            except_blank(response.xpath('//div[@class="PrimaryDetailsBottom_detailsWrapper_Q1KTD"]').getall())))

        people_name = ''.join(
            except_blank(response.xpath('//a[@class="AgencyPanel_agencyNameLink_nCd-h"]/text()').getall()))
        people_address = ''.join(
            except_blank(response.xpath('//address[@class="AgencyPanel_agencyAddress_aTG-m"]/text()').getall()))

        item = RealcommercialItem()
        item["app_model"] = response.meta.get('app_model') or None
        item["app_id"] = response.meta.get('app_id') or None
        item["location"] = location  or None
        item["purpose_to"] = purpose_to or None
        item["price_information"] = price_information or None

        item["land_area"] = key_information["Land area"] if "Land area" in list(key_information.keys()) else None
        item["floor_area"] = key_information["Floor area"] if "Floor area" in list(key_information.keys()) else None
        item["property_extent"] = key_information["Property extent"] if "Property extent" in list(
            key_information.keys()) else None
        item["tenure_type"] = key_information["Tenure type"] if "Tenure type" in list(key_information.keys()) else None
        item["car_spaces"] = key_information["Car spaces"] if "Car spaces" in list(key_information.keys()) else None
        item["parking_info"] = key_information["Parking info"] if "Parking info" in list(
            key_information.keys()) else None
        item["municipality"] = key_information["Municipality"] if "Municipality" in list(
            key_information.keys()) else None
        item["sold_on"] = key_information["Sold on"] if "Sold on" in list(key_information.keys()) else None
        item["zoning_"] = key_information["Zoning"] if "Zoning" in list(key_information.keys()) else None

        item["description"] = description or None
        item["people_name"] = people_name or None
        item["people_address"] = people_address or None

        yield item
    def parse_detail1(self, response):
        location = ''.join(except_blank(
            response.xpath('//div[@class="building-basic-info"]/h1/span/text()').getall()))
        purpose_to = ''.join(
            except_blank(response.xpath('//div[@class="building-basic-info"]/h1/ul/li/p/text()').getall()))
        key_information={}
        price_information = ''.join(
            except_blank(response.xpath('//div[@class="Price_priceLabel_18amG"]/text()').getall()))
        key_information_title = except_blank(
            response.xpath('//div[@class="AttributesPanel_main_Tn4u3"]/div/div/p/text()').getall())
        key_information_data = except_blank(
            response.xpath('//div[@class="AttributesPanel_main_Tn4u3"]/div/button/p/text()').getall())
        if len(key_information_title) == len(key_information_data):
            key_information = dict(zip(key_information_title, key_information_data))
            if "Leased on" in list(key_information.keys()):
                price_information = key_information["Leased on"]

        description = ''.join(data_wash_tag(
            except_blank(response.xpath('//section[@class="building-summary padded-layout rui-clearfix"]').getall())))

        people_name = ''.join(
            except_blank(response.xpath('//span[@class="customer-name text-truncate"]/text()').getall()))
        people_address = ''.join(
            except_blank(response.xpath('//address[@class="customer-address"]/span/text()').getall()))

        item = RealcommercialItem()
        item["app_model"] = response.meta.get('app_model') or None
        item["app_id"] = response.meta.get('app_id') or None
        item["location"] = location  or None
        item["purpose_to"] = purpose_to or None
        item["price_information"] = price_information or None

        item["land_area"] = key_information["Land area"] if "Land area" in list(key_information.keys()) else None
        item["floor_area"] = key_information["Floor area"] if "Floor area" in list(key_information.keys()) else None
        item["property_extent"] = key_information["Property extent"] if "Property extent" in list(
            key_information.keys()) else None
        item["tenure_type"] = key_information["Tenure type"] if "Tenure type" in list(key_information.keys()) else None
        item["car_spaces"] = key_information["Car spaces"] if "Car spaces" in list(key_information.keys()) else None
        item["parking_info"] = key_information["Parking info"] if "Parking info" in list(
            key_information.keys()) else None
        item["municipality"] = key_information["Municipality"] if "Municipality" in list(
            key_information.keys()) else None
        item["sold_on"] = key_information["Sold on"] if "Sold on" in list(key_information.keys()) else None
        item["zoning_"] = key_information["Zoning"] if "Zoning" in list(key_information.keys()) else None

        item["description"] = description or None
        item["people_name"] = people_name or None
        item["people_address"] = people_address or None

        yield item
