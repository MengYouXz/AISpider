import scrapy
from scrapy import Request
import json
from bs4 import BeautifulSoup
import random
import requests
from AISpider.items.southgippsland_items import Southgippsland
from common._date import get_all_month

import time
from datetime import date, datetime, timedelta
from common._date import get_all_month
from common.set_date import get_this_month,get_next_month

# 最早的数据在1900年
# 1900-2000 年大概270条
# 2000-2024.04 大概10900条
global_url = ''
class SouthgippslandSpider(scrapy.Spider):
    name = "southgippsland"
    allowed_domains = ["eservices.southgippsland.vic.gov.au"]
    start_urls = ["https://eservices.southgippsland.vic.gov.au/ePathway/ePathProd/Web/Default.aspx"]
    custom_settings = {
        'LOG_STDOUT': True,
        #'LOG_FILE': 'scrapy_southgippsland.log',
        'DOWNLOAD_TIMEOUT': 1200
    }
    def __init__(self,category=None,days=None,*args, **kwargs):
        self.url_default = 'https://eservices.southgippsland.vic.gov.au/ePathway/ePathProd/Web/Default.aspx'
        self.url_enquiry_lists = 'https://eservices.southgippsland.vic.gov.au/ePathway/ePathProd/Web/GeneralEnquiry/EnquiryLists.aspx'
        self.url_enquiry_summary_view = 'https://eservices.southgippsland.vic.gov.au/ePathway/ePathProd/Web/GeneralEnquiry/EnquirySummaryView.aspx?EnquiryListId=55'
        self.url_enquiry_search = 'https://eservices.southgippsland.vic.gov.au/ePathway/ePathProd/Web/GeneralEnquiry/EnquirySearch.aspx?EnquiryListId=57'
        self.url_enquiry_summary_view2 = 'https://eservices.southgippsland.vic.gov.au/ePathway/ePathProd/Web/GeneralEnquiry/EnquirySummaryView.aspx?EnquiryListId=57'
        self.url_enquiry_summary = 'https://eservices.southgippsland.vic.gov.au/ePathway/ePathProd/Web/GeneralEnquiry/EnquirySummaryView.aspx'
        self.headers = {
        }
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

    
    def parse(self, response):
        '''
        搜索页面有两个
        '''
        if self.category == 'first':
            for item in self.deal_first_search_first():
                yield item
        # 这个网页请求的日期超过当前日期会报错
        # 按照年份请求每年 改按照月份4.25
        else:
            all_month = get_all_month(self.days, "%d/%m/%Y")
            for index, y_date in enumerate(all_month):
                if y_date == all_month[-1]:
                    break
                start_time = y_date
                end_time = all_month[index + 1]

                judge_result = self.judge_date(start_time)
                if datetime.strptime(self.days, '%d/%m/%Y').timestamp() > datetime.strptime(start_time, '%d/%m/%Y').timestamp() and judge_result==True:continue
                if self.days.split('/')[1] == start_time.split('/')[1] and self.days.split('/')[2] == start_time.split('/')[2]:
                    start_time = self.days
                if end_time == get_next_month():
                    end_time = datetime.now().date().strftime('%d/%m/%Y')
                print(start_time + "-----" + end_time)
                for item in self.deal_first_search_second(start_time,end_time):
                    yield item

    def judge_date(self,start_time):
        if self.days.split('/')[2] == start_time.split('/')[2]:
            if self.days.split('/')[1] == start_time.split('/')[1]:
                return False
            else:return True
        else:
            return False

    def deal_first_search_first(self):
        '''
        处理第一个搜索的第一个
        '''
        session = requests.Session()
        resp = session.get(self.url_enquiry_lists)
        form_data = self.deal_form_date(resp,1)
        session.post(self.url_enquiry_lists,data=form_data)
        resp = session.get(self.url_enquiry_summary_view)
        for item in self.deal_first_url(resp,session=session):
            yield item

    def deal_first_search_second(self,start_time,end_time):
        '''
        处理第一个搜索的第二个
        '''
        print(start_time+"-------"+end_time)
        session = requests.Session()
        resp = session.get(self.url_enquiry_lists)
        form_data = self.deal_form_date(resp,2)
        session.post(self.url_enquiry_lists,data=form_data)
        resp = session.get(self.url_enquiry_search)
        form_data = self.deal_form_date(resp,3)
        resp = session.post(self.url_enquiry_search,data=form_data)
        form_data = self.deal_form_date(resp,4,start_time,end_time)
        # 这里传的form_data是选择时间
        session.post(self.url_enquiry_search,data=form_data)
        resp = session.get(self.url_enquiry_summary_view2)  
        all_url_list = self.deal_second_url(resp)
    
        num = 2
        while True:
            all_data = self.get_next_page(num,session=session,response=resp)
            if all_data == None:break
            next_page_url_list = all_data[0]
            resp = all_data[1]
            num += 1
            for i in next_page_url_list:
                all_url_list.append(i)
                    
        # print(all_url_list)
        cookie = str(session.cookies)
        cookie1 = cookie.split('=',2)[1].split(' ',3)[0]
        cookie2 = cookie.split('=',2)[2].split(' ',2)[0]
        self.cookies = {
            'ASP.NET_SessionId':cookie1,
            'Infor.ePathway':cookie2,
        }
        for all_url in all_url_list:
            yield Request(all_url,method="GET",cookies=self.cookies,callback=self.parse_details2,headers=self.headers)       

    def deal_form_date(self, response,num=None,start_time=None,end_time=None):
        soup = BeautifulSoup(response.text,'html.parser')
        __VIEWSTATE = soup.select_one("#__VIEWSTATE").get('value')
        __VIEWSTATEGENERATOR = soup.select_one("#__VIEWSTATEGENERATOR").get('value')
        __EVENTVALIDATION = soup.select_one("#__EVENTVALIDATION").get('value')
        CSRFToken = soup.select_one("#CSRFToken").get('value')
        try :
            __PREVIOUSPAGE = soup.select_one("#__PREVIOUSPAGE").get('value')
        except:
            __PREVIOUSPAGE = ''
        x = random.randint(6,8)
        y = random.randint(13,15)
        width = random.randint(950,960)
        height = random.randint(900,910)
        first = 'ctl00$MainBodyContent$mDataList$ctl03$mDataGrid$ctl02$ctl00'
        second  = 'ctl00$MainBodyContent$mDataList$ctl03$mDataGrid$ctl03$ctl00'
        if num == 1:
            form_data = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': __VIEWSTATE,
                '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR,
                '__VIEWSTATEENCRYPTED': '',
                '__EVENTVALIDATION': __EVENTVALIDATION,
                'ctl00$CSRFToken': CSRFToken,
                'mDataGrid:Column0:Property': first,
                'ctl00$MainBodyContent$mContinueButton': 'Next',
                'ctl00$mWidth': width,
                'ctl00$mHeight': height ,
            }
            return form_data
        if num == 2:
            form_data = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': __VIEWSTATE,
                '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR,
                '__VIEWSTATEENCRYPTED': '',
                '__EVENTVALIDATION': __EVENTVALIDATION,
                'ctl00$CSRFToken': CSRFToken,
                'mDataGrid:Column0:Property': second,
                'ctl00$MainBodyContent$mContinueButton': 'Next',
                'ctl00$mWidth': width,
                'ctl00$mHeight': height ,
            }
            return form_data
        if num == 3:
            form_data = {
                '__EVENTTARGET': 'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$tabControlMenu',
                '__EVENTARGUMENT': 2,
                '__LASTFOCUS': '',
                '__VIEWSTATE': __VIEWSTATE,
                '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR,
                '__EVENTVALIDATION': __EVENTVALIDATION,
                'ctl00$CSRFToken': CSRFToken,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mEnquiryListsDropDownList': 57,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mHiddenSingleLineAddressTpk': '',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mStreetNumberTextBox': '',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mStreetNameTextBox': '',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mStreetTypeDropDown': '(any)',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mSuburbTextBox': '',
                'ctl00$mWidth': width,
                'ctl00$mHeight': height,
                'hiddenInputToUpdateATBuffer_CommonToolkitScripts': 1 ,
            }
            return form_data
        if num == 4:
            form_data = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__LASTFOCUS': '',
                '__VIEWSTATE': __VIEWSTATE,
                '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR,
                '__EVENTVALIDATION': __EVENTVALIDATION,
                'ctl00$CSRFToken': CSRFToken,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mEnquiryListsDropDownList': 57,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl14$DateSearchRadioGroup': 'mLast30RadioButton',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl14$mFromDatePicker$dateTextBox': start_time,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl14$mToDatePicker$dateTextBox': end_time,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mSearchButton': 'Search',
                'ctl00$mWidth': width,
                'ctl00$mHeight': height,
            }
            return form_data
        if num == 5:
            form_data={
                '__EVENTTARGET': 'ctl00_MainBodyContent_mPagingControl_nextPageHyperLink',
                '__EVENTARGUMENT': '',
                '__LASTFOCUS':'',
                '__VIEWSTATE': __VIEWSTATE,
                '__VIEWSTATEGENERATOR': __VIEWSTATEGENERATOR,
                '__PREVIOUSPAGE':__PREVIOUSPAGE,
                '__EVENTVALIDATION': __EVENTVALIDATION,
                'ctl00$CSRFToken': CSRFToken,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mEnquiryListsDropDownList': 57,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mHiddenSingleLineAddressTpk': '',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mStreetNumberTextBox':'' ,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mStreetNameTextBox': '',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mStreetTypeDropDown': '(any)',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mSuburbTextBox': '',
                'ctl00$MainBodyContent$mPagingControl$nextPageHyperLink.x': x,
                'ctl00$MainBodyContent$mPagingControl$nextPageHyperLink.y': y,
                'ctl00$mWidth': width,
                'ctl00$mHeight': height ,
                'hiddenInputToUpdateATBuffer_CommonToolkitScripts':1 ,
            }
            return form_data

    def deal_first_url(self, response,session):
        '''
        处理第一个搜索url的第一个搜索结果
        '''
        soup = BeautifulSoup(response.text,'html.parser')
        url1 = soup.select('.ContentPanel .ContentPanel a')
        url2 = soup.select('.ContentPanel .AlternateContentPanel a')
        url_list = []
        for url in url1:
            url_list.append(url.get('href'))
        for url in url2:
            url_list.append(url.get('href'))
        print(url_list)
        cookie = str(session.cookies)
        cookie1 = cookie.split('=',2)[1].split(' ',3)[0]
        cookie2 = cookie.split('=',2)[2].split(' ',2)[0]
        self.cookie = {
            'ASP.NET_SessionId':cookie1,
            'Infor.ePathway':cookie2,
        }
        for url in url_list:
            url =  'https://eservices.southgippsland.vic.gov.au/ePathway/ePathProd/Web/GeneralEnquiry/' + url
            print(url)
            yield Request(url=url,cookies=self.cookie,dont_filter=False,method="GET",callback=self.parse_details)
    
    def get_next_page(self,num,session,response):
        '''
        获取下一页搜索结果
        return next_page_url_list
        if None return None
        '''
        soup = BeautifulSoup(response.text,'html.parser')
        judge = soup.select('.ErrorContentText')
        if judge:
            return None

        global global_url 
        url = self.url_enquiry_summary + f'?PageNumber={num}'
        form_data = self.deal_form_date(response,5)
        resp = session.post(url= url,data=form_data)
        url_list = self.deal_second_url(resp)
        temp_data = [url_list,resp]
        if global_url == '':
            global_url = url_list[-1]
            return temp_data
        elif global_url == url_list[-1]:
            global_url = ''
            return None
        else :
            global_url = url_list[-1]
            return temp_data

    def deal_second_url(self, response):
        '''
        处理第一个搜索的第二个搜索结果
        return url_list
        '''
        soup = BeautifulSoup(response.text,'html.parser')
        url_list = []
        judge = soup.select('.ErrorContentText')
        if judge:
            return url_list
        url1 = soup.select('.ContentPanel .ContentPanel a')
        url2 = soup.select('.ContentPanel .AlternateContentPanel a')
     
        for url in url1:
            url_list.append('https://eservices.southgippsland.vic.gov.au' + url.get('href'))
        for url in url2:
            url_list.append('https://eservices.southgippsland.vic.gov.au' + url.get('href'))
      
        return url_list
       
    def parse_details(self, response):
        item = Southgippsland()
        soup = BeautifulSoup(response.text, 'html.parser')
        judge = soup.select('.ErrorContentText')
        if judge:
            return None
        title_list = soup.select('.field .field .AlternateContentHeading')
        text_list = soup.select('.field .field .AlternateContentText')
        temp_dict = {}
        try:
            for x,y in zip(title_list,text_list):
                temp_dict[x.get_text().replace('\n','').replace('\t','').replace('\r','')] = y.get_text().replace('\n','').replace('\t','').replace('\r','')
            # print(temp_dict)
            try:
                item['app_number'] = temp_dict['Application Number']
            except:
                item['app_number'] = ''
            try:
                item['app_proposal'] =temp_dict['Application Proposal']
            except:
                item['app_proposal'] = ''
            try:
                item['app_location'] = temp_dict['Application Location']
            except:
                item['app_location'] = ''
            try:
                item['app_type'] = temp_dict['Application Type']
            except:
                item['app_type'] = ''
            try:
                item['app_decision'] = temp_dict['Application Description']
            except:
                item['app_decision'] = ''
            try:
                item['status'] = temp_dict['Status']
            except:
                item['status'] = ''    
            try:
                item['responsible_officer'] = temp_dict['Responsible officer']
            except:
                item['responsible_officer'] = '' 
            try:
                item['alternate_property_address'] = temp_dict['Alternate Property address']
            except:
                item['alternate_property_address'] = ''
        except:
            print('特殊情况未判定')
        src = soup.select_one('#ctl00_MainBodyContent_group_426 img').get('src')
        item['document'] = src
        print(item)
        yield item
    def parse_details2(self, response):
        item = Southgippsland()
        soup = BeautifulSoup(response.text, 'html.parser')
        judge = soup.select('.ErrorContentText')
        if judge:
            return None
        
        title_list = soup.select('.field .field .AlternateContentHeading')
        text_list = soup.select('.field .field .AlternateContentText')
        temp_dict = {}
        try :
            for x,y in zip(title_list,text_list):
                temp_dict[x.get_text().replace('\n','').replace('\t','').replace('\r','')] = y.get_text().replace('\n','').replace('\t','').replace('\r','')
            try:
                item['app_number'] = temp_dict['Application Number']
            except:
                item['app_number'] = ''
            try:
                lodged_date = temp_dict['Application Date']
                time_array = time.strptime(lodged_date, '%d/%m/%Y')
                temp_data = int(time.mktime(time_array))
                item['app_date'] = temp_data if lodged_date else None
            except:
                item['app_date'] = None
            try:
                item['app_location'] = temp_dict['Application Location']
            except:
                item['app_location'] = ''
            try:
                item['app_type'] = temp_dict['Application Type']
            except:
                item['app_type'] = ''
            try:
                item['app_decision'] = temp_dict['Application Description']
            except:
                item['app_decision'] = ''
            try:
                item['status'] = temp_dict['Status']
            except:
                item['status'] = ''       
        except:
            print('特殊情况未判定')

        pro_address = ''
        try:
            data = soup.select('#ctl00_MainBodyContent_group_429 .ContentPanel .ContentText')
            for d in data:
                pro_address += d.get_text().replace('\n','').replace('\r','').replace('\t','')+';'
            item['property_address'] = pro_address
        except:
            item['property_address'] = ''
        try:
            data = soup.select('#ctl00_MainBodyContent_group_430 .ContentPanel .ContentText')
            temp_list = []
            for d in data:
                temp_list.append(d.get_text().replace('\n','').replace('\r','').replace('\t',''))
            try:
                item['app_task_type'] = temp_list[0]
            except:
                item['app_task_type'] = ''
            try:
                lodged_date = temp_list[1].strip()
                time_array = time.strptime(lodged_date, '%d/%m/%Y')
                temp_data = int(time.mktime(time_array))
                item['actual_started_date'] = temp_data if lodged_date else None
            except:
                item['actual_started_date'] = None
            try:
                lodged_date = temp_list[2].strip()
                time_array = time.strptime(lodged_date, '%d/%m/%Y')
                temp_data = int(time.mktime(time_array))
                item['actual_completed_date'] = temp_data if lodged_date else None
            except:
                item['actual_completed_date'] = None
        except:
            item['app_task_type'] = ''
            item['actual_started_date'] = None
            item['actual_completed_date'] = None
        
        yield item
