import scrapy
from urllib.parse import urlencode
from AISpider.items.dandenong_items import DandenongItem
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from datetime import date, datetime, timedelta
from common._date import get_all_month_
from common.set_date import get_this_month
import json
class DandenongSpider(scrapy.Spider):
    name = 'dandenong'
    allowed_domains = ["mygreaterdandenong.com"]
    start_urls = [
        'https://mygreaterdandenong.com/eProperty/P1/eTrack/eTrackApplicationSearch.aspx']
    custom_settings = {
        'LOG_STDOUT': True,
        # 'LOG_FILE': 'scrapy_dandenong.log',
    }

    def __init__(self, days=None):
        self.time_lists = []
        self.cookies = {
                    'ASP.NET_SessionId': '',
                }
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://mygreaterdandenong.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36', 
        }
        self.data = {
                    'ctl00_Content_ajaxToolkitManager_HiddenField': '',
                    '__EVENTTARGET': 'ctl00$Content$btnSearch',
                    '__EVENTARGUMENT': '',
                    '__VIEWSTATE': '',
                    '__VIEWSTATEGENERATOR': 'CA8B432D',
                    '__SCROLLPOSITIONX': '0',
                    '__SCROLLPOSITIONY': '48',
                    '__EVENTVALIDATION': '',
                    'ctl00$Content$txtApplicationID$txtText': '',
                    'ctl00$Content$txtDateFrom$txtText': '',
                    'ctl00$Content$txtDateTo$txtText': '',
                    'ctl00$Content$txtDescription$txtText': '',
                    'ctl00$Content$ddlApplicationType$elbList': 'all',
                    'ctl00$Content$txtStreetNoFrom$txtText': '',
                    'ctl00$Content$txtStreetNoTo$txtText': '',
                    'ctl00$Content$txtStreet$txtText': '',
                    'ctl00$Content$txtStreetType$txtText': '',
                    'ctl00$Content$txtSuburb$txtText': '',
                    'ctl00$Content$txtPlanNo$txtText': '',
                    'ctl00$Content$cusFieldsAppInformation$PropertyElectorate$elbList': 'NotSelected',
                }
        self.data1 = {
                    '__EVENTTARGET': 'ctl00$Content$cusResultsGrid$repWebGrid$ctl00$grdWebGridTabularView',
                    '__EVENTARGUMENT': '',
                    '__VIEWSTATE': '',
                    '__VIEWSTATEGENERATOR': 'C1608850',
                    '__SCROLLPOSITIONX': '0',
                    '__SCROLLPOSITIONY': '48',
                    '__EVENTVALIDATION': '',
                }
        self.ids = []
        self.page = 1
        self.temp_str =''
        self.proxy = {'https': 'http://127.0.0.1:8888'}
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
        self.time_lists = get_all_month_(self.days,datetime.now().strftime('%d/%m/%Y'))
        all_month = self.time_lists 
        for index, y_date in enumerate(all_month):
            if y_date == all_month[-1]:
                break
            start_time = y_date
            end_time = all_month[index + 1]
            print(f'{start_time}-----------------{end_time}')
            resp = self.get_search_result(start_time,end_time)
            for item in self.parse(resp):
                yield item

    

    def get_search_result(self,start_time=None,end_time=None):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome(options=chrome_options)
        browser.get("https://mygreaterdandenong.com/eProperty/P1/eTrack/eTrackApplicationSearch.aspx")
        agree = WebDriverWait(browser, 20, 1).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cgdAgreeTerms"]')))
        agree.click()
        search = WebDriverWait(browser, 20, 1).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cssTaskpane"]/div/div/ul[3]/li[2]/a')))
        search.click()
        browser.find_element(By.XPATH, '//*[@id="ctl00_Content_txtDateFrom_txtText"]').send_keys(start_time)
        browser.find_element(By.XPATH, '//*[@id="ctl00_Content_txtDateTo_txtText"]').send_keys(end_time)
        search_new = WebDriverWait(browser, 20, 1).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_Content_btnSearch"]')))
        search_new.click()
        self.cookies = {
            'ASP.NET_SessionId':browser.get_cookies()[4]['value']
            }
        return browser.page_source

    def parse(self, resp):
        judge_results = self.judge_error(resp)
        if judge_results==False:
           return
        else:
            page = 2
            all_id = []
            while True:
                try:
                    soup = BeautifulSoup(resp, 'html.parser')
                except:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                table_grid = soup.find('table', class_='grid')
                rows = table_grid.find_all('tr', class_=['alternateRow', 'normalRow'])
                for row in rows:
                    id = row.find('input').get('value')
                    all_id.append(id)

                viewstate_input = soup.select_one('#__VIEWSTATE').get('value')
                event_input = soup.select_one('#__EVENTVALIDATION').get('value')
                self.data1['__VIEWSTATE'] = viewstate_input
                self.data1['__EVENTVALIDATION'] = event_input
            
                url = 'https://mygreaterdandenong.com/eProperty/P1/eTrack/eTrackApplicationSearchResults.aspx?r=P1.WEBGUEST&f=%24P1.ETR.RESULTS.VIW'
               
                self.data1['__EVENTARGUMENT'] = f'Page${page}'
                page +=1
                resp = requests.post(url,headers=self.headers,data=self.data1,cookies=self.cookies,)
                judge_result = self.judge_error(resp)

                if judge_result == False:
                    for item in self.get_detial(all_id):
                        yield item
                    break
                
                # if self.ids[-1] == self.temp_str:
                #     for item in self.get_detial():
                #         yield item
                #     break
                # else:
                #     self.temp_str = self.ids[-1]

    def judge_error(self,resp):
        try:
            soup = BeautifulSoup(resp, 'html.parser')
            title = soup.select_one('title').text
            if "Error" in title:
                return False
            else:
                return True
        except:
            soup = BeautifulSoup(resp.text, 'html.parser')
            title = soup.select_one('title').text
            if "Error" in title:
                return False
            else:
                return True
        
    def get_detial(self,all_id):
        if all_id:
            unique_ids = list(set(all_id))
            print('================================================================')
            print(len(all_id))
            print(unique_ids)
            print('================================================================')
            for idd in unique_ids:
                hrefs = []
                href = f'https://planningdocuments.cgd.vic.gov.au/?plnNum{idd}'
                hrefs.append(href)
                idd = idd.replace('/', '%2F')
                url = f'https://mygreaterdandenong.com/eProperty/P1/eTrack/eTrackApplicationDetails.aspx?r=P1.WEBGUEST&f=%24P1.ETR.APPDET.VIW&ApplicationId={idd}'
                yield scrapy.Request(
                    url=url,
                    headers=self.headers,
                    callback=self.parse_detail,
                    meta={'hrefs': hrefs}
                )

    def parse_detail(self, response):
        hrefs = response.meta.get('hrefs')
        item = DandenongItem()
        soup3 = BeautifulSoup(response.text, 'lxml')
        table_all = soup3.find_all('table', class_='grid')
        fields = {}
        for i in range(3):
            for tr in table_all[i].find_all('tr', class_=['alternateRow', 'normalRow']):
                tds = tr.find_all('td')
                header = tds[0].get_text(strip=True)
                value = tds[1].get_text(strip=True)
                fields[header] = value
        addresss = []
        for m in range(3, len(table_all) - 1):
            add = table_all[m].find('input').get('value')
            trss = table_all[m].find_all('tr')
            ress = trss[1].find_all('td')[1].text.strip()
            address = f'{add}-{ress}'
            addresss.append(address)
        fields['address'] = addresss

        lodged = fields.get('Application Lodged')
        meetingdate = fields.get('Council Meeting Date')
        authdecisiondate = fields.get('Responsible Authority Decision Date')
        vcatappeallodgeddate = fields.get('VCAT Appeal Lodged Date')
        vcatdecisiondate = fields.get('VCAT Decision Date')
        finaloutcomedate = fields.get('Final Outcome Date')
        plancertified = fields.get('Plan Certified')
        statementcompliance = fields.get('Statement of Compliance')

        lodged = datetime.strptime(lodged, '%d/%m/%Y').date() if lodged else None
        obj_lodged = int(time.mktime(lodged.timetuple())) if lodged else None
        meetingdate = datetime.strptime(meetingdate, '%d/%m/%Y').date() if meetingdate else None
        obj_meetingdate = int(time.mktime(meetingdate.timetuple())) if meetingdate else None
        authdecisiondate = datetime.strptime(authdecisiondate, '%d/%m/%Y').date() if authdecisiondate else None
        obj_authdecisiondate = int(time.mktime(authdecisiondate.timetuple())) if authdecisiondate else None
        vcatappeallodgeddate = datetime.strptime(vcatappeallodgeddate, '%d/%m/%Y').date() if vcatappeallodgeddate else None
        obj_vcatappeallodgeddate = int(time.mktime(vcatappeallodgeddate.timetuple())) if vcatappeallodgeddate else None
        vcatdecisiondate = datetime.strptime(vcatdecisiondate, '%d/%m/%Y').date() if vcatdecisiondate else None
        obj_vcatdecisiondate = int(time.mktime(vcatdecisiondate.timetuple())) if vcatdecisiondate else None
        finaloutcomedate = datetime.strptime(finaloutcomedate, '%d/%m/%Y').date() if finaloutcomedate else None
        obj_finaloutcomedate = int(time.mktime(finaloutcomedate.timetuple())) if finaloutcomedate else None
        plancertified = datetime.strptime(plancertified, '%d/%m/%Y').date() if plancertified else None
        obj_plancertified = int(time.mktime(plancertified.timetuple())) if plancertified else None
        statementcompliance = datetime.strptime(statementcompliance, '%d/%m/%Y').date() if statementcompliance else None
        obj_statementcompliance = int(time.mktime(statementcompliance.timetuple())) if statementcompliance else None


        item['applicationid'] = fields.get('Application ID No.')
        item['category'] = fields.get('Category')
        item['subcategory'] = fields.get('Sub Category')
        item['word'] = fields.get('Ward')
        item['description'] = fields.get('Proposal Description')
        item['lodged'] = obj_lodged
        item['cost'] = fields.get('Estimated Cost')
        item['decision'] = fields.get('Stage/Decision')
        item['required'] = fields.get('Advertising Required')
        item['commenced'] = fields.get('Advertising Commenced')
        item['meetingdate'] = obj_meetingdate
        item['authdecision'] = fields.get('Responsible Authority Decision')
        item['authdecisiondate'] = obj_authdecisiondate
        item['vcatappeallodgeddate'] = obj_vcatappeallodgeddate
        item['vcatdecisiondate'] = obj_vcatdecisiondate
        item['vcatdecision'] = fields.get('VCAT Decision')
        item['correctiondecision'] = fields.get('Correction of Decision')
        item['applicationamended'] = fields.get('Application Amended')
        item['finaloutcome'] = fields.get('Final Outcome')
        item['finaloutcomedate'] = obj_finaloutcomedate
        item['lodgedplannumber'] = fields.get('Lodged Plan Number')
        item['plancertified'] = obj_plancertified
        item['planrecertified'] = fields.get('Plan Recertified')
        item['statementcompliance'] = obj_statementcompliance
        item['address'] = fields.get('addresss')
        item['documents'] = hrefs
        print(item)
        yield item
