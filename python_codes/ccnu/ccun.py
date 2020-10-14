import requests
from bs4 import BeautifulSoup
payload = {"input[pageNo]": "0", "input[pageSize]": "9", "input[sort][beginsName]": "asc",
           "input[mustWildcardFilter][teacherName-keyword]": "",
           "input[mustWildcardFilter][researchDirection-keyword]": "", "input[mustFilter][resumeType-keyword][]": "CH"}
headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
           'Accept-Encoding': 'gzip, deflate',
           'Accept-Language': 'zh-CN,zh;q=0.9',
           'Cache-Control': 'max-age=0',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
           'Connection': 'keep-alive',
           'Host': 'faculty.ccnu.edu.cn',
           'Upgrade-Insecure-Requests': '1'}
url = 'http://grzy.cug.edu.cn/KaiCao/zh_CN/index.htm'
#http://grzy.cug.edu.cn/KaiCao/zh_CN/index.htm
req = requests.get(url = url,data=payload,headers = headers)

req.encoding = 'utf-8'
req.text
req.status_code









