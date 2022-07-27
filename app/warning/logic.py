from ast import Or
import numpy as np
from app.data.parameters import Constant, Alarm
from app.warning.advice_dict import H2_dict, Oil_dict, Water_dict


class Generator(object):
    @staticmethod
    def status(speed):
        return (1, '机组运行状态——停机') if speed is not None and speed < Constant.SPEED_JUDGEMENT_STOP else (0, "")

class Hydrogen(object):
    @staticmethod
    def chk_pur(pur, swt, thr, alpha, flag):
        pur_l, pur_ll = swt
        p = {'发电机内氢气纯度低': 0}
        advice = []
        level = Constant.INIT_LEVEL

        if (
            flag 
            and (np.sum(pur[-Constant.PREDICT_POINTS:] < thr * alpha) >= Constant.MAX_EARLY_WARNING_POINTS 
            or pur[-Constant.PREDICT_POINTS - 1: -Constant.PREDICT_POINTS] < thr) 
            or pur_l > 0 or pur_ll > 0
        ):
            p['发电机内氢气纯度低'] = 1
            level = Constant.LEVEL_H2_PURITY_LOW
            advice.append(H2_dict.pur)
        else:
            advice.append({'adv': Constant.NULL_ADVICE, 'des': Constant.NULL_DESCRIPTION})

        return p, advice, level

    @staticmethod
    def chk_hum(hum, thr, alpha, flag):
        p = {'发电机内氢气湿度高': 0}
        advice = []
        level = Constant.INIT_LEVEL

        if (
            flag 
            and (np.sum(hum[-Constant.PREDICT_POINTS:] > thr * alpha) >= Constant.MAX_EARLY_WARNING_POINTS 
            or hum[-Constant.PREDICT_POINTS - 1: -Constant.PREDICT_POINTS] > thr)
        ):
            p['发电机内氢气湿度高'] = 1
            level = Constant.LEVEL_H2_HUMIDITY_HIGH
            advice.append(H2_dict.hum)
        else:
            advice.append({'adv': Constant.NULL_ADVICE, 'des': Constant.NULL_DESCRIPTION})

        return p, advice, level
    
    @staticmethod
    def chk_lkg(lkg, prs, lkg_thr, prs_thr, alpha1, alpha2,
                hyd_prs_low, switch_fe, flag):
        p = {f: 0 for f in ['发电机氢压低'] + switch_fe}
        advice = []
        level = Constant.INIT_LEVEL
        if (
            flag 
            and (np.sum(prs[-Constant.PREDICT_POINTS:] < prs_thr * alpha2) >= Constant.MAX_EARLY_WARNING_POINTS 
            or prs[-Constant.PREDICT_POINTS - 1: -Constant.PREDICT_POINTS] < prs_thr) 
            or hyd_prs_low
        ):
            p['发电机氢压低'] = 1
            level = Constant.LEVEL_H2_PRESSURE_LOW_OR_LEAKAGE
            advice.append(H2_dict.prs_low)
        else:
            advice.append({'adv': Constant.NULL_ADVICE, 'des': Constant.NULL_DESCRIPTION})

        for i, f in enumerate(switch_fe):
            if flag and (np.sum(lkg[i][-Constant.PREDICT_POINTS:] > lkg_thr * alpha1) >= Constant.MAX_EARLY_WARNING_POINTS \
                or lkg[i][-Constant.PREDICT_POINTS - 1: -Constant.PREDICT_POINTS] > lkg_thr):
                p[f] = 1
                level = Constant.LEVEL_H2_PRESSURE_LOW_OR_LEAKAGE
                advice.append(H2_dict.lkg[i])
            else:
                advice.append({'adv': Constant.NULL_ADVICE, 'des': Constant.NULL_DESCRIPTION})

        return p, advice, level

    @staticmethod
    def chk_health(neg_point, H2Lkg_level, H2Pur_level, H2Hum_level):
        # print('H2:', neg_point, H2Lkg_level, H2Pur_level, H2Hum_level)
        if H2Lkg_level: H2Lkg_level = Constant.MAX_LEVEL - H2Lkg_level
        if H2Pur_level: H2Pur_level = Constant.MAX_LEVEL - H2Pur_level
        if H2Hum_level: H2Hum_level = Constant.MAX_LEVEL - H2Hum_level

        scores = Constant.TOTAL_SCORES - neg_point - (H2Lkg_level + H2Pur_level + H2Hum_level) * Constant.SCORES_LEVEL_WEIGHTS
        scores = max(scores, Constant.MIN_SCORES)

        return scores

class Oil(object):
    @staticmethod
    def chk_in(prsDif, thr, alpha, swt, flag):
        st_lkg, ex_lkg, slot_high, dif_low = swt
        p = {'油/氢差压高(发电机进油)': 0, '扩大槽液位高': 0, '油/氢差压低': 0}
        advice = []
        level = Constant.INIT_LEVEL

        term1 = np.sum(prsDif[-Constant.PREDICT_POINTS:] > thr[1] * alpha) >= Constant.MAX_EARLY_WARNING_POINTS \
            or prsDif[-Constant.PREDICT_POINTS - 1: -Constant.PREDICT_POINTS] > thr[1]
        term2 = st_lkg > 0 or ex_lkg > 0
        term3 = slot_high > 0
        term4 = np.sum(prsDif[-Constant.PREDICT_POINTS:] < thr[0] * alpha) >= Constant.MAX_EARLY_WARNING_POINTS \
            or prsDif[-Constant.PREDICT_POINTS - 1: -Constant.PREDICT_POINTS] < thr[0] or dif_low > 0

        if (flag and term1) or term2:
            p['油/氢差压高(发电机进油)'] = 1
            level = Constant.LEVEL_PRESSURE_DIFFERENCE_HIGH

        if flag and term1:
            advice.append(Oil_dict.prs_dif_h)
        else:
            advice.append({'adv': Constant.NULL_ADVICE, 'des': Constant.NULL_DESCRIPTION})

        if term3:
            p['扩大槽液位高'] = 1
            level = Constant.LEVEL_EXPANDING_SLOT_LEVEL_HIGH
            advice.append(Oil_dict.slot_high)
        else:
            advice.append({'adv': Constant.NULL_ADVICE, 'des': Constant.NULL_DESCRIPTION})

        if flag and term4:
            p['油/氢差压低'] = 1
            level = Constant.LEVEL_PRESSURE_DIFFERENCE_LOW
            advice.append(Oil_dict.prs_dif_l)
        else:
            advice.append({'adv': Constant.NULL_ADVICE, 'des': Constant.NULL_DESCRIPTION})

        return p, advice, level

    @staticmethod
    def chk_watercontent(watercontent, thr, alpha, flag):
        p = {'密封油含水量超标': 0}
        advice = []
        level = Constant.INIT_LEVEL

        if (
            flag 
            and (np.sum(watercontent[-Constant.PREDICT_POINTS:] > thr * alpha) >= Constant.MAX_EARLY_WARNING_POINTS 
            or watercontent[-Constant.PREDICT_POINTS - 1: -Constant.PREDICT_POINTS] > thr)
        ):
            p['密封油含水量超标'] = 1
            level = Constant.LEVEL_OIL_WATER_CONTENT_HIGH
            advice.append(Oil_dict.wc_high)
        else:
            advice.append({'adv': Constant.NULL_ADVICE, 'des': Constant.NULL_DESCRIPTION})

        return p, advice, level

    @staticmethod
    def chk_health(neg_point, OilIn_level, OilFB_level, OilWC_level, tank_low, tank_high):
        # print('Oil:', neg_point, OilIn_level, OilFB_level, OilWC_level, tank_low, tank_high)
        OilFB_level = sum(OilFB_level) // Constant.OIL_FILTERS_SWITCH
        if OilFB_level: OilFB_level = Constant.MAX_LEVEL - OilFB_level
        if OilWC_level: OilWC_level = Constant.MAX_LEVEL - OilWC_level

        advice = []
        p = {'真空油箱液位低': 0, '真空油箱液位高': 0}
        level = [Constant.INIT_LEVEL] * Constant.VACUUM_TANK_OIL_LEVEL_SWITCH
        scores = Constant.TOTAL_SCORES - neg_point - (OilIn_level + OilFB_level + OilWC_level) * Constant.SCORES_LEVEL_WEIGHTS \
            - int(tank_low + tank_high) * Constant.SCORES_BINARY_ALARM_WEIGHTS
        scores = max(scores, Constant.MIN_SCORES)

        if tank_low:
            p['真空油箱液位低'] = 1
            level[0] = Constant.LEVEL_VACUUM_TANK_OIL_LEVEL_LOW
            advice.append(Oil_dict.tank_low)
        else:
            advice.append({'adv': Constant.NULL_ADVICE, 'des': Constant.NULL_DESCRIPTION})

        if tank_high:
            p['真空油箱液位高'] = 1
            level[1] = Constant.LEVEL_VACUUM_TANK_OIL_LEVEL_HIGH
            advice.append(Oil_dict.tank_high)
        else:
            advice.append({'adv': Constant.NULL_ADVICE, 'des': Constant.NULL_DESCRIPTION})

        return scores, p, advice, level

    @staticmethod
    def chk_filterblock(fb):
        fbA, fbB = fb
        advice = []
        level = [Constant.INIT_LEVEL] * Constant.OIL_FILTERS_SWITCH
        p = {'过滤器A堵塞': 0, '过滤器B堵塞': 0}

        if fbA:
            p['过滤器A堵塞'] = 1
            level[0] = Constant.LEVEL_OIL_FILTER_BLOCK
            advice.append(Oil_dict.filterA_blk)
        else:
            advice.append({'adv': Constant.NULL_ADVICE, 'des': Constant.NULL_DESCRIPTION})

        if fbB:
            p['过滤器B堵塞'] = 1
            level[1] = Constant.LEVEL_OIL_FILTER_BLOCK
            advice.append(Oil_dict.filterB_blk)
        else:
            advice.append({'adv': Constant.NULL_ADVICE, 'des': Constant.NULL_DESCRIPTION})

        return p, advice, level

class Water(object):

    @staticmethod
    def chk_cond(cond, swt, thr, alpha, flag):
        cond_h, cond_hh = swt
        p = {'发电机进水电导率高': 0}
        advice = []
        level = Constant.INIT_LEVEL

        if (
            flag 
            and (np.sum(cond[-Constant.PREDICT_POINTS:] > thr * alpha) >= Constant.MAX_EARLY_WARNING_POINTS 
            or cond[-Constant.PREDICT_POINTS - 1: -Constant.PREDICT_POINTS] > thr) 
            or cond_h == 1 or cond_hh == 1
        ):
            p['发电机进水电导率高'] = 1
            level = Constant.LEVEL_WATER_CONDUCTIVITY_HIGH
            advice.append(Water_dict.incond_high)
        else:
            advice.append({'adv': Constant.NULL_ADVICE, 'des': Constant.NULL_DESCRIPTION})
            
        return p, advice, level

    @staticmethod
    def chk_flow(flow, swt, thr, alpha, flag):
        flow_l1, flow_l2, flow_l3 = swt
        p = {'发电机断水 冷却水流量低': 0}
        advice = []
        level = Constant.INIT_LEVEL

        if (
            flag 
            and (np.sum(flow[-Constant.PREDICT_POINTS:] < thr * alpha) >= Constant.MAX_EARLY_WARNING_POINTS 
            or flow[-Constant.PREDICT_POINTS - 1: -Constant.PREDICT_POINTS] < thr) 
            or flow_l1 == 1  or flow_l2 == 1  or flow_l3 == 1
        ):
            p['发电机断水 冷却水流量低'] = 1
            level = Constant.LEVEL_WATER_FLOW_LOW
            advice.append(Water_dict.flow_low)
        else:
            advice.append({'adv': Constant.NULL_ADVICE, 'des': Constant.NULL_DESCRIPTION})
            
        return p, advice, level

    @staticmethod
    def chk_PH(flow, thr, alpha, flag):
        p = {'PH值低': 0}
        advice = []
        level = Constant.INIT_LEVEL

        if (
            flag 
            and (np.sum(flow[-Constant.PREDICT_POINTS:] < thr * alpha) >= Constant.MAX_EARLY_WARNING_POINTS 
            or flow[-Constant.PREDICT_POINTS - 1: -Constant.PREDICT_POINTS] < thr)
        ):
            p['PH值低'] = 1
            level = Constant.LEVEL_WATER_PH_LOW
            advice.append(Water_dict.PH_low)
        else:
            advice.append({'adv': Constant.NULL_ADVICE, 'des': Constant.NULL_DESCRIPTION})

        return p, advice, level

    @staticmethod
    def chk_health(neg_point, WaterFlow_level, WaterCond_level, WaterPH_level, 
        tank_low, tank_high, outtemp_high, outcond_high, intemp_high):
        # print('Water:', neg_point, WaterFlow_level, WaterCond_level, WaterPH_level, tank_low, tank_high, outtemp_high, outcond_high, intemp_high)
        if WaterFlow_level: WaterFlow_level = Constant.MAX_LEVEL - WaterFlow_level
        if WaterCond_level: WaterCond_level = Constant.MAX_LEVEL - WaterCond_level
        if WaterPH_level: WaterPH_level = Constant.MAX_LEVEL - WaterPH_level

        advice = []
        p = {'冷却水箱液位高': 0, '冷却水箱液位低': 0, 
             '发电机出水温度高': 0, '离子交换器出口电导率高': 0, 
             '发电机进水温度高': 0}
        level = [Constant.INIT_LEVEL] * len(p)
        scores = (
            Constant.TOTAL_SCORES - neg_point - (WaterFlow_level + (WaterCond_level \
                + Constant.SCORES_BINARY_ALARM_WEIGHTS * outcond_high) // Constant.WATER_CONDUCTIVITY_JUDGEMENT_CONDITION \
                + WaterPH_level) * Constant.SCORES_LEVEL_WEIGHTS - int(tank_high + tank_low) \
                * Constant.SCORES_BINARY_ALARM_WEIGHTS - (outtemp_high + intemp_high) * Constant.SCORES_BINARY_ALARM_WEIGHTS
            )
        scores = max(scores, Constant.MIN_SCORES)

        if tank_low:
            p['冷却水箱液位低'] = 1
            level[0] = Constant.LEVEL_TANK_WATER_LEVEL_LOW
            advice.append(Water_dict.tank_low)
        else:
            advice.append({'adv': Constant.NULL_ADVICE, 'des': Constant.NULL_DESCRIPTION})

        if tank_high:
            p['冷却水箱液位高'] = 1
            level[1] = Constant.LEVEL_TANK_WATER_LEVEL_HIGH
            advice.append(Water_dict.tank_high)
        else:
            advice.append({'adv': Constant.NULL_ADVICE, 'des': Constant.NULL_DESCRIPTION})
            
        if outtemp_high:
            p['发电机出水温度高'] = 1
            level[2] = Constant.LEVEL_GENERATOR_OUTPUT_WATER_TEMPERATURE_HIGH
            advice.append(Water_dict.outtemp_high)
        else:
            advice.append({'adv': Constant.NULL_ADVICE, 'des': Constant.NULL_DESCRIPTION})

        if outcond_high:
            p['离子交换器出口电导率高'] = 1
            level[3] = Constant.LEVEL_ION_EXCHANGER_OUTLET_CONDUCTIVITY_HIGH
            advice.append(Water_dict.outcond_high)
        else:
            advice.append({'adv': Constant.NULL_ADVICE, 'des': Constant.NULL_DESCRIPTION})

        if intemp_high:
            p['发电机进水温度高'] = 1
            level[4] = Constant.LEVEL_GENERATOR_INPUT_WATER_TEMPERATURE_HIGH
            advice.append(Water_dict.intemp_high)
        else:
            advice.append({'adv': Constant.NULL_ADVICE, 'des': Constant.NULL_DESCRIPTION})

        return scores, p, advice, level

class DisplayLogic(object):

    @staticmethod
    def lkg(H2Lkg, H2LkgVol):
        if np.array(H2Lkg).any() or H2LkgVol > Constant.H2_LEAKAGE_VOL_HIGH:
            return Constant.DISPLAY_ALARM, Constant.LEVEL_H2_PRESSURE_LOW_OR_LEAKAGE
        return Constant.DISPLAY_NORMAL, Constant.INIT_LEVEL

    @staticmethod
    def fbl(OilFB):
        if np.array(OilFB).any():
            return Constant.DISPLAY_ALARM, Constant.LEVEL_OIL_FILTER_BLOCK
        return Constant.DISPLAY_NORMAL, Constant.INIT_LEVEL

    @staticmethod
    def oin(OilIn):
        if OilIn[0]:
            return Constant.DISPLAY_ALARM, Constant.LEVEL_PRESSURE_DIFFERENCE_HIGH
        return Constant.DISPLAY_NORMAL, Constant.INIT_LEVEL

    @staticmethod
    def h2q(H2Pur, H2Hum):
        if H2Pur[0] or H2Hum[0]:
            return Constant.DISPLAY_ALARM, Constant.LEVEL_H2_HUMIDITY_HIGH
        return Constant.DISPLAY_NORMAL, Constant.INIT_LEVEL
    
    @staticmethod
    def oilq(OilWC):
        if OilWC[0]:
            return Constant.DISPLAY_ALARM, Constant.LEVEL_OIL_WATER_CONTENT_HIGH
        return Constant.DISPLAY_NORMAL, Constant.INIT_LEVEL
    
    @staticmethod
    def watf(WaterFlow):
        if WaterFlow[0]:
            return Constant.DISPLAY_ALARM, Constant.LEVEL_WATER_FLOW_LOW
        return Constant.DISPLAY_NORMAL, Constant.INIT_LEVEL

    @staticmethod
    def watq(Watercond, WaterPH):
        if Watercond[0] or WaterPH[0]:
            return Constant.DISPLAY_ALARM, Constant.LEVEL_WATER_PH_LOW
        return Constant.DISPLAY_NORMAL, Constant.INIT_LEVEL
