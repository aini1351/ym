#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@limoruirui https://github.com/limoruirui
# @Time : 2022/11/11 10:42
# -------------------------------
# cron "*/30 10-20 * * *"
# const $ = new Env('某营业厅直播抽奖');
"""
1. 脚本仅供学习交流使用, 请在下载后24h内删除
2. 环境变量说明:
    必须  TELECOM_PHONE : 电信手机号
    必须  TELECOM_PASSWORD : 电信服务密码
3. 必须登录过 电信营业厅 app的账号才能正常运行
"""
import requests
from random import randint
from re import findall
from time import mktime, strptime
from requests import post, get
from datetime import datetime
from base64 import b64encode
from os import environ
from tools.tool import timestamp, get_environ
from app_telecom_task import ChinaTelecom
from sendNotify import send
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
phone_nums = environ.get("TELECOM_PHONE") if environ.get("TELECOM_PHONE") else ""
foods = int(float(get_environ("TELECOM_FOOD", 10, False)))
if phone_nums.find('\n') != -1:
    phone_numArr = phone_nums.split('\n')
else:
    phone_numArr = phone_nums

class TelecomLotter:
    def __init__(self, phone, password):
        self.msg = ''
        self.phone = phone
        chinaTelecom = ChinaTelecom(phone, password)
        chinaTelecom.init()
        chinaTelecom.author()
        self.authorization = chinaTelecom.authorization
        self.ua = chinaTelecom.ua
        self.token = chinaTelecom.token

    def get_action_id(self, liveId):
        url = "https://appkefu.189.cn:8301/query/getWaresList"
        body = {
            "headerInfos": {
                "code": "getWaresList",
                "timestamp": datetime.now().__format__("%Y%m%d%H%M%S"),
                "broadAccount": "",
                "broadToken": "",
                "clientType": "#9.6.1#channel128#samsung SM-G9860#",
                "shopId": "20002",
                "source": "110003",
                "sourcePassword": "Sid98s",
                "token": self.token,
                "userLoginName": self.phone
            },
            "content": {
                "attach": "test",
                "fieldData": {
                    "limit": "",
                    "page": "1",
                    "liveId": liveId
                }
            }
        }
        headers = {
            "User-Agent": self.ua,
            "authorization": self.authorization
        }
        data = post(url, headers=headers, json=body).json()
        try:
            for waresInfo in data["responseData"]["data"]["waresInfos"]:
                print(waresInfo["title"])
                if "转盘" in waresInfo["title"] :
                    active_code = findall(r"active_code\u003d(.*?)\u0026", waresInfo["link"])[0]
                    return active_code
            return None
        except:
            return None
    def lotter(self, liveId, period):
        active_code = self.get_action_id(liveId)
        if active_code is None:
            print(f"此直播间无抽奖活动, 退出")
            return
        url = "https://xbk.189.cn/xbkapi/active/v2/lottery/do"
        body = {
            "active_code": active_code,
            "liveId": liveId,
            "period": period
        }
        headers = {
            "User-Agent": self.ua,
            "authorization": self.authorization
        }
    
        data = post(url, headers=headers, json=body).json()
        #print(data)
        
        if data['data']:
            self.msg += f'\n账户 {self.phone} 抽奖结果：\n'
            self.msg += data['data']['title'] + '\n'
        return self.msg

def main(phone, password):
    url = "https://xbk.189.cn/xbkapi/lteration/index/recommend/anchorRecommend?provinceCode=21"
    random_phone = f"1537266{randint(1000, 9999)}"
    headers = {
        "referer": "https://xbk.189.cn/xbk/newHome?version=9.4.0&yjz=no&l=card&longitude=%24longitude%24&latitude=%24latitude%24&utm_ch=hg_app&utm_sch=hg_sh_shdbcdl&utm_as=xbk_tj&loginType=1",
        "user-agent": f"CtClient;9.6.1;Android;12;SM-G9860;{b64encode(random_phone[5:11].encode()).decode().strip('=+')}!#!{b64encode(random_phone[0:5].encode()).decode().strip('=+')}"
    }
    data = get(url, headers=headers).json()
    #print(data)
    mainmsg = ''
    if data["code"] == 0:
        for liveInfo in data["data"]:
            #print(timestamp(True))
            #print(int(mktime(strptime(liveInfo["start_time"], "%Y-%m-%d %H:%M:%S"))))
            mainmsgs = ''
            
            if 17400 > timestamp(True) - int(mktime(strptime(liveInfo["start_time"], "%Y-%m-%d %H:%M:%S"))) > 0:
                print(f"直播间 {liveInfo['nickname']}")
            
                mainmsgs = TelecomLotter(phone, password).lotter(liveInfo["liveId"], liveInfo["period"])
                if mainmsgs:
                    mainmsg += "\n直播间 {liveInfo['nickname']}：\n"
                    mainmsg += mainmsgs

    if mainmsg:
        return mainmsg



if __name__ == "__main__":
    print('共' + str(len(phone_numArr)) + '个账户')
    c = 0
    l = []
    msg = ''
    #shuffle(phone_numArr)
    print(phone_numArr)
    for i in phone_numArr:
        c = c + 1
        print('\n账户' + str(c) + '：' + str(i) + '\n')
        '''
        p = threading.Thread(target=ChinaTelecom(i).main(msg), args=(i,))
        l.append(p)
        p.start()
 '''
        if '@' in i and len(i.split('@')[1]) > 4:
            m = ''
            m = main(i.split('@')[0], i.split('@')[1])
            if m:
                msg += m
        else:
            print_now('当前账户未填密码，无法抽奖，退出')
            #msg += ChinaTelecom(i,'').main()

    if msg:
        send("电信app直播间抽奖", msg)
    exit(0)
    

