import simplejson as json
import pandas as pd
import time
import datetime
import redis
from config import Config
from app.data.parameters import Constant

rdb = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, password=Config.REDIS_PASSWORD, 
    decode_responses=True, db=Config.REDIS_DATABASE)

def load_dic():
    with open('app/static/codemap.json', 'r', encoding='utf-8') as js:
        dic = json.load(js)
    return dic

dic = load_dic()

def redisHSet(rdb, maxCapacity, tableName, key, dataNow, columnNames, collectionTime, dataHGet, expireTime):
    res = dict(zip(['time'] + columnNames, [collectionTime] + dataNow))
    # print(tableName, len(dataHGet))
    if len(dataHGet) > maxCapacity:
        rdb.hset(tableName, key, str(dataHGet[1:] + [res]))
    else:
        rdb.hset(tableName, key, str(dataHGet + [res]))
    rdb.expire(tableName, expireTime)

def js2rd(js):
    rawDataPackage = js['rawDataPackage']
    substdCode = []
    srcValue = []
    #print(rawDataPackage.keys())
    
    for c in dic:
        if c in list(rawDataPackage.keys()): 
            substdCode.append(rawDataPackage[c]['srcCode']) # 'substdCode'
            srcValue.append(rawDataPackage[c]['srcValue'])
        else:
            substdCode.append(c)
            srcValue.append(None)

    collectionTime = js['collectionTime']
    collectionTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(collectionTime)) # +3600*8

    data_H2LeakgeVol = []
    H2LeakageDataCodes = ['10AIRCP001', '10MKG71CP101', '10MKG80CT301', '10MKG80CT304']
    for c in H2LeakageDataCodes:
        if c in list(rawDataPackage.keys()):
            data_H2LeakgeVol.append(rawDataPackage[c]['srcValue'])

    if len(data_H2LeakgeVol)==len(H2LeakageDataCodes):
        H2LeakageData = rdb.hget(Config.TABLE_H2_LEAKAGE_DATA, Config.KEY_H2_LEAKAGE_DATA)
        H2LeakageData = list(eval(H2LeakageData)) if H2LeakageData else []
         
        redisHSet(
            rdb=rdb, maxCapacity=Constant.MAX_CAPACITY_TABLE_H2_LEAKAGE_DATA, tableName=Config.TABLE_H2_LEAKAGE_DATA,
            key=Config.KEY_H2_LEAKAGE_DATA, dataNow=data_H2LeakgeVol, columnNames=['B', 'P', 't_steam', 't_excitation'],
            collectionTime=collectionTime, dataHGet=H2LeakageData, expireTime=Constant.TABLE_H2_LEAKAGE_DATA_EXPIRE_TIME)

    dataTemp = rdb.hget(Config.TABLE_MAIN, Config.KEY_MAIN)
    if not dataTemp:
        dataTemp = []
    else:
        dataTemp = list(eval(dataTemp))
        if str(datetime.datetime.strptime(dataTemp[-1]['time'], "%Y-%m-%d %H:%M:%S") + datetime.timedelta(minutes=5)) \
            < collectionTime:
            rdb.delete(Config.TABLE_MAIN)
            dataTemp = []
    
    redisHSet(
        rdb=rdb, maxCapacity=Constant.MAX_CAPACITY_TABLE_MAIN, tableName=Config.TABLE_MAIN, key=Config.KEY_MAIN,
        dataNow=srcValue, columnNames=substdCode, collectionTime=collectionTime, dataHGet=dataTemp, 
        expireTime=Constant.TABLE_MAIN_EXPIRE_TIME)

    return len(dataTemp), collectionTime

def rd2pd():
    dataTemp = rdb.hget(Config.TABLE_MAIN, Config.KEY_MAIN)
    if dataTemp:
        dataTemp = eval(dataTemp)[-Constant.MAX_CAPACITY_TABLE_MAIN:]
    else:
        return None, None

    value = []
    for data in dataTemp:
        value.append(list(data.values()))
    df = pd.DataFrame(value, columns=list(data.keys()))
    # df = pd.DataFrame.from_dict(dataTemp)
    df = df.rename(columns=dic)
    genRunning = False if (df['发电机频率'] > Constant.MAX_SPEED_GENERATOR_RUN).any() \
        or (df['发电机频率'] < Constant.MIN_SPEED_GENERATOR_RUN).any() else True

    return df, genRunning

def H2LeakageVol(genVol):
    H2LeakageData = rdb.hget(Config.TABLE_H2_LEAKAGE_DATA, Config.KEY_H2_LEAKAGE_DATA)
    if H2LeakageData:
        H2LeakageData = eval(H2LeakageData)
        if H2FillJudge():
            return 0
            
        if len(H2LeakageData) > 2 * Constant.H2_LEAKAGE_DATA_FILTER_TIME:  
            P1, t1, B1, P2, t2, B2 = [0] * 6

            for i in range(Constant.H2_LEAKAGE_DATA_FILTER_TIME):
                P2 += H2LeakageData[i]['P']
                t2 += H2LeakageData[i]['t_steam'] + H2LeakageData[i]['t_excitation']
                B2 += H2LeakageData[i]['B'] 
            P2 /= Constant.H2_LEAKAGE_DATA_FILTER_TIME
            t2 /= Constant.H2_LEAKAGE_DATA_FILTER_TIME * 2
            B2 *= Constant.KPA_TO_MPA_FACTOR / Constant.H2_LEAKAGE_DATA_FILTER_TIME

            for i in range(-1, -Constant.H2_LEAKAGE_DATA_FILTER_TIME - 1, -1):
                P1 += H2LeakageData[i]['P']
                t1 += H2LeakageData[i]['t_steam'] + H2LeakageData[i]['t_excitation']
                B1 += H2LeakageData[i]['B']
            P1 /= Constant.H2_LEAKAGE_DATA_FILTER_TIME
            t1 /= Constant.H2_LEAKAGE_DATA_FILTER_TIME * 2
            B1 *= Constant.KPA_TO_MPA_FACTOR / Constant.H2_LEAKAGE_DATA_FILTER_TIME
            # print(P1, B1, t1, P2, B2, t2)
            leakageVolume = Constant.GAS_CONSTANT * genVol \
                * ((P1 + B1) / (Constant.C_TO_K_FACTOR + t1) - (P2 + B2) / (Constant.C_TO_K_FACTOR + t2))
            
            return max(leakageVolume, 0)
    return 0

def H2LeakageCalSave(H2LeakageVol, collectionTime):
    H2LeakageCal = rdb.hget(Config.TABLE_H2_LEAKAGE_CAL, Config.KEY_H2_LEAKAGE_CAL)
    H2LeakageCal = list(eval(H2LeakageCal)) if H2LeakageCal else []

    length = len(H2LeakageCal)
    if length > Constant.H2_LEAKAGE_CAL_FILTER_TIME:
        H2LeakageVol = max(H2LeakageCal[0]['leakage'] + (H2LeakageVol - H2LeakageCal[-1]['leakage']) / (length + 1), 0)
    H2LeakageVol *= Constant.H2_LEAKAGE_MODIFICATION_FACTOR
    # print(H2LeakageVol)    
    redisHSet(
        rdb=rdb, maxCapacity=Constant.MAX_CAPACITY_TABLE_H2_LEAKAGE_CAL, tableName=Config.TABLE_H2_LEAKAGE_CAL,
        key=Config.KEY_H2_LEAKAGE_CAL, dataNow=[H2LeakageVol], columnNames=['leakage'],
        collectionTime=collectionTime, dataHGet=H2LeakageCal, expireTime=Constant.TABLE_H2_LEAKAGE_CAL_EXPIRE_TIME)

    return H2LeakageVol

def H2FillJudge():
    H2LeakageCal = rdb.hget(Config.TABLE_H2_LEAKAGE_CAL, Config.KEY_H2_LEAKAGE_CAL)
    if H2LeakageCal:
        H2LeakageCal = eval(H2LeakageCal)
        count = 0
        if len(H2LeakageCal) > Constant.H2_FILL_JUDGE_NUMS:
            for i in range(1, Constant.H2_FILL_JUDGE_NUMS + 1):
                count += H2LeakageCal[i]['leakage'] > H2LeakageCal[i-1]['leakage']
            if count > Constant.H2_FILL_JUDGE_NUMS * Constant.H2_FILL_JUDGE_RATIO:
                return True
    return False