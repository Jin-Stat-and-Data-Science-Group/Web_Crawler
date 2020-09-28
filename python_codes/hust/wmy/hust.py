import re
import requests
import pandas as pd 
import xlwt
from bs4 import BeautifulSoup
#函数一:得到学院+ID
def getCollegeId():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
    url = "http://faculty.hust.edu.cn/xylb.jsp?urltype=tree.TreeTempUrl&wbtreeid=1003"
    req = requests.get(url=url,headers=headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text, 'html.parser')
    collegeListLabel = soup.find('ul', class_="coll-list")  # 学院所在列表
    collegeLabelList = collegeListLabel.find_all('a')  # 学院名及学院对应id所在超链接标签
    collegeIdDict = {}  # 学院-id字典
    for item in collegeLabelList:
        collegeIdDict.update({item.em.string: int(item.get('id')[3:])})
    return pd.DataFrame(collegeIdDict,index=['collegeId']).T

getCollegeId().to_excel('./collegeid.xlsx')

#函数二：
def getCollegeTeachersNum(collegeId):
    # 浏览器头部
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
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
    req = requests.get("http://faculty.hust.edu.cn/system/resource/tsites/asy/asyqueryteacher.jsp?",params=params,headers=headers)
    req.encoding = 'utf-8'
    pat = re.compile(r'"totalnum":[0-9]+')
    totalNum = int(pat.search(req.text).group()[11:])  # 正则表达式筛出学院教师数

    PARAMS = {'collegeid': collegeId,
                  'disciplineid': 0,
                  'pageindex': 1,
                  'pagesize': 300,
                  'rankid': 0,
                  'honorid': 0,
                  'py': '',
                  'viewmode': 8,
                  'viewid': 66517,
                  'siteOwner': 1391599222,
                  'viewUniqueId': 66517,
                  'showlang': '',
                  'type': 'collgeteacher'}
    req = requests.get("http://faculty.hust.edu.cn/system/resource/tsites/asy/asyqueryteacher.jsp?",params=PARAMS,headers=headers)
    req.encoding = 'utf-8'
    teachersData = eval(req.text)["teacherData"]
    teacherInfoList = []
    for j in range(len(teachersData)):
        teacherInfoList.append({'姓名': teachersData[j]['name'],'教师ID':teachersData[j]['teacherId'], "个人主页": teachersData[j]['url'],'职称': teachersData[j]['prorank'],  '性别': teachersData[j]['sex'], '硕导': teachersData[j]['gtutor'], '博导': teachersData[j]['doctorTutor']})
    return teacherInfoList
dat = pd.read_excel('./collegeid.xlsx')
s=[]
for i in dat['collegeId']:
    s.append(getCollegeTeachersNum(i))
teacherInfoList = []
for k in s:
    teacherInfoList += k
pd.DataFrame(teacherInfoList)[['姓名','教师ID','性别','职称','硕导','博导','个人主页']].to_excel('./teacherInfoList1.xlsx')

##函数三
def getCollegeTeacherInfo2(url,teacherId):           
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
        req = requests.get(url=url,headers=headers)
        req.encoding = 'utf-8'
        soup = BeautifulSoup(req.text.replace('</br>',''),'html.parser')
        teacherInfoList = [{'姓名':'','所在单位':'','学历':'','学位':'','学科':'','入职年份':'','科研项目信息':'','论文发表信息':''}]
        teacherInfoList[-1].update({'姓名':soup.title.string[:3]})
        try:
            info = soup.find('div','cont').p.get_text().strip()
            patt = re.compile("(.*)：(.*)")#正则
            #通过循环移除已匹配项来获得多个正则匹配项
            m = patt.search(info)
            while m:
                if m.group(1) in teacherInfoList[-1].keys():
                    teacherInfoList[-1].update({m.group(1): m.group(2)})
                    info = info.replace(m.group(), '')
                    m = patt.search(info)
            # 获取入职年份（个人主页开通年份）
            # 模拟提交表单数据
            data = {'timeformat': 'yyyy-MM-dd&zh',
            'teacherid': teacherId,
            'homepageid': 140721,
            'ac': 'gethomepageopentime'}
            timeReq = requests.post("http://faculty.hust.edu.cn/system/resource/tsites/latestupdatetime.jsp",data=data,headers=headers)
            teacherInfoList[-1].update({"入职年份": eval(timeReq.text)['year']})
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
            pass
        return teacherInfoList


dat2 = pd.read_excel('./teacherInfoList1.xlsx')
teacherInfo = []
for i in range(len(dat2)):
    teacherInfo.append(getCollegeTeacherInfo2(dat2['个人主页'][i],dat2['教师ID'][i]))
teacherInfoList2 = []
for j in teacherInfo:
    teacherInfoList2 += j
pd.DataFrame(teacherInfoList2)[['姓名','入职年份','学位','学历','学科','所在单位','科研项目信息','论文发表信息']].to_excel('./teacherInfoList2.xlsx')



    
