
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import scrapy

from scrapy.http import Response

from AISpider.items.hobart_items import HobartItem

from common._string import except_blank


class HobartSpider(scrapy.Spider):
    """
    gave up retrying
    """
    name = "hobart"
    allowed_domains = ["apply.hobartcity.com.au"]
    start_urls = ["https://apply.hobartcity.com.au/Pages/XC.Track/PlanningApplication.aspx?t=PLN",
                  'https://apply.hobartcity.com.au/Pages/XC.Track/BuildingApplication.aspx?t=BLD',
                  'https://apply.hobartcity.com.au/Pages/XC.Track/PlumbingApplication.aspx?t=PMB',
                  ] # 同意页面url
    start_agree = "https://apply.hobartcity.com.au/Common/Common/terms.aspx" # 同意页面url

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
        super(HobartSpider, self).__init__(*args, **kwargs)
        self.cookie = None

    def start_requests(self):
        """
        添加请求负载
        """
        self.update_cookie()
        for url in self.start_urls:
            yield scrapy.Request(url, method="GET", dont_filter=True, headers=self.headers, cookies=self.cookie)

    def parse(self, response: Response, **kwargs: any):
        # print(response.text)
        model_url=except_blank(response.xpath('//div[@class="Links LinksGroup"]/div/a/@href').getall())
        for url in model_url:
            url=url.strip().replace('../../','https://apply.hobartcity.com.au/')
            yield scrapy.Request(url, method="GET", dont_filter=True, headers=self.headers,callback=self.parse_list)



    def parse_list(self, response: Response, **kwargs: any):
        url_details = response.xpath('//div[@id="hiddenresult"]/div/a/@href').getall()
        if url_details != []:
            app_id=''
            for url in url_details:
                if len(url.split('=',1))==2:
                    app_id=url.split('=',1)[1]
                url=url.strip().replace('../../','https://apply.hobartcity.com.au/')
                yield scrapy.Request(url=url, method="GET",callback=self.parse_detail,meta={'app_id':app_id})


    def parse_detail(self, response):
        app_num=''.join(except_blank(response.xpath('//div[@id="ctl00_ctMain_info_pnlApplication"]/div/h2/text()').getall()))
        app_detail=''.join(except_blank(response.xpath('//div[@id="b_ctl00_ctMain_info_app"]/text()').getall()))or None
        officer=except_blank(response.xpath('//div[@id="b_ctl00_ctMain_info_Officer"]/text()').getall())or None
        if officer != None:
            officer=''.join([item.strip().replace('\r\n','').replace('  ','') for item in officer ])
        data=except_blank(response.xpath('//div[@id="b_ctl00_ctMain_info_det"]/text()').getall())
        status=except_blank(response.xpath('//div[@id="b_ctl00_ctMain_info_det"]/strong/text()').getall())
        if len(data)==len(status)>=1:
            data_status=''.join([data[item]+':'+status[item]+';' for item in range(len(data))])
        else:
            data_status=''.join([data[item]+';' for item in range(len(data))])
        app_related=''.join(except_blank(response.xpath('//div[@id="b_ctl00_ctMain_info_rel"]/text()').getall())) or None
        location=''.join(except_blank(response.xpath('//div[@id="b_ctl00_ctMain_info_prop"]/a/text()').getall())) or None
        documents=response.xpath('//div[@id="b_trimdocs"]/table/tbody/tr/td/a/@href').getall() or None
        if documents != None:
            documents=''.join([url.strip().replace('../../','https://apply.hobartcity.com.au/')  for url in documents ])

        item = HobartItem()

        item["app_id"] = response.meta.get('app_id')
        item["app_num"] = app_num
        item["app_detail"] = app_detail
        item["officer"] = officer
        item["data_status"] = data_status
        item["app_related"] = app_related
        item["location"] = location
        item["documents"] = documents

        yield item

    def update_cookie(self):
        """需要调用semuluar同意用户条款"""
        opt = webdriver.ChromeOptions()
        opt.add_argument('--headless')
        opt.add_argument('--no-sandbox')
        opt.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome(opt)
        browser.get(self.start_agree)

        wait = WebDriverWait(browser, 1)

        agree_button = wait.until(EC.element_to_be_clickable((By.ID, 'ctl00_ctMain_BtnAgree')))
        agree_button.click()

        # 获取cookie
        cookie = browser.get_cookie('ASP.NET_SessionId')
        self.cookie = {'ASP.NET_SessionId': cookie['value']}
        # 关闭浏览器
        browser.close()

        print(f'cookies:{self.cookie}')
