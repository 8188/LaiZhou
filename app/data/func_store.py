from os import times
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

    timeStamp = js['collectionTime']
    collectionTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timeStamp)) # +3600*8

    H2LeakageDataCodesBegin = ['10AIRCP001', '10MKG71CP101', '10MKG80CT301', '10MKG80CT304'] # from end of fill H2
    H2LeakageColumnNamesBegin = ['B', 'P', 't_steam', 't_excitation']
    H2LeakageDataCodes = H2LeakageDataCodesBegin + ['10MKG80CF101']
    H2LeakageColumnNames = H2LeakageColumnNamesBegin + ['volFilled']

    data_H2LeakgeVol = []
    for c in H2LeakageDataCodes:
        if c in list(rawDataPackage.keys()):
            data_H2LeakgeVol.append(rawDataPackage[c]['srcValue'])

    if len(data_H2LeakgeVol)==len(H2LeakageDataCodes):
        H2LeakageData = rdb.hget(Config.TABLE_H2_LEAKAGE_DATA, Config.KEY_H2_LEAKAGE_DATA)
        H2LeakageData = list(eval(H2LeakageData)) if H2LeakageData else []

        if data_H2LeakgeVol['10MKG80CF101'] > Constant.H2_FILL_JUDGE_UPPER_BOUND:
            rdb.hdel(Config.TABLE_H2_LEAKAGE_DATA, Config.KEY_H2_LEAKAGE_DATA)
            rdb.hdel(Config.TABLE_H2_LEAKAGE_DATA_BEGIN, Config.KEY_H2_LEAKAGE_DATA_BEGIN) # delete fill H2 as well
        elif data_H2LeakgeVol['10MKG80CF101'] < Constant.H2_FILL_JUDGE_LOWER_BOUND:
            redisHSet(
                rdb=rdb, maxCapacity=Constant.MAX_CAPACITY_TABLE_H2_LEAKAGE_DATA, tableName=Config.TABLE_H2_LEAKAGE_DATA,
                key=Config.KEY_H2_LEAKAGE_DATA, dataNow=data_H2LeakgeVol, columnNames=H2LeakageColumnNames,
                collectionTime=timeStamp, dataHGet=H2LeakageData, expireTime=Constant.TABLE_H2_LEAKAGE_DATA_EXPIRE_TIME)

    H2LeakageDataBegin = rdb.hget(Config.TABLE_H2_LEAKAGE_DATA_BEGIN, Config.KEY_H2_LEAKAGE_DATA_BEGIN)
    H2LeakageDataBegin = list(eval(H2LeakageDataBegin)) if H2LeakageDataBegin else []
    if len(H2LeakageDataBegin) < Constant.MAX_CAPACITY_TABLE_H2_LEAKAGE_BEGIN:
        data_H2LeakgeVolBegin = data_H2LeakgeVol[:len(H2LeakageDataCodesBegin)] 

        if len(data_H2LeakgeVolBegin)==len(H2LeakageDataCodesBegin):
            redisHSet(
                rdb=rdb, maxCapacity=Constant.MAX_CAPACITY_TABLE_H2_LEAKAGE_DATA_BEGIN, tableName=Config.TABLE_H2_LEAKAGE_DATA_BEGIN,
                key=Config.KEY_H2_LEAKAGE_DATA_BEGIN, dataNow=data_H2LeakgeVolBegin, columnNames=H2LeakageColumnNamesBegin,
                collectionTime=timeStamp, dataHGet=H2LeakageDataBegin, expireTime=Constant.TABLE_H2_LEAKAGE_BEGIN_EXPIRE_TIME)
    elif len(H2LeakageDataBegin) == Constant.MAX_CAPACITY_TABLE_H2_LEAKAGE_BEGIN:
        tempB, tempP, tempT_steam, tempT_excitation = [0] * 4
        for i in range(Constant.MAX_CAPACITY_TABLE_H2_LEAKAGE_BEGIN):
            tempB += H2LeakageDataBegin[i]['B']
            tempP += H2LeakageDataBegin[i]['P']
            tempT_steam += H2LeakageDataBegin[i]['t_steam']
            tempT_excitation += H2LeakageDataBegin[i]['t_excitation']
        tempB /= Constant.MAX_CAPACITY_TABLE_H2_LEAKAGE_BEGIN
        tempP /= Constant.MAX_CAPACITY_TABLE_H2_LEAKAGE_BEGIN
        tempT_steam /= Constant.MAX_CAPACITY_TABLE_H2_LEAKAGE_BEGIN
        tempT_excitation /= Constant.MAX_CAPACITY_TABLE_H2_LEAKAGE_BEGIN
        dataMean = [tempB, tempP, tempT_steam, tempT_excitation]

        res = dict(zip(['time'] + H2LeakageColumnNamesBegin, [timeStamp] + dataMean))

        rdb.hset(Config.TABLE_H2_LEAKAGE_DATA_BEGIN, Config.KEY_H2_LEAKAGE_DATA_BEGIN, str(H2LeakageDataBegin + [res]))

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
    H2LeakageDataBegin = rdb.hget(Config.TABLE_H2_LEAKAGE_DATA_BEGIN, Config.KEY_H2_LEAKAGE_DATA_BEGIN)

    if H2LeakageData:
        H2LeakageData = eval(H2LeakageData)

        if H2LeakageData[-1]['P'] > Constant.H2_PRESSURE_MIN:
            if len(H2LeakageData) >= Constant.H2_LEAKAGE_DATA_FILTER_TIME:  
                P1 = H2LeakageDataBegin[-1]['P']
                t1 = (H2LeakageDataBegin[-1]['t_steam'] + H2LeakageDataBegin[-1]['t_excitation']) / 2
                B1 = H2LeakageDataBegin[-1]['B'] * Constant.KPA_TO_MPA_FACTOR

                P2, t2, B2 = [0] * 3
                for i in range(-1, -Constant.H2_LEAKAGE_DATA_FILTER_TIME - 1, -1):
                    P2 += H2LeakageData[i]['P']
                    t2 += H2LeakageData[i]['t_steam'] + H2LeakageData[i]['t_excitation']
                    B2 += H2LeakageData[i]['B']
                P2 /= Constant.H2_LEAKAGE_DATA_FILTER_TIME
                t2 /= Constant.H2_LEAKAGE_DATA_FILTER_TIME * 2
                B2 *= Constant.KPA_TO_MPA_FACTOR / Constant.H2_LEAKAGE_DATA_FILTER_TIME
                # print(P1, B1, t1, P2, B2, t2)
                interval = (H2LeakageData[-1] - H2LeakageDataBegin[-1]) / 3600 + 1
                leakageVolume = Constant.GAS_CONSTANT * genVol / interval * Constant.H2_LEAKAGE_MODIFICATION_FACTOR \
                    * ((P1 + B1) / (Constant.C_TO_K_FACTOR + t1) - (P2 + B2) / (Constant.C_TO_K_FACTOR + t2))
                
                return max(leakageVolume, 0)
    return 0
