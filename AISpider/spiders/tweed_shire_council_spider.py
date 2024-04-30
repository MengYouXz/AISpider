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

from AISpider.items.tweed_items import TweedItem
# from AISpider.AISpider.items.tweed_items import TweedItem
from common._string import except_blank


class TweedSpider(scrapy.Spider):
    """
    gave up retrying
    """
    name = "tweed"
    allowed_domains = ["chcc-icon.saas.t1cloud.com"]
    start_urls = ["https://datracker.tweed.nsw.gov.au/Pages/XC.Track/SearchApplication.aspx?as=a"]

    term_url = "https://datracker.tweed.nsw.gov.au/Pages/Disclaimer.aspx"  # 同意页面url

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

    def __init__(self,run_type='all', days=30, *args, **kwargs):
        super(TweedSpider, self).__init__(*args, **kwargs)
        self.cookie = None
        self.run_type = run_type
        self.days = int(days)

    def start_requests(self):
        """
        添加请求负载
        """
        self.update_cookie()
        url = 'https://datracker.tweed.nsw.gov.au/Pages/XC.Track/SearchApplication.aspx?as=a'
        yield scrapy.Request(url, method="GET", dont_filter=True, headers=self.headers, cookies=self.cookie)

    def parse(self, response: Response, **kwargs: any):
        for url in self.start_urls:

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://datracker.tweed.nsw.gov.au",
                "Accept - Language": "zh - CN, zh;q = 0.9, en;q = 0.8, en - GB;q = 0.7, en - US;q = 0.6",
                "Cache - Control": "max - age = 0",
            }
            now = datetime.now()
            date_from='1/9/1980'
            # search_class = 'all'
            if self.run_type == 'all':
                all_month = get_all_month(date_from,now.strftime('%d/%m/%Y'))
            else:
                date_from = (now - timedelta(days=self.days)).date().strftime('%d/%m/%Y')
                all_month = get_all_month(date_from, now.strftime('%d/%m/%Y'))

            for index, y_date in enumerate(all_month):
                if y_date == all_month[-1]:
                    break
                page = 1
                date_from = y_date
                date_to = all_month[index + 1]
                json_date_from1 = self.json_date1(date_from)
                json_date_from2 = self.json_date1(date_to)
                print(f"{date_from}--{date_to}")

                payloads_json1 = {"enabled": True, "emptyMessage": "", "validationText": json_date_from1,
                                  "valueAsString": json_date_from1, "minDateStr": "1980-01-01-00-00-00",
                                  "maxDateStr": "2099-12-31-00-00-00", "lastSetTextBoxValue": date_from}
                payloads_json2 = {"enabled": True, "emptyMessage": "", "validationText": json_date_from2,
                                  "valueAsString": json_date_from2, "minDateStr": "1980-01-01-00-00-00",
                                  "maxDateStr": "2099-12-31-00-00-00", "lastSetTextBoxValue": date_to}
                selector = Selector(text=response.text)
                payloads = {

                    "ctl00_rcss_TSSM": selector.css('#ctl00_rcss_TSSM::attr(value)').get() or '',
                    "ctl00_script_TSM": selector.css('#ctl00_script_TSM::attr(value)').get() or '',
                    "__EVENTTARGET": '',
                    "__EVENTARGUMENT": '',
                    "__VIEWSTATE": selector.css('#__VIEWSTATE::attr(value)').get() or '',
                    "__VIEWSTATEGENERATOR": selector.css('#__VIEWSTATEGENERATOR::attr(value)').get(),
                    "__EVENTVALIDATION": selector.css('#__EVENTVALIDATION::attr(value)').get(),

                    "ctl00$ctMain$oldSearch$datRange$datRange_txt1$dateInput": date_from,
                    "ctl00_ctMain_oldSearch_datRange_datRange_txt1_dateInput_ClientState": json.dumps(payloads_json1),

                    "ctl00$ctMain$oldSearch$datRange$datRange_txt2$dateInput": date_to,
                    "ctl00_ctMain_oldSearch_datRange_datRange_txt2_dateInput_ClientState": json.dumps(payloads_json2),

                    "ctl00$ctMain$oldSearch$rbl": "LodgementDate",

                    "ctl00$ctMain$oldSearch$btnSearch3": "Search",
                }
                payloads = copy.copy(payloads)
                payloads_urlcode = urlencode(payloads)
                # print(payloads_urlcode)

                yield scrapy.Request(url, method="POST", dont_filter=True, headers=headers,
                                     body=payloads_urlcode, callback=self.parse_list,
                                     meta={'url': url, 'headers': headers, 'payloads_urlcode': "payloads_urlcode"}

                                     )

    def parse_list(self, response: Response, **kwargs: any):
        # pass
        # print(3)
        url_details = response.xpath('//div[@id="hiddenresult"]/div[@class="result"]/a[1]/@href').getall()
        if url_details == []:
            yield scrapy.Request(url=response.meta.get("url"), method="POST", dont_filter=True,
                                 headers=response.meta.get("headers"), body=response.meta.get("payloads_urlcode"),
                                 callback=self.parse_detail,
                                 )
        i = 1
        # print(url_details)
        for item in url_details:
            app_id = item.split("=", 1)[1]
            # print(app_id)
            # https: // datracker.tweed.nsw.gov.au / Pages / XC.Track / SearchApplication.aspx?as=a
            # https: // datracker.tweed.nsw.gov.au / Pages / XC.Track / SearchApplication.aspx?id = 1000118

            url_detail = "https://datracker.tweed.nsw.gov.au/" + item.replace("../../", "")
            yield scrapy.Request(url=url_detail, method="GET", dont_filter=True, callback=self.parse_detail,
                                 meta={"app_id": app_id})
            # print(url_detail)
            i += 1
        # print(f"共有：{i}条数据")

    def parse_detail(self, response):
        # pass
        # print(3)
        # total=response.xpath('//div[@class="MainPanel"]/div')
        # global  detail_cost, detail_officer, people_Applicant_tf
        detail_cost = ''
        title = response.xpath('//div[@class="MainPanel"]/div/h2/text()').getall()
        # detailright=total.xpath('//div[@class="MainPanel"]/div/div[@class="detail"]/div[@class="detailright"]')

        detail_text = response.xpath(
            f'//div[@class="MainPanel"]/div/div[@class="detail"]/div[@class="detailright"]/p[1]/text()').getall()

        detail_Lodged_data = ''.join(response.xpath(
            '//div[@class="MainPanel"]/div/div[@class="detail"]/div[@class="detailright"]/p[2]/text()').getall())
        detail_Lodged_data = datetime.strptime(detail_Lodged_data, '%d/%m/%Y').timestamp() if detail_Lodged_data else None

        detail_Determined_data = response.xpath(
            '//div[@class="MainPanel"]/div/div[@class="detail"]/div[@class="detailright"]/p/b[contains(text(),"Determined:")]/text()').getall()
        # print(detail_Determined_data)
        # print(detail_Determined_data[0])
        if detail_Determined_data == []:
            detail_Determined_data = None
            detail_cost = response.xpath(
                '//div[@class="MainPanel"]/div/div[@class="detail"]/div[@class="detailright"]/p[3]/text()').getall() or None
            detail_cost = except_blank(detail_cost)
            detail_officer = response.xpath(
                '//div[@class="MainPanel"]/div/div[@class="detail"]/div[@class="detailright"]/p[4]/text()').getall()
            # print(detail_officer)
            detail_officer = ";".join([i.strip() for i in detail_officer if detail_officer])
        elif detail_Determined_data[0] == 'Determined: ':
            # print(detail_Determined_data[0])
            detail_Determined_data = response.xpath(
                '//div[@class="MainPanel"]/div/div[@class="detail"]/div[@class="detailright"]/p[3]/text()').getall()
            detail_Determined_data = str(detail_Determined_data[0].split("\r", 1)[0]).strip() + str(
                detail_Determined_data[0].split("\r", 1)[1]).strip()
            detail_cost = response.xpath(
                '//div[@class="MainPanel"]/div/div[@class="detail"]/div[@class="detailright"]/p[4]/text()').getall()
            detail_cost = except_blank(detail_cost)
            detail_officer = response.xpath(
                '//div[@class="MainPanel"]/div/div[@class="detail"]/div[@class="detailright"]/p[5]/text()').getall()
            detail_officer = ";".join([i.strip() for i in detail_officer if detail_officer ])
        # detail_contact=response.xpath('//div[@class="MainPanel"]/div/p/a/@href').getall()
        location = response.css('#b_ctl00_ctMain_info_prop a::text').extract_first()
        location = str(location).strip()
        location_url = response.css('#b_ctl00_ctMain_info_prop a::attr(href)').extract_first()
        location_url = 'https://datracker.tweed.nsw.gov.au/Pages' + str(location_url).lstrip('../ ')
        # Further_mapping=response.css('.mt-3 mb-2 a::attr(href)').extract_first()
        people_Applicant = response.xpath('//div[@id="b_ctl00_ctMain_info_party"]/p/text()[2]').getall()
        # print(people_Applicant)
        if people_Applicant == '':
            people_Applicant = None
        else:
            people_Applicant_tf = ''
            for item in people_Applicant:
                item = 'Applicant: ' + str(item)
                people_Applicant_tf = people_Applicant_tf + item + ";"
            # print(people_Applicant_tf)
        documents_url_js = response.xpath(
            '//div[@class="isection"]/div[@class="detail"]/div[@class="detailright"]/p/a/@href').getall()
        # # documents_url="https: // datracker.tweed.nsw.gov.au /"+str(documents_url_js).lstrip()
        # print1 = f"{title}--{detail_text}--{detail_Lodged_data}--" \
        #          f"'{detail_Determined_data}'--" \
        #          f"{detail_cost}--{detail_officer}" \
        #          f"--{[location]}--{[location_url]}--{[people_Applicant_tf]}"
        # # print2=f'--{[location]}--{[location_url]}--{[people_Applicant]}'

        documents_all = ''
        for item in documents_url_js:
            documents_url = "https://datracker.tweed.nsw.gov.au/" + item.replace("../../", "") + '\\\\'
            documents_all += documents_url
        # print(documents_all)
        # https: // datracker.tweed.nsw.gov.au / Pages / XC.Track / SearchApplication.aspx?id = 1001643
        # https: // datracker.tweed.nsw.gov.au / Common / Output / Document.aspx?id = 7996453 & ext = pdf
        print(f"已成功{title}--{detail_Lodged_data}")
        # print(print2)

        item = TweedItem()
        # print(response.meta["app_id"])
        # print(response.meta.get('app_id'))
        item["app_id"] = response.meta.get('app_id')

        item["app_num"] = ''.join(title)
        item["detail_text"] = ''.join(detail_text)

        item["detail_Lodged_data"] = detail_Lodged_data
        item["detail_Determined_data"] = detail_Determined_data
        # item["detail_contact"] = detail_contact
        item["detail_cost"] = ''.join(detail_cost)
        item["detail_officer"] = detail_officer
        item["location"] = location
        # item["location_url"] = location_url
        item["people_Applicant"] = people_Applicant_tf
        item["documents_url"] = documents_all

        yield item

    def update_cookie(self):
        """需要调用semuluar同意用户条款"""
        driver_path = str(Path(__file__).parent.parent.parent / 'chrome/chromedriver.exe')
        opt = webdriver.EdgeOptions()
        opt.add_experimental_option('binary', driver_path)
        opt.add_argument('--headless')
        opt.add_argument('--no-sandbox')
        opt.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Edge(opt)
        browser.get(self.term_url)
        # print(1)
        wait = WebDriverWait(browser, 1)
        # agree_box = wait.until(EC.presence_of_element_located((By.ID, 'ctl00_ctMain_chkAgree_chk1')))
        # if not agree_box.is_selected():
        #     agree_box.click()
        agree_button = wait.until(EC.element_to_be_clickable((By.ID, 'ctl00_ctMain_btnAgree')))
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

    def json_date1(self, date):
        """
        dd/MM/yyyy 转为 yyyy-MM-dd
        """
        d_M_y = date.split("/")
        return d_M_y[2] + "-" + d_M_y[1] + "-" + d_M_y[0] + "-" + "00" + "-" + "00" + "-" + "00"

