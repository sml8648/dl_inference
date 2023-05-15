FROM python:3.8-slim-buster

RUN apt-get update -y \
    && apt-get install -y curl git openjdk-11-jdk

RUN git clone https://github.com/pytorch/serve.git \
    && python ./serve/ts_scripts/install_dependencies.py

WORKDIR /dl_inference

COPY . .
RUN pip install --no-cache-dir -r requirements.txt \
    && bash ./model_down_register.sh

ENV server_name="my_server" \
    server_version="1.0" \
    management_server="http://localhost:8081" \
    inference_server="http://localhost:8080"

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
