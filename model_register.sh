#!/bin/bash
torchserve --start --model-store model_store --models bert_seqcls=BERTSeqClassification.mar --nc
sleep 10s
curl -v -X PUT "http://localhost:8081/models/bert_seqcls/1.0?max_worker=1"

sleep 10s
curl -X POST  "http://localhost:8081/models?url=BERTSeqClassification2.mar&model_name=bert_seqcls"
sleep 10s
curl -v -X PUT "http://localhost:8081/models/bert_seqcls/2.0?min_worker=1"

sleep 10s
curl -X POST  "http://localhost:8081/models?url=BERTTokenClassification.mar&model_name=bert_tokencls"
sleep 10s
curl -v -X PUT "http://localhost:8081/models/bert_tokencls/1.0?min_worker=1"

sleep 10s
curl -X POST  "http://localhost:8081/models?url=BERTTokenClassification2.mar&model_name=bert_tokencls"
sleep 10s
curl -v -X PUT "http://localhost:8081/models/bert_tokencls/2.0?min_worker=1"