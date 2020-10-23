import re
import time # 控制爬虫的时间
import requests
import pandas as pd 
from bs4 import BeautifulSoup
import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import selenium.webdriver.support.ui as ui

dat = pd.read_excel('./datUrl.xlsx') #读取学院及网址
URL = dat['网址']
browser = webdriver.Firefox()
NameUrl = pd.DataFrame()
###Step1: 对学院网址循环，从而得到每个老师的主页网址
for k in range(len(dat)):
    url = URL[k]
    #browser = webdriver.Firefox()
    browser.get(url)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find('ul',class_="list1 clearfix")
    #c = soup.find_all('ul','list1 clearfix')
    collegeListLabel = content.find_all('a') # 选择在职
    nameUrlDict = []  # 学院-url字典
    for i in range(len(collegeListLabel)): #前两行与学院信息无关，故剔除
        if  "http://faculty.zuel.edu.cn" in str(collegeListLabel[i]): #筛选出学院信息
            message = str(collegeListLabel[i])
            mycollege = dat['学院名称'][k]
            myname = re.findall(r".*>(.*)<",message)[0]
            myurl = eval(re.findall(r".*href=(.*) target",message)[0])#去掉斜杠
            nameUrlDict.append({'学院':mycollege,'姓名':myname,'教师主页':myurl})
        nameUrl = pd.DataFrame(nameUrlDict)
    NameUrl = NameUrl.append(nameUrl)

NameUrl.to_excel('../data/CollegeNameUrlOn-job.xlsx')#所有在职人员的学院，姓名和个人主页
len(NameUrl['学院'].unique())#检查学院个数是否为15个
