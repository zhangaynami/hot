import requests
import pandas as pd
import json
import re
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime,timedelta
import os
import sys
import io
import tkinter as tk
import akshare as ak
import streamlit as st

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# 获取同花顺热搜
def get_ths_hot_data():

    url = "https://dq.10jqka.com.cn/fuyao/hot_list_data/out/hot_list/v1/stock?stock_type=a&type=day&list_type=value"
    headers = {
        "Referer": "https://eq.10jqka.com.cn/webpage/ths-hot-list/index.html",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        stock_list = data.get('data').get('stock_list')
        print("获取同花顺数据")
        for stock in stock_list:
        # 提取concept_tag并将其转换为字符串格式
            stock['concept_tag'] = ', '.join(stock['tag'].get('concept_tag', []))
            # 删除原始的'tag'键
            del stock['tag']
        data = pd.DataFrame(stock_list)
        pd.set_option('display.max_columns', None)  # 显示所有列
        pd.set_option('display.width', None)        # 自动调整输出宽度
        pd.set_option('display.max_colwidth', None) # 显示列中完整内容
        get_title = ["code","rise_and_fall","name","display_order","concept_tag"]
        # 列名中英文对照字典
        columns_chinese = {
            "code": "股票代码",
            "rise_and_fall": "涨跌幅",
            "name": "股票名称",
            "display_order": "显示顺序",
            "concept_tag": "概念标签"
        }
        fin_data = data[get_title]
        fin_data = fin_data.head(20)
        # 修改DataFrame的列名为中文
        fin_data.rename(columns=columns_chinese, inplace=True)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建完整文件路径
        # png_filename = os.path.join(script_dir, "同花顺热搜.png")
        # generate_chart(fin_data, png_filename, title="同花顺热搜")
        csv_filename = os.path.join(script_dir, "同花顺热搜.csv")
        fin_data.to_csv(csv_filename, index=False, encoding='utf-8-sig')

        print("同花顺数据输出成功")
        return fin_data 
    else:
        print("请求失败，状态码：", response.status_code)

# 获取东方财富热榜
def get_dfcf_hot():
    print("获取东方财富热搜")
    get_requests = {}
    # 获取发起请求的基础信息
    def getUtandeFields():
        url = "https://vipmoney.eastmoney.com/collect/app_ranking/static/script/ranking/app/app_4b428acb7c6b72baafe1.js?v=4b428acb7c6b72baafe1"
        headers = {    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        response = requests.get(url, headers=headers).text
        # print(response)
        ut = re.compile(r'api/qt/ulist.np/get\?ut=([^\s&]+)&fltt=2')
        get_ut = ut.findall(response)[0]
        get_requests['ut'] = get_ut
        fields = re.compile(r'&fields=([^\s&]+)&')
        get_fields = fields.findall(response)[0].replace("%2C", ",")
        get_requests['fields'] = get_fields
        fltt = re.compile(r'&fltt=([^\s&]+)&')
        get_fltt = fltt.findall(response)[0].replace("%2C", ",")
        get_requests['fltt'] = get_fltt
        invt = re.compile(r'&invt=([^\s&]+)&')
        get_invt = invt.findall(response)[0].replace("%2C", ",")
        get_requests['invt'] = get_invt
        globalId = re.compile(r'globalId:"([^\s&]+)"')
        get_globalId = globalId.findall(response)[0]
        get_requests['globalId'] = get_globalId
        appId = re.compile(r'appId:"([^\s&]+)"')
        get_appId = appId.findall(response)[0]
        get_requests['appId'] = get_appId
        pageSize = re.compile(r'pageSize:([^\s&]+)}')
        get_pageSize = pageSize.findall(response)[0]
        get_requests['pageSize'] = get_pageSize
        pageNo = re.compile(r'pageNo:([^\s&]+),pageSize')
        get_pageNo = pageNo.findall(response)[0]
        get_requests['pageNo'] = get_pageNo
        return get_requests

    # 获取股票列表
    def getSecids(appId=None,globalId=None,pageNo=None,pageSize=None):
        url = "https://emappdata.eastmoney.com/stockrank/getAllCurrentList"
        headers = {    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        headers['Host'] = "emappdata.eastmoney.com"
        headers['Origin'] = "https://vipmoney.eastmoney.com"
        data = {
            'appId': appId,
            'globalId': globalId,
            'pageNo': pageNo,
            'pageSize': pageSize,
        }
        response = requests.post(url,headers=headers,json=data).text
        jsData = json.loads(response)['data']
        secids = ""
        securityCodes= ""
        for item in jsData:
            sc = item['sc']
            securityCodes += sc + ","
            if "SH" in sc:
                secids += sc.replace("SH", "1.") + ","
            else:
                secids += sc.replace("SZ", "0.") + ","
        values = secids.split(',')
        modified_string = ','.join(values[:-1])
        securityCodes_values = securityCodes.split(',')
        modified_securityCodes_string = ','.join(securityCodes_values[:-1])
        return modified_string,modified_securityCodes_string
    getkey = getUtandeFields()
    secids,securityCodes = getSecids(getkey['appId'],getkey['globalId'],getkey['pageNo'],getkey['pageSize'])
    
    # 获取热搜列表
    def get_hot_list(getkey,secids,securityCodes,num=20):
        # 股票列表
        get_stocks_url="https://push2.eastmoney.com/api/qt/ulist.np/get?ut="+getkey['ut']+"&fltt="+getkey['fltt']+"&invt="+getkey['invt']+"&fields="+getkey['fields']+"&secids=" + secids
        data = {
            'appId': getkey["appId"],
            'globalId': getkey["globalId"],
            'securityCodes': securityCodes
        }       
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}    
        stocks_response = requests.get(get_stocks_url,headers=headers)
        if stocks_response.status_code == 200:
            json_str = json.loads(stocks_response.text)
            get_data = json_str.get("data").get("diff")[0:num]
            data = pd.DataFrame(get_data)
            get_title = ["f2","f3","f12","f14"]
            
            # 列名中英文对照字典
            columns_chinese = {
                "f2": "现价",
                "f3": "涨跌幅",
                "f12": "股票代码",
                "f14": "股票名称"
            }
            fin_data = data[get_title]
            # # 修改DataFrame的列名为中文
            fin_data.rename(columns=columns_chinese, inplace=True)

        else:
            print("请求失败，状态码：", stocks_response.status_code)

        # 股票的板块题材
        get_tips_url = "https://emappdata.eastmoney.com/label/getSecurityCodeLabelList"
        data = {
            'appId': getkey["appId"],
            'globalId': getkey["globalId"],
            'securityCodes': securityCodes
        }   
        tips_response = requests.post(get_tips_url,headers=headers,json=data)      
        if tips_response.status_code == 200:
            json_str = json.loads(tips_response.text)
            get_data = json_str.get("data")[0:num]
            all_tips_content= []
            for i in range(len(get_data)):
                tips_content = {} 
                srcSecurityCode = get_data[i]["srcSecurityCode"]
                stocks = get_data[i]['labelItemList']
                labelNames = ""
                for label in stocks:
                    labelName = label.get("labelName")
                    labelNames += labelName + " "
                tips_content["股票代码"] = srcSecurityCode
                tips_content["概念"] = labelNames
                
                all_tips_content.append(tips_content)
            # print(all_tips_content)
        data = pd.DataFrame(fin_data)
        all_tips_data = pd.DataFrame(all_tips_content)
        all_tips_data["股票代码"] = all_tips_data["股票代码"].str[2:]
        result = pd.merge(data, all_tips_data,on='股票代码', how='left')
        print("获取东方财富热搜成功")

        return result

    final_data = get_hot_list(getkey,secids,securityCodes)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # png_filename = os.path.join(script_dir, "东方财富热搜.png")
    # generate_chart(final_data, png_filename, title="东方财富热搜")
    csv_filename = os.path.join(script_dir, "东方财富热搜.csv")
    final_data.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    return final_data
# 获取雪球数据
def get_xueqiuhot_data():
    print("开始获取雪球热股")
    url = "https://stock.xueqiu.com/v5/stock/hot_stock/list.json?page=1&size=9&_type=12&type=12"
    params = {
        "page": 1,
        "size": 9,
        "_type": 12,
        "type": 12,
        "md5__1632": "n4mx9DcDnAKmqYK5GNDQTYBK0QUQj%2BA8duB4bD"
    }

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://xueqiu.com/',
    'Cookie': "cookiesu=721731590156481; device_id=fba857a90e016b92c2681d18abc27deb; s=bl11r6stce; xq_is_login=1; u=7991686944; bid=eed923e2fdd3360a48952826f1511b29_m472p3lf; xq_a_token=520a9765936f49b43ded6111854c12347d8f5f51; xqat=520a9765936f49b43ded6111854c12347d8f5f51; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjc5OTE2ODY5NDQsImlzcyI6InVjIiwiZXhwIjoxNzQzOTQzMjM4LCJjdG0iOjE3NDEzNTEyMzgxMDQsImNpZCI6ImQ5ZDBuNEFadXAifQ.j6yD_rgIvzlh2b-ZN1LjyAwIon28YQbUaVaFrFfTu6RTo_ZI7M8ZIYj1Zok76VyU45zwAPdRZLnLgAQZoNAvK6qBYVaNETB1dJfpViwaC-0vI2_NsBRA_hHcOYfKDdOIKUOoIZB5S328HS-vX_q8_oU-SSUwpfSlmX0BI5g323j01gpbph0dC1z0H04dBtfEPEKqQjuGd_AePAOURajZX-CtVOp3yf9yNuVajU0exlGMZ7g4nwD5S7kow4UlNxQQGFuNPFTMWOujXLG56Ro6K5pgtPoX_dhMbKnuBDbDGBzDoys14VN67HO31HG3UHJtP7_xfCN6-G6UZBXYjjCHlQ; xq_r_token=ad6a9637058304802a23f5f5607e62a4b12f49cb; Hm_lvt_1db88642e346389874251b5a1eded6e3=1739967845,1740056743,1741351239,1741505095; HMACCOUNT=1D1DA734BA99746D; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1741505167; ssxmod_itna=eqRhBKiKD50IzmDhaDcCD0iDIxIxYKDO7DzxC5iOsDuP4jKidoDUiHPbtCDiuiPFpxNFnEWhCDBu5oDSxD=7DK4GTmG6kh2KO4FiO+qeKi3rpK7WUk5Sx1zAnHPmArH/CScgYxB3DEx06tbYvxxYAEDBYD74G+DDeDiO3Dj4GmDGA3deDFCmbQcnrerxDwDB=DmqG2i2rDm4DfDDd5HMjY2DDl0GHQ77heDYP5XjNWrraDALwd57D5x0UaDBL3IKq5xDtf6KwtXmOvqKoe=cWDtqD986RVW1IYVQu4qIj1i3h1YEeKYrU9K04Y08Cw/bi5YDi9hGSi5YTkfGqBaKnwr95oDiTHn+ZAxmACAk1tf1XwedY5jE=BTouhe1ixv2QdYQIQ5l05Dox7Ddd7Qa0D=753A4q8D7iDD; ssxmod_itna2=eqRhBKiKD50IzmDhaDcCD0iDIxIxYKDO7DzxC5iOsDuP4jKidoDUiHPbtCDiuiPFpxNFnEWxbD8+WEpmFtDT+t=Rcjn+CllxQxI1dFQ08ux+2YD"
    }

    response = requests.get(url, headers=headers,params=params)
    response.encoding = "utf-8"
    if response.status_code == 200:
        
        data = response.text
        json_data = json.loads(data)
        get_data = json_data.get("data").get('items')
        # print(get_data)
        get_title = ["code","name","percent","current"]
        # 列名中英文对照字典
        columns_chinese = {
            "code": "股票代码",
            "name": "股票名称",
            "percent": "涨跌幅",
            "current": "当前股价"
        }
        df = pd.DataFrame(get_data)
        df['code'] = df['code'].apply(lambda x: x[2:] if isinstance(x, str) and len(x) > 2 else x)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_filename = os.path.join(script_dir, "雪球热股.csv")
        
        df = df[get_title]
        # # 修改DataFrame的列名为中文
        df.rename(columns=columns_chinese, inplace=True)
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print("雪球热股数据获取完成")
    else:
        print("请求失败，状态码：", response.status_code)# 获取雪球数据


    print("开始获取雪球热股")
    url = "https://stock.xueqiu.com/v5/stock/hot_stock/list.json?page=1&size=9&_type=12&type=12"
    params = {
        "page": 1,
        "size": 9,
        "_type": 12,
        "type": 12,
        "md5__1632": "n4mx9DcDnAKmqYK5GNDQTYBK0QUQj%2BA8duB4bD"
    }

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://xueqiu.com/',
    'Cookie': "cookiesu=721731590156481; device_id=fba857a90e016b92c2681d18abc27deb; s=bl11r6stce; xq_is_login=1; u=7991686944; bid=eed923e2fdd3360a48952826f1511b29_m472p3lf; xq_a_token=520a9765936f49b43ded6111854c12347d8f5f51; xqat=520a9765936f49b43ded6111854c12347d8f5f51; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjc5OTE2ODY5NDQsImlzcyI6InVjIiwiZXhwIjoxNzQzOTQzMjM4LCJjdG0iOjE3NDEzNTEyMzgxMDQsImNpZCI6ImQ5ZDBuNEFadXAifQ.j6yD_rgIvzlh2b-ZN1LjyAwIon28YQbUaVaFrFfTu6RTo_ZI7M8ZIYj1Zok76VyU45zwAPdRZLnLgAQZoNAvK6qBYVaNETB1dJfpViwaC-0vI2_NsBRA_hHcOYfKDdOIKUOoIZB5S328HS-vX_q8_oU-SSUwpfSlmX0BI5g323j01gpbph0dC1z0H04dBtfEPEKqQjuGd_AePAOURajZX-CtVOp3yf9yNuVajU0exlGMZ7g4nwD5S7kow4UlNxQQGFuNPFTMWOujXLG56Ro6K5pgtPoX_dhMbKnuBDbDGBzDoys14VN67HO31HG3UHJtP7_xfCN6-G6UZBXYjjCHlQ; xq_r_token=ad6a9637058304802a23f5f5607e62a4b12f49cb; Hm_lvt_1db88642e346389874251b5a1eded6e3=1739967845,1740056743,1741351239,1741505095; HMACCOUNT=1D1DA734BA99746D; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1741505167; ssxmod_itna=eqRhBKiKD50IzmDhaDcCD0iDIxIxYKDO7DzxC5iOsDuP4jKidoDUiHPbtCDiuiPFpxNFnEWhCDBu5oDSxD=7DK4GTmG6kh2KO4FiO+qeKi3rpK7WUk5Sx1zAnHPmArH/CScgYxB3DEx06tbYvxxYAEDBYD74G+DDeDiO3Dj4GmDGA3deDFCmbQcnrerxDwDB=DmqG2i2rDm4DfDDd5HMjY2DDl0GHQ77heDYP5XjNWrraDALwd57D5x0UaDBL3IKq5xDtf6KwtXmOvqKoe=cWDtqD986RVW1IYVQu4qIj1i3h1YEeKYrU9K04Y08Cw/bi5YDi9hGSi5YTkfGqBaKnwr95oDiTHn+ZAxmACAk1tf1XwedY5jE=BTouhe1ixv2QdYQIQ5l05Dox7Ddd7Qa0D=753A4q8D7iDD; ssxmod_itna2=eqRhBKiKD50IzmDhaDcCD0iDIxIxYKDO7DzxC5iOsDuP4jKidoDUiHPbtCDiuiPFpxNFnEWxbD8+WEpmFtDT+t=Rcjn+CllxQxI1dFQ08ux+2YD"
    }

    response = requests.get(url, headers=headers,params=params)
    response.encoding = "utf-8"
    if response.status_code == 200:
        
        data = response.text
        json_data = json.loads(data)
        get_data = json_data.get("data").get('items')
        # print(get_data)
        get_title = ["code","name","percent","current"]
        # 列名中英文对照字典
        columns_chinese = {
            "code": "股票代码",
            "name": "股票名称",
            "percent": "涨跌幅",
            "current": "当前股价"
        }
        df = pd.DataFrame(get_data)
        df['code'] = df['code'].apply(lambda x: x[2:] if isinstance(x, str) and len(x) > 2 else x)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_filename = os.path.join(script_dir, "雪球热股.csv")
        
        df = df[get_title]
        # # 修改DataFrame的列名为中文
        df.rename(columns=columns_chinese, inplace=True)
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print("雪球热股数据获取完成")
    else:
        print("请求失败，状态码：", response.status_code)


# 获取淘股吧热股
def get_tgb_hot():
    url = "https://www.tgb.cn/new/nrnt/getNoticeStock?type=H"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("开始获取淘股吧热股")
        data = response.text
        json_data = json.loads(data)
        get_data = json_data.get("dto")
                # 提取gnName
        for record in get_data:
            # 确保 gnList 是可迭代的（即不是 None）
            gn_names = [item.get('gnName', '') for item in (record.get('gnList') or [])]
            record['gnNamesCombined'] = ','.join(gn_names)  # 将所有gnName连接成一个字符串

        df = pd.DataFrame(get_data)[0:20]
        get_title = ["fullCode","stockName","ranking","remark",'gnNamesCombined',"linkingBoard"]
        columns_chinese = {
            "fullCode": "股票代码",
            "stockName": "股票名称",
            "ranking": "排名",
            "remark":"题材",
            'gnNamesCombined':"详情",
            "linkingBoard":"市场表现"
            }
        df = df[get_title]
        df['fullCode'] = df['fullCode'].apply(lambda x: x[2:] if isinstance(x, str) and len(x) > 2 else x)
        df.rename(columns=columns_chinese, inplace=True)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_filename = os.path.join(script_dir, "淘股吧热股.csv")
        df.to_csv(csv_filename, index=False)
        print("淘股吧热股获取成功")
    else:
        print("请求失败，状态码为：", response.status_code)


def start_get_data():
    print("开始获取数据")
    get_ths_hot_data()
    get_dfcf_hot()
    get_xueqiuhot_data()
    get_tgb_hot()
    print("数据获取完成")

start_get_data()
