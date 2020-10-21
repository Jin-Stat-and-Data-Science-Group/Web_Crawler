############从华师教师主页http://faculty.ccnu.edu.cn/ch/index爬取#############
import requests
import json
import re
import pandas as pd
from bs4 import BeautifulSoup
data = {
	"input[pageNo]": "1",
	"input[pageSize]": "210",
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

pd.DataFrame(teacherinfolist)[["姓名","工号","学院","出生年月","专业职称","教育背景"]].to_excel('../data/ccun_teacherinfolist.xlsx')

##################################从华师各个学院入口爬取#####################################
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
os.getcwd()
urllist = pd.read_excel('../data/url.xlsx')
ccun_url = 'http://foaie.ccnu.edu.cn'

Headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0'}

#人工智能教育学部-教学科研系列
def rgznjxky(url):
    req = requests.get(url = url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,'html.parser')
    rgznjxky_info = soup.find_all('div',class_ = 'sz-xianshi')
    teacherinfolist = []
    for i in range(len(rgznjxky_info)):
        sss = rgznjxky_info[i].find_all("div",class_ = "sz-sznr yingyong")[0].ul.find_all("li",class_="sz-sznrulli")
        for j in range(len(sss)):
            teacherinfolist.append({"姓名":sss[j].a.string,
                                    "学院":soup.head.title.get_text(),
                                    "职称":rgznjxky_info[i].find_all('div',class_ = "xy-biaoti")[0].p.get_text(),
                                    "个人主页url":ccun_url + sss[j].a.get("href")[2:]})
    return pd.DataFrame(teacherinfolist)
rgznjxky(urllist.url[0]).to_excel("../data/人工智能教育学部.xlsx") # 2. 人工智能教育学部-教学科研系列 108



#教育学院——全体教师 72
def jyxyqtjs(url):
    req = requests.get(url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,'html.parser')
    jy_allinfo = soup.find_all("div",class_="texts")[0].find_all("ul")
    teacherinfolist = []
    for i in range(len(jy_allinfo)):
        for j in range(len(jy_allinfo[i].find_all("li"))):
            teacherinfolist.append({"姓名":jy_allinfo[i].find_all("li")[j].get_text(),
                                   "学院":soup.head.title.get_text(),
                                   "职称":jy_allinfo[i].h2.get_text(),
                                   "个人主页url":ccun_url + jy_allinfo[i].find_all("li")[j].a.get("href")[5:]})
    return pd.DataFrame(teacherinfolist)
jyxyqtjs(urllist.url[1]).to_excel("../data/教育学院.xlsx")

##心理学院——教师列表
def xlxyjslb(url):
    req = requests.get(url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,'html.parser')
    xl_allinfo = soup.tbody.find_all("tr")
    teacherinfolist = []
    for i in range(len(soup.tbody.find_all("tr"))):
        try:
            teacherinfolist.append({"姓名":xl_allinfo[i].find_all("span")[0].string.replace("\xa0",''),
                                   "学院":soup.title.text,
                                   "职称":xl_allinfo[i].find_all("span")[1].string,
                                   "个人主页url":ccun_url + xl_allinfo[i].a.get("href")[2:]})
        except:
            pass
    return pd.DataFrame(teacherinfolist)
xlxyjslb(urllist.url[2]).to_excel("../data/心理学院.xlsx")

##文学院——在职老师
def wxyzhls(url):
    req = requests.get(url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,'html.parser')
    wen_allinfo = soup.find_all("ul",class_ = "team")[0].find_all("ul")
    teacherinfolist = []
    for i in range(len(wen_allinfo)):
        for j in range(len(wen_allinfo[i])):
            try:
                teacherinfolist.append({"姓名":wen_allinfo[i].find_all("li")[j].a.text,
                                        "学院":soup.title.get_text(),
                                        "职称":"",
                                        "个人主页url":wen_allinfo[0].find_all("li")[0].a.get("href")[2:]
            })
            except:
                pass
    return pd.DataFrame(teacherinfolist)
wxyzhls(urllist.url[3]).to_excel("../data/文学院.xlsx") #文学院在职老师 90个

##5.新闻传播学院——专任教师
def xwcbzrjs(url):
    req = requests.get(url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,"html.parser")
    xwcb_allinfo = soup.tbody.find_all("td")
    teacherinfolist = []
    soup.tbody.find_all("td")[2].a.span.string.replace("\u3000","")#姓名
    soup.tbody.find_all("td")[2].a.get("href")[2:]#个人主页url
    soup.title.get_text()#学院
    for i in range(len(xwcb_allinfo)):
        try:
            teacherinfolist.append({"姓名":xwcb_allinfo[i].a.span.string.replace("\u3000",""),
                                    "学院":soup.title.get_text(),
                                    "职称":"",
                                    "个人主页url":ccun_url + xwcb_allinfo[i].a.get("href")[2:]})
        except:
            pass
    return pd.DataFrame(teacherinfolist)
xwcbzrjs(urllist.url[4]).to_excel("../data/新闻传播学院.xlsx")
            
##历史文化学院——历史文化学院教学科研人员
def lswhjxky(url):
    req = requests.get(url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,"html.parser")
    lswh_allinfo = soup.find_all("div",class_= "v_news_content")[0].find_all("a")
    teacherinfolist = []
    for i in range(len(lswh_allinfo)):
        teacherinfolist.append({"姓名":lswh_allinfo[i].span.text,
                                "学院":soup.title.get_text(),
                                "职称":"",
                                "个人主页url":lswh_allinfo[i].get("href")
    })
    return pd.DataFrame(teacherinfolist)
lswhjxky(urllist.url[5]).to_excel("../data/历史文化学院.xlsx")

##马克思主义学院——教学科研人员
def mkszyjxky(url):
    req = requests.get(url = url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,"html.parser")
    mkszy_allinfo = soup.find_all("div",class_= "read")[0].find_all("a")
    teacherinfolist = []
    for i in range(len(mkszy_allinfo)):
        teacherinfolist.append({"姓名":mkszy_allinfo[i].text.replace("\u3000","").strip()[0:3].replace("（",""),
                                "学院":soup.title.get_text(),
                                "职称":mkszy_allinfo[i].text.replace("\u3000","").strip()[-4:-1],
                                "个人主页url":ccun_url + mkszy_allinfo[0].get("href")[2:]
    })
    return pd.DataFrame(teacherinfolist)
mkszyjxky(urllist.url[6]).to_excel("../data/马克思主义学院.xlsx")


##经济与工商管理学院——国际经济与贸易系
def jjygsglxy(url):
    req = requests.get(url = url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,"html.parser")
    jjygsgl_allinfo = soup.find_all("div",class_= "col-md-8")
    # teacherinfolist = []
    for i in range(1,len(jjygsgl_allinfo),1):
        teacherinfolist.append({"姓名":jjygsgl_allinfo[i].a.text[:3],
                                "学院":soup.title.get_text(),
                                "职称":jjygsgl_allinfo[i].a.text[-4:-1].replace("（",""),
                                "个人主页url":ccun_url + jjygsgl_allinfo[i].a.get("href")[2:]
            })
    return pd.DataFrame(teacherinfolist)
jjygsgl_urllist = ['http://econ.ccnu.edu.cn/szdw/gjjjymyx.htm',
                   'http://econ.ccnu.edu.cn/szdw/gjjjymyx/1.htm',
                   'http://econ.ccnu.edu.cn/szdw/jjx.htm',
                   'http://econ.ccnu.edu.cn/szdw/jjx/3.htm',
                   'http://econ.ccnu.edu.cn/szdw/jjx/2.htm',
                   'http://econ.ccnu.edu.cn/szdw/jjx/1.htm',
                   'http://econ.ccnu.edu.cn/szdw/csjjx.htm',
                   'http://econ.ccnu.edu.cn/szdw/csjjx/2.htm',
                   'http://econ.ccnu.edu.cn/szdw/csjjx/1.htm',
                   'http://econ.ccnu.edu.cn/szdw/gsglx.htm',
                   'http://econ.ccnu.edu.cn/szdw/gsglx/2.htm',
                   'http://econ.ccnu.edu.cn/szdw/gsglx/1.htm',
                   'http://econ.ccnu.edu.cn/szdw/cwhjx.htm',
                   'http://econ.ccnu.edu.cn/szdw/cwhjx/1.htm',
                   'http://econ.ccnu.edu.cn/szdw/jrx.htm',
                   'http://econ.ccnu.edu.cn/szdw/jrx/1.htm']
teacherinfolist = []
for k in jjygsgl_urllist:
    jjygsglxy(k)
ss = []  
for j in teacherinfolist:
    ss.append(j)
pd.DataFrame(ss).to_excel("../data/经济与工商管理学院.xlsx")

##公共管理学院——专职教师
def ggglzzjs(url):
    req = requests.get(url = url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,"html.parser")
    gggl_allinfo = soup.find_all("div",class_= "main-szdw1x")
    teacherinfolist = []
    for i in range(len(gggl_allinfo)):
        for j in range(len(gggl_allinfo[i].find_all("li"))):
            teacherinfolist.append({"姓名":gggl_allinfo[i].find_all("li")[j].text,
                                    "学院":soup.title.get_text(),
                                    "职称":"",
                                    "个人主页url":ccun_url + gggl_allinfo[i].find_all("li")[j].a.get("href")[2:]
    })
    return pd.DataFrame(teacherinfolist)
ggglzzjs(urllist.url[13]).to_excel("../data/公共管理学院.xlsx")

##法学院——教师队伍
def rgznjxky(url):
    req = requests.get(url = url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,'html.parser')
    fxy_url = 'http://law.ccnu.edu.cn/info/1155'
    teacherinfolist = []
    fxy_allinfo = soup.find_all('div',class_ = 'v_news_content')[0].find_all("span")
    for i in [2,6,11]:
        for j in range(len(fxy_allinfo[2].find_all("a"))):
            teacherinfolist.append({"姓名":fxy_allinfo[i].find_all("a")[j].text,
                                    "学院":soup.head.title.get_text(),
                                    "职称":"",
                                    "个人主页url":fxy_url + fxy_allinfo[i].find_all("a")[0].get("href")})
    return pd.DataFrame(teacherinfolist)
rgznjxky(urllist.url[14]).to_excel("../data/法学院.xlsx")


##社会学院——专任教师
def shxyzrjs(url):
    req = requests.get(url = url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,"html.parser")
    shxy_allinfo = soup.find_all("li",class_= "pic-news")
    for i in range(len(shxy_allinfo)):
        teacherinfolist.append({"姓名":shxy_allinfo[i].find("a",class_ = "news-name").text,
                                "学院":soup.title.get_text(),
                                "职称":"",
                                "个人主页url":ccun_url + shxy_allinfo[i].find("a",class_ = "news-name").get("href")[2:]
            })
    return pd.DataFrame(teacherinfolist)

shxyzrjs("http://shxy.ccnu.edu.cn/sz/zrjs.htm")
jjygsgl_urllist = ['http://shxy.ccnu.edu.cn/sz/zrjs.htm',
                   'http://shxy.ccnu.edu.cn/sz/zrjs/2.htm',
                   'http://shxy.ccnu.edu.cn/sz/zrjs/1.htm']
teacherinfolist = []
for k in jjygsgl_urllist:
    shxyzrjs(k)
sh = []
for j in teacherinfolist:
    sh.append(j)
pd.DataFrame(sh).to_excel("../data/社会学院.xlsx")

##外国语学院
def wgyxy(url):
    req = requests.get(url = url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,"html.parser")
    wgy_allinfo = soup.find_all("div",class_= "tplb")
    for i in range(len(wgy_allinfo)):
        for j in range(len(wgy_allinfo[i].find_all("li"))):
            teacherinfolist_wgy.append({"姓名":wgy_allinfo[i].find_all("li")[j].p.text,
                                "学院":soup.title.get_text(),
                                "职称":wgy_allinfo[i].h4.text,
                                "个人主页url":ccun_url + wgy_allinfo[i].find_all("li")[j].a.get("href")[2:]
            })
teacherinfolist_wgy = []
for k in urllist.url[16:23]:
    wgyxy(k)
pd.DataFrame(teacherinfolist_wgy).to_excel("../data/外国语学院.xlsx")

##信息管理学院——专任教师
def xxglzrjs(url):
    req = requests.get(url = url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,"html.parser")
    xxgl_allinfo = soup.find_all("div",class_= "stu1")
    teacherinfolist = []
    for i in range(len(xxgl_allinfo)):
        for j in range(len(xxgl_allinfo[i].find_all("dd"))):
            teacherinfolist.append({"姓名":xxgl_allinfo[i].find_all("dd")[j].text,
                                "学院":soup.title.get_text(),
                                "职称":"",
                                "个人主页url":xxgl_allinfo[i].find_all("dd")[j].a.get("href")
            })
    return pd.DataFrame(teacherinfolist)
xxglzrjs(urllist.url[23]).to_excel("../data/信息管理学院.xlsx")

##音乐学院
def yyxy(url):
    req = requests.get(url = url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,"html.parser")
    yyxy_allinfo = soup.find_all("div",class_= "main_rpicR")
    for i in range(len(yyxy_allinfo)):
        teacherinfolist_yy.append({"姓名":yyxy_allinfo[i].h3.string,
                                "学院":soup.title.get_text(),
                                "职称":"",
                                "个人主页url":ccun_url + yyxy_allinfo[i].span.a.get("href")[2:]
            })
    # return pd.DataFrame(teacherinfolist)
yyxy_urllist = ['http://music.ccnu.edu.cn/szdw/slx.htm',
                'http://music.ccnu.edu.cn/szdw/slx/1.htm',
                'http://music.ccnu.edu.cn/szdw/gqx.htm',
                'http://music.ccnu.edu.cn/szdw/gqx/2.htm',
                'http://music.ccnu.edu.cn/szdw/gqx/1.htm',
                'http://music.ccnu.edu.cn/szdw/qlx.htm',
                'http://music.ccnu.edu.cn/szdw/qlx/1.htm',
                'http://music.ccnu.edu.cn/szdw/ylxx/1.htm',
                'http://music.ccnu.edu.cn/szdw/ylxx.htm',
                'http://music.ccnu.edu.cn/szdw/wdx.htm',
                'http://music.ccnu.edu.cn/szdw/zqyzhx.htm'
]
teacherinfolist_yy = []
for k in yyxy_urllist:
    yyxy(k)
pd.DataFrame(teacherinfolist).to_excel("../data/音乐学院.xlsx")

##数学与统计学院——师资队伍

def tjysxszdw(url):
    req = requests.get(url = url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,"html.parser")
    tjysx_allinfo = soup.find_all("table",class_ = "table teacherList")[0].find_all("a")
    for i in range(len(tjysx_allinfo)):
        teacherinfolist_ts.append({"姓名":tjysx_allinfo[i].text,
                                   "学院":soup.title.get_text(),
                                   "职称":soup.find("h4",class_ = "teacherTitle").text,
                                   "个人主页url":ccun_url + tjysx_allinfo[i].get("href")
            })
    # return pd.DataFrame(teacherinfolist)
tjysx_urllist = ['http://maths.ccnu.edu.cn/szdw1/js.htm',
                 'http://maths.ccnu.edu.cn/szdw1/fjs.htm',
                 'http://maths.ccnu.edu.cn/szdw1/js1.htm']
teacherinfolist_ts = []                 
for k in tjysx_urllist:
    tjysxszdw(k)
pd.DataFrame(teacherinfolist_ts).to_excel("../data/数学与统计学院.xlsx")

##物理科学与技术学院——师资概况
def wlkxyjs(url):
    req = requests.get(url = url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,"html.parser")
    wl_allinfo = soup.find_all("div",class_ = "main_conR main_conRa")[0].find_all("li")
    patt = re.compile(r'[(](.*?)[)]', re.S)
    teacherinfolist = []
    for i in range(len(wl_allinfo)):

        teacherinfolist.append({"姓名":wl_allinfo[i].a.text[:4].replace("(",""),
                                   "学院":soup.title.get_text(),
                                   "职称":re.findall(patt,wl_allinfo[0].a.text),
                                   "个人主页url":ccun_url + wl_allinfo[0].a.get("href")[2:]
            })
    return pd.DataFrame(teacherinfolist)
wlkxyjs(urllist.url[31]).to_excel("../data/物理科学与技术学院.xlsx")

##化学学院——师资队伍
def hxxyszdw(url):
    req = requests.get(url = url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,"html.parser")
    hx_allinfo = soup.find_all("div",class_ = "txt_info")[0]
    teacherinfolist = []
    for i in range(len(hx_allinfo.find_all("div",class_="title"))):
        for j in range(len(hx_allinfo.find_all("div",class_ = "name")[i].find_all("a"))):
            teacherinfolist.append({"姓名":hx_allinfo.find_all("div",class_ = "name")[i].find_all("a")[i].text,
                                   "学院":soup.title.get_text(),
                                   "职称":hx_allinfo.find_all("div",class_="title")[i],
                                   "个人主页url":ccun_url + '/' + hx_allinfo.find_all("div",class_ = "name")[i].find_all("a")[j].get("href")
            })
    return pd.DataFrame(teacherinfolist)
hxxyszdw(urllist.url[32]).to_excel("../data/化学学院.xlsx")


##生命科学学院——专任教师
def smkxxyzrjs(url):
    req = requests.get(url = url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,"html.parser")
    smkx_allinfo = soup.find_all("div",class_ = "col-news-con")[0].find_all("li",class_ = "news")
    teacherinfolist = []
    for i in range(1,len(smkx_allinfo),1):
        try:
            teacherinfolist.append({"姓名":smkx_allinfo[i].a.text,
                                   "学院":soup.title.get_text(),
                                   "职称":smkx_allinfo[i].span.text,
                                   "个人主页url":ccun_url + smkx_allinfo[i].a.get("href")[5:]
            })
        except:
            pass
    return pd.DataFrame(teacherinfolist)
smkxxyzrjs(urllist.url[33]).to_excel("../data/生命科学学院.xlsx")


##计算机学院——师资一览
def jsjxyszyl(url):
    req = requests.get(url = url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,"html.parser")
    jsj_allinfo = soup.find_all("div",id = "vsb_content")[0].find_all("p")
    zhicheng = ["教授","副教授","讲师"]
    teacherinfolist = []
    for i in range(len(jsj_allinfo)):
        for j in range(len(jsj_allinfo[i].find_all("a"))):
            teacherinfolist.append({"姓名":jsj_allinfo[i].find_all("a")[j].text,
                                   "学院":soup.title.get_text(),
                                   "职称":zhicheng[i],
                                   "个人主页url":ccun_url + jsj_allinfo[i].find_all("a")[j].get("href")[2:]
            })
    return pd.DataFrame(teacherinfolist)
jsjxyszyl(urllist.url[34]).to_excel("../data/计算机学院.xlsx")


##城市与环境科学学院——师资队伍
def csyhjkxxy(url):
    req = requests.get(url = url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,"html.parser")
    cshjkx_allinfo = soup.find_all("div",class_="group")
    zhicheng = ["教授","副教授","讲师"]
    teacherinfolist = []
    for i in range(3):
        for j in range(len(cshjkx_allinfo[i].find_all("a"))):
            teacherinfolist.append({"姓名":cshjkx_allinfo[i].find_all("a")[j].text.strip(),
                                   "学院":soup.title.get_text(),
                                   "职称":zhicheng[i],
                                   "个人主页url":ccun_url + "/" + cshjkx_allinfo[i].find_all("a")[j].get("href")
            })
    return pd.DataFrame(teacherinfolist)
csyhjkxxy(urllist.url[35]).to_excel("../data/城市与环境科学学院.xlsx")

##政治与国际关系学院
def zzygjgx(url):
    req = requests.get(url = url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,"html.parser")
    zzygjgx_allinfo = soup.find_all("div",class_="list")[0].find_all("li")
    for i in range(len(zzygjgx_allinfo)):
        teacherinfolist_zg.append({"姓名":zzygjgx_allinfo[i].a.text,
                                   "学院":soup.title.get_text(),
                                   "职称":"",
                                   "个人主页url":ccun_url + zzygjgx_allinfo[0].a.get("href")[5:]
            })
teacherinfolist_zg = []
for k in urllist.url[36:39]:
    zzygjgx(k)
pd.DataFrame(teacherinfolist_zg).to_excel("../data/政治与国际关系学院.xlsx")

## 中国农村研究院——专职研究人员--------------已通过手工整理


## 语言与语言教育研究中心——专职人员
def yyjyyjzx(url):
    req = requests.get(url = url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,"html.parser")
    yyjyyjzx_allinfo = soup.find_all("table",class_='teachertable')[0].find_all("tr")
    teacherinfolist = []
    for i in range(1,len(yyjyyjzx_allinfo),1):
        teacherinfolist.append({"姓名":yyjyyjzx_allinfo[i].a.text,
                                   "学院":soup.title.get_text(),
                                   "职称":yyjyyjzx_allinfo[i].find_all("td")[1].text,
                                   "个人主页url":ccun_url + "/" + yyjyyjzx_allinfo[i].a.get("href")[2:]
            })
    return pd.DataFrame(teacherinfolist)
yyjyyjzx(urllist.url[40]).to_excel("../data/语言与语言教育研究中心.xlsx")


##中国近代史研究所
def zgjdsyjs(url):
    req = requests.get(url = url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,"html.parser")
    zgjds_allinfo = soup.find_all("div",class_ = "right_bottom list")[0].find_all("a")
    for i in range(len(zgjds_allinfo)):
        teacherinfolist_jds.append({"姓名":zgjds_allinfo[i].text,
                                   "学院":soup.title.get_text(),
                                   "职称":"",
                                   "个人主页url":ccun_url + zgjds_allinfo[i].get("href")
            })
teacherinfolist_jds = []                 
for k in urllist.url[41:45]:
    zgjdsyjs(k)
pd.DataFrame(teacherinfolist_jds).to_excel("../data/中国近代史研究所.xlsx")


##国家文化产业研究中心——专职教师
def gjwhcyyjzx(url):
    req = requests.get(url = url,headers = Headers)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text,"html.parser")
    gjwh_allinfo = soup.find_all("table",class_='winstyle217915')[0].find_all("a")
    teacherinfolist = []
    for i in range(1,len(gjwh_allinfo),2):
        teacherinfolist.append({"姓名":gjwh_allinfo[1].text,
                                "学院":soup.title.get_text(),
                                "职称":"",
                                "个人主页url":ccun_url + "/" + gjwh_allinfo[1].get("href")
            })
    return pd.DataFrame(teacherinfolist)
gjwhcyyjzx(urllist.url[45]).to_excel("./data/国家文化产业研究中心.xlsx")
dat1 = pd.read_excel("./data/城市与环境科学学院.xlsx")
for info in os.listdir('./data'):
    dat = pd.read_excel('../data/' + info)
    dat1 = pd.concat([dat1,dat],ignore_index=True)
dat1.to_excel("../data/teacherlisturl.xlsx")#导出所有教师的url信息

