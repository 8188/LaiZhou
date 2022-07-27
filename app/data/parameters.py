class Constant(object):
    DECIMAL_INPUT_DATA = 2
    DECIMAL_OUTPUT_DATA = 3
    MIN_PREDICTABLE_DATE_LENGTH = 35

    MODIFICATION_FACTOR_H2_LEAKAGE = 1
    MODIFICATION_FACTOR_H2_PRESSURE = 1
    MODIFICATION_FACTOR_PRESSURE_DIFFERENCE = 1
    MODIFICATION_FACTOR_H2_PURITY = 1
    MODIFICATION_FACTOR_H2_HUMIDITY = 1
    MODIFICATION_FACTOR_OIL_WATER_CONTENT = 1
    MODIFICATION_FACTOR_WATER_FLOW = 1
    MODIFICATION_FACTOR_WATER_CONDUCTIVITY = 1
    MODIFICATION_FACTOR_WATER_PH_LOW = 1

    OIL_WATERCONTENT_CONVERTION = 0.0011481 # 1/871 g/L -> %
    VOLUME_GENERATOR = 143
    MODEL_NAME = 'H2OilWater'
    OWNER = '00'
    FLAG_NULL_MODEL_RESULT = 0

    SPEED_JUDGEMENT_STOP = 30
    MAX_EARLY_WARNING_POINTS = 4

    LEVEL_MESSURE_POINTS_LOST = 4
    LEVEL_GENERATOR_STATUS = 4
    LEVEL_H2_PURITY_LOW = 3
    LEVEL_H2_HUMIDITY_HIGH = 3
    LEVEL_H2_PRESSURE_LOW_OR_LEAKAGE = 3
    LEVEL_PRESSURE_DIFFERENCE_HIGH = 3
    LEVEL_PRESSURE_DIFFERENCE_LOW = 3
    LEVEL_EXPANDING_SLOT_LEVEL_HIGH = 3
    LEVEL_OIL_WATER_CONTENT_HIGH = 3
    LEVEL_VACUUM_TANK_OIL_LEVEL_LOW = 4
    LEVEL_VACUUM_TANK_OIL_LEVEL_HIGH = 4
    LEVEL_OIL_FILTER_BLOCK = 4
    LEVEL_WATER_CONDUCTIVITY_HIGH = 3
    LEVEL_WATER_FLOW_LOW = 3
    LEVEL_WATER_PH_LOW = 3
    LEVEL_TANK_WATER_LEVEL_LOW = 4
    LEVEL_TANK_WATER_LEVEL_HIGH = 4
    LEVEL_GENERATOR_OUTPUT_WATER_TEMPERATURE_HIGH = 4
    LEVEL_GENERATOR_INPUT_WATER_TEMPERATURE_HIGH = 4
    LEVEL_ION_EXCHANGER_OUTLET_CONDUCTIVITY_HIGH = 4

    MAX_LEVEL = 5
    INIT_LEVEL = 0
    TOTAL_SCORES = 100
    MIN_SCORES = 80
    SCORES_LEVEL_WEIGHTS = 2
    SCORES_BINARY_ALARM_WEIGHTS = 2
    OIL_FILTERS_SWITCH = 2
    VACUUM_TANK_OIL_LEVEL_SWITCH = 2
    WATER_CONDUCTIVITY_JUDGEMENT_CONDITION = 2
    PREDICT_POINTS = 5
    NULL_ADVICE = ['']
    NULL_DESCRIPTION = ['']
    DISPLAY_ALARM = '预警'
    DISPLAY_NORMAL = '正常'

    TABLE_H2_LEAKAGE_DATA_EXPIRE_TIME = 400
    TABLE_H2_LEAKAGE_DATA_BEGIN_EXPIRE_TIME = None # forever
    TABLE_MAIN_EXPIRE_TIME = 14400
    MAX_CAPACITY_TABLE_H2_LEAKAGE_DATA = 20
    MAX_CAPACITY_TABLE_H2_LEAKAGE_DATA_BEGIN = 20
    MAX_CAPACITY_TABLE_MAIN = 720
    MAX_SPEED_GENERATOR_RUN = 50.5
    MIN_SPEED_GENERATOR_RUN = 49.5
    KPA_TO_MPA_FACTOR = 0.001
    C_TO_K_FACTOR = 273
    HOUR_TO_DAY_FACTOR = 24
    GAS_CONSTANT = 70320 # (273+20)*24/0.1 (20℃，0.1MPa下)
    H2_LEAKAGE_VOL_HIGH = 15 # m3/d
    H2_LEAKAGE_DATA_FILTER_TIME = 20
    H2_LEAKAGE_MODIFICATION_FACTOR = 1
    H2_FILL_JUDGE_UPPER_BOUND = 5
    H2_FILL_JUDGE_LOWER_BOUND = 1
    H2_PRESSURE_MIN = 0.01

    IN_CHANNELS_ENCODER = 3
    IN_CHANNELS_DECODER = 256
    MIN_HEALTH_MODEL_DATA = 300
    MIN_PREDICT_MODEL_DATA = 500
    HEALTH_MODEL_TEST_TIME_INTERVAL = 10
    HEALTH_MODEL_TRAIN_END_RATIO = 0.4
    # assert(MIN_HEALTH_MODEL_DATA * HEALTH_MODEL_TRAIN_END_RATIO > HEALTH_MODEL_TEST_TIME_INTERVAL)
    HEALTH_MODEL_VALID_START_RATIO = 0.4
    HEALTH_MODEL_TEST_START_RATIO = 0.8
    MAX_DISPLAY_HISTORY_LEGNTH = MIN_PREDICTABLE_DATE_LENGTH - PREDICT_POINTS

    MSCRED_ERROR_THRESHOLD = 0.005
    MSCRED_MODIFICATION_FACTOR = 1.5
    MSCRED_TIME_GAP = 10


class Alarm(object):
    H2_leakage = 4
    H2_pressure = 0.44
    Oil_H2_pressure_diff = [36, 76]
    H2_purity = 92
    H2_humidity = 0
    Water_content = 0.03
    Water_Flow = 22
    Water_conductivity = 2
    Water_PH = [7, 9]
    Water_outTemp = 76
    Water_inTemp = 55
    Ion_exchanger_outlet_conductivity = 0.5


class H2_leakage(object):
    switch_fe = [
        '发电机内冷水箱氢气泄漏高报警', '发电机密封油励侧回油氢气泄漏高报警',
        '发电机密封油汽侧回油氢气泄漏高', '发电机封闭母线A相氢气泄漏高', 
        '发电机封闭母线B相氢气泄漏高',  '发电机封闭母线C相氢气泄漏高', 
        '发电机封闭母线中性点1氢气泄漏高', '发电机封闭母线中性点2氢气泄漏高',
        ]


class H2_health(object):
    path = 'app/static/testData/health.sample'
    save_path = 'app/static/model/'
    renew_path = 'app/static/renew/'
    fe = [
        'time', '发电机内冷水箱氢气泄漏', '发电机密封油励侧回油氢气泄漏', '发电机密封油汽侧回油氢气泄漏', 
        '发电机封闭母线A相氢气泄漏', '发电机封闭母线B相氢气泄漏', '发电机封闭母线C相氢气泄漏', 
        '发电机封闭母线中性点1氢气泄漏', '发电机封闭母线中性点2氢气泄漏', '进氢压力',
        '发电机内氢气纯度',  '发电机出氢湿度', '发电机氢干燥装置后氢气湿度', 
        ]
    length = Constant.MIN_HEALTH_MODEL_DATA
    label = 'H2'
    period = 'T'
    op1 = 0
    op2 = 0
    op3 = 1
    op4 = 0
    test = False


class Oil_health(object):
    path = 'app/static/testData/health.sample'
    save_path = 'app/static/model/'
    renew_path = 'app/static/renew/'
    fe = [
        'time', '10#轴承回油温度', '4#轴承回油温度', '9#轴承回油温度', '11#轴承回油温度',
        '发电机密封油-氢气差压', '机组发电机密封油汽端压力', '机组发电机密封油励端压力',
        '发电机密封油油含水量', 'B浮子油箱油位', 
        '发电机密封油主密封油泵A电流', '发电机密封油主密封油泵B电流', '发电机密封油事故密封油泵电流',
    ]
    length = Constant.MIN_HEALTH_MODEL_DATA
    label = 'Oil'
    period = 'T'
    op1 = 0
    op2 = 0
    op3 = 1
    op4 = 0
    test = False


class Water_health(object):
    path = 'app/static/testData/health.sample'
    save_path = 'app/static/model/'
    renew_path = 'app/static/renew/'
    fe = [
        'time', '发电机定子线棒层间温度1', '发电机定子铁芯温度1', '发电机定子铜屏蔽温度1',
        '发电机定子线圈出水温度1', '发电机定子冷却水出水温度1', '发电机定子冷却水入水温度1', '发电机定子冷却水温度调节阀控制指令',
        '发电机定子冷却水电导率', '发电机离子交换器出水电导率', '发电机定子冷却水油水PH计', 
        '发电机定子冷却水流量1差压', '机组发电机引出线流量'
        ]
    length = Constant.MIN_HEALTH_MODEL_DATA
    label = 'Water'
    period = 'T'
    op1 = 0
    op2 = 0
    op3 = 1
    op4 = 0
    test = False


class RF_All(object):
    path = 'app/static/testData/all.sample'
    windows = [5, 60, 720]
    tar_fe = [
        '发电机内冷水箱氢气泄漏', '发电机密封油励侧回油氢气泄漏', '发电机密封油汽侧回油氢气泄漏', 
        '发电机封闭母线A相氢气泄漏', '发电机封闭母线B相氢气泄漏', '发电机封闭母线C相氢气泄漏', 
        '发电机封闭母线中性点1氢气泄漏', '发电机封闭母线中性点2氢气泄漏', '进氢压力',
        '发电机内氢气纯度',  '发电机出氢湿度', 
        '发电机密封油-氢气差压', '发电机密封油油含水量', 
        '发电机定子冷却水电导率', '发电机定子冷却水油水PH计', '发电机定子冷却水流量1差压'
        ]
    switch_alarm = [
        '发电机氢气纯度低', '发电机氢气纯度低低', 
        '发电机汽端液漏', '发电机励端液漏1', '发电机密封油回油扩大槽液位高', '发电机密封油差压低',
        '发电机密封油真空油箱液位低', '发电机密封油真空油箱液位高',
        '发电机定子冷却水进水流量低1', '发电机定子冷却水进水流量低2', '发电机定子冷却水进水流量低3', 
        '发电机定子冷却水导电率高', '发电机定子冷却水导电率高高',
        '定子冷却水箱液位低', '定子冷却水箱液位高',
        '发电机进氢压力低',
        'A密封油过滤器差压高', 'B密封油过滤器差压高',
        '发电机离子交换器出水电导率',
        '发电机定子冷却水出水温度1', '发电机定子冷却水入水温度1'
        ]
    train_fe = [
        'time', '发电机A相电流', '发电机B相电流', '发电机C相电流', '发电机负序电流',
        '发电机定子AB线电压', '发电机定子BC线电压', '发电机定子CA线电压',
        '发电机机端零序电压', '发电机无功功率', '发电机功率因数', '发电机频率',
        '10#轴承回油温度', '4#轴承回油温度', '9#轴承回油温度', '11#轴承回油温度',
        '发电机励磁电流', '发电机励磁电压', '发电机封闭母线A相氢气泄漏',
        '发电机封闭母线B相氢气泄漏', '发电机封闭母线C相氢气泄漏', '发电机封闭母线中性点1氢气泄漏',
        '发电机密封油励侧回油氢气泄漏', '发电机密封油汽侧回油氢气泄漏', '发电机内冷水箱氢气泄漏',
        '进氢压力', '发电机封闭母线中性点2氢气泄漏', '发电机内氢气纯度', '发电机氢干燥装置后氢气湿度',
        '发电机出氢湿度', '发电机密封油-氢气差压', '机组发电机密封油汽端压力', '机组发电机密封油励端压力',
        '发电机密封油油含水量', '发电机密封油主密封油泵A电流', '发电机密封油主密封油泵B电流',
        '发电机定子线棒层间温度1', '发电机定子线圈出水温度1', '发电机汽端冷却器入口热风温度1',
        '发电机汽端冷却器出口冷风温度1', '发电机汽端冷却器出口冷风温度2', '发电机定子铁芯温度1',
        '发电机定子铜屏蔽温度1', '发电机励端冷却器入口热风温度1', '发电机励端冷却器出口冷风温度1',
        '发电机励端冷却器出口冷风温度2', '发电机定子冷却水电导率', '发电机离子交换器出水电导率',
        '发电机定子冷却水油水PH计', '发电机定子冷却水温度调节阀控制指令', '发电机定子冷却水出水温度1',
        '发电机定子冷却水流量1差压', '机组发电机引出线流量', '汽端轴承温度', '励端轴承温度',
        '集电环进气口温度', '集电环出气口温度', '发电机供氢流量', 'B浮子油箱油位', '轴振9X',
        '瓦振9X', '瓦振9Y', '发电机密封油事故密封油泵电流', '发电机定子冷却水入水温度1',
        '发电机有功功率'
        ]
    test = False