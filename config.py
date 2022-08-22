import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
    REDIS_DATABASE = os.getenv('REDIS_DATABASE')

    POOLS_NUM = os.getenv('POOLS_NUM') 
    SCHEDULER_TIMEZONE = os.getenv('TIMEZONE')

    TABLE_MAIN = os.getenv('TABLE_MAIN')
    KEY_MAIN = os.getenv('KEY_MAIN')
    TABLE_H2_LEAKAGE_DATA = os.getenv('TABLE_H2_LEAKAGE_DATA')
    KEY_H2_LEAKAGE_DATA = os.getenv('KEY_H2_LEAKAGE_DATA')
    TABLE_H2_LEAKAGE_DATA_BEGIN = os.getenv('TABLE_H2_LEAKAGE_DATA_BEGIN')
    KEY_H2_LEAKAGE_DATA_BEGIN = os.getenv('KEY_H2_LEAKAGE_DATA_BEGIN')
    
    WSGI_HOST = os.getenv('WEB_SERVER_GATEWAY_INTERFACE_HOST')
    WSGI_PORT = int(os.getenv('WEB_SERVER_GATEWAY_INTERFACE_PORT'))

    SCHEDULER_API_ENABLED = True
    # JOBS = [
    #     {
    #         'id': 'mscred_renew', 
    #         'func': 'app.main.model_train:mscred_train', 
    #         'args': '', 
    #         'trigger': {
    #             'type': 'cron',
    #             'day_of_week': 1, # day_of_week 0 星期一
    #             'hour': 15,
    #             'minute': 38
    #         }
    #     },
    # ]
