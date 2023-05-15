from typing import Union
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import json
import os
from utils import *

from datetime import datetime

server_name = os.getenv("server_name")
server_version = os.getenv("server_version")
management_server = os.getenv("management_server")
inference_server = os.getenv("inference_server")

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "This is deep-learning inference server ~ !"}

# Health
@app.get("/v2/health/live")
async def health_live():
    response = await request_handler(f"{management_server}/api-description")

    if response.status_code == 200:
        Server_live_response = {"response": "Inference server is alive"}
        return Server_live_response
    else:
        error_handler(response)


@app.get("/v2/health/ready")
async def health_ready():
    response = await request_handler(f"{management_server}/models")
    models = json.loads(response.text)["models"]

    if response.status_code == 200:
        flag = True
        for model in models:
            # 각각의 모델 마다 돌면서 상태 확인함
            model_name = model["modelName"]
            model_query = await request_handler(f"{management_server}/models/{model_name}")
            model_status = json.loads(model_query.text)[0]["workers"]
            if not len(model_status):
                # 가용하지 않은 모델 발견
                flag = False

        if flag:
            Server_Ready_response = {"response": "All models in server are ready"}
            return Server_Ready_response
        else:
            Server_Ready_error_response = {
                "response": "There are errors in some models in server"
            }
            return Server_Ready_error_response
    else:
        error_handler(response)


@app.get("/v2/models/{model_name}/ready")
async def health_model(model_name: str):
    response = await request_handler(f"{management_server}/models/{model_name}")

    if response.status_code == 200:
        # model_name의 default version의 워커의 상태를 점검
        model_workers = json.loads(response.text)[0]["workers"]

        flag = False
        for worker in model_workers:
            if worker["status"] == "READY":
                flag = True

        if flag:
            Model_Ready_response = {"response": f"{model_name} is now ready"}
            return Model_Ready_response
        else:
            # 모델이 등록은 되었지만 worker가 할당되어 있지 않을때
            Model_Ready_error_response = {"response": f"{model_name} is not ready now"}
            return Model_Ready_error_response

    else:
        error_handler(response)


@app.get("/v2/models/{model_name}/version/{model_version}/ready")
async def health_model_with_version(model_name: str, model_version: str):
    response = await request_handler(f"{management_server}/models/{model_name}/{model_version}")

    if response.status_code == 200:
        model_workers = json.loads(response.text)[0]["workers"]
        # model_name.model_version 의 워커의 상태를 점검
        flag = False
        for worker in model_workers:
            if worker["status"] == "READY":
                flag = True

        if flag:
            Model_Ready_response = {"response": f"{model_name} is now ready"}
            return Model_Ready_response
        else:
            Model_Ready_error_response = {"response": f"{model_name} is not ready now"}
            return Model_Ready_error_response

    else:
        error_handler(response)


# Server Metadata
@app.get("/v2")
def server_metadata():
    try:
        metadata_server_response = {
            "name": server_name,
            "version": server_version,
            "extensions": None,
        }
        return metadata_server_response

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


# Model Metadata
@app.get("/v2/model/{model_name}")
async def model_metadata(model_name: str):
    response = await request_handler(f"{management_server}/models/{model_name}")

    if response.status_code == 200:
        response_json = json.loads(response.text)[0]

        metadata_model_response = {
            "name": response_json["modelName"],
            "version": response_json["modelVersion"],
            # 질문 : pytorcheager 모드는 platform에 따로 없는지?
            "platform": "pytorch_torchscript",
            # 질문 : NLP 모델임으로 입력으로 문자열을 받는다고 하면 shape는 따로 어떻게 설정을 해줘야 하는걸까요?
            "inputs": {
                "metadata_tensor": {"name": "input_sentence", "datatype": "string"}
            },
            "outputs": {
                "metadata_tensor": {"name": "Positive_negative", "datatype": "string"}
            },
        }

        return metadata_model_response

    else:
        error_handler(response)

@app.get("/v2/model/{model_name}/versions/{model_version}")
async def model_metadata_with_version(model_name: str, model_version: str):
    
    response = await request_handler(f"{management_server}/models/{model_name}/{model_version}")

    if response.status_code == 200:
        response_json = json.loads(response.text)[0]

        metadata_model_response = {
            "name": response_json["modelName"],
            "version": response_json["modelVersion"],
            "platform": "pytorch_torchscript",
            "inputs": {
                "metadata_tensor": {"name": "input_sentence", "datatype": "string"}
            },
            "outputs": {
                "metadata_tensor": {"name": "Positive_negative", "datatype": "string"}
            },
        }

        return metadata_model_response

    else:
        error_handler(response)


# Inference
@app.post("/v2/models/{model_name}/infer")
async def model_infer(model_name: str, inputstr: InputStr):

    input_json = jsonable_encoder(inputstr)

    breakpoint()
    
    file_hash = hash(datetime.now())
    file_path = f"./tmp/{file_hash}.txt"

    with open(file_path, "w") as file:
        file.write(str(input_json))

    url = f"{inference_server}/predictions/{model_name}"
    response = await request_post_handler(url, file_path)

    os.remove(file_path)

    if response.status_code == 200:
        inference_response = {
            "model_name": model_name,
            "id": "tmp_string",
            "outputs": {
                "Positive_negative": {
                    "name": "inference_result",
                    #"shape":[]
                    "datatype":"string",
                    #"parameter":[]
                    "result": response.text,
                }
            },
        }

        return inference_response

    else:
        error_handler(response)


@app.post("/v2/models/{model_name}/versions/{model_version}/infer")
async def model_infer_with_version(
    model_name: str, model_version: str, inputstr: InputStr
):
    input_json = jsonable_encoder(inputstr)

    file_hash = hash(datetime.now())
    file_path = f"./tmp/{file_hash}.txt"

    with open(file_path, "w") as file:
        file.write(str(input_json))

    url = f"{inference_server}/predictions/{model_name}/{model_version}"
    response = await request_post_handler(url, file_path)

    os.remove(file_path)

    if response.status_code == 200:
        inference_response = {
            "model_name": model_name,
            "model_version": model_version,
            "id": "tmp_string",
            "outputs": {
                "Positive_negative": {
                    "name": "inference_result",
                    #"shape":[]
                    "datatype":"string",
                    #"parameter":[]
                    "result": response.text,
                }
            },
        }

        return inference_response

    else:
        error_handler(response)
