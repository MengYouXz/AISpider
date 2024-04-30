import re
import time
from datetime import date, datetime, timedelta

import json
import requests
import scrapy
from scrapy import Selector
from scrapy.http import Response

from urllib.parse import urlencode

from AISpider.items.northern_beaches_council__item import northern_beaches_council_Item
from common._date import get_all_month, get_last_days

from common._string import  except_blank




class Eservices_Spider(scrapy.Spider):
    """
    gave up retrying
    """
    name = "northern_beaches_council"
    allowed_domains = ["eservices.northernbeaches.nsw.gov.au.com"]
    start_urls = [
        "https://eservices.northernbeaches.nsw.gov.au/ePlanning/live/Public/XC.Spatial.Applications/MapApplications.aspx"]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json,text/javascript,*/*;q=0.01"
        # 'Content-Type': 'application/json; charset=utf-8'
    }

    custom_settings = {
        # 'ITEM_PIPELINES': {
        #     "AISpider.pipelines.AispiderPipeline": None,
        # }
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'LOG_STDOUT': True,
        #'LOG_FILE': 'scrapy_eservices.log',
        'DOWNLOAD_TIMEOUT': 1200
    }

    index = 1

    def __init__(self, run_type='all', days=30,*args, **kwargs):
        super(Eservices_Spider, self).__init__(*args, **kwargs)
        self.cookie = None
        self.run_type = run_type
        self.days = int(days)

    def start_requests(self):

        # print(1)
        model = ['d','s','o']
        # o:https://nb-icongis.azurewebsites.net/data.ashx?dataid=1&t=o&_=1711524503397
        # s:https://nb-icongis.azurewebsites.net/data.ashx?dataid=1&t=s&d1=25/03/2024&d2=27/03/2024&_=1711524456090
        # d:https://nb-icongis.azurewebsites.net/data.ashx?dataid=1&t=d&d1=25/03/2024&d2=27/03/2024&_=1711524468676
        for item in model:
            now = datetime.now()
            now_mkt = int(time.mktime(now.timetuple()) * 1000.0 + now.microsecond / 1000.0)
            date_from = '1/02/1990'
            if item=='o':
                url = f'https://nb-icongis.azurewebsites.net/data.ashx?dataid=1&t={item}&_={now_mkt}'
                yield scrapy.Request(url, method="GET", dont_filter=True, headers=self.headers)
                continue
            if self.run_type == 'all':
                all_month = get_all_month(date_from, now.strftime('%d/%m/%Y'))  # now.strftime('%d/%m/%Y'))
            else:
                date_from = (now - timedelta(days=self.days)).date().strftime('%d/%m/%Y')
                all_month = get_all_month(date_from, now.strftime('%d/%m/%Y'))
            for index, y_date in enumerate(all_month):
                if y_date == all_month[-1]:
                    break
                date_from = y_date
                date_to = all_month[index + 1]
                print(f'{date_from}--{date_to}')
                url = f'https://nb-icongis.azurewebsites.net/data.ashx?dataid=1&t={item}&d1={date_from}&d2={date_to}&_={now_mkt}'
                yield scrapy.Request(url, method="GET", dont_filter=True, headers=self.headers)

    def parse(self, response: Response, **kwargs: any):

        # print(2)
        infos = json.loads(response.text)
        data = infos.get("marker")
        print(f"共{len(data)}条数据")
        for item in data:
            # print(item)
            href = (Selector(text=item.get('content')).css("a::attr(href)").extract_first() or '').strip()
            if not href:
                continue
            app_id = ''.join(re.findall('=(\d+)',href))
            yield scrapy.Request(url=href, method="GET", dont_filter=True, headers=self.headers,
                                 callback=self.parse_detail, meta={"app_id": app_id})

    def parse_detail(self, response: Response, **kwargs: any):
        app_num = except_blank(response.css('#ctl00_ctMain_info_pnlApplication div h2::text').extract())
        app_num=''.join(app_num).split(':',)[1].strip() or None

        appdetails_src = response.css("div#ctl00_ctMain_info_pnlApplication > div > div.detail").extract()
        # 去除appdetails中的标签对
        appdetails_de_tag = [re.sub(r'<.*?>', '', i) for i in appdetails_src]
        details = {}
        for i in range(len(appdetails_de_tag)):
            row = appdetails_de_tag[i].split(":") if appdetails_de_tag[i] else ['', '']
            details[row[0].strip()] = row[1].strip().replace("\r\n", "")

        related = response.xpath('//div[@id="addr"]/div[@class="detail"][1]/div[@class="detailright"]/text()').getall()
        if related != 'There are no related applications.':
            related = response.xpath(
                '//div[@id="addr"]/div[@class="detail"][1]/div[@class="detailright"]/a/text()').getall()
            related = ";".join([r.strip() for r in related if related])
        location = response.xpath('//div[@id="b_ctl00_ctMain_info_prop"]/a/text()').getall()
        location = ";".join([ l.strip() for l in location if location])

        people =except_blank(response.css('#b_ctl00_ctMain_info_party div div::text').extract())
        people = ";".join([i.strip() for i in people if people])

        docs_name = response.css("div#edms tr > td:nth-child(2) a::text").extract()
        docs_url = response.css("div#edms tr > td:nth-child(2) a::attr(href)").extract()
        docs = "".join(
            [docs_name[i]+':'+"https://eservices.northernbeaches.nsw.gov.au/ePlanning/live/" + docs_url[i].replace("../../", "")
             + "@@"  for i in range(len(docs_url))])

        item = northern_beaches_council_Item()

        item["app_id"] = response.meta.get('app_id')
        item["app_num"] = app_num
        item["description"] = details["Description"] if "Description" in list(details.keys()) else None
        item["applicationType"] = details["Application Type"] if "Application Type" in list(details.keys()) else None
        item["status"] = details["Status"] if "Status" in list(details.keys()) else None
        item["submitted"] = datetime.strptime(details["Submitted"],'%d/%m/%Y').timestamp()  if "Submitted" in list(details.keys()) else None

        item["exhibitionPeriod"] = re.sub(r'\s+', " ",details["Exhibition Period"].replace('\t', ' ')) if "Exhibition Period" in list(details.keys()) else None
        item["determined"] = datetime.strptime(details["Determined"],'%d/%m/%Y').timestamp() if "Determined" in list(details.keys()) else None#datetime
        item["determination_level"] =details["Determination Level"] if "Determination Level" in list(details.keys()) else None
        item["appeal_status"] = details["Appeal Status"] if "Appeal Status" in list(details.keys()) else None
        item["cost"] = details["Cost of Work"] if "Cost of Work" in list(details.keys()) else None
        item["officer"] = details["Officer"] if "Officer" in list(details.keys()) else None
        item["location"] = location
        item["people"] = people
        item["docs"] = docs

        yield item

