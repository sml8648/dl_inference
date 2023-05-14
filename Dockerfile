FROM python:3.8-slim-buster

RUN apt-get update -y && apt-get install curl -y && apt-get install git -y && \
apt-get install -y openjdk-11-jdk && git clone https://github.com/pytorch/serve.git

CMD ["python", "./serve/ts_scripts/install_dependencies.py"]

COPY . /dl_inference
WORKDIR /dl_inference

RUN pip install -r requirements.txt && bash ./model_down_register.sh
ENV server_name="my_server" \ server_version="1.0" \ management_server="http://localhost:8081" \ inference_server="http://localhost:8080"

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]