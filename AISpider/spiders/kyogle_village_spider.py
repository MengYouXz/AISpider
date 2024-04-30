import re
from datetime import date, datetime, timedelta
from pathlib import Path
import scrapy
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import copy
import json
import requests
import scrapy
from scrapy import Selector
from scrapy.http import Response
from urllib.parse import urlencode

# from AISpider.items.chcc_items import CHCCItem
from common._date import get_all_month, get_last_days

# from AISpider.AISpider.items.tweed_items import TweedItem
from common._string import except_blank

from AISpider.items.kyogle_village_items import kyogle_villageItem


class KyogleSpider(scrapy.Spider):
    """
    gave up retrying
    """
    name = "kyogle_village"
    allowed_domains = ["etrack.kyogle.nsw.gov.au.com"]
    start_urls = ["https://etrack.kyogle.nsw.gov.au/Pages/XC.Track/SearchApplication.aspx"]

    term_url = "https://etrack.kyogle.nsw.gov.au/Common/Common/terms.aspx"  # 同意页面url

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
        super(KyogleSpider, self).__init__(*args, **kwargs)
        self.cookie = None

    def start_requests(self):
        """
        添加请求负载
        """
        self.update_cookie()
        for url in self.start_urls:
            yield scrapy.Request(url, method="GET", dont_filter=True, headers=self.headers, cookies=self.cookie)

    def parse(self, response: Response, **kwargs: any):
        url_list=response.css('#i1 a::attr(href)').extract()
        for item in url_list:
            item='https://etrack.kyogle.nsw.gov.au/'+item.replace('../../','')
            yield scrapy.Request(url=item, method="GET", dont_filter=True,
                                  callback=self.parse_list
                                 )

    def parse_list(self, response: Response, **kwargs: any):
        url_details =response.xpath('//div[@id="hiddenresult"]/div[@class="result"]/div[2]/a[1]/@href').getall()

        for item in url_details:
            # app_id = item.split('=', 1)[1]
            item='https://etrack.kyogle.nsw.gov.au/'+item.replace('../../','')
            # print(item)
            yield scrapy.Request(item, method="GET", dont_filter=True,
                                 callback=self.parse_detail
                                 )

    def parse_detail(self, response):
        app_id=response.css('#ctl00_ctMain_info_pnlApplication div h2::text').extract_first()
        detail_text=except_blank(response.css('#ctl00_ctMain_info_pnlApplication #b_ctl00_ctMain_info_app::text').extract())
        #多条数据，需要处理
        detail_txt = detail_text[0].split('\r\n\t\t')[0].strip()
        detail_Lodged = detail_text[1].split(':')[1].strip()
        if detail_Lodged !='//':
            detail_Lodged = datetime.strptime(detail_Lodged,'%d/%m/%Y').timestamp()
        else:
            detail_Lodged =None
        if detail_text[2].split(':',1)[0].strip() =="Determined":
            # detail_Determined = detail_text[2].split('\r\n\t\t')[1].strip()
            detail_Determined = detail_text[2].split('\r\n\t\t')[1].strip()
            detail_Determined = datetime.strptime(detail_Determined,'%d/%m/%Y').timestamp()
            detail_status = detail_text[3].split(' ', 1)[1].strip()
            detail_cost = detail_text[4].split('\r\n\t\t')[1].strip()
            detail_officer = detail_text[5].split(':')[1].strip()
        elif detail_text[2].split(':',1)[0].strip() =="Estimated Cost of Work":
            detail_Determined = None
            detail_status = None
            detail_cost = detail_text[2].split('\r\n\t\t')[1].strip()
            detail_officer = detail_text[3].split(':')[1].strip()

        location=response.css('#b_ctl00_ctMain_info_prop a::text').extract_first()
        people=except_blank(response.css('#b_ctl00_ctMain_info_party::text').extract())#两条数据
        people_null=""
        for item in people:
           people_null=people_null+item.strip()+';'
        people=people_null
        item = kyogle_villageItem()
        item["app_id"] = app_id
        item["detail_txt"] = detail_txt

        item["detail_Lodged"] = detail_Lodged
        item["detail_Determined"] = detail_Determined
        # item["detail_contact"] = detail_contact
        item["detail_status"] = detail_status
        item["detail_cost"] = detail_cost
        item["detail_officer"] = detail_officer
        item["location"] = location
        item["people"] = people
        # item["documents_url"] = documents_all

        yield item

    def update_cookie(self):
        """需要调用semuluar同意用户条款"""
        opt = webdriver.ChromeOptions()
        opt.add_argument('--headless')
        opt.add_argument('--no-sandbox')
        opt.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome(opt)
        browser.get(self.term_url)
        # print(1)
        wait = WebDriverWait(browser, 1)
        agree_box = wait.until(EC.presence_of_element_located((By.ID, 'ctl00_ctMain_chkAgree_chk1')))
        if not agree_box.is_selected():
            agree_box.click()
        agree_button = wait.until(EC.element_to_be_clickable((By.ID, 'ctl00_ctMain_BtnAgree')))
        agree_button.click()
        # print(1)
        # 获取cookie
        cookie = browser.get_cookie('ASP.NET_SessionId')
        self.cookie = {'ASP.NET_SessionId': cookie['value']}
        # 关闭浏览器
        browser.close()

        print(f'cookies:{self.cookie}')

