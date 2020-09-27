import numpy as np 
import pandas as pd 
import threading #线程模块
import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
import re##正则表达式
import requests##发送请求
import xlwt ##读写excel
from bs4 import BeautifulSoup

##1、第一个函数获取id和学院名称，根据37-49行
def getCollegeId():
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/83.0.4103.61 Safari/537.36'}##可以删除试试
        req = requests.get("http://faculty.hust.edu.cn/xylb.jsp?urltype=tree.TreeTempUrl&wbtreeid=1003",
                           headers=headers)##服务器发送请求
        req.encoding = 'utf-8'
        soup = BeautifulSoup(req.text, 'html.parser')
        collegeListLabel = soup.find('ul', class_="coll-list")  # 学院所在列表
        collegeLabelList = collegeListLabel.find_all('a')  # 学院名及学院对应id所在超链接标签
        collegeIdDict = []  # 学院-id字典
        for item in collegeLabelList:
            collegeIdDict.append([item.em.string,int(item.get('id')[3:])])##第三列
        return collegeIdDict
collegeid=pd.DataFrame(getCollegeId(),columns=['name','id'],index=np.arange(len(getCollegeId())))
collegeid.to_excel('collegename_id.xls',sheet_name='学院名称_id')

#3、第三个函数获取学院所有老师的人数，包含学院名称、学院ID、学院人数，根据代码95-119行
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
a=collegeid['id']
b=[]
for i in a:
    b.append(getCollegeTeachersNum(i))
c=pd.concat([collegeid,pd.DataFrame(b)],axis=1)
c.columns=['name','id','numbers']
c.to_excel('collegenumbers.xls',sheet_name='各学院人数')

##4、第四个函数获取学院每个老师的网址，根据代码121-145行

def getCollegeTeacherUrl(collegeId):
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
        teacherinfo=[]
        for i in range(len(teachersData)):
            teacherinfo.append([teachersData[i]['name'], teachersData[i]['url']])
        return pd.DataFrame(teacherinfo)

a=collegeid['id']
for collegeId in a:
    teacherweb=getCollegeTeacherUrl(collegeId)
teacherweb##运行失败

##选取2288+学院名
teacherweb=getCollegeTeacherUrl(2288)
ID=pd.DataFrame(a[0].repeat(c['numbers'][0]))
web=pd.concat([ID,teacherweb],axis=1)
web.columns=['ID','teacher_name','teacher_url']
web


##加上各学院
for j in range(len(a)):
    teacherweb=getCollegeTeacherUrl(a[j])
    ID=pd.DataFrame(a[j].repeat(c['numbers'][j]))
web=pd.concat([ID,teacherweb],axis=1)
web.columns=['ID','teacher_name','teacher_url']
web.to_excel('teacherweb.xls',sheet_name='学院id_老师姓名_网址')

a[0]
for collegeId in a:
    id={'学院id':collegeId}
    df_id=pd.DataFrame(id)
    web=pd.concat(df_id,teacherweb,axis=1)
web


##2、第二个函数获取每个学院老师的网址（地址）得到学院+老师姓名+网址，可以以一个
#老师（蔡必卿）为例，获取他的9列信息，根据代码147-202行（姓名、个人主页、入职年
#份、职称、毕业院校、性别、学科、科研项目信息、论文发表信息）

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

caiinfo= pd.DataFrame(getCollegeTeachersInfo(2,2288))
caiinfo.to_excel('caiinfo.xls',sheet_name='蔡必卿个人信息')