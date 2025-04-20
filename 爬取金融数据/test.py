import requests
import re
import json
import pandas as pd 
from datetime import datetime,timedelta
import os
import sys
import io
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

get_dfcf_hot()