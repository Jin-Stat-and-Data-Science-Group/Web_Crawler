import os
os.getcwd()
dat1 = pd.read_excel("../data/caizheng.xlsx")
for info in os.listdir('../data')[2:]:
    dat = pd.read_excel('../data/' + info)
    dat1 = pd.concat([dat1,dat],ignore_index=True)
dat1.to_excel("../data/collegeConcat.xlsx")
