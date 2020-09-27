import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
import xlwt
import threading #线程模块
import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox

### 函数一
def getAcademy_list(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' 
                                 'Chrome/83.0.4103.61 Safari/537.36'}
    req = requests.get(url,headers=headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,'html.parser')
    academy = soup.find_all('ul',class_='coll-list')
    academy_list = academy[0].find_all('li')
    aca_list=[]
    for item in academy_list:
        academy_dict={}
        for academy_id in item.find_all('a'):
            academy_dict['学院id'] = academy_id['id'][3:]
            academy_dict['学院名称']=academy_id.em.string
            aca_list.append(academy_dict)
    return(pd.DataFrame(aca_list))

url='http://faculty.hust.edu.cn/xylb.jsp?urltype=tree.TreeTempUrl&wbtreeid=1003'
academyandID=getAcademy_list(url)
academyandID.to_excel('函数一.xls')

### 函数二
    def getCollegeTeacherInfo(collegeId,j):
        # 先获取教师人数
        totalNum = getCollegeTeachersNum(collegeId)
        # 浏览器头部
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/83.0.4103.61 Safari/537.36'}
        # 表单提交参数
        params = {'collegeid': collegeId,
                  'disciplineid': 0,
                  'pageindex': 1,
                  'pagesize': totalNum,
                  'rankid': 0,
                  'honorid': 0,
                  'py': '',
                  'viewmode': 8,
                  'viewid': 66517,
                  'siteOwner': 1391599222,
                  'viewUniqueId': 66517,
                  'showlang': '',
                  'type': 'collgeteacher'}
        req = requests.get("http://faculty.hust.edu.cn/system/resource/tsites/asy/asyqueryteacher.jsp?",
                           params=params,
                           headers=headers)
        req.encoding = 'utf-8'
        teachersData = eval(req.text)["teacherData"]
        # 爬取各自个人主页中的详细有关信息
        teacherInfoList = []
        teacherInfoList.append({'姓名': teachersData[j]['name'], "个人主页": teachersData[j]['url'], '入职年份': '',
                                    '职称': teachersData[j]['gtutor'], '毕业院校': '', '性别': '',
                                    '学科': '', '科研项目信息': '', '论文发表信息': ""})
            # 存在某些教师个人主页没有数据或者网页非模板
        try:
            req = requests.get(teachersData[j]['url'], headers=headers)
            req.encoding = 'utf-8'
            soup = BeautifulSoup(req.text.replace("</br>", ""), 'html.parser')
            info = soup.find('div', class_='cont').p.get_text().strip()
            patt = re.compile("(.*)：(.*)")  # 正则
                # 通过循环移除已匹配项来获得多个正则匹配项
            m = patt.search(info)
            while m:
                if m.group(1) in teacherInfoList[-1].keys():
                    teacherInfoList[-1].update({m.group(1): m.group(2)})
                info = info.replace(m.group(), '')
                m = patt.search(info)
                # 获取入职年份（个人主页开通年份）
                # 模拟提交表单数据
            data = {'timeformat': 'yyyy-MM-dd&zh',
                        'teacherid': teachersData[j]['teacherId'],
                        'homepageid': 140721,
                        'ac': 'gethomepageopentime'}
            timeReq = requests.post("http://faculty.hust.edu.cn/system/resource/tsites/latestupdatetime.jsp",
                                        data=data, headers=headers)
            teacherInfoList[-1].update({"入职年份": eval(timeReq.text)['year']})
                # 获取科研成果
            researchUrl = soup.find_all("li", class_="fNiv")
            for url in researchUrl:
                if url.a.string == "科学研究":
                    researchUrl = url.a.get("href")
                    break
            researchReq = requests.get("http://faculty.hust.edu.cn" + researchUrl)
            researchReq.encoding = 'utf-8'
            researchSoup = BeautifulSoup(researchReq.text, 'html.parser')
            researchDiv = researchSoup.find_all('div', class_="cont")
            researchProjectParagraph = researchDiv[5].find_all('p')
            researchProject = ""  # 科研项目信息
                # 对于某些没有科研项目信息的跳过
            try:
                for i in range(len(researchProjectParagraph)):
                    researchProject += "[" + str(i + 1) + "] " + researchProjectParagraph[i].string.strip() + ";"
                teacherInfoList[-1].update({'科研项目信息': researchProject})
            except:
                pass
            paperProjectParagraph = researchDiv[2].find_all('p')
            paperProject = ""  # 论文发表信息
            for i in range(len(paperProjectParagraph)):
                paperProject += "[" + str(i + 1) + "] " + paperProjectParagraph[i].string.strip() + ";"
            teacherInfoList[-1].update({'论文发表信息': paperProject})
        except:
            pass  # 特殊网页模板或者网页故障的跳过
        return teacherInfoList

teacher3=getCollegeTeacherInfo(2288,2)
pd.DataFrame(teacher3).to_excel('函数二.xls')

### 函数三
def getCollegeTeachersNum(collegeId):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/83.0.4103.61 Safari/537.36'}
        # 表单提交参数
    params = {'collegeid': collegeId,
                'disciplineid': 0,
                'pageindex': 1,
                'pagesize': 1,
                'rankid': 0,
                'honorid': 0,
                'py': '',
                'viewmode': 8,
                'viewid': 66517,
                'siteOwner': 1391599222,
                'viewUniqueId': 66517,
                'showlang': '',
                'type': 'collgeteacher'}
    req = requests.get("http://faculty.hust.edu.cn/system/resource/tsites/asy/asyqueryteacher.jsp?",
                         params=params,
                         headers={'Connection':'close'})
    req.encoding = 'utf-8'
    pat = re.compile(r'"totalnum":[0-9]+')
    totalNum = int(pat.search(req.text).group()[11:])  # 正则表达式筛出学院教师数
    return totalNum

collegeId = academyandID['学院id']
num = []
for i in collegeId:
    num.append(getCollegeTeachersNum(collegeId=i))

total_num={'教师人数':num}
pd.concat([academyandID,pd.DataFrame(total_num)],axis=1).to_excel('函数三.xls')


### 函数四
def getCollegeTeacherPage(collegeId):
    totalNum = getCollegeTeachersNum(collegeId)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/83.0.4103.61 Safari/537.36'}
    params = {'collegeid': collegeId,
                  'disciplineid': 0,
                  'pageindex': 1,
                  'pagesize': totalNum,
                  'rankid': 0,
                  'honorid': 0,
                  'py': '',
                  'viewmode': 8,
                  'viewid': 66517,
                  'siteOwner': 1391599222,
                  'viewUniqueId': 66517,
                  'showlang': '',
                  'type': 'collgeteacher'}
    req = requests.get("http://faculty.hust.edu.cn/system/resource/tsites/asy/asyqueryteacher.jsp?",
                           params=params,
                           headers=headers)
    req.encoding = 'utf-8'
    teachersData = eval(req.text)["teacherData"]
    teacherInfoList = []
    for j in range(len(teachersData)):
        teacherInfoList.append({'姓名': teachersData[j]['name'], "个人主页": teachersData[j]['url']})
        try:
            req = requests.get(teachersData[j]['url'], headers=headers)
            req.encoding = 'utf-8'
            soup = BeautifulSoup(req.text.replace("</br>", ""), 'html.parser')
            info = soup.find('div', class_='cont').p.get_text().strip()
            patt = re.compile("(.*)：(.*)")
            m = patt.search(info)
            while m:
                if m.group(1) in teacherInfoList[-1].keys():
                    teacherInfoList[-1].update({m.group(1): m.group(2)})
                info = info.replace(m.group(), '')
                m = patt.search(info)
        except:
            pass  # 特殊网页模板或者网页故障的跳过
    return teacherInfoList

collegeId = academyandID['学院id']

info=pd.DataFrame()
for i in collegeId:
    id={'学院id':[i]}
    df_id=pd.DataFrame(id)
    df_info=pd.concat([df_id,pd.DataFrame(getCollegeTeacherPage(i))],axis=1)
    info = pd.concat([info,df_info])

info.to_excel('函数四.xls')
