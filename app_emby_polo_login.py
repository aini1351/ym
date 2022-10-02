'''
new Env('POLO登录')
'''
import time
import random
from requests import post, get
from sendNotify import send
from os import environ
from hashlib import md5
from sys import stdout, exit
#from datetime import datetime


def print_now(content):
    print(content)
    stdout.flush()


account = environ.get('emby_polo') if environ.get('emby_polo') else ''
url = environ.get('emby_polo_url') if environ.get('emby_polo_url') else ''
if account == '':
    print_now('未填写账号密码，退出')
    exit(0)
accountArr = account.split('&')

if url == '':
    print_now('未填写url，使用脚本内置')
    url = 'http://cu.poloemby.xyz:8088'

def encrypt_md5(s):
    # 创建md5对象
    new_md5 = md5()
    # 这里必须用encode()函数对字符串进行编码，不然会报 TypeError: Unicode-objects must be encoded before hashing
    new_md5.update(s.encode(encoding='utf-8'))
    # 加密
    return new_md5.hexdigest()

def sjs(a, b):
    return random.randint(a, b)



class emby_polo:
    def __init__(self, usr, pwd, url):
        self.url = url
        self.usr = usr
        self.pwd = pwd
        self.headers ={
            'Host': url.replace('http://', ''),
            'Proxy-Connection': 'keep-alive',
            'Content-Length': '25',
            'accept': 'application/json',
            'DNT': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': url,
            'Referer': url + '/web/index.html',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        self.deviceid = encrypt_md5(usr)[0:8] + '-' + encrypt_md5(usr)[8:12] + '-' + encrypt_md5(usr)[12:16] + '-' + encrypt_md5(usr)[16:20] + '-' + encrypt_md5(usr)[20:32]
    
    def login(self):
        url = self.url + f'/emby/Users/authenticatebyname?X-Emby-Client=Emby+Web&X-Emby-Device-Name=Chrome+Windows&X-Emby-Device-Id={self.deviceid}&X-Emby-Client-Version=4.7.3.0'
        data = {
            'Username': self.usr,
            'Pw': self.pwd
        }
        headers = self.headers
        #print(headers, data, url)
        req = post(url, data = data, headers = headers)
        #print(req.json())
        try:
            self.token = req.json()['AccessToken']
            self.Id =  req.json()['User']['Id']
            print_now('获取token成功：' + self.token)
            msg.append('登陆成功')
        except:
            req.encoding = 'utg-8'
            print_now(req.text)
            msg.append(req.text)

    def view(self):
        url = self.url + f'/emby/Users/{self.Id}/Views?X-Emby-Client=Emby%20Web&X-Emby-Device-Name=Chrome%20Windows&X-Emby-Device-Id={self.deviceid}&X-Emby-Client-Version=4.7.3.0&X-Emby-Token={self.token}'
        headers = {
            'accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'DNT': '1',
            'Host': self.url.replace('http://', ''),
            'Proxy-Connection': 'keep-alive',
            'Referer': url + '/web/index.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        }
        #print(url,headers)
        req = get(url, headers = headers)
        
        #print(req.json())
        try:
            fl = req.json()['TotalRecordCount']
            print_now('获取到总类别数：' + str(fl))
            msg.append('总类别数：' + str(fl))
        except:
            req.encoding = 'utf-8'
            print_now(req.text)
            msg.append(req.text)
    def main(self):
        self.login()
        time.sleep(sjs(10,1000))
        self.view()
            
if __name__  == '__main__':
    msg = []
    for i in accountArr:
        print_now('\n********开始账号' + str(accountArr.index(i) + 1) + '：' + i.split('@')[0] + '********\n')
        msg.append('\n****账号'  + str(accountArr.index(i) + 1) + '：' + i.split('@')[0] + '****\n')
        emby_polo(i.split('@')[0], i.split('@')[1], url).main()
        sj = sjs(100,500)
        print_now('随机等待' + str(sj) + '秒')
        time.sleep(sj)
    msg.append('当前访问url：' + url)
    send('POLO登录', '\n'.join(msg))
