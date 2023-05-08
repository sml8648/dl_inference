# TODO http error를 어떻게 다루는지 알아보자
# default model version을 설정을 해야한다.

from typing import Union
from fastapi import FastAPI, HTTPException
import httpx
import asyncio
import json

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "This is deep-learning inference server ~ !"}

async def request(client, url):
    response = await client.get(url)
    return response

async def task(url):
    async with httpx.AsyncClient() as client:
        tasks = request(client, url)
        result = await asyncio.gather(tasks)
        return result[0]

# Health
@app.get("/v2/health/live")
async def health_live():

    result = await task("http://localhost:8081/api-description")

    if result.status_code == 200:
        Server_live_response = {"response":"Inference server is alive"}
        return Server_live_response
    
    else:
        Server_live_error_response = {"error":"Server Internal error occurred"}
        return Server_live_error_response

@app.get("/v2/health/ready")
async def health_ready():

    # 이렇게 하는거 맞는건가?
    result = await task("http://localhost:8081/models")
    models = json.loads(result.text)['models']
    
    flag = True
    for model in models:
        # 각각의 모델 마다 돌면서 상태 확인함
        model_name = model['modelName']
        model_query = await task(f"http://localhost:8081/models/{model_name}")
        model_status = json.loads(model_query.text)[0]['workers']
        if not len(model_status):
            flag = False

    if flag:
        Server_Ready_response = {"response":"All models in server are ready"}
        return Server_Ready_response
    else:
        Server_Ready_error_response = {"response":"There are errors in some models in server"}
        return Server_Ready_error_response

@app.get("/v2/models/{model_name}/ready")
async def health_model(model_name: str):

    result = await task(f"http://localhost:8081/models/{model_name}")

    if result.status_code == 200:
        model_workers = json.loads(result.text)[0]['workers']

        flag = False
        for worker in model_workers:
            if worker['status'] == 'READY':
                flag = True
        
        if flag:
            Model_Ready_response = {"response":f"{model_name} is now ready"}
            return Model_Ready_response
        else:
            # When the model has been registered but there are no workers
            Model_Ready_error_response = {"response":f"{model_name} is not ready now"}
            return Model_Ready_error_response
        
    elif result.status_code == 404:
        Model_Ready_error_response = {"response":f"{model_name} model is not exist"}
        return Model_Ready_error_response
    
    else:
        Model_Ready_error_response = {"response":"Internal server error"}
        return Model_Ready_error_response

@app.get("/v2/models/{model_name}/version/{model_version}/ready")
async def health_model_with_version(
    model_name: str,
    model_version: str
):
    result = await task(f"http://localhost:8081/models/{model_name}/{model_version}")

    if result.status_code == 200:
        model_workers = json.loads(result.text)[0]['workers']

        flag = False
        for worker in model_workers:
            if worker['status'] == 'READY':
                flag = True
        
        if flag:
            Model_Ready_response = {"response":f"{model_name} is now ready"}
            return Model_Ready_response
        else:
            # When the model has been registered but there are no workers
            Model_Ready_error_response = {"response":f"{model_name} is not ready now"}
            return Model_Ready_error_response
        
    elif result.status_code == 404:
        raise HTTPException(status_code=404, detail=f"{model_name}:{model_version} model is not exist")
    
    else:
        raise HTTPException(status_code=500, detail="Internal Server error occurred")

# Server Metadata
@app.get("/v2")
def server_metadata():

    # name, version은 환경변수로 받는것으로 변경 필요
    try:
        metadata_server_response = {
            "name": "Inference server",
            "version": "1.0",
            "extensions": None,
        }
        return metadata_server_response

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


# Model Metadata
@app.get("/v2/model/{model_name}")
def model_metadata(model_name: str):
    # curl to torchserve
    pass

@app.get("/v2/model/{model_name}/versions/{model_version}")
def model_metadata_with_version(
    model_name: str,
    model_version: str
):
    # curl to torchserve
    pass

# Inference
@app.get("/v2/models/{model_name}/infer")
def model_infer(
    model_name: str
):
    # curl to torchserve
    pass

@app.get("/v2/models/{model_name}/versions/{model_version}/infer")
def model_infer_with_version(
    model_name: str,
    model_version: str
):
    # curl to torchserve
    pass