mkdir model_store
python ./config/transformer_download.py setup_config_sequence.json
torch-model-archiver --model-name BERTSeqClassification --version 1.0 --serialized-file Transformer_model/pytorch_model.bin --handler ./config/Transformer_handler_sequence.py --extra-files "Transformer_model/config.json,./config/setup_config_sequence.json,./config/Seq_classification_artifacts/index_to_name.json"
mv BERTSeqClassification.mar model_store
torchserve --start --model-store model_store --models bert_seqcls=BERTSeqClassification.mar --ncs

torch-model-archiver --model-name BERTSeqClassification2 --version 2.0 --serialized-file Transformer_model/pytorch_model.bin --handler ./config/Transformer_handler_sequence.py --extra-files "Transformer_model/config.json,./config/setup_config_sequence.json,./config/Seq_classification_artifacts/index_to_name.json"
mv BERTSeqClassification2.mar model_store
curl -X POST  "http://localhost:8081/models?url=BERTSeqClassification2.mar&model_name=bert_seqcls"
curl -v -X PUT "http://localhost:8081/models/bert_seqcls/2.0?min_worker=1"


python ./config/transformer_download.py setup_config_token.json
torch-model-archiver --model-name BERTTokenClassification --version 1.0 --serialized-file Transformer_model/pytorch_model.bin --handler ./config/Transformer_handler_token.py --extra-files "Transformer_model/config.json,./config/setup_config_token.json,./config/token_classification_artifacts/index_to_name.json"
mv BERTTokenClassification.mar model_store
curl -X POST  "http://localhost:8081/models?url=BERTTokenClassification.mar&model_name=bert_tokencls"
curl -v -X PUT "http://localhost:8081/models/bert_tokencls/1.0?min_worker=1"


torch-model-archiver --model-name BERTTokenClassification2 --version 2.0 --serialized-file Transformer_model/pytorch_model.bin --handler ./config/Transformer_handler_token.py --extra-files "Transformer_model/config.json,./config/setup_config_token.json,./config/token_classification_artifacts/index_to_name.json"
mv BERTTokenClassification2.mar model_store
curl -X POST  "http://localhost:8081/models?url=BERTTokenClassification2.mar&model_name=bert_tokencls"
curl -v -X PUT "http://localhost:8081/models/bert_tokencls/2.0?min_worker=1"