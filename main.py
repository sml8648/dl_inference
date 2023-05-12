from typing import Union
from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import httpx
import asyncio
import json
import os

from datetime import datetime

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

    # TODO : 서버주소 환경 변수로 받기
    result = await task("http://localhost:8081/api-description")

    if result.status_code == 200:
        Server_live_response = {"response":"Inference server is alive"}
        return Server_live_response
    
    else:
        Server_live_error_response = {"error":"Server Internal error occurred"}
        return Server_live_error_response

@app.get("/v2/health/ready")
async def health_ready():

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

    # TODO : name, version은 환경변수로 받는것으로 변경 필요
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
async def model_metadata(model_name: str):

    response = await task(f"http://localhost:8081/models/{model_name}")

    if response.status_code == 200:
        
        response_json = json.loads(response.text)[0]

        metadata_model_response = {
            "name": response_json['modelName'],
            "version": response_json['modelVersion'],
            "platform": "pytorch_torchscript",
            "inputs": {
                "metadata_tensor":{
                    "name":"input_sentence",
                    "datatype":"string"
                }
            },
            "outputs": {
                "metadata_tensor":{
                    "name":"Positive_negative",
                    "datatype":"string"
                }
            }
        }

        return metadata_model_response
    
    elif response.status_code == 404:
        # TODO : detail 말고 metadata_model_error_response로 override 하는법 찾기
        raise HTTPException(status_code=404, detail={"error": "Model not found or Model version not found"})
    else:
        # status_code 500
        raise HTTPException(status_code=404, detail={"error": "Internal Server Error"})


@app.get("/v2/model/{model_name}/versions/{model_version}")
async def model_metadata_with_version(
    model_name: str,
    model_version: str
):
    # TODO 중복되는 코드 줄이는 방법 생각해보기
    response = await task(f"http://localhost:8081/models/{model_name}/{model_version}")

    if response.status_code == 200:
        
        response_json = json.loads(response.text)[0]

        metadata_model_response = {
            "name": response_json['modelName'],
            "version": response_json['modelVersion'],
            "platform": "pytorch_torchscript",
            "inputs": {
                "metadata_tensor":{
                    "name":"input_sentence",
                    "datatype":"string"
                }
            },
            "outputs": {
                "metadata_tensor":{
                    "name":"Positive_negative",
                    "datatype":"string"
                }
            }
        }

        return metadata_model_response
    
    elif response.status_code == 404:
        raise HTTPException(status_code=404, detail={"error": "Model not found or Model version not found"})
    else: # status_code 500
        raise HTTPException(status_code=404, detail={"error": "Internal Server Error"})

class InputStr(BaseModel):
    text:str

async def request_post(client, url, data):
    response = await client.post(url, data=data)
    return response

async def task_post(url, file_path):
    async with httpx.AsyncClient() as client:
        # Read the file content
        with open(file_path, "r") as file:
            file_content = file.read()

        tasks = request_post(client, url, data=file_content)
        result = await asyncio.gather(tasks)
        return result[0]
    
# Inference
@app.post("/v2/models/{model_name}/infer")
async def model_infer(
    model_name: str,
    inputstr: InputStr
):

    input_json = jsonable_encoder(inputstr)

    file_hash = hash(datetime.now())
    file_path = f'./tmp/{file_hash}.txt'

    with open(file_path,"w") as file:
        file.write(str(input_json))

    url = f"http://127.0.0.1:8080/predictions/{model_name}"
    response = await task_post(url,file_path)

    os.remove(file_path)

    if response.status_code == 200:

        inference_response = {
            "model_name":model_name,
            "id":"tmp_string",
            "outputs": {
                "Positive_negative":{
                    "result":response.text,
                }
            }
        }

        return inference_response
    
    elif response.status_code == 404:
        raise HTTPException(status_code=404, detail={"error": "Model not found or Model version not found"})
    elif response.status_code == 500:
        raise HTTPException(status_code=404, detail={"error": "Internal Server Error"})
    elif response.status_code == 503:
        raise HTTPException(status_code=404, detail={"error": "No worker is available to serve request"})

@app.post("/v2/models/{model_name}/versions/{model_version}/infer")
async def model_infer_with_version(
    model_name: str,
    model_version: str,
    inputstr: InputStr
):
    input_json = jsonable_encoder(inputstr)

    file_hash = hash(datetime.now())
    file_path = f'./tmp/{file_hash}.txt'

    with open(file_path,"w") as file:
        file.write(str(input_json))

    url = f"http://127.0.0.1:8080/predictions/{model_name}/{model_version}"
    response = await task_post(url,file_path)

    os.remove(file_path)

    if response.status_code == 200:

        inference_response = {
            "model_name":model_name,
            "id":"tmp_string",
            "outputs": {
                "Positive_negative":{
                    "result":response.text,
                }
            }
        }

        return inference_response
    
    elif response.status_code == 404:
        raise HTTPException(status_code=404, detail={"error": "Model not found or Model version not found"})
    elif response.status_code == 500:
        raise HTTPException(status_code=404, detail={"error": "Internal Server Error"})
    elif response.status_code == 503:
        raise HTTPException(status_code=404, detail={"error": "No worker is available to serve request"})
