'''
new Env('tgbot签到')
https://apitruecaptcha.org/api.html
'''
import asyncio
import base64
import json
import re
import time
import random
import requests
import os
from datetime import datetime
from os import environ
from sendNotify import send
from sys import stdout, exit
from xpinyin import Pinyin
from telethon import TelegramClient, events

py = Pinyin() #转拼音
now = datetime.now()

API_ID1 = environ.get('api_id')	if environ.get('api_id') else '' #输入api_id，一个账号一项
API_HASH1 = environ.get('api_hash')	if environ.get('api_hash') else ''   #输入api_hash，一个账号一项
captcha_username = environ.get('captcha_username') if environ.get('captcha_username') else ''
captcha_pwd = environ.get('captcha_pwd') if environ.get('captcha_pwd') else ''

#session_name = API_ID[:]
CHANNEL_ID = ['@qweybgbot', '@EmbyPublicBot','@blueseamusic_bot']
if len(API_HASH1) == 0 or len(API_ID1) == 0:
    print('未填api_id或api_hash，退出')
    exit(0)
else:
    API_ID = API_ID1.split('&')
    API_HASH = API_HASH1.split('&')



def sj(a, b):
    return random.randint(a, b)

async def captcha_solver(dealcap):
    with open('./captcha.jpg', 'rb') as tp:
        base64data = base64.b64encode(tp.read())
        #print_now(base64data)
    captcha_url = 'https://api.apitruecaptcha.org/one/gettext'
    data = {
        "userid":captcha_username,
        "apikey":captcha_pwd,
        'case':'lower',
        "data":str(base64data.decode('utf-8'))
    }
    #print_now(str(base64data.decode('utf-8'))) #'data:image/jpeg;base64,' +  
    response = requests.post(url=captcha_url, json=data)
    print_now(response.json())

    if response.json()["result"]:
        solved_result = response.json()["result"]
    else:
        solved_result = '2b'
        print_now('识别图片验证码失败，输入2b尝试')
    if len(solved_result) != 2 and dealcap:
        print_now('识别结果过长，取最后两位尝试')
        solved_result = solved_result[-2:]
    return solved_result
    #return base64data





def print_now(content):
    print(content)
    stdout.flush()


async def main(api_id, api_hash, channel_id):
    MSG = '/checkin'
    async with TelegramClient("id_" + str(api_id), api_id, api_hash) as client:
        me = await client.get_me() #获取当前账号信息       
        if me.username not in ''.join(msg):
            print_now(me.first_name + ' @' + me.username)
            msg.append(me.first_name + ' @' + me.username + '\n')

        print_now('\n准备去签到:' + channel_id)
        msg.append('\n准备去签到:' + channel_id)
        await client.send_message(channel_id, MSG)
        @client.on(events.NewMessage(chats=channel_id))

        async def my_event_handler(event):
            global cishu
            cishu += 1
            print_now('当前第' + str(cishu) + '次尝试')
            print_now(event.message.text)
            time.sleep(sj(3,8))
            if cishu > 8:
                print_now('尝试次数已达到8次仍未成功，退出')
                msg.append('尝试次数已达到8次仍未签到成功')
                if channel_id == '@EmbyPublicBot':
                    await client.send_message(channel_id, '/cancel')
                await client.send_read_acknowledge(channel_id)
                await client.disconnect()
            # 根据button count 区分消息类型
            if "已经签到过" in event.message.text or "距离下次可签到" in event.message.text or '当前积分' in event.message.text or "已签过到" in event.message.text or "You have checkined today" in event.message.text:
                # 结束循环
                print_now('已签到，终止')
                
                if '积分' in event.message.text or '总分' in event.message.text or "your point" in event.message.text:
                    msg.append('已签到:')
                    print_now(event.message.text)
                    msg.append(event.message.text)
                    await client.send_read_acknowledge(channel_id) #退出运行
                    await client.disconnect()
                else:
                    await client.send_message(channel_id, '/userinfo') #查询分数

                
                
            elif 'KeyboardButtonCallback' in str(event.message): #计算签到
                buttons = event.message.reply_markup.rows[0].buttons
                print_now( event.message.reply_markup.rows[0])
                sz = re.findall(r'\d+', event.message.message)
                print_now(sz)
                sz[0] = int(sz[0])
                sz[1] = int(sz[1])
                mespin = py.get_pinyin(event.message.message)
                if 'jian' in mespin or '－' in mespin:
                    print_now('本次执行减法')
                    res = sz[0] - sz[1]
                elif 'jia' in mespin or '+' in mespin:
                    print_now('本次执行加法')
                    res = sz[0] + sz[1]
                elif 'cheng' in mespin or '*' in mespin or '×' in mespin:
                    print_now('本次执行×法')
                    res = sz[0] * sz[1]
                elif 'chu' in mespin or '/' in mespin or '÷' in mespin:
                    print_now('本次执行÷法')
                    res = sz[0] / sz[1]
                else:
                    res = 0
                print_now('计算结果：' + str(res))
                if res:
                    for button in buttons:
                        if int(button.text) == res:
                            print_now('点击提交正确答案按钮')
                            #await event.message.click(button)
                            time.sleep(sj(2,7))
                            await event.message.click(buttons.index(button))
                            
                    print_now('提交过正确答案，不清楚是否成功，终止')
                    msg.append('提交过正确答案，不清楚是否成功')
                    await client.send_read_acknowledge(channel_id)
                    await client.disconnect()
                    
                else:
                    print_now('没匹配到算法，重新获取')
                    time.sleep(sj(5,30))
                    await client.send_message(event.message.chat_id, MSG)
            elif "会话超时已取消" in event.message.text or "验证码错误" in event.message.text or "Wrong captcha code" in event.message.text or "Session canceled due to timeout" in event.message.text:
                await client.send_message(channel_id, MSG)
                        
            elif "输入签到验证码" in event.message.text or "输入错误或超时" in event.message.text or "输入验证码" in event.message.text or "Please input the captcha code" in event.message.text:  # 获取图像验证码
                if len(captcha_pwd) < 2 or len(captcha_username) < 2:
                    print_now('未填验证码识别账号信息，退出')
                    await client.send_read_acknowledge(channel_id)
                    await client.disconnect()
                await client.download_media(event.message.photo, "captcha.jpg")
                # 使用 TRUECAPTCHA 模块解析验证码
                if "输入验证码" in event.message.text or "Please input the captcha code" in event.message.text:
                    print_now('blue')
                    solved_result = await captcha_solver(0)  
                else:
                    print_now('终点')
                    solved_result = await captcha_solver(1)
                time.sleep(sj(4,10))
                print_now('输入验证码为：' + solved_result)
                await client.send_message(event.message.chat_id, solved_result)
                
                # 删除临时文件
                os.remove("captcha.jpg")
            # 是否成功签到
            elif '签到成功' in event.message.text or '你回答正确' in event.message.text or "Checkin successful" in event.message.text:
                msg.append(event.message.text)
                print_now(event.message.text)
                await client.send_read_acknowledge(channel_id)
                await client.disconnect()
            else :
                print_now('不知道咋回事，防止意外，退出')
                msg.append('出现意外，未签到')
                #time.sleep(sj(5,10))
                await client.send_read_acknowledge(channel_id)	#将机器人回应设为已读
                await client.disconnect()
            #await client.send_read_acknowledge(channel_id)	#将机器人回应设为已读
            #await client.disconnect()
        await client.start()
        await client.run_until_disconnected()    
        
if __name__ == "__main__":
    msg = []
    print('共' + str(len(API_ID)) + '个账户：' + API_ID1.replace('&', '  '))
    print('签到bot：' + '  '.join(CHANNEL_ID))
    zh = 0
    for i in API_ID:       
        zh += 1 
        print_now('\n\n开始执行账号' + str(zh) + '：' + str(i) + '：' '\n')
        msg.append('\n账号' + str(zh) + '：' + str(i) + '：' '\n')
        yc = sj(30,100)
        print_now('随机延迟' + str(yc) + '秒后开始执行')
        #time.sleep(yc)
        for j in CHANNEL_ID:
            if i == API_ID[0] and j == CHANNEL_ID[1]:
                continue
            cishu = 0     #每个账号尝试签到次数

            asyncio.run(main(i, API_HASH[API_ID.index(i)], j))
            #main(i, API_HASH[API_ID.index(i)], j)
            #break
    
    if int(now.strftime('%H')) > 12:
        print_now('当前小时为' + now.strftime('%H') + '发送通知。。。')
        send('tgbot签到', '\n'.join(msg))  
    else:
        print_now('当前小时为'+ now.strftime('%H') + '取消通知')
    exit(0)
