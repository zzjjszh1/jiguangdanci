
# coding: utf-8

# In[101]:


import requests;
import os;
import json;
from datetime import datetime;
import zlib
import pytz
tz = pytz.timezone(pytz.country_timezones('cn')[0])
import pandas as DF


# In[102]:


def resolveRawHeader(data):
    headers={}
    uri=""
    host=""
    ending = False
    body = ""
    timestamp_str = ""
    cookies={}
    for i in data:
        if i.startswith("POST") or i.startswith("GET"):
            uri = i.split(" ")[1]
            par = uri.split("?")[1]
            if(par.find("ts")>=0):
                for j in par.split("&"):
                    if(j.startswith("ts")):
                        timestamp_str=datetime.fromtimestamp(int(j.split("=")[1])/1000,tz=tz)
        elif (i.startswith("cookie") or i.startswith("Cookie")):
            temp = i[7:].split("&")
            for cookie_sector in temp:
                cookie_spliter =  cookie_sector.find("=")
                cookie_field_name = cookie_sector[0:cookie_spliter]
                cookie_field_value = cookie_sector[cookie_spliter+1:]
                cookies[cookie_field_name] = cookie_field_value
        elif(not ending):
            if(i==""):
                ending = True
                continue
            field = i.split(": ")
            fieldname = field[0]
            fieldvalue = field[1]
            if(fieldname == 'Host'):
                host = fieldvalue
            elif(fieldname == 'Content-Length' or fieldname == 'content-length'):
                pass
            else:
                headers[fieldname] = fieldvalue   
        else:
            body = i 
    url = "https://"+host+uri
    if("accept-encoding" in headers):
        headers["accept-encoding"]="gzip,deflate"
    else:
        headers["Accept-Encoding"]="gzip,deflate"
    print(url)
    print(timestamp_str)
    return (url,headers,cookies,body)


# In[103]:


# for pathname,foldername,filenames in os.walk("./data"):
for pathname,foldername,filenames in os.walk("/storage/emulated/0/HttpCanary/download"):
    for filename in filenames:
        if(not filename.find("raw")>=0):continue
        print(os.path.join(pathname,filename))
        raw_packet = open(os.path.join(pathname,filename)).read()
        raw_packet = raw_packet.split("\n")
        url,headers,cookies,body = resolveRawHeader(raw_packet)
        break


# In[104]:


chooseopt = input("today list(1)/collect list(2)")
if(chooseopt=='1'):
    url = "https://qiniu-api.jiguangdanci.com/user/today-cache-simple"
if(chooseopt=='2'):
    url = "https://qiniu-api.jiguangdanci.com/user/word-collection-show"
r = requests.post(url,headers=headers,cookies=cookies,data=body)
WordList = json.loads(r.text)["data"]["words"]


# In[105]:


url = "https://qiniu-api.jiguangdanci.com/user/showWordsDetails"
body = "JIGUANG_REQUEST_ENCODE=JSON_IN_ENCODED_BODY&JIGUANG_REQUEST_BODY=%%7B%%22wordId%%22%%3A%s%%7D"
WordListDetailed = []
for word in WordList:
    r = requests.post(url,headers=headers,cookies=cookies,data=body%word["id"])
    word_with_detail = json.loads(r.text)["data"]["word"]
    url2 = "https://qiniu-file.jiguangdanci.com/words/%s.json"%word["word"]
    r = requests.get(url2,headers=headers,cookies=cookies)
    if(r.status_code==200):
        word_detail_add = json.loads(r.text)
        word_with_detail["vedio"] = []
        word_with_detail["detailid"] = word_detail_add["data"]["id"]
        if(word_detail_add["data"]["playUrl"]):
            for vediourl in json.loads(word_detail_add["data"]["playUrl"]):
                word_with_detail["vedio"].append(vediourl["PlayURL"])
    WordListDetailed.append(word_with_detail)


# In[106]:


outputline=""
for i in WordListDetailed:
    outputline+=i["word"]+"\n"
    outputline+="发音：["+i["phoneticSymbol"]+"]\n\n"
    outputline+="释义："+i["definition"]+"\n"
    outputline+="例句："+i["sampleSentence"]+"\n"
    outputline+="例句释义："+i["sampleSentenceTranslation"]+"\n"
    outputline+="例句来源："+i["sampleSentenceSource"]+"\n\n"
    if("vedio"  in i ):
        if(len(i["vedio"])>0):
            outputline+="单词例句视频：\n"
            num=0
            for j in i["vedio"]:
                num+=1
                outputline+="播放地址%d:  "%(num)+j+"\n"
    outputline+="-------------------------------\n\n\n"


# In[107]:


for i in range(1,1000):
    if(i==1):
        filename="/storage/emulated/0/Download/待导入印象笔记的文件.txt"
    else:
        filename="/storage/emulated/0/Download/待导入印象笔记的文件%d.txt"%(i)
    if(os.path.exists(filename)):
        pass
    else:
        break
open(filename,"w").write(outputline)
print(outputline)

