from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.pool import ProcessPoolExecutor
from app import settings


REDIS_DB = {
    "db": settings.REDIS_DATABASE,
    "host": settings.REDIS_HOST
}

interval_task = {
    "jobstores": 
    {
        "default": RedisJobStore(**REDIS_DB)
    },
	"executors": 
    {
	    "default": ProcessPoolExecutor(settings.POOLS_NUMS)
	},
    "job_defaults": 
    {
        "coalesce": False,  # 是否合并执行
        "max_instances": 3,  # 最大实例数
    },
    "timezone": settings.SCHEDULER_TIMEZONE
}

scheduler = BackgroundScheduler(**interval_task)

job1 = {
    "id": "mscred_renew", 
    "func": "app.main.model_train:mscred_renew", 
    "args": (), 
    "trigger": "cron",
    "day_of_week": 1, # day_of_week 0 星期一
    "hour": 15,
    "minute": 38,
    "replace_existing": True,
}

scheduler.add_job(**job1)