from datetime import datetime
import scrapy
from scrapy.http import JsonRequest
from bs4 import BeautifulSoup
import json
import re
from lxml import html
from AISpider.items.wollongong import WollongongItem
from urllib.parse import urlencode
import time
from DrissionPage import ChromiumPage, ChromiumOptions


class WollongongSpider(scrapy.Spider):
    name = 'wollongong'
    allowed_domains = ["wcc.t1cloud.com"]
    start_urls = [
        'https://wcc.t1cloud.com/T1Default/CiAnywhere/Web/WCC/Compliance/ApplicationPortalMyEnquiry/ReadMoreThumbnailData']
    custom_settings = {
        'LOG_STDOUT': True,
        'LOG_FILE': 'scrapy_wollongong.log',
    }

    def __init__(self, page_number=None):
        self.cookies = None
        self.headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            # 'cookie': 'LogonPortal=CookieValue=%22PR_ONLINE_PORTAL%22; Theme-GUEST_99D4CBAF-WCC=#WCCCRM; _ga=GA1.1.481572798.1713262015; CiAnywhere.Auth=07855EF8DFB35896DFE5FF25CEA2C5CC9C9447FF2BCED9297A694E857D10A5886FD4028A3CE9F1C65FC7C02C532AB4AB117D8D85E8AC25743FC5CE1AA368ADA206064315CEF9A2E79111330D58895FF987DD395027FD16DC142CBD66D60A1D488081AEC6751DE52088034997EDB18D2964D67C37AC8DF41447B2090910CC0665AF617E5C0F66F503954F8DBEA866187D3E4C7CF1E6238D8BD598072750C6FB4AC655AA4217B632B74F31E2611BE61DF07480C55838F7A21A90C6C53EC47C60DDA16238AD96AA1978FC13C0AAB81F27C2FCED21F03E03D308472213FFCCC60797255AE370C875AAC9321F701B49E386F1F0184A72F7E444E6D5BEEFE2E0090CD22E68799E3A3D62DC7EE7A425638A07267C286D62998750D4E310FC751BC86CAC954A70E0D82D2FD1CE4455DA2CCC4C9E86E2EBB2809FD5AFC9BDE57A0EB5A49913312F5CD010DD4ED41DD6167533150D71309165265C1CA0841EA7498A39241283063103E7468D264C52D2AF67D70B564811650D5EBEB36FD5D806947353637F2911237D84F8A85CA02957F17C3687BFDF62A1AADA6E77352D84CEDB125AD16EE472FEB14272213E6F1519AB0D497C1C8287855A40C66A19BDCE005D9DCF8E483E5CC287C3BB114FE9C67074293CE5F0FBD5F2795735EFBD11092A009AF2AADAC37225909B3CA7E1BC2E436DD04BC10123E8DE2E7A527ECB38ECC43E952949D2B44A25D9CEE584129AEBCC49869041B259E5204A91863C43E53C6D0CCAEEEA2F8E86A93ADDC51A9FE3B70C16C66D281FE78C8052D2E4A099CE60E043A1CADFD2FCB51B730F2AF9A148389224DC1A81FEA4E2F69972EC218AE69E3B0DE6996D2D103198D5A4A4065E480B150EFEA988852F8570BCD3124B5475FA6A659CDB7204B7C35D184A474C3FC662188BC8F4CE4EDF052910B13114A8C29FB910E9BA37C5A354BC5069349831285F64EC839BF3C3B958E9A64CA2029195978CF7718B182D953DFE093A7626D2F559C6A686D557663628E6655983C8ACE56444D3DEE44A8BDA9F4FD000C31EAF93D14A08E467C0B647E803BB54625CAC8E554B41FA54F3DDBA82D5F8C239F9B11B6A5293BB1B3B9979DAB81A5ECC2D05A6181528086AC52BF0933DA8A5C520A05FD947EE70C4ED9283F3DDA49CD06C5199504CBCB0E75408751FF351EE7CABAB28980D3F3906D9882F88465F0DF89594E5C7327D2FBCB9239A6EFC03CD87E79AECB2A8F888A4518066D3378C54B1D54E4A3888F99288BC8FE9424D511EB1FE459894A2BA6CD4B7B09530EE0D2BB955A502F321DA4B63B291A60291B06BAA20ECF82DF8D60BCEE4BF428EA25A5740489A725D2BE6476EBAD0ED34A28EE53D3E14E09D253EAA1B0245ABC6E30888336D8286AC302845032435D9FC79ACB1524A99A2317656714D934842502B65505AE908F71BA7BDF7E1E1B159691BFDDC751924B7CD60E08DEDB90D5DF25C7DF809B7887AC9C5FE3F6FABE47542EA9CAFC226A7CA67B91D7FCF16A993E26017925AB4E0A1E4FD402796F2B97743844C593BA652414EE799B0D0142168E1F583F4763FB7CA10E3C3E7D2B8287912944C1AD29E3AD2D35C5E4715DB856CD645CA6B6990C19975613355EF1E24F4B42F15F100FA5022CFA25B2CBD32EF08FDAFF86AA5F9B46C93E48E78806E8D40634510828EA2C57F3C561567C34DD382B0D36A; _ga_HGDXPBS245=GS1.1.1713925371.2.1.1713928500.0.0.0',
            'origin': 'https://wcc.t1cloud.com',
            'priority': 'u=1, i',
            'referer': 'https://wcc.t1cloud.com/T1Default/CiAnywhere/Web/WCC/Compliance/ApplicationPortalMyEnquiry?f=%24P1.COM.APPLNDAT.ENQ&h=glPrhg0jV5&t=16D4D24A&suite=PR&pagekey=20240424110344',
            'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'x-amzn-trace-id': '2df25cf7-5088-4b21-9f45-20373ebdee7e',
            'x-requested-with': 'XMLHttpRequest',
        }
        self.page_number = page_number

    def update_cookie(self):
        co = ChromiumOptions()
        co.set_paths(address='172.20.0.3:9222')
        page1 = ChromiumPage('co')
        page1.get('https://www.wollongong.nsw.gov.au/development/view-an-application')
        services = page1.ele('x://*[@id="online_services_text_button_159602"]/div[1]/a').click()
        tab = page1.latest_tab
        tracking = tab.ele('x:/html/body/div[1]/div[4]/div[4]/div/div/div[2]/div[1]/div[4]/a').click()
        self.cookies = tab.cookies(as_dict=True)


    def parse(self, response):
        self.update_cookie()
        params = {
            'f': '$P1.COM.APPLNDAT.ENQ',
            'h': 'glPrhg0jV5',
            't': '16D4D24A',
            'suite': 'PR',
            'uuid': '2df25cf7-5088-4b21-9f45-20373ebdee7e',
        }
        json_data = {
            'NewSearch': False,
            'IsFirstLoad': False,
            'PickListData': {
                'PickListMode': False,
                'IsExtendedPicklistField': False,
            },
            'RequestData': {
                'f': '$P1.COM.APPLNDAT.ENQ',
                'h': 'glPrhg0jV5',
                't': '16D4D24A',
                'suite': 'PR',
                'pagekey': '20240424110344',
            },
            'TabName': '',
            'DisplayFields': [
                {
                    'FieldName': 'FileId',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAEZpbGVJZAB5kvvdnXS/7q75FS/JR/2CeeQiSYxpOnKII41izt/pCA==',
                },
                {
                    'FieldName': 'PrimaryPropertyAddress',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAFByaW1hcnlQcm9wZXJ0eUFkZHJlc3MAz3oRR56mT5XTZapVQDNUQFvl3wSdfiVL2eQNgQGeLjk=',
                },
                {
                    'FieldName': 'ApplnType_Description',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAEFwcGxuVHlwZV9EZXNjcmlwdGlvbgDCSYyGVaT8f4U674qpsUyOXgR7TgW0P+bwc8dHBV0Cnw==',
                },
                {
                    'FieldName': 'Category_Description',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAENhdGVnb3J5X0Rlc2NyaXB0aW9uAOiQs19l5oZP1Qb8FxKcC1RxXgi3maxYZkmybQaCQV6a',
                },
                {
                    'FieldName': 'Description',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAERlc2NyaXB0aW9uAD/rAvAmMBAzdQo8NvJyMVzQ2wO7/bY736qIaHhuSzqO',
                },
                {
                    'FieldName': 'LodgedDate',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAExvZGdlZERhdGUA3tMMK2XFPjBoGXjoJrSJDKxNhWfzo2b6SK8ondAsyLc=',
                },
                {
                    'FieldName': 'AcceptedDate',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAEFjY2VwdGVkRGF0ZQBDuirqjvuYJmhBVAxEsJvNbYGAMPBh4MshvPrz8xCLNg==',
                },
                {
                    'FieldName': 'DecisionDate',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAERlY2lzaW9uRGF0ZQBS5nRaNvx4JRsZyR36wj0OJSFbaXJNkZwmMsz1pXjAMg==',
                },
                {
                    'FieldName': 'EffectiveDate',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAEVmZmVjdGl2ZURhdGUA/0gyufQLkEoY/OjXZkhzXCJ8X8ZmuBALQKZ4tWpDHDY=',
                },
                {
                    'FieldName': 'CompletedDate',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAENvbXBsZXRlZERhdGUAR/xSSikL86b3NdtYAckAM3CHyC6HFDHvz6AKwoAUTqA=',
                },
                {
                    'FieldName': 'ApplnStage_Description',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAEFwcGxuU3RhZ2VfRGVzY3JpcHRpb24AfE/2d8dc7Go3RcnU3e441vkysmN4/OG5NWyO8qrtTP4=',
                },
                {
                    'FieldName': 'SC_StatusCode',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAFNDX1N0YXR1c0NvZGUAKdltSkcYnoIc+AUlF1ofyrY+CNl30UGitKNVbqyymhA=',
                },
                {
                    'FieldName': 'StatusColour',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAFN0YXR1c0NvbG91cgAzynb7BVRy9i+wgyvZ6x8O4bAXEW/00mG5+PM1MHo6Lw==',
                },
                {
                    'FieldName': 'ComplianceSystem',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAENvbXBsaWFuY2VTeXN0ZW0ABM/+9KDX78DjGWc8Hvx3TONyZmiq87ia+d40Zg/wC2Q=',
                },
                {
                    'FieldName': 'ApplicationId',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAEFwcGxpY2F0aW9uSWQATGDTlb/2tqzvLgOWLp+CD5qFbBlcwZO+aS94Zhph+Hw=',
                },
                {
                    'FieldName': 'ApplicationType',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAEFwcGxpY2F0aW9uVHlwZQBWm3I3f3bsNULl1iJkp13z3NwYbx+/dAtSop/fjoLEpQ==',
                },
                {
                    'FieldName': 'CategoryCode',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAENhdGVnb3J5Q29kZQDwKsYiYWQQ5Za/3WQYQVMb0Q98gPnXz+pQh+3qL5DqcQ==',
                },
                {
                    'FieldName': 'StatusCode',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAFN0YXR1c0NvZGUAjqYL/PqK1auHKEO+bHfqBPqxCFTv1M5gCqkVyYk9cpU=',
                },
                {
                    'FieldName': 'ApplicationStageCode',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAEFwcGxpY2F0aW9uU3RhZ2VDb2RlAHmKyRKqx1biTqSCDvY1Xil6gY6PJBgDXH2eEMojuI2o',
                },
                {
                    'FieldName': 'ProjectId',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAFByb2plY3RJZAAo6os0eyJZoNIifa6UGjlXqSc6FjknqN3cvvSPK34+1Q==',
                },
                {
                    'FieldName': 'ParentApplicationId',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAFBhcmVudEFwcGxpY2F0aW9uSWQAbzmtKe8HNdPTzgpz/5xfV8S/PNB0ceb4YGxWCyneCsY=',
                },
                {
                    'FieldName': 'FileYear',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAEZpbGVZZWFyAGrr087AyISBkJzHCbj/Qa2EPxUhf5v/vujadOlflgtK',
                },
                {
                    'FieldName': 'FileNumber',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAEZpbGVOdW1iZXIAkmSqNmIqdmc05bnSwgnYUKiiS3jaBNXpicDvpzYsdKw=',
                },
                {
                    'FieldName': 'FileStage',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAEZpbGVTdGFnZQBA8Zv7cuC31emX1zomhYDRwlox3EtRqNy5NBj/heWuLw==',
                },
                {
                    'FieldName': 'FileVersion',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAEZpbGVWZXJzaW9uAP4TTy11RKDzUnffxa0W6S//SxRNFuuTnOhi3M3Imhj5',
                },
                {
                    'FieldName': 'FileAmendment',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAEZpbGVBbWVuZG1lbnQAgtYd2LgfivpP5HXEDBY+Z62EvLpAha2YTUVDPZh283w=',
                },
                {
                    'FieldName': 'PrimaryPropertyId',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAFByaW1hcnlQcm9wZXJ0eUlkAOyp7gVKzMTB7fjA2v7EhzQwM87iPOaL8v92SCiDYrtw',
                },
                {
                    'FieldName': 'PrimaryPropertyLocality1',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAFByaW1hcnlQcm9wZXJ0eUxvY2FsaXR5MQDzYKGwVGfHntVqiiWuAihIDPfXiqyu4JsYJLSJQojVdg==',
                },
                {
                    'FieldName': 'PrimaryPropertyLocality2',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAFByaW1hcnlQcm9wZXJ0eUxvY2FsaXR5MgCkTryB7E1EM13ER9danVLbP8a9M8Go9+1k7QfIpwyHJw==',
                },
                {
                    'FieldName': 'PrimaryPropertyLocality3',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAFByaW1hcnlQcm9wZXJ0eUxvY2FsaXR5MwDwsZGJoHrI1Ty7oKvEidycpG5FF+/rxmwKqUFf3zu8Qg==',
                },
                {
                    'FieldName': 'PrimaryPropertySystem',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAFByaW1hcnlQcm9wZXJ0eVN5c3RlbQCb4oTBCuzxAbnKXSILIpNNcT17blGLHbal+lkqlbtiAw==',
                },
                {
                    'FieldName': 'ApplnType_ApplicationType',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAEFwcGxuVHlwZV9BcHBsaWNhdGlvblR5cGUAa9DfAqFg68RbZ4aSNF7TWMNGV4cza4lr45+1kpr5Oy0=',
                },
                {
                    'FieldName': 'ApplnStage_ApplicationStageCode',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjYxMjQ5MDVaAEFwcGxuU3RhZ2VfQXBwbGljYXRpb25TdGFnZUNvZGUAT1oQ4jA6q3T76hRauo4ceqCqBOhwS+XBuzX3SkW3/5U=',
                },
            ],
            'Parameters': [
                {
                    'FieldName': 'MasterSystem',
                    'Value': 'CNCL',
                    'SyncKey': 'P1.MasterSystem',
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjU1NTc4MDVaAENOQ0wAxJiflLOJSK61fPHHpN8X+ZF6aUSAU3hTx1B86AnNzN4=',
                },
                {
                    'FieldName': 'ComplianceSystem',
                    'Value': 'CNCL',
                    'SyncKey': 'P1COM_SYSTEM',
                    'Hash': 'VQAyMDI0LTA0LTI0VDAzOjAzOjQ0LjU1NTc4MDVaAENOQ0wAxJiflLOJSK61fPHHpN8X+ZF6aUSAU3hTx1B86AnNzN4=',
                },
            ],
            'FormData': {
                'Tables': [],
                'Fields': [
                    {
                        'FieldName': 'SearchValue',
                        'DataType': 'String',
                        'Value': '',
                    },
                ],
                'Maps': [],
            },
            'SelectedFilters': [],
            'CustomFiltersData': [],
            'MultiSortFields': [
                {
                    'SortDirection': 'D',
                    'FieldName': 'LodgedDate',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                },
                {
                    'SortDirection': 'D',
                    'FieldName': 'FileId',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                },
            ],
            'AnalyserItemNavigatorData': {
                'NavigatorMode': False,
            },
            'SearchValue': '',
            'ActiveView': 0,
            'ShowBooleanAsCheckbox': True,
            'LayoutName': 'CARD',
            'dbPageNumber': 3,
            'PageNumber': 3,
            'PageSize': 40,
        }
        url = 'https://wcc.t1cloud.com/T1Default/CiAnywhere/Web/WCC/Compliance/ApplicationPortalMyEnquiry/ReadMoreThumbnailData'
        new_url = str(url) + '?' + urlencode(params, doseq=True)
        for v in range(1, int(self.page_number)+1):
            json_data['dbPageNumber'] = v
            json_data['PageNumber'] = v
            yield JsonRequest(
                url=new_url,
                data=json_data,
                headers=self.headers,
                cookies=self.cookies,
                callback=self.parse_first_request
            )

    def parse_first_request(self, response):
        params = {
            'f': '$P1.COM.APPLNDAT.ENQ',
            'h': 'OWVz18JTQx',
            't': '16AD3E7B',
            'suite': 'PR',
            'uuid': '476e49af-02b1-4be0-9bd6-00fd89e14081',
            'ts': '1711335970954',
        }
        json_data1 = {
            'SyncKeys': '',
            'HeaderValue': '',
            'IsFavourite': False,
            # 'RecordID': '1',
            'Parameters': [
                {
                    'FieldName': 'MasterSystem',
                    'Value': 'CNCL',
                    'SyncKey': 'P1.MasterSystem',
                    'Hash': 'VQAyMDI0LTAzLTI1VDAzOjA0OjEwLjk1ODA5MjJaAENOQ0wAeCwg2i0BCAB31iCsn26Dhi2Eiuyik0+LASXrah/PD5I=',
                },
                {
                    'FieldName': 'ComplianceSystem',
                    'Value': 'CNCL',
                    'SyncKey': 'P1COM_SYSTEM',
                    'Hash': 'VQAyMDI0LTAzLTI1VDAzOjA0OjEwLjk1ODA5MjJaAENOQ0wAeCwg2i0BCAB31iCsn26Dhi2Eiuyik0+LASXrah/PD5I=',
                },
            ],
            'RequestData': {
                'SectionName': 'ApplicationSummaryForEnquirySection',
                'f': '$P1.COM.APPLNDAT.ENQ',
                'h': 'OWVz18JTQx',
                't': '16AD3E7B',
                'suite': 'PR',
                'pagekey': '20240325093454',
            },
            'EnableFavourites': False,
        }
        response_json = json.loads(response.body)
        sync_keys_list = []
        ApplicationIds = []

        for i in range(40):
            sync_keys = response_json['Items'][i]['SyncKeys']
            applicationId = response_json['Items'][i]['ActionMenu']['RowAction']['Items'][0]['Parameters']['ApplicationId']
            sync_keys_list.append(sync_keys)
            ApplicationIds.append(applicationId)
        url = 'https://wcc.t1cloud.com/T1Default/CiAnywhere/Web/WCC/Compliance/ApplicationPortalMyEnquiry/GetDetailsPanel'
        new_url = str(url) + '?' + urlencode(params, doseq=True)
        for sync_keys in sync_keys_list:
            json_data1['SyncKeys'] = sync_keys
            yield JsonRequest(
                url=new_url,
                data=json_data1,
                headers=self.headers,
                cookies=self.cookies,
                # dont_filter=True,
                callback=self.parse_second_request,
                cb_kwargs={'ApplicationIds': ApplicationIds}
            )

    def parse_second_request(self, response, ApplicationIds):
        fields_lists = []
        response_json = json.loads(response.body)
        a = response_json['Html']
        soup = BeautifulSoup(a, 'lxml')
        content_div = soup.find('div', class_="contentContainer initialisableControl fixedWidth")
        data_t1_control = content_div.get('data-t1-control')
        data = json.loads(data_t1_control)
        fields_list = data['InitialData']['Fields']
        fields_lists.append(fields_list)
        params4 = {
            'f': '$P1.COM.APPLNDAT.MNT',
            'h': 'LSdPkBBOWH',
            't': '16AD5503',
            'suite': 'PR',
            'uuid': '36b1a0bb-fe55-4b6f-9b67-19eb21b01a2e',
        }
        json_data3 = {
            'NewSearch': True,
            'IsFirstLoad': True,
            'PickListData': {
                'PickListMode': False,
                'IsExtendedPicklistField': False,
            },
            'HierarchyLevel': 0,
            'RequestData': {
                'f': '$P1.COM.APPLNDAT.MNT',
                'h': '6G4YVYZQp2',
                't': '16D505C6',
                'suite': 'PR',
                'pagekey': '20240424144438',
            },
            'TabName': 'Tab_AttachmentRdpSection',
            'DisplayFields': [
                {
                    'FieldName': 'LINK_FIELD__',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAExJTktfRklFTERfXwBrvPjx8vOei7aVQNPvydJqv+wnFIFMFbjz7B0U3GuPCQ==',
                },
                {
                    'FieldName': 'SmallImageUrl',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAFNtYWxsSW1hZ2VVcmwAN81Q4ikBzX5xY9VeXbQmTotdUl3/mTk8Y5aBKbH1t8c=',
                },
                {
                    'FieldName': 'LargeImageUrl',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAExhcmdlSW1hZ2VVcmwA9mIZa+KPWQP0fpfU8973xDWELajbjq7LZmC7mYlrraw=',
                },
                {
                    'FieldName': 'Description',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAERlc2NyaXB0aW9uANRxGwEpZlSromyYFVCtm8i392QrkUA4DZKafOQ9BsZi',
                },
                {
                    'FieldName': 'AttachmentType',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAEF0dGFjaG1lbnRUeXBlALZH+3IFTD3pQ77Kj70lTVm+fkd1XODcYn+hj25yNsNd',
                },
                {
                    'FieldName': 'AttachmentDate',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAEF0dGFjaG1lbnREYXRlAIr+3P9yFSDjvW3HdU/8Kb8u/6Beb6AXNzeNhq4jN1d9',
                },
                {
                    'FieldName': 'Extension',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAEV4dGVuc2lvbgD9uR+a5Yi5kHF4Fz/UEoUw89ntTJpipOGuTv+Qxacpgg==',
                },
                {
                    'FieldName': 'AttachmentFileSize',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAEF0dGFjaG1lbnRGaWxlU2l6ZQDgPBlsiMi20Aw8NooFbsZua48JziLJB41+9EH2d0MLAA==',
                },
                {
                    'FieldName': 'DownloadImageUrl',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAERvd25sb2FkSW1hZ2VVcmwA2RpOZf2KWgAyUuvT3DYG8oEo4eVUcOeSyUb7o9QuV6I=',
                },
                {
                    'FieldName': 'SC_Status',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAFNDX1N0YXR1cwB1QIzGXTSmrJ3Ll5wqmMfvPC5F6Pdl6DyIOXFcqUyirw==',
                },
                {
                    'FieldName': 'StatusColour',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAFN0YXR1c0NvbG91cgBFO3jXg1hOktIiOVDDasrGH1VHSfzrd5iCG9ZcKnMjuQ==',
                },
                {
                    'FieldName': 'ComplianceSystem',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAENvbXBsaWFuY2VTeXN0ZW0AHCIn1OCOybqi9gpYRP0Md3oYl9/izpyuJ0b2shQaR0I=',
                },
                {
                    'FieldName': 'ApplicationId',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAEFwcGxpY2F0aW9uSWQA6YzgcC/v0NN7JZoXXZOTn/cEwDR//XhZO75toyw+V/o=',
                },
                {
                    'FieldName': 'UniqueNumber',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAFVuaXF1ZU51bWJlcgAUqQaYmbVLKG/1gtLAwa71NAIYGbHLkIuD8kcydqVk4A==',
                },
                {
                    'FieldName': 'SequenceNumber',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAFNlcXVlbmNlTnVtYmVyAPEom1GKLyr8DNiwcrrrsnUoP9BKj7HtryJHtSrmdi0U',
                },
                {
                    'FieldName': 'SourceDocumentType',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAFNvdXJjZURvY3VtZW50VHlwZQAaW+fleddn2MbhFUkhZLwCHQx0t5Vqfh49GArNEzT5pw==',
                },
                {
                    'FieldName': 'IsDeleted',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAElzRGVsZXRlZADCp1o/oUJatRUZ+/TYxs4wG1ib4TK14wm4BYWNn/fm2A==',
                },
                {
                    'FieldName': 'SourceUploaded',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAFNvdXJjZVVwbG9hZGVkAPPMnSnDJYrd03hhWT1JFMto50WsQKooqRJt51WBiqq8',
                },
                {
                    'FieldName': 'SourceDocumentUrl',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAFNvdXJjZURvY3VtZW50VXJsABC72+Afq6Fn5EYKZtRjWaEzNOpTPCLFxz66YsxrQxNZ',
                },
                {
                    'FieldName': 'Notes',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAE5vdGVzABBtWPX8GvkWzA5oClbwOLlX5OsC2wWz2irmiS4kiauL',
                },
                {
                    'FieldName': 'Status',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAFN0YXR1cwCwlAuq0sJU6Uv33DIK42Bj2j7YKwLl+z0QVudrxsW+IA==',
                },
                {
                    'FieldName': 'Source',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAFNvdXJjZQC+h+h6kn3OfobBwHOs3+d2YdnEbywiJIxoR8LmZwXehg==',
                },
                {
                    'FieldName': 'SC_Source',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAFNDX1NvdXJjZQChoSEQ+4Vhy559gfagz7jU/AgqnTJA+5u9OizYKRZRyQ==',
                },
                {
                    'FieldName': 'Visibility',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAFZpc2liaWxpdHkA9PQzsnUTK0IFbnO2fRQZ9OL9ELBbBN6Ezuo8DagtGDI=',
                },
                {
                    'FieldName': 'SC_Visibility',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAFNDX1Zpc2liaWxpdHkAXIEOyLaS65vvw9AHzIF1+InJ2+Peq5zkA2+u6UzcK4I=',
                },
                {
                    'FieldName': 'IsSuperseded',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAElzU3VwZXJzZWRlZADZB/FcGlccsSJCO0FRUs74ptluKQmT0eHRNDgCAGznFA==',
                },
                {
                    'FieldName': 'SC_IsSuperseded',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAFNDX0lzU3VwZXJzZWRlZADNPZR7KY2FPjNFnHRMXYydZ6FVCnMciMU3hBFWcNQ9nA==',
                },
                {
                    'FieldName': 'IsFinal',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAElzRmluYWwAK3dKFNpG1GDzQGTia7lRR3GmfJovNwL0GJYzXywtl78=',
                },
                {
                    'FieldName': 'SC_IsFinal',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAFNDX0lzRmluYWwA+JhfDL4bQKRN7NQFxRlrFPonbcB8opIiq/kru0Oslj4=',
                },
                {
                    'FieldName': 'SC_IsDeleted',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3Ljk4NTA2MjhaAFNDX0lzRGVsZXRlZADN32JdopEy6F0LtkI5p/iIZXPt1wObzTlEr5n8yBot5A==',
                },
            ],
            'Parameters': [
                {
                    'FieldName': 'MasterSystem',
                    'Value': 'CNCL',
                    'FormattedValue': '',
                    'Description': '',
                    'SyncKey': 'P1.MasterSystem',
                    'IsKeyField': True,
                    'IsNullable': False,
                    'TranslateCrLf': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3LjkzMzU3MDdaAENOQ0wAcuA8+UK8yolwPtL4MMZuhI7GwxmNQH6sdF9Oa0JnTOg=',
                    'IsRepeatableField': False,
                },
                {
                    'FieldName': 'ComplianceSystem',
                    'Value': 'CNCL',
                    'FormattedValue': '',
                    'Description': '',
                    'SyncKey': 'P1COM_SYSTEM',
                    'IsKeyField': True,
                    'IsNullable': False,
                    'TranslateCrLf': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3LjkzMzU3MDdaAENOQ0wAcuA8+UK8yolwPtL4MMZuhI7GwxmNQH6sdF9Oa0JnTOg=',
                    'IsRepeatableField': False,
                },
                {
                    'FieldName': 'ApplicationId',
                    'Value': '',
                    'FormattedValue': '',
                    'Description': '',
                    'SyncKey': 'P1_COM_APPLICATION_CODE',
                    'IsKeyField': True,
                    'IsNullable': False,
                    'TranslateCrLf': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3LjkzMzU3MDdaADE1NzU0ODIA0VxDWahpwiXxXRnhSJ1rQXGg/LDaG8F5Re2VwwNvcAw=',
                    'IsRepeatableField': False,
                },
                {
                    'FieldName': 'UniqueNumber',
                    'Value': '',
                    'Description': '',
                    'IsKeyField': False,
                    'IsNullable': False,
                    'TranslateCrLf': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3LjkzMzU3MDdaAN6ZsS7zA+Kj5yPtKAwM0zbtPZyUxJflxkmjIONNEDd3',
                    'IsRepeatableField': False,
                },
                {
                    'FieldName': 'Visibility',
                    'Value': 'P',
                    'Description': '',
                    'IsKeyField': False,
                    'IsNullable': False,
                    'TranslateCrLf': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3LjkzMzU3MDdaAFAAfFVgKboZbBvxbTfzgXLuVEaixWdH4Xw2jrSkQd+9Ax0=',
                    'IsRepeatableField': False,
                },
                {
                    'FieldName': 'ControlId',
                    'Value': '',
                    'Description': '',
                    'IsKeyField': False,
                    'IsNullable': False,
                    'TranslateCrLf': False,
                    'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ1OjA3LjkzMzU3MDdaAN6ZsS7zA+Kj5yPtKAwM0zbtPZyUxJflxkmjIONNEDd3',
                    'IsRepeatableField': False,
                },
            ],
            'FormData': {
                'Tables': [],
                'Fields': [
                    {
                        'SyncKey': 'P1.MasterSystem',
                        'FieldName': 'MasterSystem',
                        'Value': 'CNCL',
                        'FormattedValue': '',
                        'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ0OjQxLjQwNjI0MTJaAE1hc3RlclN5c3RlbSxDb21wbGlhbmNlU3lzdGVtLEFwcGxpY2F0aW9uSWQACtJebmaw6GXPWpGc8mX7JxdCD5wQsAdWnCrcUqSp5v4=',
                        'IsKeyField': True,
                    },
                    {
                        'SyncKey': 'P1COM_SYSTEM',
                        'FieldName': 'ComplianceSystem',
                        'Value': 'CNCL',
                        'FormattedValue': '',
                        'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ0OjQxLjQwNzgxNzVaAE1hc3RlclN5c3RlbSxDb21wbGlhbmNlU3lzdGVtLEFwcGxpY2F0aW9uSWQAAOXnN4m7fa75f01InrTD/KsKdXr4zs6lJadob6rLXY0=',
                        'IsKeyField': True,
                    },
                    {
                        'SyncKey': 'P1_COM_APPLICATION_CODE',
                        'FieldName': 'ApplicationId',
                        'Value': '1575482',
                        'FormattedValue': '',
                        'Hash': 'VQAyMDI0LTA0LTI0VDA2OjQ0OjQxLjQwNzgxNzVaAE1hc3RlclN5c3RlbSxDb21wbGlhbmNlU3lzdGVtLEFwcGxpY2F0aW9uSWQAtCfEowlhP1RhI3pKbidwfaW7zmQCadppi5jqIjef/gA=',
                        'IsKeyField': True,
                    },
                    {
                        'FieldName': 'Vers',
                        'Value': '22',
                        'FormattedValue': '',
                        'Hash': None,
                    },
                ],
                'Maps': [],
            },
            'SelectedFilters': [],
            'CustomFiltersData': [],
            'MultiSortFields': [
                {
                    'SortDirection': 'A',
                    'FieldName': 'Status',
                    'Width': 0,
                    'SequenceNumber': 0,
                    'FrozenColumn': False,
                },
            ],
            'AnalyserItemNavigatorData': {
                'NavigatorMode': False,
            },
            'SearchValue': '',
            'ActiveView': 1,
            'ShowBooleanAsCheckbox': True,
            'LayoutName': 'CARD_PORTAL_APPLN_ATTCHMTS',
            'dbPageNumber': 1,
            'PageNumber': 1,
            'PageSize': 40,
        }
        for ApplicationId in ApplicationIds:
            json_data3['Parameters'][2]['Value'] = ApplicationId
            url = 'https://wcc.t1cloud.com/T1Default/CiAnywhere/Web/WCC/Compliance/ApplicationPortalMyMaintenance/ReadMoreThumbnailData'
            new_url = str(url) + '?' + urlencode(params4, doseq=True)
            yield JsonRequest(
                url=new_url,
                cookies=self.cookies,
                headers=self.headers,
                data=json_data3,
                dont_filter=True,
                callback=self.parse_third_request,
                cb_kwargs={'fields_lists': fields_lists}
            )

    def parse_third_request(self, response, fields_lists):
        response_json = json.loads(response.body)
        documents = []
        if not response_json['Items']:
            documents.append('none')
        else:
            items = response_json['Items']
            combined_data = []
            for Item in items:
                # combined_data = ':'.join([,Item['AllFields'][2]['Value']])
                combined_data.append(f"{Item['AllFields'][2]['Value']}:{Item['AllFields'][1]['Value']}")
            documents.append('@@'.join(combined_data))

        params = {
            'f': '$P1.COM.APPLNDAT.ENQ',
            'h': 'OWVz18JTQx',
            't': '16AD3E7B',
            'suite': 'PR',
            'uuid': 'c7f9df6f-8ef2-49a3-971a-384e4d426358',
            'ts': '1711337099442',
        }
        json_data2 = {
            'FormData': {
                'Fields': '',
            },
            'ActionName': 'ReadSection',
            'RequestData': {
                'SectionName': 'ApplicationSummaryForEnquirySection',
                'f': '$P1.COM.APPLNDAT.ENQ',
                'h': 'OWVz18JTQx',
                't': '16AD3E7B',
                'suite': 'PR',
                'pagekey': '20240325093454',
            },
            'ShowLoader': True,
        }
        for fields_list in fields_lists:
            json_data2['FormData']['Fields'] = fields_list
            url = 'https://wcc.t1cloud.com/T1Default/CiAnywhere/Web/WCC/Compliance/ApplicationPortalMyEnquiry/SectionAction'
            new_url = str(url) + '?' + urlencode(params, doseq=True)
            yield JsonRequest(
                url=new_url,
                cookies=self.cookies,
                headers=self.headers,
                data=json_data2,
                # dont_filter=True,
                callback=self.parse_fourth_request,
                meta={'documents': documents}
            )

    def parse_fourth_request(self, response):

        documents = response.meta.get('documents')
        response_json = json.loads(response.body)
        b = response_json['Html']
        soup = BeautifulSoup(b, 'lxml')
        summary_text = soup.get_text(strip=True, separator='\n')

        match = re.search(r'Summary\n(.*?)\nSummary', summary_text, re.DOTALL)
        summary_values = match.group(1).strip().split('-')
        number = ' - '.join([value.strip() for value in summary_values[:2]])

        tree = html.fromstring(b)
        date = tree.xpath(
            "//table[.//h3[text()='Summary']]//following::table[.//h3[text()='Progress']]/preceding::tr[.//td][.//td]//td")
        summary = {}
        for i in range(0, len(date) - 1, 2):
            key = date[i + 1].text_content().strip()
            value = date[i + 2].text_content().strip()
            summary[key] = value
        # keys = [
        #     'ApplicationType', 'SiteName', 'Description', 'Lodged', 'Accepted',
        #     'Determined', 'Effective', 'ModificationCategory', 'development',
        #     'NSWPlanningPortal', 'notification', 'dwellinghouse', 'Lapsed', 'Complete'
        # ]
        ApplicationType = summary.get('Application Type')
        SiteName = summary.get('Site Name')
        Description = summary.get('Description')
        Lodged = summary.get('Lodged')
        Accepted = summary.get('Accepted')
        Determined = summary.get('Determined')
        Effective = summary.get('Effective')
        ModificationCategory = summary.get('Modification Category')
        development = summary.get('Is the development Integrated Development?')
        NSWPlanningPortal = summary.get('Enter the NSW Planning Portal Reference number.')
        notification = summary.get('Is notification of the Review required?')
        dwellinghouse = summary.get('Does the development involve the erection of a dwelling house with Cost of Works of less than $100,000')
        Lapsed = summary.get('Lapsed')
        Completed = summary.get('Completed')


        pattern = r'(?<=<tr><td>)([^<]+)</td><td>([^<]*)</td><td>([^<]*)</td><td>([^<]*)</td></tr>'
        extracted_content = re.findall(pattern, b)
        extracted_dict = {}
        for item in extracted_content:
            key = item[0]
            values = [val if val else 'none' for val in item[1:]]
            extracted_dict[key] = values

        match3 = re.search(r'People\n(.*?)\nProperty and Land Associations', summary_text, re.DOTALL)
        if match3:
            peo = match3.group(1)
            lines = peo.strip().split("\n")
            people = ""
            for i in range(0, len(lines), 2):
                key = lines[i]
                value = lines[i + 1]
                people += f"{key}: {value},"
            people = people.rstrip(',')
        else:
            people = ""

        match4 = re.search(r'Property and Land Associations(.*?)Documents', summary_text, re.DOTALL)
        Asso = match4.group(1)
        Associations = Asso.strip().replace("\n", "-")

        lodged = datetime.strptime(Lodged, '%d/%m/%Y').date() if Lodged else None
        obj_lodged = time.mktime(lodged.timetuple())
        accept = datetime.strptime(Accepted, '%d/%m/%Y').date() if Accepted else None
        obj_accept = time.mktime(accept.timetuple())
        effective = datetime.strptime(Effective, '%d/%m/%Y').date() if Effective else None
        obj_effective = time.mktime(effective.timetuple())
        lapsed = datetime.strptime(Lapsed, '%d/%m/%Y').date() if Lapsed else None
        obj_lapsed = time.mktime(lapsed.timetuple())
        completed = datetime.strptime(Completed, '%d/%m/%Y').date() if Completed else None
        obj_completed = time.mktime(completed.timetuple())
      
        item = WollongongItem()
        item['app_number'] = number
        item['ApplicationType'] = ApplicationType
        item['SiteName'] = SiteName
        item['Description'] = Description
        item['Lodged'] = obj_lodged
        item['Accepted'] = obj_accept
        item['Determined'] = Determined
        item['Effective'] = obj_effective
        item['ModificationCategory'] = ModificationCategory
        item['development'] = development
        item['NSWPlanningPortal'] = NSWPlanningPortal
        item['notification'] = notification
        item['dwellinghouse'] = dwellinghouse
        item['Lapsed'] = obj_lapsed
        item['Completed'] = obj_completed
        item['Progress'] = extracted_dict
        item['People'] = people
        item['Associations'] = Associations
        item['documents'] = documents
        print(item)
        yield item
