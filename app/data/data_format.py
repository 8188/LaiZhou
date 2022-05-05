class OutputData(object):
    def __init__(self, historyMax=None, historyMin=None, measuredValue=None, 
                 name=None, statePredict=None, tendencyPredict=None, 
                 predictionTime=None, theoretic=None, substdCode=None):
        super().__init__()
        self.historyMax = historyMax
        self.historyMin = historyMin
        self.measuredValue = measuredValue
        self.name = name
        self.statePredict = statePredict
        self.tendencyPredict = tendencyPredict
        self.predictionTime = predictionTime
        self.theoretic = theoretic
        self.substdCode = substdCode

class DiagResult(object):
    def __init__(self, content=None, level=None, part=None, alarmValue=None, 
                 pltType=None, pltCode=None, setCode=None, substdCode=None, 
                 srcTime=None, handleSuggest=None, systemCategory=None, 
                 branch=None, Type=None, rawData=None):
        super().__init__()
        self.content = content
        self.level = level
        self.part = part
        self.alarmValue = alarmValue
        self.pltType = pltType
        self.pltCode = pltCode
        self.setCode = setCode
        self.substdCode = substdCode
        self.srcTime = srcTime
        self.handleSuggest = handleSuggest
        self.systemCategory = systemCategory
        self.branch = branch
        self.type = Type
        self.rawData = rawData or {}

class CalcResult(object):
    def __init__(self, H2Leakage=None, OilIn=None, H2Purity=None, 
                 H2Humidity=None, H2Health=None, OilFilterBlock=None, 
                 OilContent=None, OilHealth=None, WaterFlow=None, 
                 WaterConductivity=None, WaterPH=None, WaterHealth=None):
        super().__init__()
        self.H2Leakage = H2Leakage
        self.OilIn = OilIn
        self.H2Purity = H2Purity
        self.H2Humidity = H2Humidity
        self.H2Health = H2Health
        self.OilFilterBlock = OilFilterBlock
        self.OilContent = OilContent
        self.OilHealth = OilHealth
        self.WaterFlow = WaterFlow
        self.WaterConductivity = WaterConductivity
        self.WaterPH = WaterPH
        self.WaterHealth = WaterHealth

class ModelResult(object):
    def __init__(self, calcResult=None, diagResult=None, display=None, resultState=1):
        super().__init__()
        self.calcResult = calcResult or {}
        self.diagResult = diagResult 
        self.display = display or {}
        self.resultState = resultState
        
class MainState(object):
    def __init__(self, name=None, value=None, unit=None, level=None, information=None):
        super().__init__()
        self.name = name
        self.value = value
        self.unit = unit
        self.level = level
        self.information = information

class Monitor(object):
    def __init__(self, mainState=None, graphicDisplay=None, moduleKeyInformation=None):
        super().__init__()
        self.mainState = mainState or {}
        self.graphicDisplay = graphicDisplay or {}
        self.moduleKeyInformation = moduleKeyInformation or {}

class Display(object):
    def __init__(self, pltType=None, pltCode=None, setCode=None, 
                 dataTime=None, healthIndex=None, systemKeyInformation=None, 
                 systemMainInformation=None, hydrogenMonitor=None,
                 oilMonitor=None, waterMonitor=None):
        super().__init__()
        self.pltType = pltType
        self.pltCode = pltCode
        self.setCode = setCode
        self.dataTime = dataTime
        self.healthIndex = healthIndex
        self.systemKeyInformation = systemKeyInformation or []
        self.systemMainInformation = systemMainInformation or {}
        self.hydrogenMonitor = hydrogenMonitor or {}
        self.oilMonitor = oilMonitor or {}
        self.waterMonitor = waterMonitor or {}
        
class Output(object):
    def __init__(self, modelName=None, owner=None, collectionTime=None, 
                 pltType=None, pltCode=None, setCode=None, 
                 rawDataPackage=None, modelResult=None, addtionalInfo=None):
        super().__init__()
        self.modelName = modelName
        self.owner = owner
        self.collectionTime = collectionTime
        self.pltType = pltType
        self.pltCode = pltCode
        self.setCode = setCode
        self.rawDataPackage = rawDataPackage or {}
        self.modelResult = modelResult or {}
        self.addtionalInfo = addtionalInfo or {}

        