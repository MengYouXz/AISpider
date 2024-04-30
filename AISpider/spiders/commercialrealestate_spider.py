import scrapy
from scrapy import Request
from bs4 import BeautifulSoup
from curl_cffi import requests
import json
from AISpider.items.commercialrealestate_items import Commercialrealestate
from datetime import datetime
import re
# 请求首页返回cookie
# 拿cookie请求json
# 解析json请求详情页不要cookie


class CommercialrealestateSpider(scrapy.Spider):
    name = "commercialrealestate"
    allowed_domains = ["www.commercialrealestate.com.au"]
    start_urls = ["https://www.commercialrealestate.com.au/for-sale/?kw=Childcare",
    "https://www.commercialrealestate.com.au/for-lease/?kw=Childcare",
    "https://www.commercialrealestate.com.au/sold/?kw=Childcare",
    "https://www.commercialrealestate.com.au/leased/?kw=Childcare",
    "https://www.commercialrealestate.com.au/for-sale/australia/development-land/",
    "https://www.commercialrealestate.com.au/sold/australia/development-land/"
    ]
    custom_settings = {
        'LOG_STDOUT': True,
        # 'LOG_FILE': 'scrapy_commercialrealestate5.log',
        'DOWNLOAD_TIMEOUT': 1200
    }
    def __init__(self,category=None):
        self.headers={
            'Host': 'www.commercialrealestate.com.au',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            }
        self.cookies={
        }
        self.url_interface1 = 'https://www.commercialrealestate.com.au/bf/api/gqlb?'
        self.proxy = {'https': 'http://127.0.0.1:8888'}
        self.category = category
    
    def get_page_num(self,num=0):
        session = requests.Session()
        session.headers.clear()
        session.headers.update(self.headers)
        resp = session.get(self.start_urls[num])
        soup = BeautifulSoup(resp.text,'html.parser')
        page_num = int(soup.select_one('.css-1c0mwkm').get_text().split(' ')[-1])
        return page_num
    def start_requests(self):
        if self.category == None:
            print('Please set the category')
            return
        elif self.category == 'for-sale':
            page_num = self.get_page_num(0)
            for item in self.get_sale_data(page_num):
                yield item
        elif self.category == 'for-lease':    
            page_num = self.get_page_num(1)
            for item in self.get_lease_data(page_num):
                yield item
        elif self.category == 'sold':    
            page_num = self.get_page_num(2)
            for item in self.get_sold_data(page_num):
                yield item
        elif self.category == 'leased':        
            page_num = self.get_page_num(3)
            for item in self.get_leased_data(page_num):
                yield item
        elif self.category == 'for-sale-dev':    
            page_num = self.get_page_num(4)
            for item in self.get_dev_sale_data(page_num):
                yield item
        elif self.category == 'sold-dev':                
            page_num = self.get_page_num(5)
            for item in self.get_dev_sold_data(page_num):
                yield item
        else: 
            print('Please set correct category')
            return    
    def get_sale_data(self,page_num):
        session = requests.Session()
        # 设置请求头顺序，顺序不同返回cookies不同
        session.headers.clear()
        session.headers.update(self.headers)
        resp = session.get(url=self.start_urls[0],)
        # 请求接口拿id
        for i in range(page_num+1):
            if i == 0:continue
            formdata = self.deal_formdata1(page_num=i)
            resp = session.get(url=self.url_interface1,params = formdata,)
            soup = json.loads(resp.text)
            temp_list = soup['data']['searchListings']['pagedSearchResults']
            agent_infos = soup['data']['searchListings']['pagedSearchResults']
            for agent_info,url in zip(agent_infos,temp_list):
                agent_info = agent_info['shortDescription']
                url = 'https://www.commercialrealestate.com.au'+url['seoUrl']
                yield Request(url=url,cookies={},dont_filter=False,callback=self.parse,meta={'type':'childcare for sale','agent':agent_info})

    def get_lease_data(self,page_num):
        session = requests.Session()
        # 设置请求头顺序，顺序不同返回cookies不同
        session.headers.clear()
        session.headers.update(self.headers)
        resp = session.get(url=self.start_urls[1],)
        # 请求接口拿id
        for i in range(page_num+1):
            if i == 0:continue
            formdata = self.deal_formdata2(page_num=i)
            resp = session.get(url=self.url_interface1,params = formdata,)
            soup = json.loads(resp.text)
            agent_infos = soup['data']['searchListings']['pagedSearchResults']
            temp_list = soup['data']['searchListings']['pagedSearchResults']
            for agent_info,url in zip(agent_infos,temp_list):
                agent_info = agent_info['shortDescription']
                url = 'https://www.commercialrealestate.com.au'+url['seoUrl']
                yield Request(url=url,cookies={},dont_filter=False,callback=self.parse2,meta={'type':'childcare for lease','agent':agent_info})
    
    def get_sold_data(self,page_num):
        session = requests.Session()
        # 设置请求头顺序，顺序不同返回cookies不同
        session.headers.clear()
        session.headers.update(self.headers)
        resp = session.get(url=self.start_urls[2],)
        # 请求接口拿id
        for i in range(page_num+1):
            if i == 0:continue
            formdata = self.deal_formdata3(page_num=i)
            resp = session.get(url=self.url_interface1,params = formdata,)
            soup = json.loads(resp.text)
            agent_infos = soup['data']['searchListings']['pagedSearchResults']
            temp_list = soup['data']['searchListings']['pagedSearchResults']
            for agent_info,url in zip(agent_infos,temp_list):
                agent_info = agent_info['shortDescription']
                url = 'https://www.commercialrealestate.com.au'+url['seoUrl']
                yield Request(url=url,cookies={},dont_filter=False,callback=self.parse3,meta={'type':'childcare sold','agent':agent_info})

    def get_leased_data(self,page_num):
        session = requests.Session()
        # 设置请求头顺序，顺序不同返回cookies不同
        session.headers.clear()
        session.headers.update(self.headers)
        resp = session.get(url=self.start_urls[3],)
        # 请求接口拿id
        for i in range(page_num+1):
            if i == 0:continue
            formdata = self.deal_formdata4(page_num=i)
            resp = session.get(url=self.url_interface1,params = formdata,)
            soup = json.loads(resp.text)
            agent_infos = soup['data']['searchListings']['pagedSearchResults']
            temp_list = soup['data']['searchListings']['pagedSearchResults']
            for agent_info,url in zip(agent_infos,temp_list):
                agent_info = agent_info['shortDescription']
                url = 'https://www.commercialrealestate.com.au'+url['seoUrl']
                yield Request(url=url,cookies={},dont_filter=False,callback=self.parse3,meta={'type':'childcare leased','agent':agent_info})
    
    def get_dev_sale_data(self,page_num):
        session = requests.Session()
        # 设置请求头顺序，顺序不同返回cookies不同
        session.headers.clear()
        session.headers.update(self.headers)
        resp = session.get(url=self.start_urls[4],)
        # 请求接口拿id
        for i in range(page_num+1):
            if i == 0:continue
            formdata = self.deal_formdata5(page_num=i)
            resp = session.get(url=self.url_interface1,params = formdata,)
            soup = json.loads(resp.text)
            agent_infos = soup['data']['searchListings']['pagedSearchResults']
            temp_list = soup['data']['searchListings']['pagedSearchResults']
            for agent_info,url in zip(agent_infos,temp_list):
                agent_info = agent_info['shortDescription']
                url = 'https://www.commercialrealestate.com.au'+url['seoUrl']
                yield Request(url=url,dont_filter=False,cookies={},callback=self.parse3,meta={'type':'development site for sale','agent':agent_info})
    
    def get_dev_sold_data(self,page_num):
        session = requests.Session()
        # 设置请求头顺序，顺序不同返回cookies不同
        session.headers.clear()
        session.headers.update(self.headers)
        resp = session.get(url=self.start_urls[5],)
        self.cookies = resp.cookies.get_dict()
        # 请求接口拿id
        for i in range(page_num+1):
            if i == 0:continue
            formdata = self.deal_formdata6(page_num=i)
            resp = session.get(url=self.url_interface1,params = formdata,)
            soup = json.loads(resp.text)
            agent_infos = soup['data']['searchListings']['pagedSearchResults']
            temp_list = soup['data']['searchListings']['pagedSearchResults']
            for agent_info,url in zip(agent_infos,temp_list):
                agent_info = agent_info['shortDescription']
                url = 'https://www.commercialrealestate.com.au'+url['seoUrl']
                yield Request(url=url,cookies={},dont_filter=False,callback=self.parse3,meta={'type':'development site sold','agent':agent_info})

    def deal_formdata1(self,page_num):
        temp_str = '{"detailsAdId":0,"searchType":6,"saleModeId":0,"pageNo":'
        formdata = {
            'operationName':'propertySearchQuery',
            'variables':temp_str+str(page_num)+',"pageSize":20,"sortingOption":0,"categoryIds":[],"priceFrom":null,"priceTo":null,"stateIds":[],"regionIds":[],"areaIds":[],"suburbIds":[],"adIds":[],"keywords":"Childcare","agencyIds":[],"buildingSizeFrom":null,"buildingSizeTo":null,"landSizeFrom":null,"occupancyStatus":null,"carSpaces":null,"landSizeTo":null,"saleMethod":null,"boundingBox":null,"featureFlags":"transport-component,adbridg-ads,static-enquiry-form,related-searches,property-page-bfnew"}',
            'extensions':'{"persistedQuery":{"version":1,"sha256Hash":"f8708b9598f15c29e61d58b0a20253fac0b4b54a702864c243e32d5942929d5e"}}'
        }
        return formdata

    def deal_formdata2(self,page_num):
        temp_str = '{"detailsAdId":0,"searchType":7,"saleModeId":1,"pageNo":'
        formdata = {
            'operationName':'propertySearchQuery',
            'variables':temp_str+str(page_num)+',"pageSize":20,"sortingOption":0,"categoryIds":[],"priceFrom":null,"priceTo":null,"stateIds":[],"regionIds":[],"areaIds":[],"suburbIds":[],"adIds":[],"keywords":"Childcare","agencyIds":[],"buildingSizeFrom":null,"buildingSizeTo":null,"landSizeFrom":null,"occupancyStatus":null,"carSpaces":null,"landSizeTo":null,"saleMethod":null,"boundingBox":null,"featureFlags":"transport-component,adbridg-ads,static-enquiry-form,related-searches,property-page-bfnew"}',
            'extensions':'{"persistedQuery":{"version":1,"sha256Hash":"f8708b9598f15c29e61d58b0a20253fac0b4b54a702864c243e32d5942929d5e"}}'        
        }
        return formdata

    def deal_formdata3(self,page_num):
        temp_str = '{"detailsAdId":0,"searchType":8,"saleModeId":3,"pageNo":'
        formdata = {
            'operationName':'propertySearchQuery',
            'variables':temp_str+str(page_num)+',"pageSize":20,"sortingOption":0,"categoryIds":[],"priceFrom":null,"priceTo":null,"stateIds":[],"regionIds":[],"areaIds":[],"suburbIds":[],"adIds":[],"keywords":"Childcare","agencyIds":[],"buildingSizeFrom":null,"buildingSizeTo":null,"landSizeFrom":null,"occupancyStatus":null,"carSpaces":null,"landSizeTo":null,"saleMethod":null,"boundingBox":null,"featureFlags":"transport-component,adbridg-ads,static-enquiry-form,related-searches,property-page-bfnew"}',
            'extensions':'{"persistedQuery":{"version":1,"sha256Hash":"f8708b9598f15c29e61d58b0a20253fac0b4b54a702864c243e32d5942929d5e"}}'        
        }
        return formdata

    def deal_formdata4(self,page_num):
        temp_str = '{"detailsAdId":0,"searchType":9,"saleModeId":4,"pageNo":'
        formdata = {
            'operationName':'propertySearchQuery',
            'variables':temp_str+str(page_num)+',"pageSize":20,"sortingOption":0,"categoryIds":[],"priceFrom":null,"priceTo":null,"stateIds":[],"regionIds":[],"areaIds":[],"suburbIds":[],"adIds":[],"keywords":"Childcare","agencyIds":[],"buildingSizeFrom":null,"buildingSizeTo":null,"landSizeFrom":null,"occupancyStatus":null,"carSpaces":null,"landSizeTo":null,"saleMethod":null,"boundingBox":null,"featureFlags":"transport-component,adbridg-ads,static-enquiry-form,related-searches,property-page-bfnew"}',
            'extensions':'{"persistedQuery":{"version":1,"sha256Hash":"f8708b9598f15c29e61d58b0a20253fac0b4b54a702864c243e32d5942929d5e"}}'        
        }
        return formdata


    def deal_formdata5(self,page_num):
        temp_str = '{"detailsAdId":0,"searchType":6,"saleModeId":0,"pageNo":'
        formdata = {
            'operationName':'propertySearchQuery',
            'variables':temp_str+str(page_num)+',"pageSize":20,"sortingOption":0,"categoryIds":[72],"priceFrom":null,"priceTo":null,"stateIds":[],"regionIds":[],"areaIds":[],"suburbIds":[],"adIds":[],"keywords":"","agencyIds":[],"buildingSizeFrom":null,"buildingSizeTo":null,"landSizeFrom":null,"occupancyStatus":null,"carSpaces":null,"landSizeTo":null,"saleMethod":null,"boundingBox":null,"featureFlags":"transport-component,adbridg-ads,static-enquiry-form,related-searches,property-page-bfnew"}',
            'extensions':'{"persistedQuery":{"version":1,"sha256Hash":"f8708b9598f15c29e61d58b0a20253fac0b4b54a702864c243e32d5942929d5e"}}'        
        }
        return formdata

    def deal_formdata6(self,page_num):
        temp_str = '{"detailsAdId":0,"searchType":8,"saleModeId":3,"pageNo":'
        formdata = {
            'operationName':'propertySearchQuery',
            'variables':temp_str+str(page_num)+',"pageSize":20,"sortingOption":0,"categoryIds":[72],"priceFrom":null,"priceTo":null,"stateIds":[],"regionIds":[],"areaIds":[],"suburbIds":[],"adIds":[],"keywords":"","agencyIds":[],"buildingSizeFrom":null,"buildingSizeTo":null,"landSizeFrom":null,"occupancyStatus":null,"carSpaces":null,"landSizeTo":null,"saleMethod":null,"boundingBox":null,"featureFlags":"transport-component,adbridg-ads,static-enquiry-form,related-searches,property-page-bfnew"}',
            'extensions':'{"persistedQuery":{"version":1,"sha256Hash":"f8708b9598f15c29e61d58b0a20253fac0b4b54a702864c243e32d5942929d5e"}}'        
        }
        return formdata

    def parse(self, response):
        item = Commercialrealestate()
        item['type_'] = response.meta['type']
        soup = BeautifulSoup(response.text, 'html.parser')
        address=''.join(re.findall('"fullAddress":"(.*?)",',response.text))
        item['agent_info'] = response.meta['agent']+':'+address
        item['address'] = soup.select_one('h1').get_text()
        item['value'] = soup.select_one('.css-1bcq2y2 .icon-text').get_text()
        th = soup.select('.css-5a1t3x .css-1bktxj th')
        td = soup.select('.css-5a1t3x .css-1bktxj td')
        temp_dict = {}
        for x,y in zip(th,td):
            temp_dict[x.get_text().replace('\n','').replace('\r','').replace('\t','')] = y.get_text().replace('\n','').replace('\r','').replace('\t','')
        
        temp_list = list(temp_dict.keys())
        item['floor_area'] = temp_dict['Floor Area']if 'Floor Area' in temp_list else None
        item['land_area'] = temp_dict['Land Area']if 'Land Area' in temp_list else None
        item['parking'] = temp_dict['Parking']if 'Parking' in temp_list else None
        item['annual_return'] = temp_dict['Annual Return']if 'Annual Return' in temp_list else None
        item['availability'] = temp_dict['Availability']if 'Availability' in temp_list else None
        item['app_number'] = temp_dict['Property ID']

        category = soup.select('.css-5a1t3x .css-1baulvz a')
        temp_list = []
        for c in category:
            temp_list.append(c.get_text().replace('\n','').replace('\r','').replace('\t',''))
        temp_str = ''
        for i in range(int(len(temp_list)/2)):
            temp_str += temp_list[i]
        item['category'] = temp_str
        try:
            lodged_date = soup.select_one('.css-1jttpen .css-5a1t3x tbody td').get_text().split(' ')[0]
            time_array = time.strptime(lodged_date, '%d/%m/%Y')
            temp_data = int(time.mktime(time_array))
            item['closing_date'] = temp_data if lodged_date else None 

            item['recipient_name'] = soup.select('.css-1jttpen .css-5a1t3x tbody  td')[1].get_text() 
            item['delivery_address'] = soup.select('.css-1jttpen .css-5a1t3x tbody  td')[2].get_text()
        except:
            pass
        try:
            description1 = soup.select_one('h2').get_text()
        except:
            description1 = ''
        try:
            description2 = soup.select_one('.css-hp4qv').get_text()
        except:
            description2 = ''
        try:
            description3 = soup.select_one('.css-19rklic').get_text()
        except:
            description3
        item['description'] = description1+description2+description3
        yield item

    def parse2(self, response):
        item = Commercialrealestate()
        item['type_'] = response.meta['type']
        soup = BeautifulSoup(response.text, 'html.parser')
        address=''.join(re.findall('"fullAddress":"(.*?)",',response.text))
        item['agent_info'] = response.meta['agent']+':'+address
        item['address'] = soup.select_one('h1').get_text()
        item['value'] = soup.select_one('.css-1bcq2y2 .icon-text').get_text()
        th = soup.select('.css-5a1t3x .css-1bktxj th')
        td = soup.select('.css-5a1t3x .css-1bktxj td')
        temp_dict = {}
        for x,y in zip(th,td):
            temp_dict[x.get_text().replace('\n','').replace('\r','').replace('\t','')] = y.get_text().replace('\n','').replace('\r','').replace('\t','')
        
        temp_list = list(temp_dict.keys())
        item['floor_area'] = temp_dict['Floor Area']if 'Floor Area' in temp_list else None
        item['land_area'] = temp_dict['Land Area']if 'Land Area' in temp_list else None
        item['parking'] = temp_dict['Parking']if 'Parking' in temp_list else None
        item['annual_return'] = temp_dict['Annual Return']if 'Annual Return' in temp_list else None
        item['availability'] = temp_dict['Availability']if 'Availability' in temp_list else None
        item['app_number'] = temp_dict['Property ID']

        category = soup.select('.css-5a1t3x .css-1baulvz a')
        temp_list = []
        for c in category:
            temp_list.append(c.get_text().replace('\n','').replace('\r','').replace('\t',''))
        temp_str = ''
        for i in range(int(len(temp_list)/2)):
            temp_str += temp_list[i]
        item['category'] = temp_str
        try:
            lodged_date = soup.select_one('.css-1jttpen .css-5a1t3x tbody td').get_text().split(' ')[0]
            time_array = time.strptime(lodged_date, '%d/%m/%Y')
            temp_data = int(time.mktime(time_array))
            item['closing_date'] = temp_data if lodged_date else None 

            item['recipient_name'] = soup.select('.css-1jttpen .css-5a1t3x tbody  td')[1].get_text() 
            item['delivery_address'] = soup.select('.css-1jttpen .css-5a1t3x tbody  td')[2].get_text()
        except:
            pass
        try:
            description1 = soup.select_one('h2').get_text()
        except:
            description1 = ''
        try:
            description2 = soup.select_one('.css-hp4qv').get_text()
        except:
            description2 = ''
        try:
            description3 = soup.select_one('.css-19rklic').get_text()
        except:
            description3
        item['description'] = description1+description2+description3
        yield item
    
    def parse3(self, response):
        item = Commercialrealestate()
        item['type_'] = response.meta['type']
        soup = BeautifulSoup(response.text, 'html.parser')
        address=''.join(re.findall('"fullAddress":"(.*?)",',response.text))
        try:
            item['agent_info'] = response.meta['agent']+':'+address
        except:
            item['agent_info'] = address
        item['address'] = soup.select_one('h1').get_text()
        item['value'] = soup.select_one('.css-1bcq2y2 .icon-text').get_text()
        th = soup.select('.css-5a1t3x .css-1bktxj th')
        td = soup.select('.css-5a1t3x .css-1bktxj td')
        temp_dict = {}
        for x,y in zip(th,td):
            temp_dict[x.get_text().replace('\n','').replace('\r','').replace('\t','')] = y.get_text().replace('\n','').replace('\r','').replace('\t','')
        
        temp_list = list(temp_dict.keys())
        item['floor_area'] = temp_dict['Floor Area']if 'Floor Area' in temp_list else None
        item['land_area'] = temp_dict['Land Area']if 'Land Area' in temp_list else None
        item['parking'] = temp_dict['Parking']if 'Parking' in temp_list else None
        item['annual_return'] = temp_dict['Annual Return']if 'Annual Return' in temp_list else None
        item['availability'] = temp_dict['Availability']if 'Availability' in temp_list else None
        item['app_number'] = temp_dict['Property ID']

        category = soup.select('.css-5a1t3x .css-1baulvz a')
        temp_list = []
        for c in category:
            temp_list.append(c.get_text().replace('\n','').replace('\r','').replace('\t',''))
        temp_str = ''
        for i in range(int(len(temp_list)/2)):
            temp_str += temp_list[i]
        item['category'] = temp_str
        try:
            lodged_date = temp_dict['Date Sold']
            time_array = time.strptime(lodged_date, '%d/%m/%Y')
            temp_data = int(time.mktime(time_array))
            item['closing_date'] = temp_data if lodged_date else None 

        except:
            pass
        try: 
            item['delivery_address'] = soup.select('.css-1jttpen .css-5a1t3x tbody  td')[1].get_text()
        except:
            pass
        try:
            description1 = soup.select_one('h2').get_text()
        except:
            description1 = ''
        try:
            description2 = soup.select_one('.css-hp4qv').get_text()
        except:
            description2 = ''
        try:
            description3 = soup.select_one('.css-19rklic').get_text()
        except:
            description3 = ''
        item['description'] = description1+description2+description3
        yield item