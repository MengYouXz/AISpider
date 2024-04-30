import copy
import re
from datetime import datetime
from pathlib import Path
from time import sleep
from urllib.parse import urlencode

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy import Selector
import scrapy

from scrapy.http import Response

from AISpider.items.stirling_items import StirlingItem
from common._string import except_blank, remove_non_printable


class StirlingSpider(scrapy.Spider):
    """
    gave up retrying
    """
    name = "stirling"
    allowed_domains = ["stirling-web.t1cloud.com"]
    start_urls = [
        "https://stirling-web.t1cloud.com/T1PRDefault/WebApps/eProperty/API/Templates/NavigationMenu-WEBGUEST.html",
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
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
        super(StirlingSpider, self).__init__(*args, **kwargs)
        self.cookie = None

    def start_requests(self):
        """
        添加请求负载
        """
        # self.update_cookie()

        for url in self.start_urls:
            yield scrapy.Request(url, method="GET", dont_filter=True, cookies=self.cookie, headers=self.headers)

    def parse(self, response: Response, **kwargs: any):
        # print(response.text)
        model_url = except_blank(
            response.xpath('//header[@id="header"]/nav/ul/li[5]/div/div/div/section/ul/li/a/@href').getall())
        for i in range(1, len(model_url)):
            url = 'https://stirling-web.t1cloud.com' + model_url[i].strip()
            # print(url)
            yield scrapy.Request(url, method="GET", dont_filter=True, cookies=self.cookie, headers=self.headers,
                                 callback=self.parse_list)

    def parse_list(self, response: Response, **kwargs: any):

        total_text = except_blank(response.xpath(
            '//div[@id="ctl00_Content_cusResultsGrid_pnlCustomisationGrid"]/div/table/tr[1]/td/script/text()').getall())
        for item in total_text:
            app_num = re.findall('>(.*?)</a>', item, re.DOTALL)
            app_num_tars = [item.replace('/', '%2f').strip() for item in app_num][0]
            url = f'https://stirling-web.t1cloud.com/T1PRDefault/WebApps/eProperty/P1/eTrack/eTrackApplicationDetails.aspx?r=P1.WEBGUEST&f=$P1.ETR.APPDET.VIW&ApplicationId={app_num_tars}'
            yield scrapy.Request(url, method="GET", dont_filter=True, cookies=self.cookie, headers=self.headers,
                                 callback=self.parse_detail)

    def parse_detail(self, response):
        # print(response.text)
        title = ''.join(except_blank(response.css(
            '#ctl00_Content_cusPageComponents_repPageComponents_ctl00_lblComponentHeading::text').extract()))
        details = {}
        if title == 'Application Details':
            th = except_blank(response.xpath(
                '//table[@id="ctl00_Content_cusPageComponents_repPageComponents_ctl00_cusPageComponentGrid_repWebGrid_ctl00_dtvWebGridListView"]/tr/td[1]/text()').getall())
            text = [item.replace('\xa0', '') for item in response.xpath(
                '//table[@id="ctl00_Content_cusPageComponents_repPageComponents_ctl00_cusPageComponentGrid_repWebGrid_ctl00_dtvWebGridListView"]/tr/td[2]/text()').getall()]
            if len(th) == len(text):
                for i in range(len(th)):
                    details[th[i]] = text[i]
            else:
                print('error')
        else:
            details['Application ID'] = ''.join(
                except_blank(response.xpath('//div[@id="ApplicationID"]/text()').getall()))
            details['Formatted Address'] = ''.join(
                except_blank(response.xpath('//div[@class="formattedAddress"]/text()').getall()))
            details['Description'] = ''.join(
                except_blank(response.xpath('//div[@class="Rtable-cell"][1]/text()').getall()))
            details['Category'] = ''.join(
                except_blank(response.xpath('//div[@class="Rtable-cell"][2]/text()').getall()))
            details['Sub Category'] = ''.join(
                except_blank(response.xpath('//div[@class="Rtable-cell"][3]/text()').getall()))
            details['Stage/Decision'] = ''.join(
                except_blank(response.xpath('//div[@class="Rtable-cell"][4]/text()').getall()))
            details["Primary Group"]= None
            details["Group"] =None
            details["Primary Category"]= None
            details["Estimated Cost"] =None
            details["Suburb"] = None
            details["Street"] =None
            details["Initial Target"]=  None
            details["Current Target"] = None
            details["Status"]=  None
            details["Year"]= None
            details["Charge Balance"] =None
            details["House No"] =None
            details["Property Name"]= None

        item = StirlingItem()

        item["app_num"] = details["Application ID"] if "Application ID" in list(details.keys()) else None
        item["description"] = details["Description"] if "Description" in list(details.keys()) else None
        item["primary_group"] = details["Primary Group"] if "Primary Group" in list(details.keys()) else None
        item["group_"] = details["Group"] if "Group" in list(details.keys()) else None
        item["primary_category"] = details["Primary Category"] if "Primary Category" in list(details.keys()) else None
        item["category"] = details["Category"] if "Category" in list(details.keys()) else None
        item["sub_category"] = details["Sub Category"] if "Sub Category" in list(details.keys()) else None
        item["stage_decision"] = details["Stage/Decision"] if "Stage/Decision" in list(details.keys()) else None
        item["estimated_cost"] = details["Estimated Cost"] if "Estimated Cost" in list(details.keys()) else None
        item["formatted_address"] = details["Formatted Address"] if "Formatted Address" in list(details.keys()) else None
        item["suburb"] = details["Suburb"] if "Suburb" in list(details.keys()) else None
        item["street"] = details["Street"] if "Street" in list(details.keys()) else None
        item["initial_target"] = datetime.strptime(details["Initial Target"] ,'%d/%m/%Y').timestamp() if "Initial Target" in list(details.keys())and details["Initial Target"]!='' else None
        item["current_target"] = datetime.strptime(details["Current Target"] ,'%d/%m/%Y').timestamp() if "Current Target" in list(details.keys())and details["Current Target"]!='' else None

        # item["initial_target"] = details["Initial Target"] if "Initial Target" in list(details.keys()) else None
        # item["current_target"] = details["Current Target"] if "Current Target" in list(details.keys()) else None
        item["status"] = details["Status"] if "Status" in list(details.keys()) else None
        item["year"] = details["Year"] if "Year" in list(details.keys()) else None
        item["charge_balance"] = details["Charge Balance"] if "Charge Balance" in list(details.keys()) else None
        item["house_No"] = details["House No"] if "House No" in list(details.keys()) else None
        item["property_name"] = details["Property Name"] if "Property Name" in list(details.keys()) else None

        yield item
