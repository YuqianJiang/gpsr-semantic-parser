# Models to be trained
models=("bert_base_seq2seq" "bert_large_seq2seq" "elmo_seq2seq" "openai_seq2seq" "glove_seq2seq" "seq2seq")

for model in ${models[*]}
do
  for i in {1..8}
  do
    config="{\"train_data_path\":\"data/cat2/train${i}.txt\",\"validation_data_path\":\"data/cat2/val.txt\"}"
    allennlp fine-tune -m results/$model/model.tar.gz -c experiments/${model}.json -s fine_tune_results_cat2/${model}_$i -o $config --include-package gpsr_semantic_parser
    echo "${model}_$i is done" >> fine_tune_progress_cat2.txt
  done
  config="{\"train_data_path\":\"data/cat2/train.txt\",\"validation_data_path\":\"data/cat2/val.txt\"}"
  allennlp fine-tune -m results/$model/model.tar.gz -c experiments/${model}.json -s fine_tune_results_cat2/${model} -o $config --include-package gpsr_semantic_parser
done
