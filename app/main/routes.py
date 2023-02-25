from app.main import router
from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.main.model_train import mscred_renew
from app.data.data_make import HOW_pred, redisTest
import requests
import orjson as json
from app import logger


@router.get("/health")
async def health():
    return JSONResponse(content=jsonable_encoder('Hydrogen oil water system diagnosis server check ok.'))


@router.get('/mscredTrain')
async def mscred_run():
    print("MSCRED start running-------------")
    mscred_renew()
    return "Training is finished."


# https://stackoverflow.com/questions/70658748/using-fastapi-in-a-sync-way-how-can-i-get-the-raw-body-of-a-post-request
async def get_body(request: Request):
    return await request.body()


url = "http://host.docker.internal:8084/diagnose/send"


@router.post('/HOW')
def H2_oil_water(body: bytes = Depends(get_body)):
    data=json.dumps(HOW_pred(body))
    # with open("./test3.json",'wb') as f:
    #     f.write(data)
    try:
        requests.post(url=url, data=data)
    except:
        logger.warning("Fail to Post")
    return "OK"


@router.get('/generatorDiagnosis')
async def generatorDiagnosis():
    redisTest()
    return