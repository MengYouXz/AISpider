import scrapy
import requests
from scrapy import Request
from bs4 import BeautifulSoup
import random
from AISpider.items.whitehorse_items import WhitehorseItem
from common._date import get_all_month
import time
from datetime import date, datetime, timedelta
from common._date import get_all_month
from common.set_date import get_this_month,get_next_month
'''
爬取三个页面结果
第一个 从2021年开始到2024年4月 只有2页 35个
第二个搜索结果是从2000/01/01年开始 57000左右
和第三个搜索结果是从1990/01/01年开始 28000左右
'''
# 用于分页请求排除
global_url = ''

class WhitehorseSpider(scrapy.Spider):
    name = "whitehorse"
    allowed_domains = ["eservices.whitehorse.vic.gov.au"]
    start_urls = ["https://eservices.whitehorse.vic.gov.au/ePathway/Production/Web/GeneralEnquiry/EnquiryLists.aspx"]


    def __init__(self,category=None,days=None, *args, **kwargs):
        self.headers = {
        }
        self.url_enquiry_lists='https://eservices.whitehorse.vic.gov.au/ePathway/Production/Web/GeneralEnquiry/EnquiryLists.aspx'
        self.url_enquiry_search = 'https://eservices.whitehorse.vic.gov.au/ePathway/Production/Web/GeneralEnquiry/EnquirySearch.aspx'
        self.url_enquiry_summary_view = 'https://eservices.whitehorse.vic.gov.au/ePathway/Production/Web/GeneralEnquiry/EnquirySummaryView.aspx'
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
        for url in self.start_urls:
            yield Request(url, dont_filter=False)
          
    def parse(self, response):
        cookie = str(response.headers.get('Set-Cookie')).split(';')[0].split("'")[1]
        print(cookie)   
        self.headers = {
            'Cookie': cookie
        }
        if self.category == 'first':
            for item in self.get_first_page(response):
                yield item
        elif self.category =='second':
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
                if get_next_month().split('/')[1] == end_time.split('/')[1] and get_next_month().split('/')[2] == end_time.split('/')[2]:
                    end_time = datetime.now().date().strftime('%d/%m/%Y')
                print(start_time + "-----" + end_time)
                for item2 in self.get_second_page(response,start_time,end_time):
                    yield item2
        elif self.category == 'third':
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
                if get_next_month().split('/')[1] == end_time.split('/')[1] and get_next_month().split('/')[2] == end_time.split('/')[2]:
                    end_time = datetime.now().date().strftime('%d/%m/%Y')
                print(start_time + "-----" + end_time)
                for item3 in self.get_third_page(response,start_time,end_time):
                    yield item3

    def judge_date(self,start_time):
        if self.days.split('/')[2] == start_time.split('/')[2]:
            if self.days.split('/')[1] == start_time.split('/')[1]:
                return False
            else:return True
        else:
            return False
    def get_first_page(self, response):
        '''
        获取第一个搜索结果
        不用改动时间，会返回全部时间段结果
        '''
        search_num = 1
        soup = self.post_search(response,search_num)
        url_list = self.parse_url_list(soup)
        print(url_list)
        for i in url_list:
            detial_url = 'https://eservices.whitehorse.vic.gov.au/ePathway/Production/Web/GeneralEnquiry/' + i
            yield Request(detial_url,headers=self.headers,callback=self.parse_for_first_page,method="GET")

        num = 2
        while True:
            next_page_url_list = self.get_next_page(num,)
            num += 1
            if next_page_url_list == None:break
            print(next_page_url_list)
            for i in next_page_url_list:
                detial_url = 'https://eservices.whitehorse.vic.gov.au/ePathway/Production/Web/GeneralEnquiry/' + i
                yield Request(detial_url,headers=self.headers,callback=self.parse_for_first_page,method="GET")           

    def get_second_page(self,response,start_time,end_time):
        '''
        获取第二个搜索结果
        '''
        search_num = 2
        temp_soup = self.post_search(response,search_num,start_time,end_time)
        soup = temp_soup[0]
        cookie = temp_soup[1]
        cookie1 = cookie.split('=',2)[1].split(' ',3)[0]
        cookie2 = cookie.split('=',2)[2].split(' ',2)[0]
        # print(cookie1)
        # print(cookie2)
        response = temp_soup[2]
        self.cookies ={
            'ASP.NET_SessionId': cookie1,
            'ePathway':cookie2,
        }
        url_list = self.parse_url_list(soup)
        print(url_list)
        # all_url_list = []
        for i in url_list:
            detial_url = 'https://eservices.whitehorse.vic.gov.au/ePathway/Production/Web/GeneralEnquiry/' + i
            # all_url_list.append(detial_url)
            yield Request(url=detial_url,method="GET",cookies=self.cookies,callback=self.parse_detail)

        if url_list == []:
            return None
        num = 2
        while True:
            next_page_url_list = self.get_next_page2(response,num)
            print(next_page_url_list)
            num += 1
            if next_page_url_list == None:break
            for i in next_page_url_list:
                detial_url = 'https://eservices.whitehorse.vic.gov.au/ePathway/Production/Web/GeneralEnquiry/' + i
                # all_url_list.append(detial_url)
                yield Request(url=detial_url,method="GET",cookies=self.cookies,callback=self.parse_detail)

        
        # print(all_url_list)
        # for url in all_url_list:
        #     yield Request(url=detial_url,method="GET",cookies=self.cookies,callback=self.parse_detail)

    def get_third_page(self,response,start_time,end_time):
        '''
        获取第三个搜索结果
        '''
        search_num = 3
        temp_soup = self.post_search(response,search_num,start_time,end_time)
        soup = temp_soup[0]
        cookie = temp_soup[1]
        cookie1 = cookie.split('=',2)[1].split(' ',3)[0]
        cookie2 = cookie.split('=',2)[2].split(' ',2)[0]
        # print(cookie1)
        # print(cookie2)
        response = temp_soup[2]
        self.cookies ={
            'ASP.NET_SessionId': cookie1,
            'ePathway':cookie2,
        }
        url_list = self.parse_url_list(soup)
        print(url_list)
        all_url_list = []
        for i in url_list:
            detial_url = 'https://eservices.whitehorse.vic.gov.au/ePathway/Production/Web/GeneralEnquiry/' + i
            all_url_list.append(detial_url)
            yield Request(url=detial_url,method="GET",cookies=self.cookies,callback=self.parse_detail)
        if url_list == []:
            return None
        num = 2
        while True:
            next_page_url_list = self.get_next_page2(response,num)
            print(next_page_url_list)
            num += 1
            if next_page_url_list == None:break
            for i in next_page_url_list:
                detial_url = 'https://eservices.whitehorse.vic.gov.au/ePathway/Production/Web/GeneralEnquiry/' + i
                all_url_list.append(detial_url)
                yield Request(url=detial_url,method="GET",cookies=self.cookies,callback=self.parse_detail)
        # # print(all_url_list)
        # for url in all_url_list:
        #     yield Request(url=url,method="GET",cookies=self.cookies,callback=self.parse_detail)
   
    def get_next_page(self,num):
        '''
        获取下一页搜索结果
        return next_page_url_list
        if None return None
        '''
        global global_url 
        url = self.url_enquiry_summary_view + f'?PageNumber={num}'
        resp = requests.get(url= url,headers=self.headers)
        form_date = self.deal_form_date(resp,search_num=4)
        resp = requests.get(url= url, data=form_date,headers=self.headers)
        soup = BeautifulSoup(resp.text, 'html.parser')
        url_list = self.parse_url_list(soup)
        
        if global_url == '':
            global_url = url_list[-1]
            return url_list
        elif global_url == url_list[-1]:
            global_url = ''
            return None
    
    def get_next_page2(self,response,num):
        '''
        获取下一页搜索结果
        return next_page_url_list
        if None return None
        '''
        global global_url 
        url = self.url_enquiry_summary_view + f'?PageNumber={num}'
        form_date = self.deal_form_date(response,6,num)
        resp = requests.get(url= url, data=form_date,cookies=self.cookies)
        soup = BeautifulSoup(resp.text, 'html.parser')
        url_list = self.parse_url_list(soup)
        
        if global_url == '':
            global_url = url_list[-1]
            return url_list
        elif global_url == url_list[-1]:
            global_url = ''
            return None
        else:
            global_url = url_list[-1]
            return url_list
   
    def parse_url_list(self,soup):
        '''
        获取页面url列表
        return url_list
        '''
        temp_list = []
        judge = soup.select('.ErrorContentText')
        if judge:
            return temp_list
        url1 = soup.select('.ContentPanel .AlternateContentText a')
        url2 = soup.select('.ContentPanel .ContentText a')
        
        for i in url1:
            temp_list.append(i.get('href'))
        for i in url2:
            temp_list.append(i.get('href'))

        return temp_list

    def deal_form_date(self,response,search_num,page_number=None,start_time=None,end_time=None):
        '''
        处理form_date
        return form_date
        '''
        soup = BeautifulSoup(response.text, 'html.parser')
        data_1 = soup.select_one('#__VIEWSTATE').get('value')
        data_2 = soup.select_one('#__VIEWSTATEGENERATOR').get('value')
        data_3 = soup.select_one('#__EVENTVALIDATION').get('value')
        data_4 = soup.select_one('#CSRFToken').get('value')
        try:
            data_5 = soup.select_one('#__PREVIOUSPAGE').get('value')
        except:
            data_5 = ''
        x = random.randint(6,9)
        y = random.randint(6,9)
        width = random.randint(900,1000)
        height = random.randint(900,1000)
        if search_num==1:
            form_date = {
                '__EVENTTARGET':'' ,
                '__EVENTARGUMENT':'' ,
                '__VIEWSTATE':data_1,
                '__VIEWSTATEGENERATOR': data_2,
                '__VIEWSTATEENCRYPTED': '',
                '__EVENTVALIDATION':data_3 ,
                'ctl00$CSRFToken':data_4,
                'mDataGrid:Column0:Property':'ctl00$MainBodyContent$mDataList$ctl03$mDataGrid$ctl02$ctl00' ,
                'ctl00$MainBodyContent$mContinueButton': 'Next',
                'ctl00$mWidth': width,
                'ctl00$mHeight': height,
            }
            return form_date
        elif search_num==2:
            form_date2 ={
                '__EVENTTARGET':'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$tabControlMenu' ,
                '__EVENTARGUMENT': '2',
                '__LASTFOCUS':'',
                '__VIEWSTATE':data_1,
                '__VIEWSTATEGENERATOR': data_2,
                '__EVENTVALIDATION':data_3 ,
                'ctl00$CSRFToken':data_4,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mEnquiryListsDropDownList': '2',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mStreetNumberTextBox': '',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mStreetNameTextBox': '',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mStreetTypeDropDown': '(any)',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mSuburbTextBox': '',
                'ctl00$mWidth': width,
                'ctl00$mHeight': height,
                'hiddenInputToUpdateATBuffer_CommonToolkitScripts': '1',
            }
            return form_date2
        elif search_num==3:
            form_date3={
                '__EVENTTARGET':'' ,
                '__EVENTARGUMENT': '',
                '__LASTFOCUS':'',
                '__VIEWSTATE':data_1,
                '__VIEWSTATEGENERATOR': data_2,
                '__EVENTVALIDATION':data_3 ,
                'ctl00$CSRFToken':data_4,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mEnquiryListsDropDownList': '2',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl14$DateSearchRadioGroup': 'mLast30RadioButton',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl14$mFromDatePicker$dateTextBox': start_time,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl14$mToDatePicker$dateTextBox': end_time,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mSearchButton': 'Search',
                'ctl00$mWidth': width,
                'ctl00$mHeight': height,
            }
            return form_date3
        elif search_num==4:
            form_date_details ={
                '__EVENTTARGET': f'ctl00$MainBodyContent$mPagingControl$pageButton_{page_number}',
                '__EVENTARGUMENT':'',
                '__LASTFOCUS': '',
                '__VIEWSTATE':data_1,
                '__VIEWSTATEGENERATOR': data_2,
                '__PREVIOUSPAGE': data_5,
                '__EVENTVALIDATION': data_4,
                'ctl00$CSRFToken': data_4,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mEnquiryListsDropDownList': 2,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mStreetNumberTextBox':'' ,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mStreetNameTextBox':'',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mStreetTypeDropDown': '(any)',
                'ctl00$MainBodyContent$mPagingControl$nextPageHyperLink.x': x,
                'ctl00$MainBodyContent$mPagingControl$nextPageHyperLink.y': y,
                'ctl00$mWidth': width,
                'ctl00$mHeight': height,
                'hiddenInputToUpdateATBuffer_CommonToolkitScripts': '1',
            }
            return form_date_details
        elif search_num==5:
            form_date1 = {
                '__EVENTTARGET':'' ,
                '__EVENTARGUMENT':'' ,
                '__VIEWSTATE':data_1,
                '__VIEWSTATEGENERATOR': data_2,
                '__VIEWSTATEENCRYPTED': '',
                '__EVENTVALIDATION':data_3 ,
                'ctl00$CSRFToken':data_4,
                'mDataGrid:Column0:Property':'ctl00$MainBodyContent$mDataList$ctl03$mDataGrid$ctl03$ctl00' ,
                'ctl00$MainBodyContent$mContinueButton': 'Next',
                'ctl00$mWidth': width,
                'ctl00$mHeight': height,
            }
            return form_date1
        elif search_num==6:
            form_date4 ={
                '__EVENTTARGET': f'ctl00$MainBodyContent$mPagingControl$pageButton_{page_number}',
                '__EVENTARGUMENT':'',
                '__LASTFOCUS': '',
                '__VIEWSTATE':data_1,
                '__VIEWSTATEGENERATOR': data_2,
                '__PREVIOUSPAGE': data_5,
                '__EVENTVALIDATION':data_3,
                'ctl00$CSRFToken': data_4,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mEnquiryListsDropDownList': 2,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mStreetNumberTextBox':'' ,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mStreetNameTextBox':'',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mStreetTypeDropDown': '(any)',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mSuburbTextBox':'',
                'ctl00$mWidth': 1900,
                'ctl00$mHeight': height,
                'hiddenInputToUpdateATBuffer_CommonToolkitScripts': '1',
            }
            return form_date4
        elif search_num==7:
            form_date1 = {
                '__EVENTTARGET':'' ,
                '__EVENTARGUMENT':'' ,
                '__VIEWSTATE':data_1,
                '__VIEWSTATEGENERATOR': data_2,
                '__VIEWSTATEENCRYPTED': '',
                '__EVENTVALIDATION':data_3 ,
                'ctl00$CSRFToken':data_4,
                'mDataGrid:Column0:Property':'ctl00$MainBodyContent$mDataList$ctl03$mDataGrid$ctl04$ctl00' ,
                'ctl00$MainBodyContent$mContinueButton': 'Next',
                'ctl00$mWidth': width,
                'ctl00$mHeight': height,
            }
            return form_date1
        elif search_num == 8:
            form_date2 ={
                '__EVENTTARGET':'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$tabControlMenu' ,
                '__EVENTARGUMENT': '2',
                '__LASTFOCUS':'',
                '__VIEWSTATE':data_1,
                '__VIEWSTATEGENERATOR': data_2,
                '__EVENTVALIDATION':data_3 ,
                'ctl00$CSRFToken':data_4,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mEnquiryListsDropDownList': '1',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mStreetNumberTextBox': '',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mStreetNameTextBox': '',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mStreetTypeDropDown': '(any)',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl04$mSuburbTextBox': '',
                'ctl00$mWidth': width,
                'ctl00$mHeight': height,
                'hiddenInputToUpdateATBuffer_CommonToolkitScripts': '1',
            }
            return form_date2
        elif search_num == 9:
            form_date3={
                '__EVENTTARGET':'' ,
                '__EVENTARGUMENT': '',
                '__LASTFOCUS':'',
                '__VIEWSTATE':data_1,
                '__VIEWSTATEGENERATOR': data_2,
                '__EVENTVALIDATION':data_3 ,
                'ctl00$CSRFToken':data_4,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mEnquiryListsDropDownList': '1',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl14$DateSearchRadioGroup': 'mLast30RadioButton',
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl14$mFromDatePicker$dateTextBox': start_time,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mTabControl$ctl14$mToDatePicker$dateTextBox': end_time,
                'ctl00$MainBodyContent$mGeneralEnquirySearchControl$mSearchButton': 'Search',
                'ctl00$mWidth': width,
                'ctl00$mHeight': height,
            }
            return form_date3
 
    def post_search(self,response,search_num,start_time=None,end_time=None):
        '''
        获取搜索
        post results 解析为soup 返回
        '''
        if search_num == 1:
            form_date = self.deal_form_date(response,1)
            # 在请求第一个页面前需要post一下
            url = self.url_enquiry_lists
            requests.post(url= url, data=form_date,headers=self.headers)
            url = self.url_enquiry_summary_view
            resp = requests.get(url= url,headers=self.headers)
            soup = BeautifulSoup(resp.text, 'html.parser')
            return soup
        elif search_num == 2:
            session = requests.Session()
            url = self.url_enquiry_lists
            resp = session.get(url= url)
            form_date = self.deal_form_date(resp,5)
            session.post(url= url, data=form_date,)
            url = self.url_enquiry_search
            resp = session.get(url= url,)
            form_date = self.deal_form_date(resp,2)
            resp = session.post(url= url, data=form_date)
            form_date = self.deal_form_date(resp,3,start_time=start_time,end_time=end_time)
            session.post(url= url, data=form_date)
            url = self.url_enquiry_summary_view
            resp = session.get(url= url)
            soup = BeautifulSoup(resp.text, 'html.parser')
            cookies_data = str(session.cookies)
            #  cookie = data.split('=',2)[1].split(' ',3)[0]
            temp_list = [soup,cookies_data,resp]
            return temp_list
        else:
            session = requests.Session()
            url = self.url_enquiry_lists
            resp = session.get(url= url)
            form_date = self.deal_form_date(resp,7)
            session.post(url= url, data=form_date,)
            url = self.url_enquiry_search
            resp = session.get(url= url,)
            form_date = self.deal_form_date(resp,8)
            resp = session.post(url= url, data=form_date)
            form_date = self.deal_form_date(resp,9,start_time=start_time,end_time=end_time)
            session.post(url= url, data=form_date)
            url = self.url_enquiry_summary_view
            resp = session.get(url= url)
            soup = BeautifulSoup(resp.text, 'html.parser')
            cookies_data = str(session.cookies)
            #  cookie = data.split('=',2)[1].split(' ',3)[0]
            temp_list = [soup,cookies_data,resp]
            return temp_list
    
    def parse_detail(self,response):
        item = WhitehorseItem()
        soup = BeautifulSoup(response.text, 'html.parser')
       
        #只取前两个 有的没有name_details
        temp_text = ''
        judge = soup.select('fieldset legend')
        for i in judge:
            temp_text += i.get_text()
        temp_list = []
        temp_lists = decision_details = soup.select('.ContentPanel .ContentPanel td')
        for i in temp_lists:
            temp_list.append(i.get_text().replace('\n','').replace('\t','').replace('\r',''))  
        try:
            test = soup.select('fieldset table')
            for t in test:
                t = t.get_text().replace('\n','').replace('\t','').replace('\r','')
                if 'Formatted' in t:
                    try:
                        name_detail = temp_list[0]+':'+temp_list[1]
                        item['name_details'] = name_detail
                    except:
                        item['name_details'] = ''
                if 'Decision' in t:
                    try:
                        detail1 = temp_list[-1]
                        detail2 = temp_list[-2]
                        lodged_date = detail1
                        time_array = time.strptime(lodged_date, '%d/%m/%Y')
                        temp_data = int(time.mktime(time_array))
                        item['decision_date'] = temp_data if lodged_date else None
                        item['decision_type'] = detail2
                    except:
                        item['decision_date'] = None
                        item['decision_type'] = ''
        except:
            pass

        title_list = soup.select('.field .field .AlternateContentHeading')
        text_list = soup.select('.field .field .AlternateContentText')
        temp_dict = {}
        temp_str = ''
        try :
            for x,y in zip(title_list,text_list):
                temp_dict[x.get_text().replace('\n','').replace('\t','').replace('\r','')] = y.get_text().replace('\n','').replace('\t','').replace('\r','')
            try:
                item['app_class'] = temp_dict['Application Class']
            except:
                item['app_class'] = ''
            try:
                item['app_type'] = temp_dict['Application Type']
            except:
                item['app_type'] = ''
            try:
                item['app_description'] = temp_dict['Application Description']
            except:
                item['app_description'] = ''
            try:
                item['app_number'] = temp_dict['Application Number']
            except:
                item['app_number'] = ''
            try:
                item['location'] = temp_dict['Location']
            except:
                item['location'] = ''
            try:
                item['status'] = temp_dict['Status']
            except:
                item['status'] = ''
            try:
                item['current_decision'] = temp_dict['Current Decision']
            except:
                item['current_decision'] = ''
            try:
                lodged_date = temp_dict['Application Date']
                time_array = time.strptime(lodged_date, '%d/%m/%Y')
                temp_data = int(time.mktime(time_array))
                item['application_date'] = temp_data if lodged_date else None
            except:
                item['application_date'] = None
            try:
                lodged_date = temp_dict['To be Commenced By Date']
                time_array = time.strptime(lodged_date, '%d/%m/%Y')
                temp_data = int(time.mktime(time_array))
                item['to_be_commenced_by_date'] =temp_data if lodged_date else None
            except:
                item['to_be_commenced_by_date'] = None
            try:
                lodged_date = temp_dict['Lodgement Date']
                time_array = time.strptime(lodged_date, '%d/%m/%Y')
                temp_data = int(time.mktime(time_array))
                item['lodgement_date'] = temp_data if lodged_date else None
            except:
                item['lodgement_date'] = None
            try:
                lodged_date = temp_dict['Expiry Date']
                time_array = time.strptime(lodged_date, '%d/%m/%Y')
                temp_data = int(time.mktime(time_array))
                item['expiry_date'] =  temp_data if lodged_date else None
            except:
                item['expiry_date'] = None
              
        except:
            print('特殊情况未判定')
        yield item
        print("=============================================================")

    def parse_for_first_page(self,response):
        item = WhitehorseItem()
        soup = BeautifulSoup(response.text, 'html.parser')
        title_list = soup.select('.field .field .AlternateContentHeading')
        text_list = soup.select('.field .field .AlternateContentText')
        temp_dict = {}
        temp_str = ''
        try :
            for x,y in zip(title_list,text_list):
                temp_dict[x.get_text().replace('\n','').replace('\t','').replace('\r','')] = y.get_text().replace('\n','').replace('\t','').replace('\r','')
            try:
                item['location'] = temp_dict['Site Address']
            except:
                item['location'] = ''
            try:
                item['office'] = temp_dict['Responsible Officer']
            except:
                item['office'] = ''
            try:
                item['app_description'] = temp_dict['Description']
            except:
                item['app_description'] = ''
            try:
                item['app_number'] = temp_dict['Application Number']
            except:
                item['app_number'] = ''
        except:
            print('特殊情况未判定')
        try:
            temp = ''
            name_detail = soup.select('.ContentPanel .ContentPanel')
            num = 0
            lodged_date = ''
            for name in name_detail:
                if num <=1:
                    temp += name.get_text().replace('\n','').replace('\t','').replace('\r','') + ':'
                else:
                    lodged_date = name.get_text().replace('\n','').replace('\t','').replace('\r','')
            try:
                time_array = time.strptime(lodged_date, '%d/%m/%Y')
                temp_data = int(time.mktime(time_array))
            except:
                temp_data = None
            item['start_date'] =  temp_data if lodged_date else None
            item['name_details'] = temp
        except:
            item['name_details'] = ''
            item['start_date'] = None
        
        url = f"https://edocsprod.whitehorse.vic.gov.au/KapishWebGrid/default.aspx?s=eServicesFiles&container={temp_dict['Application Number']}"
        resp = requests.get(url=url,headers=self.headers)
        soup = BeautifulSoup(resp.text, 'html.parser')
        url_list = soup.select('.rgRow a')
        url_list1 = soup.select('.rgAltRow a')
        document = ''
        for url in url_list:
            document += url.get('href').replace(url.get('href').split('&')[2]+"&",'')+';'
        for url in url_list1:
            document += url.get('href').replace(url.get('href').split('&')[2]+"&",'')+';'
        item['document'] = document
        yield item
   