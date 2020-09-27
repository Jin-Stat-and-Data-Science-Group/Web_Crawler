### function1:获取学院id和名称
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
'Chrome/83.0.4103.61 Safari/537.36'}
req = requests.get("http://faculty.hust.edu.cn/xylb.jsp?urltype=tree.TreeTempUrl&wbtreeid=1003",headers={'Connection':'close'})
req.encoding = 'utf-8'
soup = BeautifulSoup(req.text, 'html.parser')
collegeListLabel = soup.find('ul', class_="coll-list") # 学院所在列表
collegeLabelList = collegeListLabel.find_all('a')  # 学院名及学院对应id所在超链接标签
collegeIdDict = {}  # 学院id字典
for item in collegeLabelList:
    collegeIdDict.update({int(item.get('id')[3:]): item.em.string})
collegeIdDict

df=pd.DataFrame.from_dict(collegeIdDict,orient='index',columns=['name'])
df=df.reset_index().rename(columns={'index':'id'})
df
df.to_excel('function1.xlsx')

### function2:获取每个学院老师的网址，得到学院+老师姓名+网址，以蔡老师为例，获取他的九列信息（姓名、个人主页、入职年份、职称、毕业院校、性别、学科、科研项目信息、论文发表信息）

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
                           headers={'Connection':'close'})
    req.encoding = 'utf-8'
    teachersData = eval(req.text)["teacherData"]
    # 蔡必卿老师主页信息
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

df4=pd.DataFrame(getCollegeTeachersInfo(2,2288))
df4.to_excel('function2.xlsx')

### function3:获取各学院老师的人数，得到学院名称、id、人数

# 暴力方法可行但不建议使用
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
'Chrome/83.0.4103.61 Safari/537.36'}

Num=[]
for i in range(49):
    params = {'collegeid': df['id'][i],
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
    req = requests.get("http://faculty.hust.edu.cn/system/resource/tsites/asy/asyqueryteacher.jsp?", params=params, headers={'Connection':'close'})
    req.encoding = 'utf-8'
    pat = re.compile(r'"totalnum":[0-9]+')
    totalNum = int(pat.search(req.text).group()[11:])
    str(totalNum).split()
    Num.append(totalNum)
    print(totalNum)
Num



def getCollegeTeachersNum(collegeId):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/83.0.4103.61 Safari/537.36'}
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
    totalNum = int(pat.search(req.text).group()[11:])
    return totalNum

Num=[]
for collegeId in df['id']:
    Num.append(getCollegeTeachersNum(collegeId))
teachersNum={'教师人数':Num}
df1=pd.concat([df,pd.DataFrame(teachersNum)],axis=1)
df1.to_excel('function3.xlsx')

### function4:获取每个学院老师的网址

def getCollegeTeacherInfo(collegeId):
    # 先获取教师人数
    totalNum = getCollegeTeachersNum(collegeId)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/83.0.4103.61 Safari/537.36'}
    params = {'collegeid': collegeId,
              'disciplineid': 0,
              'pageindex': 1,
              'pagesize': Num,
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
    teachersData = eval(req.text)["teacherData"]
    teacherInfoList=[]
    for i in range(len(teachersData)):
        teacherInfoList.append([teachersData[i]['name'],teachersData[i]['url']])
    return pd.DataFrame(teacherInfoList)

teachersUrl=pd.DataFrame()
for collegeId in df['id']:
    teachersUrl=pd.concat([teachersUrl,getCollegeTeacherInfo(collegeId)])
df2=teachersUrl.rename(columns={0:'姓名',1:'个人主页'})
df2.to_excel('function4.xlsx')

# proxyerror
teachersUrl1=pd.DataFrame()
for collegeId in df['id']:
    id=pd.DataFrame({'id':[2288]})
    df3=pd.concat([id,getCollegeTeacherInfo(collegeId)],axis=1)
    teachersUrl=pd.concat([teachersUrl,df3])
df21=teachersUrl1.rename(columns={0:'id',1:'姓名',2:'个人主页'})