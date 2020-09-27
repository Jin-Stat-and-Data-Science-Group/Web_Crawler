import re
import requests
import pandas as pd 
import xlwt
from bs4 import BeautifulSoup

##第一个函数获取学院名称和学院ID
def getCollegeId(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
    #url = "http://faculty.hust.edu.cn/xylb.jsp?urltype=tree.TreeTempUrl&wbtreeid=1003"
    req = requests.get(url=url,headers=headers)
    req.encoding = 'utf-8'#编码方式
    soup = BeautifulSoup(req.text, 'html.parser')
    collegeListLabel = soup.find('ul', class_="coll-list")  # 学院所在列表
    collegeLabelList = collegeListLabel.find_all('a')  # 学院名及学院对应id所在超链接标签
    collegeIdDict = {}  # 学院-id字典
    for item in collegeLabelList:
        collegeIdDict.update({item.em.string: int(item.get('id')[3:])})
    return collegeIdDict


url = "http://faculty.hust.edu.cn/xylb.jsp?urltype=tree.TreeTempUrl&wbtreeid=1003"
dat = pd.DataFrame(getCollegeId(url),index=['collegeId']).T
dat.to_excel('./collegeid.xlsx')

##第二个以（蔡必卿）为例，获取他的9列信息，根据代码147-202行（姓名、个人主页、入职年份、
#职称、毕业院校、性别、学科、科研项目信息、论文发表信息）根据代码147-202行

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
# 表单提交参数
params = {'collegeid': 2288,
                  'disciplineid': 0,
                  'pageindex': 1,
                  'pagesize': 68,
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
teachersData = eval(req.text)["teacherData"]
teachersData = teachersData[2]
teachersData['name']
teacherInfoList = []
teacherInfoList.append({'姓名': teachersData['name'], "个人主页": teachersData['url'], '入职年份': '', '职称': teachersData['gtutor'], '毕业院校': '', '性别': '','学科': '', '科研项目信息': '', '论文发表信息': ""})
teacherInfoList

##获取学科
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'}
req = requests.get('http://faculty.hust.edu.cn/caibiqing/zh_CN/index.htm',headers=headers)
req.encoding = 'utf-8'
soup = BeautifulSoup(req.text.replace('</br>',''),"html.parser")
info = soup.find('div','cont').p.get_text().strip()
patt = re.compile("(.*)：(.*)$") 
m = re.search(patt,info)
teacherInfoList[-1].update({m.group(1):m.group(2)})
##获取入职年份
data = {'timeformat': 'yyyy-MM-dd&zh',
        'teacherid': teachersData['teacherId'],
        'homepageid': 140721,
        'ac': 'gethomepageopentime'}
timeReq = requests.post("http://faculty.hust.edu.cn/system/resource/tsites/latestupdatetime.jsp",data=data,headers=headers)
teacherInfoList[-1].update({"入职年份": eval(timeReq.text)['year']})
# 获取科研成果
researchUrl = soup.find_all("li", class_="fNiv")
for url in researchUrl:
    if url.a.string == "科学研究":
        researchUrl = url.a.get("href")
        break
researchReq = requests.get('http://faculty.hust.edu.cn'+researchUrl)
researchReq.encoding = 'utf-8'
researchSoup = BeautifulSoup(researchReq.text,'html.parser')
researchDiv = researchSoup.find_all('div',class_= 'cont')
researchProjectParagraph = researchDiv[5].find_all('p')
researchProject = ""# 科研项目信息

# 对于某些没有科研项目信息的下面可以跳过
try:
    for i in range(len(researchProjectParagraph)):
        researchProject += '[' + str(i+1) + ']' + researchProjectParagraph[i].string.strip() + ';'
        teacherInfoList[-1].update({'科研项目信息':researchProject})
except:
    pass       

paperProjectParagraph = researchDiv[2].find_all('p')
paperProject = ""# 论文发表信息
try:
    for i in range(len(paperProjectParagraph)):
        paperProject += '[' + str(i+1) + ']' +paperProjectParagraph[i].string.strip() + ';'
        teacherInfoList[-1].update({'论文发表信息':paperProject})
except:
    pass

print(teacherInfoList)
    


##第三个函数，获取所有学院所有老师的人数，包含学院名称、学院ID、学院人数，根据代码95-119行

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
    return totalNum

dat1 = pd.read_excel('./学院代码fun1.xlsx')
s = []
for i in dat1['collegeId']:
    s.append(getCollegeTeachersNum(i))
dat1['totalnum'] = pd.DataFrame(s,index=dat1.index)
dat1.to_excel('./totalnum.xlsx')


##第四个函数获取学院每个老师的个人主页网址

def getCollegeTeacherInfo(collegeId,totalNum):
    # 先获取教师人数
    #totalNum = getCollegeTeachersNum(collegeId)
    # 浏览器头部
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
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
    req = requests.get("http://faculty.hust.edu.cn/system/resource/tsites/asy/asyqueryteacher.jsp?",params=params,headers=headers)
    req.encoding = 'utf-8'
    teachersData = eval(req.text)["teacherData"]
    teacherInfoList = []
    for j in range(len(teachersData)):
        teacherInfoList.append({'姓名': teachersData[j]['name'], "个人主页": teachersData[j]['url'], '入职年份': '',
                                    '职称': teachersData[j]['gtutor'], '毕业院校': '', '性别': '',
                                    '学科': '', '科研项目信息': '', '论文发表信息': ""})
    return teacherInfoList

dat2 = pd.read_excel('./totalnum.xlsx')
url_info=[]
for i in range(0,len(dat2)):
    a = getCollegeTeacherInfo(dat2.collegeId[i],dat2.totalnum[i])
    for j in range(dat2.totalnum[i]):
        url_info.append([dat2.index[i],a[j]['姓名'],a[j]['个人主页']])

url_info = pd.DataFrame(url_info,columns=["所在学院",'姓名','个人主页'])
url_info.to_excel('./url_info.xlsx')





