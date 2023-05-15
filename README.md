# dl_inference

## 개요
* FastAPI를 이용하여 딥러닝 모델 서빙 api를 요청할 수 있는 서버 구축
* Dockerfile을 이용해 빌드하여 컨테이너 환경에서 실행 시킬 수 있는 형태로 구축

## 세부 구현 사항
* 표준 서빙 프로토콜인 v2 inference 프로토콜에서 HTTP 프로토콜로 구현
  - **Health** : GET v2/health/live GET v2/health/ready GET v2/models/${MODEL_NAME}[/versions/${MODEL_VERSION}]/ready
  - **Server Metadata** : GET v2
  - **Model Metadata** : GET v2/models/${MODEL_NAME}[/versions/${MODEL_VERSION}]
  - **Inference** : POST v2/models/${MODEL_NAME}[/versions/${MODEL_VERSION}]/infer
  - ref : https://kserve.github.io/website/0.8/modelserving/inference_api/#httprest
  
 * TorchServe를 이용하여 고성능 인퍼런스 서버로 인퍼런스 구성
   - huggingface의 Transformer 모델을 서빙(SequenceClassification, TokenClassification)
   - Naver cloud의 고성능 cpu 서버를 활용(GPU 가용 불가)
   - ref : https://github.com/pytorch/serve/blob/master/README.md#serve-a-model
   
 * Github action을 이용하여 CI 구축
 * Dockerfile을 이용하여 msa 형태로 구축
 * Web-single-pattern으로 배포
   - 단일 REST 서버(FastAPI) 인터페이스, 전처리, 모델을 한곳에서 사용
   - <img src="./asset/diagram.png" width=50% height=50%>
   - 출처 : https://github.com/mercari/ml-system-design-pattern/blob/master/Serving-patterns/Web-single-pattern/design_ko.md
 

## Directory structure
```
dl_inderence
├──📁logs
├──📁model_store -> torchserver를 위한 .mar file 저장
├──📁Transformer_model -> .mar file을 만들기 위한 transformer 모델 저장공간
├──📁configs -> Transformer 모델을 다운로드 받기위한 config 파일 및 handler
├── Dockerfile
├── model_down_register.sh -> 서빙하기 위한 모델을 다운받는 script
├── model_register.sh -> 모델을 torchserve에 등록하는 script
├── main.py # fastapi server
├── utils.py
├── requirements.txt
└── README.md
```
 
## 설치 명령어
```
git clone https://github.com/sml8648/dl_inference.git
cd dl_inference
docker build . -t inference_server
docker run --name inference_server -d -p 8000:8000 inference_server
docker exec -i inference_server bash ./model_register.sh
```

