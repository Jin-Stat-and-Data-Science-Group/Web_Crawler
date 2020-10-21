import os
os.getcwd()
dat1 = pd.read_excel("../data/城市与环境科学学院.xlsx")
for info in os.listdir('../data')[2:]:
    dat = pd.read_excel('../data/' + info)
    dat1 = pd.concat([dat1,dat],ignore_index=True)
dat1[['学院',"姓名","职称","个人主页url"]].to_excel("../data/teacherlisturl.xlsx")#导出所有教师的url信息