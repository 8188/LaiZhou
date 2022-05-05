import pandas as pd
import numpy as np
import random
import sys
import torch
from app.data.parameters import H2_health, Oil_health, Water_health, Constant
sys.path.append('app/algorithm/Pytorch-MSCRED-master/')
from utils.matrix_generator import generate_signature_matrix_node, generate_train_test_data
from utils.evaluate import mscred_evaluate
from utils.data import load_data
from model.mscred import MSCRED
from main_mscred import test as mscred_test
import _pickle as cPickle


with open('app/static/model/XGBoosting.pickle', 'rb') as f:
    XGB_model = cPickle.load(f)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
mscred_H2 = MSCRED(Constant.IN_CHANNELS_ENCODER, Constant.IN_CHANNELS_DECODER,
    H2_health.op1, H2_health.op2, H2_health.op3, H2_health.op4)
mscred_H2.load_state_dict(
    torch.load(H2_health.save_path + H2_health.label + ".pth", map_location=device))
mscred_H2.to(device)

mscred_Oil = MSCRED(Constant.IN_CHANNELS_ENCODER, Constant.IN_CHANNELS_DECODER, 
    Oil_health.op1, Oil_health.op2, Oil_health.op3, Oil_health.op4)
mscred_Oil.load_state_dict(
    torch.load(Oil_health.save_path + Oil_health.label + ".pth", map_location=device))
mscred_Oil.to(device)

mscred_Water = MSCRED(Constant.IN_CHANNELS_ENCODER, Constant.IN_CHANNELS_DECODER, 
    Water_health.op1, Water_health.op2, Water_health.op3, Water_health.op4)
mscred_Water.load_state_dict(
    torch.load(Water_health.save_path + Water_health.label + ".pth", map_location=device))
mscred_Water.to(device)


def chooseFe(df, fe):
    return df[fe]

def timeIndex(df):
    if 'time' in df.columns:
        t = pd.date_range(start=str(df.time.min()), end=str(df.time.max()), freq="T")
        df = df.set_index(df.time)
        #df.index = pd.to_datetime(df.index)
        #df = df.reindex(t)
        df = df.drop(['time'], axis=1)
    return df

def datetimeIndex(df):
    df.index = pd.DatetimeIndex(df.index)
    return df

def reSample(df, period):
    df = df.resample(period).mean()
    return df

def nullCope(df):
    for col in df.columns:
        df[col] = df[col].interpolate()
    return df

def timeFeature(df):
    # df['month'] = df.index.month
    df['day'] = df.index.day
    df['hour'] = df.index.hour
    df['dayofweek'] = df.index.dayofweek
    df['daylight'] = ((df['hour'] >= 7) & (df['hour'] <= 22)).astype(int)
    df['weekday'] = (df['dayofweek'] < 5).astype(int)
    # df.loc[df['day'] <= 10, 'xun'] = 0
    # df.loc[(df['day'] <= 20) & (df['day'] > 10), 'xun'] = 1
    # df.loc[df['day'] > 20, 'xun'] = 2
    # df.loc[(df['month'] <= 2) | (df['month'] >= 12), 'season'] = 0
    # df.loc[(df['month'] >=3) & (df['month'] <= 5), 'season'] = 1
    # df.loc[(df['month'] >=6) & (df['month'] <= 8), 'season'] = 2
    # df.loc[(df['month'] >=9) & (df['month'] <= 11), 'season'] = 3
    # df.drop(['day', 'month',], axis=1, inplace=True)
    # df['season'] = df['season'].astype(np.int8)
    # df['xun'] = df['xun'].astype(np.int8)
    return df

def statistic(df, windows, tar_fe):
    for w in windows:
        for f in tar_fe:
            df[f'{f}_{w}_min'] = df[f].rolling(window=w, min_periods=1).min()
            df[f'{f}_{w}_max'] = df[f].rolling(window=w, min_periods=1).max()
            df[f'{f}_{w}_emean'] = df[f].ewm(span=w, min_periods=1).mean()
            df[f'{f}_{w}_estd'] = df[f].ewm(span=w, min_periods=1).std()   
    return df

def switch(df, switch_fe):
    df[switch_fe] = np.ceil(df[switch_fe]).astype(np.int8)
    return df

def shift_tar(df, tar_fe, periods):
    df[tar_fe] = df[tar_fe].shift(-periods)
    return df

from pandas.api.types import is_datetime64_any_dtype as is_datetime
from pandas.api.types import is_categorical_dtype

def reduce_mem_usage(df, use_float16=False):
    """
    Iterate through all the columns of a dataframe and modify the data type to reduce memory usage.        
    """
    
    # start_mem = df.memory_usage().sum() / 1024**2
    # print("Memory usage of dataframe is {:.2f} MB".format(start_mem))
    
    for col in df.columns:
        if is_datetime(df[col]) or is_categorical_dtype(df[col]):
            continue
        col_type = df[col].dtype
        
        if col_type != object:
            c_min = df[col].min()
            c_max = df[col].max()
            if str(col_type)[:3] == "int":
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)  
            else:
                if use_float16 and c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)
        else:
            df[col] = df[col].astype("category")

    # end_mem = df.memory_usage().sum() / 1024**2
    # print("Memory usage after optimization is: {:.2f} MB".format(end_mem))
    # print("Decreased by {:.1f}%".format(100 * (start_mem - end_mem) / start_mem))
    
    return df


def health_pipe(df, fe, period):
    df = (
        df
        .pipe(chooseFe, fe=fe)
        .pipe(timeIndex)
        #.pipe(reSample, period)
        .pipe(nullCope)
        .fillna(0)  #######
        .reset_index(drop=True)
        .pipe(reduce_mem_usage) 
        .T
    )
    return df

def health_handle(length, path, fe, period, save_path, label, model, test, df_rd2pd):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if test:
        df = pd.read_pickle(path)
    else:
        df, genRunning = df_rd2pd

    if len(df) >= Constant.MIN_HEALTH_MODEL_DATA and genRunning:
        df.time = pd.to_datetime(df.time)
        df = health_pipe(df, fe, period)
        df = df.iloc[:, -length:]
        df.to_csv(save_path + label + '.csv', index=False)
        generate_signature_matrix_node(
            raw_data_path=save_path + label + '.csv',
            save_data_path=save_path,
            max_time=length)
        generate_train_test_data(
            save_data_path=save_path,
            train_end=int(length * Constant.HEALTH_MODEL_TRAIN_END_RATIO), 
            test_start=int(length * Constant.HEALTH_MODEL_TRAIN_END_RATIO), 
            test_end=length)
        dataLoader = load_data(
            train_data_path=save_path + "matrix_data/train_data/", 
            test_data_path=save_path + "matrix_data/test_data/")

        mscred_test(dataLoader['test'], model, device,
            reconstructed_data_path=save_path + "matrix_data/reconstructed_data/",
            test_start=int(length * Constant.HEALTH_MODEL_TRAIN_END_RATIO) // Constant.HEALTH_MODEL_TEST_TIME_INTERVAL)
        anomaly_score, threshold = mscred_evaluate(
            valid_start_point=int(length * Constant.HEALTH_MODEL_VALID_START_RATIO), 
                valid_end_point=int(length * Constant.HEALTH_MODEL_TEST_START_RATIO),
            test_start_point=int(length * Constant.HEALTH_MODEL_TEST_START_RATIO), test_end_point=length,
            test_data_path=save_path + 'matrix_data/test_data/',
            reconstructed_data_path=save_path + 'matrix_data/reconstructed_data/')

        # print(anomaly_score, threshold)
        return anomaly_score, threshold
    else:
        return np.array(0), 0


def rf_handle(path, windows, tar_fe, switch_alarm, train_fe, test, df_rd2pd):
    if test:
        df = pd.read_pickle(path)
    else:
        df, _ = df_rd2pd

    if df is None:
        return None, None, None
    
    df_length = len(df)
    history_length = min(df_length, Constant.MAX_DISPLAY_HISTORY_LEGNTH)
    df.time = pd.to_datetime(df.time)
    t1 = df.time.values[-history_length:]
    t2 = np.array([df.time.values[-1] + np.timedelta64(i, 'm') for i in range(1, 1 + Constant.PREDICT_POINTS)])
    t = np.hstack((t1, t2))
    
    try:
        swt = df[switch_alarm].values[-1]
    except:
        swt = [0] * len(switch_alarm)
    
    flow = df[tar_fe][-history_length:].values
    if df_length >= Constant.MIN_PREDICTABLE_DATE_LENGTH:
        df = (
            df
            .pipe(chooseFe, fe=train_fe)
            .pipe(timeIndex)
            .pipe(reSample, 'T')
            .pipe(nullCope)
            .fillna(0)
            .pipe(timeFeature) 
            .pipe(statistic, 
                  windows=windows,
                  tar_fe=tar_fe) 
            # .pipe(reduce_mem_usage) 
        )
        train_cols = df.columns[~df.columns.isin(tar_fe)]
        pre = df[-1:][train_cols]

        pred = XGB_model.predict(pre)

        flow = np.vstack([flow, pred, pred * (1 + 0.01 * random.random()), pred * (1 + 0.01 * random.random()), 
            pred * (1 + 0.01 * random.random()), pred * (1 + 0.01 * random.random())])
    
    t = pd.to_datetime(t).strftime("%Y/%m/%d %H:%M:%S").tolist()

    return t, flow, swt