import re
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import scrapy

from scrapy.http import Response
from AISpider.items.gosnells_items import GosnellsItem
from common._string import except_blank


class GosnellsSpider(scrapy.Spider):
    """
    gave up retrying
    """
    name = "gosnells"
    allowed_domains = ["apps.gosnells.wa.gov.au"]
    start_urls = ["https://apps.gosnells.wa.gov.au/pages/xc.track/searchapplication.aspx",]
    start_agree = "https://apps.gosnells.wa.gov.au/Common/Common/terms.aspx" # 同意页面url

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
        super(GosnellsSpider, self).__init__(*args, **kwargs)
        self.cookie = None

    def start_requests(self):
        """
        添加请求负载
        """
        self.update_cookie()
        for url in self.start_urls:
            yield scrapy.Request(url, method="GET", dont_filter=True, headers=self.headers, cookies=self.cookie)

    def parse(self, response: Response, **kwargs: any):
        model_url=except_blank(response.css('#i10187 a::attr(href)').extract())
        for url in model_url:
            url=url.strip().replace('../../','https://apps.gosnells.wa.gov.au/')
            yield scrapy.Request(url, method="GET", dont_filter=True, cookies=self.cookie,headers=self.headers,callback=self.parse_list)

    def parse_list(self, response: Response, **kwargs: any):
        # print(response.text)
        url_details = except_blank(response.xpath('//div[@id="hiddenresult"]/div/a[1]/@href').getall())
        if url_details != []:
            app_id=''
            for url in url_details:
                if len(url.split('=',1))==2:
                    app_id=url.split('=',1)[1]
                url=url.strip().replace('../../','https://apps.gosnells.wa.gov.au/')
                # print(url)
                yield scrapy.Request(url=url, method="GET",callback=self.parse_detail,meta={'app_id':app_id})


    def parse_detail(self, response):
        app_num=''.join(except_blank(response.xpath('//div[@id="ctl00_ctMain_info_pnlApplication"]/div/h2/text()').getall()))
        app_detail=''.join(except_blank(response.xpath('//div[@id="b_ctl00_ctMain_info_app"]/div/text()').getall()))or None
        status=''.join(except_blank(response.xpath('//div[@id="b_ctl00_ctMain_info_app"]/strong[1]/text()').getall()))or None
        text=response.xpath('//div[@id="b_ctl00_ctMain_info_app"]/text()').getall()
        details={}
        for item in text:
            lodged_time_ex = re.findall('Lodged: (.*?)\r\n', item, re.DOTALL)
            if lodged_time_ex != []:
                details['lodged_time'] = [datetime.strptime(item.strip(), '%d/%m/%Y').timestamp() for item in lodged_time_ex][0]
            determined_time_ex = re.findall('Determined:\r\n\t\t\t(.*?)\r\n', item, re.DOTALL)
            if determined_time_ex != []:
                details['determined_time'] = [datetime.strptime(item.strip(), '%d/%m/%Y').timestamp() for item in determined_time_ex][0]
                # print(details['determined_time'])
            officer_ex = re.findall('Officer:\r\n\t\t(.*?)\r\n', item, re.DOTALL)
            if officer_ex != []:
                details['officer'] = ''.join([item.strip() for item in officer_ex])
        app_outcome = ''.join(except_blank(response.xpath('//div[@id="b_ctl00_ctMain_info_app"]/strong[2]/text()').getall()))or None

        location=''.join(except_blank(response.xpath('//div[@id="b_ctl00_ctMain_info_prop"]/a/text()').getall())) or None

        description=except_blank(response.xpath('//div[@id="b_ctl00_ctMain_info_history"]/div/table/tr/td/text()').getall())
        description_detail=''
        for i in range(1,len(description)+1):
            if i %3!=0:
                description_detail=description_detail+description[i-1]+':'
            else:
                description_detail=description_detail+description[i-1]+';'
        people=except_blank(response.xpath('//div[@id="b_ctl00_ctMain_info_party"]/text()').getall())
        people=''.join([item+';' for item in people])
        app_related=''.join(except_blank(response.xpath('//div[@id="b_ctl00_ctMain_info_related"]/text()').getall())) or None

        item = GosnellsItem()

        item["app_id"] = response.meta.get('app_id')
        item["app_num"] = app_num
        item["app_detail"] = app_detail
        item["status"] = status
        item["lodged_time"] = details["lodged_time"] if "lodged_time" in list(details.keys()) else None
        item["determined_time"] =details["determined_time"] if "determined_time" in list(details.keys()) else None
        item["app_outcome"] = app_outcome
        item["app_outcome"] = app_outcome
        item["officer"] = details["officer"] if "officer" in list(details.keys()) else None
        item["location"] = location
        item["description_detail"] = description_detail
        item["people"] = people
        item["app_related"] = app_related
        yield item

    def update_cookie(self):
        """需要调用semuluar同意用户条款"""
        opt = webdriver.ChromeOptions()
        opt.add_argument('--headless')
        opt.add_argument('--no-sandbox')
        opt.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome(opt)
        browser.get(self.start_agree)
        # print(1)
        wait = WebDriverWait(browser, 1)
        # agree_box = wait.until(EC.presence_of_element_located((By.ID, 'ctl00_ctMain_chkAgree_chk1')))
        # if not agree_box.is_selected():
        #     agree_box.click()
        agree_button = wait.until(EC.element_to_be_clickable((By.ID, 'ctl00_ctMain_BtnAgree')))
        agree_button.click()
        # print(1)
        # 获取cookie
        cookie = browser.get_cookie('ASP.NET_SessionId')
        self.cookie = {'ASP.NET_SessionId': cookie['value']}
        # 关闭浏览器
        browser.close()
        # print(1)
        # r = requests.get(self.term_url)
        # self.cookie = {'ASP.NET_SessionId': r.cookies.get('ASP.NET_SessionId')}
        print(f'cookies:{self.cookie}')

