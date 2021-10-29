#!/bin/bash

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

REPO_DIR=${ROOT_DIR}/../data/
mkdir -p ${REPO_DIR}

FINAL_AMR_DIR=${REPO_DIR}/processed_amr
mkdir -p ${FINAL_AMR_DIR}

DATA_DIR=${1}

PREPROC_DIR=${REPO_DIR}/tmp_amr
mkdir -p ${PREPROC_DIR}

ORIG_AMR_DIR=${DATA_DIR}/data/alignments/split

mkdir -p ${PREPROC_DIR}/train
mkdir -p ${PREPROC_DIR}/dev
mkdir -p ${PREPROC_DIR}/test


cat ${ORIG_AMR_DIR}/training/amr-* > ${PREPROC_DIR}/train/raw_amrs.txt
cat ${ORIG_AMR_DIR}/dev/amr-* > ${PREPROC_DIR}/dev/raw_amrs.txt
cat ${ORIG_AMR_DIR}/test/amr-* > ${PREPROC_DIR}/test/raw_amrs.txt


for SPLIT in train dev test; do
    echo "processing $SPLIT..."
    python ${ROOT_DIR}/split_amr_align.py ${PREPROC_DIR}/${SPLIT}/raw_amrs.txt ${PREPROC_DIR}/${SPLIT}/surface.txt.tok ${PREPROC_DIR}/${SPLIT}/graphs.txt
    perl ${ROOT_DIR}/detokenize.perl -l en -q < ${PREPROC_DIR}/${SPLIT}/surface.txt.tok > ${PREPROC_DIR}/${SPLIT}/surface.txt
    python ${ROOT_DIR}/preproc_amr_graph.py ${PREPROC_DIR}/${SPLIT}/graphs.txt ${PREPROC_DIR}/${SPLIT}/surface.txt ${FINAL_AMR_DIR}/${SPLIT}.source ${FINAL_AMR_DIR}/${SPLIT}.target --mode LINE_GRAPH --triples-output ${FINAL_AMR_DIR}/${SPLIT}.graph
    echo "done."
done

mv ${FINAL_AMR_DIR}/dev.graph ${FINAL_AMR_DIR}/val.graph
mv ${FINAL_AMR_DIR}/dev.reentrances ${FINAL_AMR_DIR}/val.reentrances
mv ${FINAL_AMR_DIR}/dev.source ${FINAL_AMR_DIR}/val.source
mv ${FINAL_AMR_DIR}/dev.target ${FINAL_AMR_DIR}/val.target

python ${ROOT_DIR}/../convert_graph_tokenizer.py ${FINAL_AMR_DIR}/
