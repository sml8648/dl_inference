mkdir model_store
python transformer_download.py setup_config_sequence.json
torch-model-archiver --model-name BERTSeqClassification --version 1.0 --serialized-file Transformer_model/pytorch_model.bin --handler ./Transformer_handler_generalized.py --extra-files "Transformer_model/config.json,./setup_config_sequence.json,./Seq_classification_artifacts/index_to_name.json"
mv BERTSeqClassification.mar model_store
torchserve --start --model-store model_store --models my_tc=BERTSeqClassification.mar --ncs

torch-model-archiver --model-name BERTSeqClassification2 --version 2.0 --serialized-file Transformer_model/pytorch_model.bin --handler ./Transformer_handler_generalized.py --extra-files "Transformer_model/config.json,./setup_config_sequence.json,./Seq_classification_artifacts/index_to_name.json"
mv BERTSeqClassification2.mar model_store
curl -X POST  "http://localhost:8081/models?url=BERTSeqClassification2.mar&model_name=my_tc"
curl -v -X PUT "http://localhost:8081/models/my_tc/2.0?min_worker=1"