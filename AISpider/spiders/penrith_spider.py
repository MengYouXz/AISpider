import requests
import scrapy
from datetime import datetime
from scrapy.http import Request
from bs4 import BeautifulSoup
from AISpider.items.penrith_items import PenrithItem
import time

class PenrithSpider(scrapy.Spider):
    name = "penrith"
    allowed_domains = ["datracker.penrithcity.nsw.gov.au"]
    start_urls = ["https://datracker.penrithcity.nsw.gov.au/track/Pages/XC.Track/SearchApplication.aspx"]
    custom_settings = {
        'LOG_STDOUT': True,
        # 'LOG_FILE': 'scrapy_penrith.log',
        'DOWNLOAD_TIMEOUT': 1200
    }


    def __init__(self, *args, **kwargs):
        super(PenrithSpider, self).__init__(*args, **kwargs)
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }


    def parse(self, response):
        """
        获取结果列表页
        """
        soup = BeautifulSoup(response.text,'lxml')
        url_list = soup.find("div", id="i1").find_all("a")
        for url in url_list:
            url = url.get('href')
            url = url.split("/", 2)[2]
            url = 'https://datracker.penrithcity.nsw.gov.au/track/'+ url
            yield Request(url, callback=self.list_url)

 
    def list_url(self, response):
        """ 
        列表页面提取url
        """
        soup = BeautifulSoup(response.text, 'lxml')
        url_list = soup.select('#hiddenresult .result .search')
        for url in url_list:
            url = url.get('href')
            url = url.split("/", 2)[2]
            url = 'https://datracker.penrithcity.nsw.gov.au/track/' + url
            # print('内容页url：'+ url)
            yield Request(url,method="GET",callback=self.parse_detail)

    
    def parse_detail(self,response):
        """
        详情页取内容
        """
        main_page = BeautifulSoup(response.text, "html.parser")
        atenAppNumber = main_page.select_one('.MainPanel #atenAppNumber')
        atenAppNumber = atenAppNumber.text
        item = PenrithItem()
        item["app_number"] = atenAppNumber
        detailleft = main_page.select('.MainPanel .detail .detailleft')
        detailright = main_page.select('.MainPanel .detail .detailright')
        for x, y in zip(detailleft, detailright):
            x = x.text.strip().split('\n')[0].replace(':', '')
            if x == 'Location':
                y = y.select('a')
                location_list = "Properties:"
                for z in y:
                    z = z.get('href')
                    z = z.strip("..")
                    z = "https://datracker.penrithcity.nsw.gov.au/track/Pages" + z + ';'
                    location_list += z
                # print(location_list)
                item["location"] = location_list
            elif x == 'Properties':
                pass
            elif x == "Description":
                y = y.text.strip().split('\n')[0].replace(':', '').replace("\r", '')
                item["description"] = y
            elif x == "Category":
                y = y.text.strip().split('\n')[0].replace(':', '').replace("\r", '')
                item["category"] = y
            elif x == "Status":
                y = y.text.strip().split('\n')[0].replace(':', '').replace("\r", '')
                item["status"] = y
            elif x == "Lodged":
                lodged_date = y.text.strip().split('\n')[0].replace(':', '').replace("\r", '')
                time_array = time.strptime(lodged_date, '%d/%m/%Y')
                temp_data = int(time.mktime(time_array))
                item["lodged"] = temp_data if lodged_date else None
            elif x == "Estimated Cost of Work":
                y = y.text.strip().split('\n')[0].replace(':', '').replace("\r", '')
                item["estimated_cost"] = y
            elif x == "Officer":
                y = y.text.strip().split('\n')[0].replace(':', '').replace("\r", '')
                item["officer"] = y
            elif x == "Decision":
                y = y.text.strip().split('\n')[0].replace(':', '').replace("\r", '')
                item["decision"] = y

        url = 'https://infolinkiconapipccprod.azurewebsites.net/api/ecmdocument/list?'
        playlod = f"appNumber={atenAppNumber}"
        print(playlod)
        session = requests.Session()
        resp = session.get(url,params=playlod)
        resp.encoding = 'utf-8'
        resp = resp.json()
        titles = ''
        for i in range(len(resp)):
            title = "https://infolinkiconapipccprod.azurewebsites.net/api/ecmdocument/download?relativePath="+resp[i]['OriginalPath']+";"
            titles += title
        item["documents"] = titles

        yield item







