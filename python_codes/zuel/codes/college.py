###从各个学院官网爬取

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


###(1)马克思主义
dat = pd.read_excel('./datUrlDetail.xlsx')
collegeurl = dat
url = dat['网址'][0]
browser = webdriver.Firefox()
browser.get(url)
html = browser.page_source
soup = BeautifulSoup(html, 'html.parser')
content = soup.find('div',class_="wp_articlecontent")
collegeListLabel = content.find_all('a') # 选择教师

nameUrlList = [] # 学院-url列表  
for i in range(len(collegeListLabel)):
#for i in range(5):
    myurl = eval(re.findall(r".*=(.*) s",str(collegeListLabel[i])[7:70])[0])
    mycollege = dat['学院名称'][0]
    message1 = str(collegeListLabel[i])[-24:-2].replace('</','kkk',1)
    message2 = message1.replace('>','ooo',1)
    message_name = re.findall(r".*ooo(.*)kkk",message2)[0]
    if message_name == '':
        message = str(collegeListLabel[i]).replace('"><','"ooo',1)
        myname = eval(re.findall(r".*textvalue=(.*)ooo",message)[0])
        if len(myname)==1:
            print(myname,myurl)
    else:
         myname = message_name
         if len(myname)==1:
            print(myname,myurl)
    nameUrlDict = {'学院':mycollege,'姓名':myname,'教师主页':myurl}
    nameUrlList.extend([nameUrlDict])
nameUrlFrame = pd.DataFrame(nameUrlList)
nameUrlFrame[nameUrlFrame['姓名'] == '溪']['姓名']=['高晓溪'] #修改名字不全的教师 
nameUrlFrame.to_excel('./college/ma.xlsx')

###（2）哲学院
dat = pd.read_excel('./datUrlDetail.xlsx')
url = dat['网址'][1]
browser = webdriver.Firefox()
NameUrl = pd.DataFrame()
browser.get(url)
html = browser.page_source
soup = BeautifulSoup(html, 'html.parser')
collegeListLabel = soup.find_all('span',class_="column-news-title")
nameUrlList = [] # 学院-url列表  
for i in range(len(collegeListLabel)):
    myname = re.findall(r".*>(.*)<",str(collegeListLabel[i])[-18:-10])[0]
    myurl = "http://zxy.zuel.edu.cn" + eval(re.findall(r".*href=(.*) tar",str(collegeListLabel[i]))[0])
    mycollege = dat['学院名称'][1]
    nameUrlDict = {'学院':mycollege,'姓名':myname,'教师主页':myurl}
    nameUrlList.extend([nameUrlDict])
nameUrlFrame = pd.DataFrame(nameUrlList)
nameUrlFrame.to_excel('./college/zhe.xlsx')

###(3)经济学院

dat = pd.read_excel('./datUrlDetail.xlsx')
url = dat['网址'][2]
browser = webdriver.Firefox()
browser.get(url)
html = browser.page_source
soup = BeautifulSoup(html, 'html.parser')
collegeListLabel = soup.find_all('a') #索引从59到130 range(59,131)

nameUrlList = [] # 学院-url列表  
for i in range(59,131):
    message1 = str(collegeListLabel[i])[-30:-5].replace(';">','ooo',1)
    message2 = message1.replace('</sp','kkk',1)
    myname = re.findall(r".*ooo(.*)kkk",message2)[0]
    myurl = eval(re.findall(r".*href=(.*) s",str(collegeListLabel[i])[:67])[0])
    mycollege = dat['学院名称'][2]
    nameUrlDict = {'学院':mycollege,'姓名':myname,'教师主页':myurl}
    nameUrlList.extend([nameUrlDict])
nameUrlFrame = pd.DataFrame(nameUrlList)
nameUrlFrame.to_excel('./college/economy.xlsx')

###(4) 财政税务学院

dat = pd.read_excel('./datUrlDetail.xlsx')
#url = dat['网址'][3]
url = "http://csxy.zuel.edu.cn/7121/list.htm"
browser = webdriver.Firefox()
browser.get(url)
html = browser.page_source
soup = BeautifulSoup(html, 'html.parser')
content = soup.find('div',id="divShowContent")
collegeListLabel = content.find_all('a') #索引从59到130 range(59,131)
nameUrlList = [] # 学院-url列表  
for i in range(len(collegeListLabel)):
    myname = collegeListLabel[i].get_text()
    myurl = collegeListLabel[i].get('href')
    mycollege = dat['学院名称'][3]
    nameUrlDict = {'学院':mycollege,'姓名':myname,'教师主页':myurl}
    nameUrlList.extend([nameUrlDict])
nameUrlFrame = pd.DataFrame(nameUrlList)
nameUrlFrame.to_excel('./college/caizheng.xlsx')

####Question 有多个页面，点下一页界面不会变化应该怎么弄？
##################################
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
req = requests.get(url=url,headers=headers)
req.encoding = 'utf-8'
soup = BeautifulSoup(req.text, 'html.parser')

soup.find_all('ul',class_="news_list clearfix")
soup.find('div',class_="txt")
####################################

###(5) 金融学院
dat = pd.read_excel('./datUrlDetail.xlsx')
url = dat['网址'][4]
browser = webdriver.Firefox()
browser.get(url)
html = browser.page_source
soup = BeautifulSoup(html, 'html.parser')
collegeListLabel = soup.find_all('span',class_="Article_Title")
nameUrlList = [] # 学院-url列表  
for i in range(len(collegeListLabel)):
    myname = collegeListLabel[i].get_text()
    myurl = "http://finance.zuel.edu.cn"+collegeListLabel[i].a.get('href')
    mycollege = dat['学院名称'][4]
    nameUrlDict = {'学院':mycollege,'姓名':myname,'教师主页':myurl}
    nameUrlList.extend([nameUrlDict])
nameUrlFrame = pd.DataFrame(nameUrlList)
nameUrlFrame.to_excel('./college/finance.xlsx')

###(6) 法学院 与学校一样

### (7) 刑事司法
def get_collegeListLabel(url):
    browser = webdriver.Firefox()
    browser.get(url)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    collegeListLabel = soup.find_all('span',class_="Article_Title")
    content = soup.find('table',class_="wp_article_list_table")
    collegeListLabel = content.find_all('a')
    nameUrlList = [] # 学院-url列表 
    for i in range(len(collegeListLabel)):
            myname = collegeListLabel[i].get_text()
            myurl = "http://cjs.zuel.edu.cn"+collegeListLabel[i].get('href')
            mycollege = dat['学院名称'][k][:-1]
            nameUrlDict = {'学院':mycollege,'姓名':myname,'教师主页':myurl}
            nameUrlList.extend([nameUrlDict])
    return nameUrlList

dat = pd.read_excel('./datUrlDetail.xlsx')
nameUrlList = []
for k in range(14,21):
    url = dat['网址'][k]
    nameUrlList.extend(get_collegeListLabel(url))
nameUrlFrame = pd.DataFrame(nameUrlList)
nameUrlFrame.to_excel('./college/xingshi.xlsx')

### (8)外国语

dat = pd.read_excel('./datUrlDetail.xlsx')
url = dat['网址'][21]
browser = webdriver.Firefox()
browser.get(url)
html = browser.page_source
soup = BeautifulSoup(html, 'html.parser')
content = soup.find('div',class_="wp_articlecontent")
collegeListLabel = content.find_all('a')
nameUrlList = [] # 学院-url列表  
for i in range(len(collegeListLabel)):
    myname = collegeListLabel[i].get_text()
    myurl = "http://wgyxy.zuel.edu.cn"+collegeListLabel[i].get('href')
    mycollege = dat['学院名称'][21]
    nameUrlDict = {'学院':mycollege,'姓名':myname,'教师主页':myurl}
    nameUrlList.extend([nameUrlDict])
nameUrlFrame = pd.DataFrame(nameUrlList)
nameUrlFrame.to_excel('./college/waiguoyu.xlsx')

###(9) 新闻与文化 教师主页与从学校爬的一样 所以不爬了

###（10）工商管理学院 同上

###（11）会计学院
dat = pd.read_excel('./datUrlDetail.xlsx')
url = dat['网址'][24]
browser = webdriver.Firefox()
browser.get(url)
html = browser.page_source
soup = BeautifulSoup(html, 'html.parser')
content = soup.find('div',class_="wp_articlecontent")
collegeListLabel = content.find_all('a')
nameUrlList = [] # 学院-url列表  
for i in range(len(collegeListLabel)):
    myname = collegeListLabel[i].get_text()
    myurl = collegeListLabel[i].get('href')
    mycollege = dat['学院名称'][24]
    nameUrlDict = {'学院':mycollege,'姓名':myname,'教师主页':myurl}
    nameUrlList.extend([nameUrlDict])
nameUrlFrame = pd.DataFrame(nameUrlList)
nameUrlFrame.to_excel('./college/kuaiji.xlsx')

###（12）公共管理学院
dat = pd.read_excel('./datUrlDetail.xlsx')
url = dat['网址'][25]
browser = webdriver.Firefox()
browser.get(url)
html = browser.page_source
soup = BeautifulSoup(html, 'html.parser')
content = soup.find('div',class_="wp_articlecontent")
collegeListLabel = content.find_all('a')
nameUrlList = [] # 学院-url列表  
for i in range(len(collegeListLabel)):
    myname = collegeListLabel[i].get_text()
    myurl = collegeListLabel[i].get('href')
    mycollege = dat['学院名称'][25]
    nameUrlDict = {'学院':mycollege,'姓名':myname,'教师主页':myurl}
    nameUrlList.extend([nameUrlDict])
nameUrlFrame = pd.DataFrame(nameUrlList)
nameUrlFrame.to_excel('./college/gonggongguanli.xlsx')

### (13)统计与数学学院

def get_collegeListLabel(url):
    browser = webdriver.Firefox()
    browser.get(url)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    collegeListLabel = soup.find_all('td',height="23",align="left")
    nameUrlList = [] # 学院-url列表 
    for i in range(len(collegeListLabel)):
        if "http" in collegeListLabel[i].a.get('href'):
            myurl = collegeListLabel[i].a.get('href')
        else:
            myurl = "http://tsxy.zuel.edu.cn"+collegeListLabel[i].a.get('href')
            myname = collegeListLabel[i].get_text()
            mycollege = dat['学院名称'][k][:-1]
            nameUrlDict = {'学院':mycollege,'姓名':myname,'教师主页':myurl}
            nameUrlList.extend([nameUrlDict])
    return nameUrlList

dat = pd.read_excel('./datUrlDetail.xlsx')
nameUrlList = []
for k in range(26,30):
    url = dat['网址'][k]
    nameUrlList.extend(get_collegeListLabel(url))
nameUrlFrame = pd.DataFrame(nameUrlList)
nameUrlFrame.to_excel('./college/tongshu.xlsx')

###(14)信息与安全工程学院
dat = pd.read_excel('./datUrlDetail.xlsx')
url = dat['网址'][30]
browser = webdriver.Firefox()
browser.get(url)
html = browser.page_source
soup = BeautifulSoup(html, 'html.parser')
content = soup.find('div',class_="wp_articlecontent")
collegeListLabel = content.find_all('a')
nameUrlList = [] # 学院-url列表  
for i in range(len(collegeListLabel)):
    myname = collegeListLabel[i].get_text()
    myurl = collegeListLabel[i].get('href')
    mycollege = dat['学院名称'][30]
    nameUrlDict = {'学院':mycollege,'姓名':myname,'教师主页':myurl}
    nameUrlList.extend([nameUrlDict])
nameUrlFrame = pd.DataFrame(nameUrlList)
nameUrlFrame.to_excel('./college/message.xlsx')

###(15) 文澜学院

def get_collegeListLabel(url):
    browser = webdriver.Firefox()
    browser.get(url)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find('div',id="wp_news_w2")
    collegeListLabel = content.find_all('a')
    nameUrlList = [] # 学院-url列表 
    for i in range(len(collegeListLabel)):
        if collegeListLabel[i].get('href') != '':
            if "http" in collegeListLabel[i].get('href'):
                myurl = collegeListLabel[i].get('href')
            else:
                myurl = "http://wls.zuel.edu.cn"+collegeListLabel[i].get('href')
                myname = collegeListLabel[i].get_text()
                mycollege = dat['学院名称'][31]
                nameUrlDict = {'学院':mycollege,'姓名':myname,'教师主页':myurl}
                nameUrlList.extend([nameUrlDict])
    return nameUrlList

dat = pd.read_excel('./datUrlDetail.xlsx')
nameUrlList = []
for k in range(1,4):
    url = dat['网址'][31][:-4]+str(k)+".htm"
    nameUrlList.extend(get_collegeListLabel(url))
nameUrlFrame = pd.DataFrame(nameUrlList)
nameUrlFrame.to_excel('./college/wenlan.xlsx')
