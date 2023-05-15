from pydantic import BaseModel
import httpx
import asyncio
from fastapi import HTTPException

######
class InputStr(BaseModel):
    name:str
    #shape:[]
    datatype:str
    data:str

# async get request
async def request(client, url):
    response = await client.get(url)
    return response

async def task(url):
    async with httpx.AsyncClient() as client:
        tasks = request(client, url)
        result = await asyncio.gather(tasks)
        return result[0]

# async post request
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
    
def error_handling(response):
    
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Requested information not found")
    elif response.status_code == 500:
        raise HTTPException(status_code=500, detail="Internal Server error occurred")
    elif response.status_code == 503:
        raise HTTPException(status_code=503, detail="No worker is available to serve request")