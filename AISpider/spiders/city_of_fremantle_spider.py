import copy
from datetime import datetime, timedelta
from urllib.parse import urlencode

import requests
import scrapy
from AISpider.items.fremantle_items import FremantleItem
from lxml import etree
from scrapy import Selector
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from common._date import get_all_month
from common._string import except_blank


class FremantleSpider(scrapy.Spider):
    """
    gave up retrying
    """
    name = "city_of_fremantle"
    allowed_domains = ["fremantle-web.t1cloud.com"]
    start_urls = [
        "https://fremantle-web.t1cloud.com/T1PRDefault/WebApps/eProperty/P1/eTrack/eTrackApplicationSearch.aspx?r=P1.WEBGUEST&f=%24P1.ETR.SEARCH.ENQ"]

    # term_url = "https://datracker.tweed.nsw.gov.au/Pages/Disclaimer.aspx"  # 同意页面url

    headers = {

        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Host': 'fremantle - web.t1cloud.com',
        # 'Content-Type': 'application/x-www-form-urlencoded'
    }

    custom_settings = {
        # 'ITEM_PIPELINES': {
        #     "AISpider.pipelines.AispiderPipeline": None,
        # }
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'LOG_STDOUT': True,
        # 'LOG_FILE': 'scrapy_fremantle.log',
        'DOWNLOAD_TIMEOUT': 1200
    }

    index = 1

    def __init__(self, run_type='all', days=30, *args, **kwargs):
        super(FremantleSpider, self).__init__(*args, **kwargs)
        self.cookie = None
        self.run_type = run_type
        self.days = int(days)

    def start_requests(self):
        """
        添加请求负载
        """
        self.update_cookie()
        # url = 'https://datracker.tweed.nsw.gov.au/Pages/XC.Track/SearchApplication.aspx?as=a'
        yield scrapy.Request(url=self.start_urls[0], method="GET", dont_filter=True, cookies=self.cookie)

    def parse(self, response: Response, **kwargs: any):
        models = ['P', 'C']
        for model in models:
            now = datetime.now()

            # search_class = 'all'
            if self.run_type == 'all':
                date_from = '01/06/2003'
                all_month = get_all_month(date_from, now.strftime('%d/%m/%Y'))  # now.strftime('%d/%m/%Y'))
            else:
                date_from = (now - timedelta(days=self.days)).date().strftime('%d/%m/%Y')
                all_month = get_all_month(date_from, now.strftime('%d/%m/%Y'))

            # all_month = get_all_month('1/1/2008', '1/1/2010')
            print(all_month)
            for index, y_date in enumerate(all_month):
                if y_date == all_month[-1]:
                    break
                page = 1
                date_from = y_date
                date_to = all_month[index + 1]

                print(f"{date_from}--{date_to}")

                selector = Selector(text=response.text)
                payloads = {
                    'ctl00_Content_ajaxToolkitManager_HiddenField': '',
                    '__EVENTTARGET': 'ctl00$Content$btnSearch',
                    '__EVENTARGUMENT': '',
                    '__VIEWSTATE': selector.css('#__VIEWSTATE::attr(value)').get() or '',
                    '__VIEWSTATEGENERATOR': selector.css('#__VIEWSTATEGENERATOR::attr(value)').get(),
                    '__SCROLLPOSITIONX': '0',
                    '__SCROLLPOSITIONY': '917',
                    '__EVENTVALIDATION': selector.css('#__EVENTVALIDATION::attr(value)').get(),
                    'ctl00$Content$txtApplicationID$txtText': '',
                    'ctl00$Content$txtDateFrom$txtText': date_from,
                    'ctl00$Content$txtDateTo$txtText': date_to,
                    'ctl00$Content$txtDescription$txtText': '',
                    'ctl00$Content$ddlApplicationType$elbList': 'all',
                    'ctl00$Content$ddlStatus$elbList': {model},
                    'ctl00$Content$ddlDecision$elbList': 'all',
                    'ctl00$Content$txtStreetNoFrom$txtText': '',
                    'ctl00$Content$txtStreetNoTo$txtText': '',
                    'ctl00$Content$txtStreet$txtText': '',
                    'ctl00$Content$txtStreetType$txtText': '',
                    'ctl00$Content$txtSuburb$txtText': '',
                    'ctl00$Content$txtPlanNo$txtText': '',
                    'ctl00$Content$txtPlanType$txtText': '',
                    'ctl00$Content$txtLotNo$txtText': '',
                    'ctl00$Content$txtParcelType$txtText': '',

                }
                url = 'https://fremantle-web.t1cloud.com/T1PRDefault/WebApps/eProperty/P1/eTrack/eTrackApplicationSearch.aspx'
                params = {
                    'r': 'P1.WEBGUEST',
                    'f': '$P1.ETR.SEARCH.ENQ',
                }
                response1 = requests.post(
                    url,
                    params=params,
                    cookies=self.cookie,
                    data=payloads,
                )
                resp = etree.HTML(response1.text)
                selector1 = Selector(text=response1.text)
                total_text = except_blank(resp.xpath(
                    '//div[@id="ctl00_Content_cusResultsGrid_pnlCustomisationGrid"]/div/table/tr/td[1]/a/text()'))
                for item in total_text:
                    # app_num = re.findall("doPostBack\(\'(.*?)\'", item, re.DOTALL)
                    app_num_tars = item.replace('/', '%2f').strip()
                    url_detail = f'https://fremantle-web.t1cloud.com/T1PRDefault/WebApps/eProperty/P1/eTrack/eTrackApplicationDetails.aspx?r=P1.WEBGUEST&f=%24P1.ETR.APPDET.VIW&ApplicationId={app_num_tars}'

                    yield scrapy.Request(url_detail, method="GET", dont_filter=True, cookies=self.cookie,
                                         callback=self.parse_detail)
                page_number = except_blank(resp.xpath(
                    '//div[@id="ctl00_Content_cusResultsGrid_pnlCustomisationGrid"]/div/table/tr[@class="pagerRow"]/td/@colspan'))
                if page_number != []:

                    page_number = int(page_number[0])
                    for i in range(2, page_number + 1):
                        url_page = 'https://fremantle-web.t1cloud.com/T1PRDefault/WebApps/eProperty/P1/eTrack/eTrackApplicationSearchResults.aspx?r=P1.WEBGUEST&f=%24P1.ETR.RESULTS.VIW'
                        pay_loads = {
                            '__EVENTTARGET': 'ctl00$Content$cusResultsGrid$repWebGrid$ctl00$grdWebGridTabularView',
                            '__EVENTARGUMENT': f'Page${i}',
                            '__VIEWSTATE': selector1.css('#__VIEWSTATE::attr(value)').get() or '',
                            '__VIEWSTATEGENERATOR': selector1.css('#__VIEWSTATEGENERATOR::attr(value)').get(),
                            '__SCROLLPOSITIONX': '0',
                            '__SCROLLPOSITIONY': '2007',
                            '__EVENTVALIDATION': selector1.css('#__EVENTVALIDATION::attr(value)').get(),
                        }
                        headers = {
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                            'Cache-Control': 'max-age=0',
                            'Connection': 'keep-alive',
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'Origin': 'https://fremantle-web.t1cloud.com',
                            'Referer': 'https://fremantle-web.t1cloud.com/T1PRDefault/WebApps/eProperty/P1/eTrack/eTrackApplicationSearchResults.aspx?r=P1.WEBGUEST&f=%24P1.ETR.RESULTS.VIW',
                            'Sec-Fetch-Dest': 'document',
                            'Sec-Fetch-Mode': 'navigate',
                            'Sec-Fetch-Site': 'same-origin',
                            'Sec-Fetch-User': '?1',
                            'Upgrade-Insecure-Requests': '1',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
                            'sec-ch-ua': '"Microsoft Edge";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
                            'sec-ch-ua-mobile': '?0',
                            'sec-ch-ua-platform': '"Windows"',
                        }
                        payloads1 = copy.copy(pay_loads)
                        payloads_urlcode = urlencode(payloads1)
                        yield scrapy.Request(url=url_page, method="POST", cookies=self.cookie, headers=headers,
                                             body=payloads_urlcode, callback=self.parse_list,
                                             )

    def parse_list(self, response: Response, **kwargs: any):

        total_text = except_blank(response.xpath(
            '//div[@id="ctl00_Content_cusResultsGrid_pnlCustomisationGrid"]/div/table/tr/td[1]/noscript/div/input/@value').getall())

        for item in total_text:
            # app_num = re.findall("doPostBack\(\'(.*?)\'", item, re.DOTALL)
            app_num_tars = item.replace('/', '%2f').strip()
            url_detail = f'https://fremantle-web.t1cloud.com/T1PRDefault/WebApps/eProperty/P1/eTrack/eTrackApplicationDetails.aspx?r=P1.WEBGUEST&f=%24P1.ETR.APPDET.VIW&ApplicationId={app_num_tars}'

            yield scrapy.Request(url_detail, method="GET", dont_filter=True, cookies=self.cookie,
                                 callback=self.parse_detail)

    def parse_detail(self, response):
        detail_th = response.xpath(
            '//table[@id="ctl00_Content_cusPageComponents_repPageComponents_ctl00_cusPageComponentGrid_repWebGrid_ctl00_dtvWebGridListView"]/tr/td[1]/text()').getall()
        detail_th = [item.lower() for item in detail_th]
        detail_td = response.xpath(
            '//table[@id="ctl00_Content_cusPageComponents_repPageComponents_ctl00_cusPageComponentGrid_repWebGrid_ctl00_dtvWebGridListView"]/tr/td[2]/text()').getall()
        detail_td = [item.replace('\xa0', '') for item in detail_td]
        data_dict = dict(zip(detail_th, detail_td))
        add_infomation_th = response.xpath(
            '//table[@id="ctl00_Content_cusPageComponents_repPageComponents_ctl01_cusPageComponentGrid_repWebGrid_ctl00_dtvWebGridListView"]/tr/td[1]/text()').getall()
        add_infomation_th = [item.lower() for item in add_infomation_th]
        add_infomation_td = response.xpath(
            '//table[@id="ctl00_Content_cusPageComponents_repPageComponents_ctl01_cusPageComponentGrid_repWebGrid_ctl00_dtvWebGridListView"]/tr/td[2]/text()').getall()
        add_infomation_td = [item.replace('\xa0', '') for item in add_infomation_td]
        add_dict = dict(zip(add_infomation_th, add_infomation_td))
        detail_address = ''.join(response.xpath(
            '//table[@id="ctl00_Content_cusPageComponents_repPageComponents_ctl03_cusPageComponentGrid_repWebGrid_ctl00_dtvWebGridListView"]/tr/td/noscript/div/input/@value').getall())
        detail_address_description = ''.join(response.xpath(
            '//table[@id="ctl00_Content_cusPageComponents_repPageComponents_ctl03_cusPageComponentGrid_repWebGrid_ctl00_dtvWebGridListView"]/tr[2]/td[2]/text()').getall())
        item = FremantleItem()
        item["app_num"] = data_dict["application id"] if "application id" in list(data_dict.keys()) else None
        item["app_detail"] = data_dict["description"] if "description" in list(data_dict.keys()) else None
        item["app_group"] = data_dict["group"] if "group" in list(data_dict.keys()) else None
        item["app_category"] = data_dict["category"] if "category" in list(data_dict.keys()) else None
        item["app_sub_category"] = data_dict["sub category"] if "sub category" in list(data_dict.keys()) else None
        item["app_status"] = data_dict["status"] if "status" in list(data_dict.keys()) else None
        item["lodgement_date"] = datetime.strptime(data_dict["lodgement date"],'%d/%m/%Y').timestamp() if "lodgement date" in list(data_dict.keys()) and data_dict["lodgement date"]!=''  else None

        item["stage_decision"] = data_dict["stage/decision"] if "stage/decision" in list(data_dict.keys()) else None

        item["wapc_ref"] = add_dict["wapc ref."] if "wapc ref." in list(add_dict.keys()) else None


        item["council_decision"] = add_dict["council decision"] if "council decision" in list(add_dict.keys()) else None
        item["wapc_decision"] = add_dict["wapc decision"] if "wapc decision" in list(add_dict.keys()) else None
        item["no_of_lots"] = add_dict["no of lots"] if "no of lots" in list(add_dict.keys()) else None

        item["date_received"] = datetime.strptime(add_dict["date received"],'%d/%m/%Y').timestamp() if "date received" in list(add_dict.keys()) and add_dict["date received"]!='' else None

        item["council_decision_date"] = datetime.strptime(add_dict["council decision date"],'%d/%m/%Y').timestamp() if "council decision date" in list(
            add_dict.keys())and add_dict["council decision date"]!='' else None
        item["wapc_decision_date"] = datetime.strptime(add_dict["wapc decision date"],'%d/%m/%Y').timestamp()  if "wapc decision date" in list(
            add_dict.keys())and add_dict["wapc decision date"]!='' else None

        item["advertisement_commence"] = datetime.strptime(add_dict["advertisement commence"],'%d/%m/%Y').timestamp() if "advertisement commence" in list(
            add_dict.keys())and add_dict["advertisement commence"]!='' else None
        item["advertisement_closing"] = datetime.strptime(add_dict["advertisement closing"],'%d/%m/%Y').timestamp() if "advertisement closing" in list(
            add_dict.keys()) and add_dict["advertisement closing"]!='' else None
        item["decision_date"] = datetime.strptime(add_dict["decision date"] ,'%d/%m/%Y').timestamp() if "decision date" in list(add_dict.keys())and add_dict["decision date"]!='' else None
        item["date_issued"] = datetime.strptime(add_dict["date issued"] ,'%d/%m/%Y').timestamp() if "date issued" in list(add_dict.keys())and add_dict["date issued"]!='' else None

        item["detail_address"] = detail_address
        item["detail_address_description"] = detail_address_description
        yield item
        print(f'success:{data_dict["application id"]}')

    def update_cookie(self):
        """需要调用semuluar同意用户条款"""
        opt = webdriver.ChromeOptions()
        opt.add_argument('--headless')
        opt.add_argument('--no-sandbox')
        opt.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome(opt)
        browser.get(self.start_urls[0])
        wait = WebDriverWait(browser, 1)

        # 获取cookie
        cookie = browser.get_cookie('ASP.NET_SessionId')
        self.cookie = {'ASP.NET_SessionId': cookie['value']}
        # 关闭浏览器
        browser.close()
        print(f'cookies:{self.cookie}')


