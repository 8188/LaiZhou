import numpy as np
import warnings
warnings.filterwarnings('ignore')
from app.data.func_store import H2FillJudge, H2LeakageCalSave, js2rd, rd2pd, H2LeakageVol
from app.data.data_format import OutputData, DiagResult, CalcResult, ModelResult, MainState, Monitor, Display, Output
from app.data.data_pipe import health_handle, rf_handle, mscred_H2, mscred_Oil, mscred_Water
from app.data.parameters import Alarm, H2_leakage, H2_health, Oil_health, Water_health, RF_All, Constant
from app.warning.logic import Hydrogen, Oil, Water, DisplayLogic, Generator
from flask import request
import simplejson as json


def trunc(value):
    if value is not None:
        return round(value, Constant.DECIMAL_INPUT_DATA)

def around(data):
    res = np.around(np.float64(data), Constant.DECIMAL_OUTPUT_DATA).squeeze().tolist()
    return [res] if data.shape[0] == 1 else res

def HOW_pred():
    
    try:
        inputData = request.get_data(as_text=True)
        inputData = json.loads(inputData)
        dataNum, collectionTime = js2rd(inputData)
        # print(dataNum)
    except:
        pass

    df_rd2pd = rd2pd()

    t, df, swt = rf_handle(
        path=RF_All.path, windows=RF_All.windows, 
        tar_fe=RF_All.tar_fe, switch_alarm=RF_All.switch_alarm,
        train_fe=RF_All.train_fe, test=RF_All.test, df_rd2pd=df_rd2pd
        )

    if df is not None:
        df_length = len(df)
        H2Lkg_lkg = np.array([[df[i][j] for i in range(df_length)] for j in range(8)])
        H2Prs_prs = np.array([df[i][8] for i in range(df_length)])
        H2Pur_pur = np.array([df[i][9] for i in range(df_length)])
        H2Hum_hum = np.array([df[i][10] for i in range(df_length)])
        OilIn_prsDif = np.array([df[i][11] for i in range(df_length)])
        OilWC_wc = np.array([df[i][12] for i in range(df_length)])
        WaterCond_cond = np.array([df[i][13] for i in range(df_length)])
        WaterPH_PH = np.array([df[i][14] for i in range(df_length)])
        WaterFlow_flow = np.array([df[i][15] for i in range(df_length)])

        if swt is not None:
            H2Pur_swt = swt[0:2]
            OilIn_swt = swt[2:6]
            oil_tank_low = swt[6]
            oil_tank_high = swt[7]
            WaterFlow_swt = swt[8:11]
            WaterCond_swt = swt[11:13]
            water_tank_low = swt[13]
            water_tank_high = swt[14]
            hyd_prs_low = swt[15]
            OilFB_fb = swt[16:18]
            outcond_high = int(swt[18] > Alarm.Water_conductivity)
            outtemp_high = int(swt[19] > Alarm.Water_outTemp)
            intemp_high = int(swt[20] > Alarm.Water_inTemp)

        flag = df_length == Constant.MIN_PREDICTABLE_DATE_LENGTH

        speed = inputData['rawDataPackage']['DEHSPEED']['srcValue']

        bGenStop, genStatus = Generator.status(speed) 

        H2Lkg_p, H2Lkg_advice, H2Lkg_level = Hydrogen.chk_lkg(
            H2Lkg_lkg, H2Prs_prs, Alarm.H2_leakage, Alarm.H2_pressure,
            Constant.MODIFICATION_FACTOR_H2_LEAKAGE, Constant.MODIFICATION_FACTOR_H2_PRESSURE,
            hyd_prs_low, H2_leakage.switch_fe, flag=flag)

        OilIn_p, OilIn_advice, OilIn_level = Oil.chk_in(
            OilIn_prsDif, Alarm.Oil_H2_pressure_diff, Constant.MODIFICATION_FACTOR_PRESSURE_DIFFERENCE, OilIn_swt, flag=flag)

        H2Pur_p, H2Pur_advice, H2Pur_level = Hydrogen.chk_pur(
            H2Pur_pur, H2Pur_swt, thr=Alarm.H2_purity, alpha=Constant.MODIFICATION_FACTOR_H2_PURITY, flag=flag)

        H2Hum_p, H2Hum_advice, H2Hum_level = Hydrogen.chk_hum(
            H2Hum_hum, thr=Alarm.H2_humidity, alpha=Constant.MODIFICATION_FACTOR_H2_HUMIDITY, flag=flag)

        OilWC_p, OilWC_advice, OilWC_level = Oil.chk_watercontent(
            OilWC_wc, thr=Alarm.Water_content, alpha=Constant.MODIFICATION_FACTOR_OIL_WATER_CONTENT, flag=flag)

        WaterFlow_p, WaterFlow_advice, WaterFlow_level = Water.chk_flow(
            WaterFlow_flow, WaterFlow_swt, thr=Alarm.Water_Flow, alpha=Constant.MODIFICATION_FACTOR_WATER_FLOW, flag=flag)

        WaterCond_p, WaterCond_advice, WaterCond_level = Water.chk_cond(
            WaterCond_cond, WaterCond_swt, thr=Alarm.Water_conductivity, 
            alpha=Constant.MODIFICATION_FACTOR_WATER_CONDUCTIVITY, flag=flag)

        WaterPH_p, WaterPH_advice, WaterPH_level = Water.chk_PH(
            WaterPH_PH, thr=Alarm.Water_PH[0], alpha=Constant.MODIFICATION_FACTOR_WATER_PH_LOW, flag=flag)

        OilFB_p, OilFB_advice, OilFB_level = Oil.chk_filterblock(OilFB_fb)


        H2_anomaly_score, H2_threshold = health_handle(
            H2_health.length, H2_health.path, H2_health.fe,
            H2_health.period, H2_health.save_path, H2_health.label,
            mscred_H2, H2_health.test, df_rd2pd
            )
        
        Oil_anomaly_score, Oil_threshold = health_handle(
            Oil_health.length, Oil_health.path, Oil_health.fe,
            Oil_health.period, Oil_health.save_path, Oil_health.label,
            mscred_Oil, Oil_health.test, df_rd2pd
            )

        Water_anomaly_score, Water_threshold = health_handle(
            Water_health.length, Water_health.path, Water_health.fe,
            Water_health.period, Water_health.save_path, Water_health.label,
            mscred_Water, Water_health.test, df_rd2pd
            )

        H2_neg_point = len(H2_anomaly_score[H2_anomaly_score > H2_threshold])
        Oil_neg_point = len(Oil_anomaly_score[Oil_anomaly_score > Oil_threshold])
        Water_neg_point = len(Water_anomaly_score[Water_anomaly_score > Water_threshold])

        H2_scores = Hydrogen.chk_health(
            H2_neg_point, H2Lkg_level, H2Pur_level, H2Hum_level)

        Oil_scores, Oil_p, Oil_advice, Oil_level = Oil.chk_health(
            Oil_neg_point, OilIn_level, OilFB_level, OilWC_level, oil_tank_low, oil_tank_high)

        Water_scores, Water_p, Water_advice, Water_level = Water.chk_health(
            Water_neg_point, WaterFlow_level, WaterCond_level, WaterPH_level,
            water_tank_low, water_tank_high, outtemp_high, outcond_high, 
            intemp_high)

        
        H2Leakage = [
            OutputData(historyMax=Alarm.H2_leakage, name='内冷水箱泄漏量', tendencyPredict=around(H2Lkg_lkg[0]), 
                predictionTime=t).__dict__,
            OutputData(historyMax=Alarm.H2_leakage, name='密封油励侧回油泄漏量', tendencyPredict=around(H2Lkg_lkg[1]), 
                predictionTime=t).__dict__,
            OutputData(historyMax=Alarm.H2_leakage, name='密封油汽侧回油泄漏量', tendencyPredict=around(H2Lkg_lkg[2]), 
                predictionTime=t).__dict__,
            OutputData(historyMax=Alarm.H2_leakage, name='封闭母线A相泄漏量', tendencyPredict=around(H2Lkg_lkg[3]), 
                predictionTime=t).__dict__,
            OutputData(historyMax=Alarm.H2_leakage, name='封闭母线B相泄漏量', tendencyPredict=around(H2Lkg_lkg[4]), 
                predictionTime=t).__dict__,
            OutputData(historyMax=Alarm.H2_leakage, name='封闭母线C相泄漏量', tendencyPredict=around(H2Lkg_lkg[5]), 
                predictionTime=t).__dict__,
            OutputData(historyMax=Alarm.H2_leakage, name='封闭母线中性点1泄漏量', tendencyPredict=around(H2Lkg_lkg[6]), 
                predictionTime=t).__dict__,
            OutputData(historyMax=Alarm.H2_leakage, name='封闭母线中性点2泄漏量', tendencyPredict=around(H2Lkg_lkg[7]), 
                predictionTime=t).__dict__,
            OutputData(historyMax=Alarm.H2_pressure, name='发电机内氢气压力', tendencyPredict=around(H2Prs_prs), 
                predictionTime=t).__dict__,
            ]
        
        OilIn = OutputData(historyMax=Alarm.Oil_H2_pressure_diff[1], historyMin=Alarm.Oil_H2_pressure_diff[0], 
            name='油氢压差', tendencyPredict=around(OilIn_prsDif), predictionTime=t).__dict__,
        H2Purity = OutputData(historyMax=Alarm.H2_purity, name='氢气纯度', tendencyPredict=around(H2Pur_pur), 
            predictionTime=t).__dict__,
        H2Humidity = OutputData(historyMax=Alarm.H2_humidity, name='氢气湿度', tendencyPredict=around(H2Hum_hum), 
            predictionTime=t).__dict__,
        H2Health = OutputData(name='氢系统', measuredValue=H2_scores).__dict__,
        OilFilterBlock = OutputData(name='油过滤器堵塞').__dict__,
        OilContent = OutputData(historyMax=Alarm.Water_content, name='密封油含水量', tendencyPredict=around(OilWC_wc), 
            predictionTime=t).__dict__,
        OilHealth = OutputData(name='油系统', measuredValue=Oil_scores).__dict__,
        WaterFlow = OutputData(historyMax=Alarm.Water_Flow, name='定冷水流量', tendencyPredict=around(WaterFlow_flow), 
            predictionTime=t).__dict__,
        WaterConductivity = OutputData(historyMax=Alarm.Water_conductivity, name='定冷水电导率', 
            tendencyPredict=around(WaterCond_cond), predictionTime=t).__dict__,
        WaterPH = OutputData(historyMax=Alarm.Water_PH[1], historyMin=Alarm.Water_PH[0], name='定冷水PH值', 
            tendencyPredict=around(WaterPH_PH), predictionTime=t).__dict__,
        WaterHealth = OutputData(name='水系统', measuredValue=Water_scores).__dict__,

        calcResult = CalcResult(
            H2Leakage=H2Leakage, OilIn=OilIn, H2Purity=H2Purity, 
            H2Humidity=H2Humidity, H2Health=H2Health, OilFilterBlock=OilFilterBlock, 
            OilContent=OilContent, OilHealth=OilHealth, WaterFlow=WaterFlow, 
            WaterConductivity=WaterConductivity, WaterPH=WaterPH, WaterHealth=WaterHealth).__dict__,

        diagResult = []
        
        for i in range(len(H2Lkg_advice)):
            if H2Lkg_advice[i]['adv'][0]:
                diagResult.append(
                    DiagResult(
                        content=list(H2Lkg_p.keys())[i], level=H2Lkg_level, part='氢系统', 
                        alarmValue=list(H2Lkg_p.values())[i], substdCode='10MKG71CP101',
                        handleSuggest=H2Lkg_advice[i]['adv'][0]).__dict__,
                )

        for i in range(len(OilIn_advice)):
            if OilIn_advice[i]['adv'][0]:
                diagResult.append(
                    DiagResult(
                        content=list(OilIn_p.keys())[i], level=OilIn_level, part='油系统', 
                        alarmValue=list(OilIn_p.values())[i], substdCode='10MKW10CP006',
                        handleSuggest=OilIn_advice[i]['adv'][0]).__dict__,
                )

        if H2Pur_advice[0]['adv'][0]:
            diagResult.append(
                DiagResult(
                    content=list(H2Pur_p.keys())[0], level=H2Pur_level, part='氢系统', 
                    alarmValue=list(H2Pur_p.values())[0], substdCode='10MKG60CQ101',
                    handleSuggest=H2Pur_advice[0]['adv'][0]).__dict__,
            )
        if H2Hum_advice[0]['adv'][0]:
            diagResult.append(
                DiagResult(
                    content=list(H2Hum_p.keys())[0], level=H2Hum_level, part='氢系统', 
                    alarmValue=list(H2Hum_p.values())[0], substdCode='10MKG61CM102',
                    handleSuggest=H2Hum_advice[0]['adv'][0]).__dict__,
            )
        
        for i in range(len(OilFB_advice)):
            if OilFB_advice[i]['adv'][0]:
                diagResult.append(
                    DiagResult(
                        content=list(OilFB_p.keys())[i], level=OilFB_level[i], part='油系统', 
                        alarmValue=list(OilFB_p.values())[i], substdCode='10MKW10CP004',
                        handleSuggest=OilFB_advice[i]['adv'][0]).__dict__,
                )

        if OilWC_advice[0]['adv'][0]:
            diagResult.append(
                DiagResult(
                    content=list(OilWC_p.keys())[0], level=OilWC_level, part='油系统', 
                    alarmValue=list(OilWC_p.values())[0], handleSuggest=OilWC_advice[0]['adv'][0]).__dict__,
            )
        if WaterFlow_advice[0]['adv'][0]:
            diagResult.append(
                DiagResult(
                    content=list(WaterFlow_p.keys())[0], level=WaterFlow_level, part='水系统', 
                    alarmValue=list(WaterFlow_p.values())[0], substdCode='10MKF50CF101',
                    handleSuggest=WaterFlow_advice[0]['adv'][0]).__dict__,
            )
        if WaterCond_advice[0]['adv'][0]:
            diagResult.append(
                DiagResult(
                    content=list(WaterCond_p.keys())[0], level=WaterCond_level, part='水系统', 
                    alarmValue=list(WaterCond_p.values())[0], substdCode='10MKF13CQ101',
                    handleSuggest=WaterCond_advice[0]['adv'][0]).__dict__,
            )
        if WaterPH_advice[0]['adv'][0]:
            diagResult.append(
                DiagResult(
                    content=list(WaterPH_p.keys())[0], level=WaterPH_level, part='水系统', 
                    alarmValue=list(WaterPH_p.values())[0], handleSuggest=WaterPH_advice[0]['adv'][0]).__dict__,
            )

        for i in range(len(Oil_advice)):
            if Oil_advice[i]['adv'][0]:
                diagResult.append(
                    DiagResult(
                        content=list(Oil_p.keys())[i], level=Oil_level[i], part='油系统', 
                        alarmValue=list(Oil_p.values())[i], handleSuggest=Oil_advice[i]['adv'][0]).__dict__,
                )

        Water_advice_code = None
        for i in range(len(Water_advice)):
            if Water_advice[i]['adv'][0]:
                if i == 2:
                    Water_advice_code = '10MKF13CT303'
                elif i == 4:
                    Water_advice_code = '10MKF16CT301'

                diagResult.append(
                    DiagResult(
                        content=list(Water_p.keys())[i], level=Water_level[i], part='水系统', 
                        alarmValue=list(Water_p.values())[i], substdCode=Water_advice_code,
                        handleSuggest=Water_advice[i]['adv'][0]).__dict__,
                )

        diagResult.append(
            DiagResult(content=genStatus, level=Constant.LEVEL_GENERATOR_STATUS, alarmValue=bGenStop).__dict__
        )

        hydrogenLeakageVol = H2LeakageVol(Constant.VOLUME_GENERATOR)
        hydrogenLeakageVol = trunc(H2LeakageCalSave(hydrogenLeakageVol, collectionTime))
        
        hydrogenLeakage = DisplayLogic.lkg(list(H2Lkg_p.values()), hydrogenLeakageVol)
        filterBlock = DisplayLogic.fbl(list(OilFB_p.values()))
        generatorOilIn = DisplayLogic.oin(list(OilIn_p.values()))
        hydrogenQuality = DisplayLogic.h2q(list(H2Pur_p.values()), list(H2Hum_p.values()))
        oilQuality = DisplayLogic.oilq(list(OilWC_p.values())) 
        waterFlowLow = DisplayLogic.watf(list(WaterFlow_p.values()))
        waterQuality = DisplayLogic.watq(list(WaterCond_p.values()), list(WaterPH_p.values()))
        systemMainstate = [
            MainState(name='漏氢状态', value=hydrogenLeakage[0], level=hydrogenLeakage[1]).__dict__,
            MainState(name='漏液状态', value=generatorOilIn[0], level=generatorOilIn[1]).__dict__,
            MainState(name='定冷水流量', value=waterFlowLow[0], level=waterFlowLow[1]).__dict__,
            MainState(name='线棒状态', value='正常', level=0).__dict__,
            MainState(name='氢气品质', value=hydrogenQuality[0], level=hydrogenQuality[1]).__dict__,
            MainState(name='密封油品质', value=oilQuality[0], level=oilQuality[1]).__dict__,
            MainState(name='定冷水品质', value=waterQuality[0], level=waterQuality[1]).__dict__,
            MainState(name='过滤器堵塞', value=filterBlock[0], level=filterBlock[1]).__dict__,
            ]

        hydrogenPressure = trunc(inputData['rawDataPackage']['10MKG71CP101']['srcValue'])
        hydrogenPurity = trunc(inputData['rawDataPackage']['10MKG60CQ101']['srcValue'])
        hydrogenHumidity = trunc(inputData['rawDataPackage']['10MKG61CM102']['srcValue'])
        hydrogenMainstate = [
            MainState(name='漏氢速率', value=hydrogenLeakageVol, unit='m3/d', level=None).__dict__,
            MainState(name='压力', value=hydrogenPressure, unit='MPa', level=None).__dict__,
            MainState(name='纯度', value=hydrogenPurity, unit='%', level=None).__dict__,
            MainState(name='露点温度', value=hydrogenHumidity, unit='℃', level=None).__dict__,
            ]

        oilH2PresDiff = trunc(inputData['rawDataPackage']['10MKW10CP006']['srcValue'])
        vacuumTankLev = trunc(inputData['rawDataPackage']['10MKW10CL101']['srcValue'])
        floaterTankLev = trunc(inputData['rawDataPackage']['10MKW10CL102']['srcValue'])
        expansionSlotLev = '正常' if inputData['rawDataPackage']['10MKW32CL001']['srcValue'] == 0 else '高'
        oilMainstate = [
            MainState(name='油氢压差', value=oilH2PresDiff, unit='KPa', level=None).__dict__,
            MainState(name='真空油箱液位', value=vacuumTankLev, unit='mm', level=None).__dict__,
            MainState(name='浮子油箱液位', value=floaterTankLev, unit='mm', level=None).__dict__,
            MainState(name='扩大槽液位', value=expansionSlotLev, unit=None, level=None).__dict__,
            ]

        genInWaterTemp = trunc(inputData['rawDataPackage']['10MKF16CT301']['srcValue'])
        statorWatInPressure = trunc(inputData['rawDataPackage']['10MKF40CP100']['srcValue'])
        statorWatTankLev = trunc(inputData['rawDataPackage']['10MKF16CL101']['srcValue'])
        statorWatFlow = trunc(inputData['rawDataPackage']['10MKF40CF101']['srcValue'])
        waterMainstate = [
            MainState(name='出水温度', value=genInWaterTemp, unit='℃', level=None).__dict__,
            MainState(name='进水压力', value=statorWatInPressure, unit='KPa', level=None).__dict__,
            MainState(name='水箱液位', value=statorWatTankLev, unit='mm', level=None).__dict__,
            MainState(name='流量差压', value=statorWatFlow, unit='KPa', level=None).__dict__,
            ]

        hydrogenMonitor = Monitor(mainState=hydrogenMainstate).__dict__
        oilMonitor = Monitor(mainState=oilMainstate).__dict__
        waterMonitor = Monitor(mainState=waterMainstate).__dict__

        display = Display(systemMainInformation=systemMainstate, hydrogenMonitor=hydrogenMonitor, oilMonitor=oilMonitor, 
            waterMonitor=waterMonitor).__dict__

        modelResult = ModelResult(calcResult=calcResult[0], diagResult=diagResult, display=display).__dict__

        output = Output(
            modelName=Constant.MODEL_NAME, owner=Constant.OWNER, 
            collectionTime=inputData['collectionTime'], 
            pltType=inputData['pltType'], 
            pltCode=inputData['pltCode'], 
            setCode=inputData['setCode'], 
            modelResult=modelResult).__dict__

    else: 
        output = Output(
            modelName=Constant.MODEL_NAME, owner=Constant.OWNER, collectionTime=inputData['collectionTime'], 
            pltType=inputData['pltType'], pltCode=inputData['pltCode'], setCode=inputData['setCode'], 
            modelResult=ModelResult(resultState=Constant.FLAG_NULL_MODEL_RESULT).__dict__).__dict__

    return output


def redisTest():
    inputData = request.get_data(as_text=True)
    inputData = json.loads(inputData)
    dataNum = js2rd(inputData)
    return

