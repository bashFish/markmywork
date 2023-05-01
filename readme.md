# env
.env file
- OPENAI_API_KEY="...
- OPENAI_ORGANIZATION="org-ii5ocIfWC18hfZe8buSxZBW1"

# finetunings
openai tools fine_tunes.prepare_data -f data/datasets/finetune_set.jsonl
openai api fine_tunes.create -t "finetune_set_prepared_train.jsonl" -v "finetune_set_prepared_valid.jsonl" --compute_classification_metrics --classification_n_classes 4 -m ada
openai api fine_tunes.list
openai api fine_tunes.results -i
