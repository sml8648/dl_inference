FROM python:3.8-slim-buster

RUN apt-get update -y && apt-get install curl -y && apt-get install git -y && \
apt-get install -y openjdk-11-jdk && git clone https://github.com/pytorch/serve.git

CMD ["python", "./serve/ts_scripts/install_dependencies.py"]
RUN pip install torchserve torch-model-archiver torch-workflow-archiver fastapi uvicorn torch PyYAML captum transformers==4.6.0

COPY . /dl_inference
WORKDIR /dl_inference

# RUN apt-get update && apt-get install git # git clone