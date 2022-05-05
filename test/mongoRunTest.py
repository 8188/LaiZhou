#!usr/bin/env python  
#-*- coding:utf-8 _*-  
""" 
@author:HEWENHUI 
@file: RunningTest.py 
@time: 2021/06/03 
"""

import json
import datetime
import time
import requests

# from GeneratorDiagnosis.utils.PropertiesUtil import PropertiesUtil


from pymongo import MongoClient
# 1.Connect to database service
connection = MongoClient('localhost')
# 2.Connect to the database PowerStationData. If there is no database will be created.
NewFormatData = connection.LaiZhouData # NewFormatData
emp202 = NewFormatData.TL00101_20210917AD # T00202_202107


class HttpPostData():
    def main():

        if(1):

            try:
                connection = MongoClient('localhost')
            except Exception:
                powerCodeData = None
                print("redis connection failed")
            else:
                i = 0
                j = 0
                for powerCodeData in emp202.find({}, {"_id": 0, 'pltType': 1, 'pltCode': 1, 'setCode': 1,
                                                    "collectionTime": 1, 'rawDataPackage': 1}):
                    i = i + 1

                    StartTime = datetime.datetime.now()
                    # print(powerCodeData["setCode"])
                    dataTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(powerCodeData.get("collectionTime"))))
                    print('第%d个数据，dataTime:%s ' % (i, dataTime))

                    powerCodeData['modelName'] = None
                    powerCodeData['owner'] = None
                    powerCodeData['addtionalInfo'] = {}
                    powerCodeData['modelResult '] = {'calcResult':{}, 'diagResult':{}, 'display':{}}

                    url = 'http://127.0.0.1:8990/HOW' # 'http://192.168.11.41:8990/HOW'   # 氢油水测试 HOW generatorDiagnosis
                    # print('type(ReadRedis()):' ,type(ReadRedis())) generatorStatorTemp
                    # powerCodeData = {}
                    r = requests.post(url, data= json.dumps(powerCodeData))
                    if(r.content):
                        # js_data = json.loads(r.content)
                        # with open("./test3.json",'w',encoding='utf-8') as f:
                        #     json.dump(js_data, f)
                        #print(js_data)
                        print('----------------------------------------------------Done!')

                    EndTime = datetime.datetime.now()
                    print('TimeCost:', (EndTime-StartTime))

                    # if(i > 105):
                    #     break
                    time.sleep(0.1)

            time.sleep(0.1)


    if __name__ == '__main__':
        while True:
            main()

