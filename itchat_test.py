# encoding:utf-8
import requests
api = "https://sc.ftqq.com/SCU112862T426d095c3def7b77bb50805be619c12a5f5841522f487.send"
title = u"紧急通知"
content = """
#家中老人突发状况，家庭急救机器人已出动！
##请尽快确认情况
"""
data = {
   "text": title,
   "desp": content
}
req = requests.post(api, data=data)
