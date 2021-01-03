#!/usr/bin/python
# -*- coding: utf-8 -*-
import cv2
import socket
import time
import numpy as np
import time
import requests
import requests
import json
from threading import Timer
from PIL import Image, ImageDraw, ImageFont
 # 处理图像的库，ImageFont 存储字体
i=0
framenumber=0
headers = {'api-key' :'ns80VmoAnuQHO=Xbi9gT1m52Ot4= '}
data = {'datastreams':[{'id':'temperature', 'datapoints':[{'value':11}]}]}
jdata = json.dumps(data)
puturl = 'https://api.heclouds.com/devices/635465449/datapoints'
get_mult_url = 'https://api.heclouds.com/devices/635465449/datapoints'
data2=0
#从onenet平台上获取心率数据
def http_get():
    '''
    获取数据
    '''
    r = requests.get(url=get_mult_url, headers=headers)
    b=json.loads(r.text)#解析数据
    #data2=b['data'][0]['datastreams'][0]['datapoints'][0][value]
    data2=b['data']['datastreams'][2]['datapoints'][0]['value']
    #print(data2)
    #print(b)
   # print(type(data2))
   # Timer(1.0,http_get).start()
#t=Timer(1.0,http_get)
#t.start()
#http_get()
#向老人家属微信发送紧急求救消息
def emergence():
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
    
def cv2ImgAddText(img, text, left, top, textColor=(0, 255, 0), textSize=20):
    if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img)
    # 字体的格式
    #fontStyle = ImageFont.truetype(
        #"font/simsun.ttc", textSize, encoding="utf-8")
    # 绘制文本
    draw.text((left, top), text, textColor, font=fontStyle)
    # 转换回OpenCV格式
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

cam = cv2.VideoCapture(0) #读取摄像头
cam.set(3, 640) # set video widht
cam.set(4, 480) # set video height
scale=0

#背景减除
# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(1,1))
fg = cv2.createBackgroundSubtractorMOG2()  
# fgbg = cv2.createBackgroundSubtractorKNN(detectShadows = True)
# fg = cv2.bgsegm.createBackgroundSubtractorGMG()
# fg =  cv2.createBackgroundSubtractorKNN()
# history = 5
# fgbg.setHistory(history)
# 树莓派的通信
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(('192.168.43.150',6666))  #绑定ip和端口号（IP为发送数据的树莓派ip，端口号自己指定）
s.listen(5)
cc, address = s.accept()      #等待别的树莓派接入
start_time = time.time()
while True:
    http_get()
    time.sleep(0.09)
    ret,img = cam.read()
    framenumber = framenumber + 1
    if framenumber==10:
        framenumber=0

    if not ret:break

    #canny 边缘检测
    image= img.copy()
    blurred = cv2.GaussianBlur(image, (3, 3), 0)
    gray = cv2.cvtColor(blurred, cv2.COLOR_RGB2GRAY)
    xgrad = cv2.Sobel(gray, cv2.CV_16SC1, 1, 0) #x方向梯度
    ygrad = cv2.Sobel(gray, cv2.CV_16SC1, 0, 1) #y方向梯度
    edge_output = cv2.Canny(xgrad, ygrad, 50, 150)
    # edge_output = cv2.Canny(gray, 50, 150)
    #cv2.imshow("Canny Edge", edge_output)

    # edge_output = cv2.dilate(edge_output,cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8,3)),iterations=1) 
    #背景减除
    fgmask = fg.apply(edge_output)
    # cv2.imshow("fgmask", fgmask)
    
    #闭运算
    hline = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 4), (-1, -1)) #定义结构元素，卷积核
    vline = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 1), (-1, -1))
    result = cv2.morphologyEx(fgmask,cv2.MORPH_CLOSE,hline)#水平方向
    result = cv2.morphologyEx(result,cv2.MORPH_CLOSE,vline)#垂直方向
    #cv2.imshow("result", result)


    # erodeim = cv2.erode(th,cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3)),iterations=1)  # 腐蚀 
    dilateim = cv2.dilate(result,cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4,4)),iterations=1) #膨胀
    # cv2.imshow("dilateimfgmask", dilateim)
    # dst = cv2.bitwise_and(image, image, mask= fgmask)
    # cv2.imshow("Color Edge", dst)
    #查找轮廓
    image,contours, hier = cv2.findContours(dilateim, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 
    for c in contours:
        if cv2.contourArea(c) > 1200:
            mu = cv2.moments(c, False)
            mc = [mu['m10'] / mu['m00'], mu['m01'] / mu['m00']]   #获取质心位置
           # print(mc)
            (x,y,w,h) = cv2.boundingRect(c)
            if scale==0:scale=-1;break
            scale = w/h
            cv2.putText(image, "scale:{:.3f}".format(scale), (10, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.drawContours(image, [c], -1, (255, 0, 0), 1)
            cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),1)
            image = cv2.fillPoly(image, [c], (255, 255, 255)) #填充
            P=np.zeros([11,6])
            P[framenumber,0]=x
            P[framenumber,1]=y
            P[framenumber,2]=w
            P[framenumber,3]=h
            P[framenumber,4]=mc[0]
            P[framenumber,3]=mc[1]
    #根据人体比例判断       
    if scale >0 and scale <1 :
        msg='1'#working
        print(msg)
        cc.send(msg.encode('utf-8'))
        #img = cv2ImgAddText(img, "Walking 行走中", 10, 20, (255, 0 , 0), 30)#行走中
        #cv2.putText(img, "Walking 行走中", (10, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)#行走中
    if scale >0.9 and scale <2:
        msg='2'#跌倒中
        print(msg)
        #cc.send(msg.encode('utf-8'))
        #img = cv2ImgAddText(img, "Falling 中间过程", 10, 20, (255, 0 , 0), 30)#跌倒中
        #cv2.putText(img, "Falling 跌倒中", (10, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)#跌倒中
        #综合判断信息
    if scale >2 and (P[framenumber,4]-P[np.abs(framenumber-10),4])**2+(P[framenumber,5]-P[np.abs(framenumber-10),5]**2)>40 or data2>=130 :
        msg='3'
        #img = cv2ImgAddText(img, "Falled 跌倒了", 10, 20, (255, 0 , 0), 30)#跌倒了
        #cv2.putText(img, "Falled 跌倒了", (10, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)#跌倒了
        print(msg)
        cc.send(msg.encode('utf-8'))
        #emergence()
        emergence()
        #i+=1
        #if i>=5:
        cc.send(msg.encode('utf-8'))
        #i=0
        
    #cv2.imshow('test',image)
    #cv2.imshow('image',img)



    k=cv2.waitKey(1)&0xFF
    if k==27:
        break

cv2.destroyAllWindows()
s.close()

