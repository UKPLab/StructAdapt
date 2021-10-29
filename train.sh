#!/bin/bash


export OUTPUT_DIR_NAME=outputs/exp-${RANDOM}
export CURRENT_DIR=${PWD}
export OUTPUT_DIR=${CURRENT_DIR}/${OUTPUT_DIR_NAME}

mkdir -p ${CURRENT_DIR}/outputs
mkdir -p $OUTPUT_DIR

export OMP_NUM_THREADS=10

MODEL=$1
DATA_DIR=$2
GPUID=$3
export CUDA_VISIBLE_DEVICES=${GPUID}
python finetune.py \
--data_dir=${DATA_DIR} \
--learning_rate=1e-4 \
--num_train_epochs 100 \
--early_stopping_patience 5 \
--task graph2text \
--model_name_or_path=${MODEL} \
--train_batch_size=4 \
--eval_batch_size=8 \
--gpus 1 \
--output_dir=$OUTPUT_DIR \
--max_source_length=384 \
--max_target_length=384 \
--val_max_target_length=384 \
--test_max_target_length=384 \
--eval_max_gen_length=384 \
--do_train --do_predict \
--adapter_dim 256 \
--eval_beams 5
