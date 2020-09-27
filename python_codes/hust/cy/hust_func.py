import threading #线程模块
import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
import re           # 正则表达式
import requests     # 用于发送请求
import xlwt         # 读写EXCEL的模块
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np 


###Q1 第一个函数获取id和学院名称，根据37-49行

def getCollegeId(html):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/83.0.4103.61 Safari/537.36'}
        req = requests.get(html,headers=headers)
        req.encoding = 'utf-8'
        soup = BeautifulSoup(req.text, 'html.parser')
        collegeListLabel = soup.find('ul', class_="coll-list")  # 学院所在列表
        collegeLabelList = collegeListLabel.find_all('a')  # 学院名及学院对应id所在超链接标签
        collegeIdDict = {}  # 学院-id字典
        for item in collegeLabelList:
            collegeIdDict.update({item.em.string: int(item.get('id')[3:])})
        return collegeIdDict
        
        df_college = pd.DataFrame(collegeIdDict.keys())
        df_college.columns = ['college_name']
        df_id = pd.DataFrame(collegeIdDict.values())
        df_id.columns = ['id']
        df_id_name = pd.concat([df_id,df_college],axis=1)

        outputpath = './df_id_name.xlsx'    
        df_id_name.to_excel(outputpath,index=False,header=True)

outputpath = './df_id_name.xlsx'    
df_id_name.to_excel(outputpath,index=False,header=True)

html = "http://faculty.hust.edu.cn/xylb.jsp?urltype=tree.TreeTempUrl&wbtreeid=1003"

df_id_name = getCollegeId(html) 
df_id_name #类型为字典
nameId = pd.Series(df_id_name).to_frame().reset_index().rename(columns={'index':'学院名称',0:'id'})
nameId.to_excel('Q1nameId.xls',sheet_name='学院信息')



# Q2 第二个函数获取每个学院老师的网址（地址）得到学院+老师姓名+网址，可以以一个老师（蔡必卿）为例，获取他的9列信息，根据代码147-202行（姓名、个人主页、入职年份、职称、毕业院校、性别、学科、科研项目信息、论文发表信息）根据代码147-202行

def getCollegeTeachersInfo(j,collegeId):
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
    # 爬取各自蔡必卿老师（第三个）主页中的详细有关信息
    teacherInfoList = []
    teacherInfoList.append({'姓名': teachersData[j]['name'], "个人主页": teachersData[j]['url'], '入职年份': '','职称': teachersData[j]['gtutor'], '毕业院校': '', '性别': '','学科': '', '科研项目信息': '', '论文发表信息': ""})
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
                                        data=data, headers=headers)  # 最后更新时间
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


MzCai = pd.DataFrame(getCollegeTeachersInfo(2,2288))
MzCai.to_excel('Q2MzCai.xls',sheet_name='蔡必卿个人信息')


##Q3 第三个函数获取学院所有老师的人数，包含学院名称、学院ID、学院人数，根据代码95-119行

def getCollegeTeachersNum(collegeId):
        # 浏览器头部
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
                           headers=headers)
        req.encoding = 'utf-8'
        pat = re.compile(r'"totalnum":[0-9]+')
        totalNum = int(pat.search(req.text).group()[11:])  # 正则表达式筛出学院教师数
        return totalNum

TotalNum = []
for collegeId in nameId['id']:
    TotalNum.append(getCollegeTeachersNum(collegeId))
    #print(totalNum)

num = {'人数':TotalNum}
pd_number = pd.DataFrame(num)
df_name_id_numbers = pd.concat([nameId,pd_number],axis=1)
df_name_id_numbers.to_excel('./Q3nameIdNumbers.xls',index=False,header=True,sheet_name='学院_id_人数')


# Q4 第四个函数获取学院每个老师的网址，根据代码121-145行

def getCollegeTeachersUrl(collegeId):
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
    for j in range(len(teachersData)):     # len(teachersData)即对应学院的教师人数
        teacherInfoList.append([collegeId,teachersData[j]['name'], teachersData[j]['url']])
    return pd.DataFrame(teacherInfoList)

### 调用函数写入EXCEL
url = pd.DataFrame()
for collegeId in nameId['id']:
    url= pd.concat([url,getCollegeTeachersUrl(collegeId)],axis=0)

TeacherUrl = url.rename(columns={0:'id',1:'姓名',2:'个人主页'})
TeacherUrl.to_excel('./Q4TeacherUrl.xls',index=False,header=True,sheet_name='学院老师个人主页')

