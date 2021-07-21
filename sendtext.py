import requests
import json
import re
import glob
import os 


filesList = glob.glob('new')
filesPath = os.path.join('new', '*')
files = sorted(glob.iglob(filesPath), key=os.path.getctime, reverse=True)

filesListTxt = glob.glob(files[0])
filesPathTxt = os.path.join(files[0], '*')
filesTxt = sorted(glob.iglob(filesPathTxt), key=os.path.getctime, reverse=True)

lst = []

with open(filesTxt[0], "r") as file:
    for last_line in file:
        pass

f=open(filesTxt[0])
lines=f.readlines()
testName = lines[2].split('Run:', 1)[1]
lst.append(re.split(r'\t+', last_line))
payload = {'test_name': testName, 'count': lst[0][0], 'force': lst[0][1], 'displacement': lst[0][2]}
headers = {'content-type': 'application/json'}


g = requests.post('http://localhost:5000/api', data=json.dumps(payload), headers=headers)
print("Data sent")