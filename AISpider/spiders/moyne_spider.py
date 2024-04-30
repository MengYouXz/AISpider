import scrapy
import requests
from bs4 import BeautifulSoup
from scrapy import Request
from AISpider.items.moyne_items import MoyneItem
class MoyneSpider(scrapy.Spider):
    name = "moyne"
    allowed_domains = ["www.moyne.vic.gov.au"]
    start_urls = ["https://www.moyne.vic.gov.au/Your-Property/Building-and-Planning/Planning/Statutory-Planning/Advertised-Planning-Applications"]

    def parse(self, response):
        url_m = 'https://www.moyne.vic.gov.au/Your-Property/Building-and-Planning/Planning/Statutory-Planning/Advertised-Planning-Applications'
        for i in range(4):
            if i == 0:
                pass
            else:
                url_detail = self.deal_page(num=i,url=url_m)
                print(url_detail)
                print("===================================")
                for url in url_detail:
                    yield Request(url,callback=self.parse_detail)




    def deal_page(self,num,url):
        end_data = f'?dlv_Copy%20of%20MSC%20Planning%20Application%20Listing=(pageindex={num})'
        url = url + end_data
        print(url)
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        url_list = soup.select('article a')
        url_detail = []
        for i in url_list:
            url_detail.append(i.get('href'))
        return url_detail

    def parse_detail(self,response):
        item = MoyneItem()
        soup = BeautifulSoup(response.text, 'html.parser')
        keys = soup.select('.field-label')
        values = soup.select('.field-value')
        adderss = soup.select_one('.gmap-address').get_text().strip().replace('\r', '')
        item['address'] = adderss
        temp_dick = {}
        for key, value in zip(keys, values):
            temp_dick[key.get_text()] = value.get_text()
        try:
            item['app_number'] = temp_dick['Application number'].strip().replace('\r', '')
        except:
            item['app_number'] = None
        try:
            item['description'] = temp_dick['Proposal'].strip().replace('\r', '')
        except:
            item['description'] = None
        doucuments = soup.select('.related-information-list a')
        doucument_list = ""
        for doucument in doucuments:
            doucument = 'https://www.moyne.vic.gov.au' + doucument.get('href')
            doucument_list += doucument +";"
        item['documents'] = doucument_list
        yield item