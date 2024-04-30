import scrapy
from bs4 import BeautifulSoup
from scrapy import Request
from AISpider.items.moira_items import MoiraItem
from datetime import datetime
class MoiraSpider(scrapy.Spider):
    name = "moira"
    allowed_domains = ["www.moira.vic.gov.au"]
    start_urls = ["https://www.moira.vic.gov.au/Residents/Building-and-planning/Planning/Current-applications-on-advertising"]

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        url_list = soup.select('.list-item-container a')
        for url in url_list:
            url_detail = url.get('href')
            print(url_detail)
            yield Request(url=url_detail,method="GET",callback=self.parse_detail)


    def parse_detail(self,response):
        item = MoiraItem()
        soup = BeautifulSoup(response.text, 'html.parser')
        keys = soup.select('.field-label')
        values = soup.select('.field-value')
        adderss = soup.select_one('.oc-page-title').get_text()
        item['address'] = adderss
        temp_dick = {}
        for key,value in zip(keys,values):
            temp_dick[key.get_text()]=value.get_text()
        try:
            item['app_number'] = temp_dick['Application number']
        except:
            item['app_number'] = None
        try:
            item['description'] = temp_dick['Proposal']
        except:
            item['description'] = None
        try:
            item['app_name'] = temp_dick['Applicant name']
        except:
            item['app_name'] = None
        try:
            item['lodged'] = temp_dick['Lodgement date']
        except:
            item['lodged'] = None

        doucuments = soup.select('.related-information-list a')
        doucument_list = ''
        for doucument in doucuments:
            doucument = 'https://www.moira.vic.gov.au' + doucument.get('href')
            doucument_list += doucument + ';'
        item['documents'] = doucument_list
        yield item
