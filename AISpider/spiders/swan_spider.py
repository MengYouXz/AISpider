import requests
import scrapy
from datetime import datetime
from scrapy.http import Request
from bs4 import BeautifulSoup
from AISpider.items.swan_items import SwanItem
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time
from datetime import date, datetime, timedelta
from common._date import get_all_month_
from common.set_date import get_this_month
'''
第一个 514 
第二个 138000
第三个 25000
第四个 没有时间一次全跑936
'''
class SwanSpider(scrapy.Spider):
    name = "swan"
    allowed_domains = ["eservices.swan.wa.gov.au"]
    start_urls = ["https://eservices.swan.wa.gov.au/ePathway/Production/Web/GeneralEnquiry/EnquiryLists.aspx"]
    custom_settings = {
        'LOG_STDOUT': True,
        # 'LOG_FILE': 'scrapy_swan2.log',
        'DOWNLOAD_TIMEOUT': 1200
    }


    def __init__(self,category=None,days=None):
        self.headers = {
        }
        self.cookie1 ={}
        self.cookie2 ={}
        self.cookie3 ={}
        self.cookie4 ={}
        self.category = category
        if days == None:
        # 如果没有传days默认为这个月的数据
            self.days = get_this_month()
        else:
            now = datetime.now()
            days = int(days)
            date_from = (now - timedelta(days)).date().strftime('%d/%m/%Y')
            # 这里计算出开始时间 设置到self.days
            self.days = date_from
        

    def start_requests(self):
        # start_time ='04/04/2024'
        # end_time = '07/04/2024'
        if self.category == 'first':
            all_month = get_all_month_(self.days, datetime.now().date().strftime('%d/%m/%Y'))
            for index, y_date in enumerate(all_month):
                if y_date == all_month[-1]:
                    break
                start_time = y_date
                end_time = all_month[index + 1]
                print('get_first_search_first'+start_time + "-----" + end_time)
                for item in self.get_first_search_first(start_time,end_time):
                    yield item
                print('get_first_search_second'+start_time + "-----" + end_time)
                for item in self.get_first_search_second(start_time,end_time):
                    yield item
                print('get_first_search_second'+start_time + "-----" + end_time)
                for item in self.get_first_search_third(start_time,end_time):
                    yield item
        # 第四个一次全跑
        if self.category == 'second':
            for item in self.get_second_search_first():
                yield item
       
        
    def get_first_search_first(self,start_time,end_time):
        opt = webdriver.ChromeOptions()
        opt.add_argument('--headless')
        opt.add_argument('--no-sandbox')
        opt.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome(opt)
        browser.get(self.start_urls[0])
        cookie1 = browser.get_cookie('ASP.NET_SessionId').get('value')
        cookie2 = browser.get_cookie('ePathway').get('value')
        self.cookie1 = {
            'ASP.NET_SessionId':cookie1,
            'ePathway':cookie2
        }
        browser.maximize_window()
        page_over = WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mDataList"]/tbody/tr[4]/td/legend')))
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mDataList"]/tbody/tr[4]/td/legend'))).click()
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mDataList_ctl03_mDataGrid_ctl02_ctl00"]'))).click()
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mContinueButton"]'))).click()
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mTabControl_tabControlMenun2"]'))).click()
        page_source = self.common_search(browser=browser, start=start_time, end=end_time)
        referer_url = browser.current_url
        self.headers ={
            'Referer':referer_url
        }
        url_list = self.deal_url_list(page_source)
        for url in url_list:
                yield Request(url,cookies=self.cookie1,headers=self.headers,dont_filter=False,)
        while True:
            url_list = self.nextPage(browser=browser)
            if url_list == None:break
            referer_url = browser.current_url
            self.headers ={
                'Referer':referer_url
            }
            for url in url_list:
                yield Request(url,cookies=self.cookie1,headers=self.headers,dont_filter=False,)
        browser.quit()

    def get_first_search_second(self,start_time,end_time):
        opt = webdriver.ChromeOptions()
        opt.add_argument('--headless')
        opt.add_argument('--no-sandbox')
        opt.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome(opt)
        browser.get(self.start_urls[0])
        cookie1 = browser.get_cookie('ASP.NET_SessionId').get('value')
        cookie2 = browser.get_cookie('ePathway').get('value')
        self.cookie2 = {
            'ASP.NET_SessionId':cookie1,
            'ePathway':cookie2
        }
        browser.maximize_window()
        page_over = WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mDataList"]/tbody/tr[4]/td/legend')))
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mDataList"]/tbody/tr[4]/td/legend'))).click()
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mDataList_ctl03_mDataGrid_ctl03_ctl00"]'))).click()
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mContinueButton"]'))).click()
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mTabControl_tabControlMenun3"]'))).click()
        page_source = self.common_search(browser=browser, start=start_time, end=end_time)
        referer_url = browser.current_url
        self.headers ={
            'Referer':referer_url
        }
        url_list = self.deal_url_list(page_source)
        if url_list == []:return None
        for url in url_list:
                yield Request(url,cookies=self.cookie2,headers=self.headers,dont_filter=False,)
        while True:
            url_list = self.nextPage(browser=browser)
            if url_list == None:break
            referer_url = browser.current_url
            self.headers ={
                'Referer':referer_url
            }
            for url in url_list:
                yield Request(url,cookies=self.cookie2,headers=self.headers,dont_filter=False,)

    def get_first_search_third(self,start_time,end_time):
        opt = webdriver.ChromeOptions()
        opt.add_argument('--headless')
        opt.add_argument('--no-sandbox')
        opt.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome(opt)
        browser.get(self.start_urls[0])
        cookie1 = browser.get_cookie('ASP.NET_SessionId').get('value')
        cookie2 = browser.get_cookie('ePathway').get('value')
        self.cookie3 = {
            'ASP.NET_SessionId':cookie1,
            'ePathway':cookie2
        }
        browser.maximize_window()
        start_time = WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mDataList"]/tbody/tr[4]/td/legend')))
        start_time.send
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mTabControl_tabControlMenun2"]'))).click()
        page_source = self.common_search(browser=browser, start=start_time, end=end_time)
        referer_url = browser.current_url
        self.headers ={
            'Referer':referer_url
        }
        url_list = self.deal_url_list(page_source)
        for url in url_list:
                yield Request(url,cookies=self.cookie3,headers=self.headers,dont_filter=False,)
        while True:
            url_list = self.nextPage(browser=browser)
            if url_list == None:break
            referer_url = browser.current_url
            self.headers ={
                'Referer':referer_url
            }
            for url in url_list:
                yield Request(url,cookies=self.cookie3,headers=self.headers,dont_filter=False,)

    def get_second_search_first(self):
        opt = webdriver.ChromeOptions()
        opt.add_argument('--headless')
        opt.add_argument('--no-sandbox')
        opt.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome(opt)
        browser.get(self.start_urls[0])
        cookie1 = browser.get_cookie('ASP.NET_SessionId').get('value')
        cookie2 = browser.get_cookie('ePathway').get('value')
        self.cookie4 = {
            'ASP.NET_SessionId':cookie1,
            'ePathway':cookie2
        }
        browser.maximize_window()
        page_over = WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mDataList"]/tbody/tr[6]/td/legend')))
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mDataList"]/tbody/tr[6]/td/legend'))).click()
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mDataList_ctl05_mDataGrid_ctl02_ctl00"]'))).click()
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mContinueButton"]'))).click()
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mTabControl_tabControlMenun1"]'))).click()
        WebDriverWait(browser,30,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mSearchButton"]'))).click()
        page_source = browser.page_source
        referer_url = browser.current_url
        self.headers ={
            'Referer':referer_url
        }
        url_list = self.deal_url_list2(page_source)
        for url in url_list:
                yield Request(url,cookies=self.cookie4,headers=self.headers,dont_filter=False,)
        while True:
            url_list = self.nextPage2(browser=browser)
            if url_list == None:break
            referer_url = browser.current_url
            self.headers ={
                'Referer':referer_url
            }
            for url in url_list:
                yield Request(url,cookies=self.cookie4,headers=self.headers,dont_filter=False,)
      
    def common_search(self,browser,start,end):
        '''
        用于提交每个月
        返回搜索结果页
        '''    
        try:
            start_time = browser.find_element(By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mTabControl_ctl14_mFromDatePicker_dateTextBox"]')
            end_time = browser.find_element(By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mTabControl_ctl14_mToDatePicker_dateTextBox"]')
            start_time.clear()
            end_time.clear()
            start_time.send_keys(start)
            end_time.send_keys(end)
            search = browser.find_element(By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mSearchButton"]').click()
            page_source = browser.page_source
            return page_source
        except:
            pass
        try:
            start_time = browser.find_element(By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mTabControl_ctl19_mFromDatePicker_dateTextBox"]')
            end_time = browser.find_element(By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mTabControl_ctl19_mToDatePicker_dateTextBox"]')
            start_time.clear()
            end_time.clear()
            start_time.send_keys(start)
            end_time.send_keys(end)
            search = browser.find_element(By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mSearchButton"]').click()
            page_source = browser.page_source
            return page_source

        except:
            pass
        try:
            start_time = browser.find_element(By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mTabControl_ctl14_mFromDatePicker_dateTextBox"]"]')
            end_time = browser.find_element(By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mTabControl_ctl14_mToDatePicker_dateTextBox"]')
            start_time.clear()
            end_time.clear()
            start_time.send_keys(start)
            end_time.send_keys(end)
            search = browser.find_element(By.XPATH,'//*[@id="ctl00_MainBodyContent_mGeneralEnquirySearchControl_mSearchButton"]').click()
            page_source = browser.page_source
            return page_source
        except:
            pass
        
    def deal_url_list(self,resp):
        """
        处理搜索结果页
        返回列表页URL
        """
        soup = BeautifulSoup(resp, 'html.parser')
        judge = soup.select_one('.ErrorContentText')
        temp_list = []
        if judge: return temp_list

        url_list = soup.select('#gridResults a')
        for url in url_list:
            url = 'https://eservices.swan.wa.gov.au/ePathway/Production/Web/GeneralEnquiry/' + url.get('href').strip()
            temp_list.append(url)
        # 去掉多余的url
        temp_list2 = []
        for url in temp_list:
            if "EnquirySummaryView" in url:
                pass
            else:
                temp_list2.append(url)

        return temp_list2

    def deal_url_list2(self,resp):
        """
        处理搜索结果页
        返回列表页URL
        """
        soup = BeautifulSoup(resp, 'html.parser')
        url_list = soup.select('#gridResults a')
        temp_list = []
        for url in url_list:
            url = 'https://eservices.swan.wa.gov.au' + url.get('href').strip()
            # https://eservices.swan.wa.gov.au/ePathway/Production/Web/GeneralEnquiry//ePathway/Production/Web/GeneralEnquiry/EnquiryDetailView.aspx?Id=468437
            # https://eservices.swan.wa.gov.au/ePathway/Production/Web/GeneralEnquiry/EnquiryDetailView.aspx?Id=479152
            temp_list.append(url)
        # 去掉多余的url
        temp_list2 = []
        for url in temp_list:
            if "EnquirySummaryView" in url:
                pass
            else:
                temp_list2.append(url)

        return temp_list2

    def nextPage(self, browser):
        try:
            WebDriverWait(browser,6,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mPagingControl_nextPageHyperLink"]'))).click()
            page_source = browser.page_source
            url_list = self.deal_url_list(page_source)
            return url_list
        except:
            return None

    def nextPage2(self, browser):
        try:
            WebDriverWait(browser,6,0.5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ctl00_MainBodyContent_mPagingControl_nextPageHyperLink"]'))).click()
            page_source = browser.page_source
            url_list = self.deal_url_list2(page_source)
            return url_list
        except:
            return None
            
    def parse(self, response):
        """
        处理结果
        """
        item = SwanItem()
        soup = BeautifulSoup(response.text,'html.parser')
        head = soup.select('fieldset .fields .field .AlternateContentHeading')
        text = soup.select('fieldset .fields .field .AlternateContentText')
        temp_dict = {}
        try:
            for x,y in zip(head,text):
                x = x.get_text().replace('/n','').replace('/t','').replace('/r','')
                y = y.get_text().replace('/n','').replace('/t','').replace('/r','')
                temp_dict[x] = y
            try:
                item['app_number'] = temp_dict['Application number']
            except:
                item['app_number'] = ''
            try:
                item['app_type'] = temp_dict['Application type']
            except:
                item['app_type'] = ''
            try:
                item['app_description'] = temp_dict['Application description']
            except:
                item['app_description'] = ''
            try:
                item['status'] = temp_dict['Status']
            except:
                item['status'] = ''
            try:
                lodged_date = temp_dict['Lodged']
                time_array = time.strptime(lodged_date, '%d/%m/%Y')
                temp_data = int(time.mktime(time_array))
                item['lodged'] = temp_data if lodged_date else None   
            except:
                item['lodged'] = None
            try:
                item['app_location'] = temp_dict['Application location']
            except:
                item['app_location'] = ''
            try:
                item['pro_adderss'] = temp_dict['Property Address']
            except:
                item['pro_adderss'] = ''
            try:
                item['pro_type'] = temp_dict['Property Type']
            except:
                item['pro_type'] = ''
            try:
                item['pro_ward'] = temp_dict['Property Ward']
            except:
                item['pro_ward'] = ''
            try:
                item['land_area'] = temp_dict['Land Area (Square Metres)']
            except:
                item['land_area'] = ''
            # 特殊处理
            try:
                if item['app_number'] == '':
                    item['app_number'] = temp_dict['Property ID']
            except:
                item['app_number'] = ''
            try:
                if item['app_number'] == '':
                    item['app_number'] = temp_dict['Reference']
            except:
                item['app_number'] = ''
            try:
                if item['app_location'] == '':
                    item['app_location'] = temp_dict['Primary location']
            except:
                item['app_location'] = ''
            try:
                if item['lodged'] == None:
                    lodged_date = temp_dict['Lodgement date']
                    time_array = time.strptime(lodged_date, '%d/%m/%Y')
                    temp_data = int(time.mktime(time_array))
                    item['lodged'] = datetime.strptime(lodged_date, '%d/%m/%Y') if lodged_date else None  
            except:
                item['lodged'] = None
        except :
            print("特殊情况未处理")
        try:
            other_data= soup.select('#ctl00_MainBodyContent_group_77 fieldset .ContentPanel td')
            if other_data == []:
                pass
            else:
                temp_list = []
                for x in other_data:
                    temp_list.append(x.get_text().replace('/n','').replace('/t','').replace('/r',''))
                try:
                    item['pro_adderss'] = temp_list[0]
                except:
                    item['pro_adderss'] = ''
                try:
                    item['pro_ward'] = temp_list[1]
                except:
                    item['pro_ward'] = ''
        except:
            pass
        
        yield item
         
