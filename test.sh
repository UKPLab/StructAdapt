#!/bin/bash

export OMP_NUM_THREADS=10

MODEL=$1
MODEL_DIR=$2
DATA_DIR=$3
GPUID=$4
export CUDA_VISIBLE_DEVICES=${GPUID}
python finetune.py \
--data_dir=${DATA_DIR} \
--task graph2text \
--model_name_or_path=${MODEL} \
--train_batch_size=4 \
--eval_batch_size=8 \
--gpus 1 \
--output_dir=${MODEL_DIR} \
--max_source_length=384 \
--max_target_length=384 \
--val_max_target_length=384 \
--test_max_target_length=384 \
--eval_max_gen_length=384 \
--do_predict \
--adapter_dim 256 \
--eval_beams 5
