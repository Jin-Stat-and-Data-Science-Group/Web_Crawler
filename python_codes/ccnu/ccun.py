import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
data = {
	"input[pageNo]": "1",
	"input[pageSize]": "300",
	"input[sort][beginsName]": "asc",
	"input[mustWildcardFilter][teacherName-keyword]": "",
	"input[mustWildcardFilter][researchDirection-keyword]": "",
	"input[mustFilter][resumeType-keyword][]": "CH"
}
headers = {'Accept':'application/json, text/plain, */*',
           'Accept-Encoding':'gzip, deflate',
           'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
           'Cache-Control':'max-age=0',
           'Connection':'keep-alive',
           'Content-Length':'250',
           'Content-Type':'application/x-www-form-urlencoded',
           'Host':'faculty2.ccnu.edu.cn',
           'Origin':'http://faculty.ccnu.edu.cn',
           'Referer':'http://faculty.ccnu.edu.cn/ch/index',
           'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0'}
url = 'http://faculty2.ccnu.edu.cn/resume/searchResume?random=0.6490731693679087'
req = requests.post(url = url,data=data,headers = headers)
req.status_code
req.encoding = 'utf-8'

listDatas = json.loads(req.text)["listDatas"]
teacherinfolist = []
for i in range(len(json.loads(req.text)["listDatas"])):
    teacherinfolist.append({"姓名":listDatas[i]['_source']['nameChinese'],"工号":listDatas[i]['_source']['jobCode'],"学院":listDatas[i]['_source']['college'],"出生年月":listDatas[i]['_source']['birthDate'],"专业职称":listDatas[i]['_source']['jobTitle'],"教育背景":listDatas[i]['_source']['educationBackground']})

pd.DataFrame(teacherinfolist)[["姓名","工号","学院","出生年月","专业职称","教育背景"]].to_excel('./ccun_teacherinfolist.xlsx')










