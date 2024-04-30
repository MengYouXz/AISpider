import scrapy
from scrapy import Request
from bs4 import BeautifulSoup
import requests
from AISpider.items.kalamunda_item import KalamundaItem
from datetime import datetime
import time

class KalamundaSpider(scrapy.Spider):
    name = "kalamunda"
    allowed_domains = ["https://onlineservices.kalamunda.wa.gov.au/userhome.asp?u=543"]
    start_urls = ["https://onlineservices.kalamunda.wa.gov.au/userHome.asp?u=544&mode=processForm&syn_applicationNumber=&syn_dateFrom=&syn_dateTo=&syn_lot=&syn_unit=&syn_streetNumber=&syn_streetName=&syn_streetType=&syn_suburb=&syn_postcode=&req_type=syn_listDevelopmentApplications&syn_submitNewDevelopmentApplicationSearch=Search"]
    custom_settings = {
        'LOG_STDOUT': True,
        'LOG_FILE': 'scrapy_kalamunda.log',
        'DOWNLOAD_TIMEOUT': 1200
    }

    def start_requests(self):
        session = requests.Session()
        session.get('https://onlineservices.kalamunda.wa.gov.au/userhome.asp?u=543')
        resp = session.get(self.start_urls[0])
        #在这处理cookie
        cookies = resp.cookies.get_dict()
        for item in self.parse(response=resp,cookies=cookies):
            yield item
    def parse(self, response,cookies):
        soup = BeautifulSoup(response.text, "html.parser")
        url_list = soup.select('.syn_applicationListTable a')
        temp_list = []
        for url in url_list:
            url = 'https://onlineservices.kalamunda.wa.gov.au/' + url.get('href')
            yield Request(url=url,cookies=cookies,callback=self.parse_detail)
        

    def parse_detail(self,response):
        item = KalamundaItem()
        soup = BeautifulSoup(response.text, "html.parser")
        # applicantDetails
        tb_left = soup.select("#syn_applicantDetails .syn_col1")
        tb_right = soup.select("#syn_applicantDetails .syn_col2")   
        temp_dict = {}
        for x,y in zip(tb_left,tb_right):
            temp_dict[x.get_text().replace('\n','').replace('\t','').replace('\r','')] = y.get_text().replace('\n','').replace('\t','').replace('\r','').replace('\xa0','').replace(' ','')
        # officerDetails
        tb_left = soup.select("#syn_officerDetails .syn_col1")
        tb_right = soup.select("#syn_officerDetails .syn_col2")  
        for x,y in zip(tb_left,tb_right):
            temp_dict[x.get_text().replace('\n','').replace('\t','').replace('\r','')] = y.get_text().replace('\n','').replace('\t','').replace('\r','').replace('\xa0','').replace(' ','')
        # progressDetails
        tb_left = soup.select("#syn_progressDetails .syn_col1")
        tb_right = soup.select("#syn_progressDetails .syn_col2")  
        for x,y in zip(tb_left,tb_right):
            temp_dict[x.get_text().replace('\n','').replace('\t','').replace('\r','')] = y.get_text().replace('\n','').replace('\t','').replace('\r','').replace('\xa0','').replace(' ','')
        # last Stage
        stage = soup.select("table td")
        try:
            stage_ = soup.select("table td")[-3].get_text().replace('\xa0','')
            item['stage_'] = stage_
        except:
            pass
        try:
            start_date = soup.select("table td")[-2].get_text().replace('\xa0','')
            item['start_date'] = start_date
        except:
            pass
        try:
            end_date = soup.select("table td")[-1].get_text().replace('\xa0','')
            item['end_date'] = end_date
        except:
            pass
        temp_list = list(temp_dict.keys())

        item['app_number']=temp_dict['Application Number'] if 'Description' in temp_list else None

        try:
            time_array = time.strptime(lodged_date, '%d/%m/%Y')
            temp_data = int(time.mktime(time_array))
            item['lodgement_date']=temp_data if lodged_date else None  
        except:
            pass
        #item['lodgement_date']=temp_dict['Lodgement Date'] if 'Lodgement Date' in temp_list else None
        item['description']=temp_dict['Description'] if 'Description' in temp_list else None
        item['applicant']=temp_dict['Applicant'] if 'Applicant' in temp_list else None
        
        item['name']=temp_dict['Name'] if 'Name' in temp_list else None
        item['telephone']=temp_dict['Telephone'] if 'Telephone' in temp_list else None
        item['email']=temp_dict['Email'] if 'Email' in temp_list else None
        
        item['decision']=temp_dict['Decision'] if 'Decision' in temp_list else None
        item['decision_date']=temp_dict['Decision Date'] if 'Decision Date' in temp_list else None
        
        yield item



        