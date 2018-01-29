#!/bin/bash

set -e

#usage
#./script/run_bow_model.sh

FULL_TRAIN_FILE="data/bag_of_words/full/train.tfrecord"
FULL_VALIDATION_FILE="data/bag_of_words/full/validation.tfrecord"
FULL_TEST_FILE="data/bag_of_words/full/test.tfrecord"

OMELETE_TRAIN_FILE="data/bag_of_words/omelete/train.tfrecord"
OMELETE_VALIDATION_FILE="data/bag_of_words/omelete/validation.tfrecord"
OMELETE_TEST_FILE="data/bag_of_words/omelete/test.tfrecord"

CEC_TRAIN_FILE="data/bag_of_words/cec/train.tfrecord"
CEC_VALIDATION_FILE="data/bag_of_words/cec/validation.tfrecord"
CEC_TEST_FILE="data/bag_of_words/cec/test.tfrecord"

CINECLICK_TRAIN_FILE="data/bag_of_words/cineclick/train.tfrecord"
CINECLICK_VALIDATION_FILE="data/bag_of_words/cineclick/validation.tfrecord"
CINECLICK_TEST_FILE="data/bag_of_words/cineclick/test.tfrecord"

FULL_EMBEDDING_PATH="data/bag_of_words/full/fasttext.pkl"
OMELETE_EMBEDDING_PATH="data/bag_of_words/omelete/fasttext.pkl"
CEC_EMBEDDING_PATH="data/bag_of_words/cec/fasttext.pkl"
CINECLICK_EMBEDDING_PATH="data/bag_of_words/cineclick/fasttext.pkl"

FULL_EMBEDDING_CKPT="data/bag_of_words/full/embedding.ckpt"
OMELETE_EMBEDDING_CKPT="data/bag_of_words/omelete/embedding.ckpt"
CEC_EMBEDDING_CKPT="data/bag_of_words/cec/embedding.ckpt"
CINECLICK_EMBEDDING_CKPT="data/bag_of_words/cineclick/embedding.ckpt"

EMBEDDING_CKPT_NAME="tf_embedding"
EMBEDDING_SIZE=300
DROPOUT_RATE=0.5
NUM_LABELS=5
NUM_UNITS=150
WEIGHT_DECAY=0.0001
LEARNING_RATE=0.001
BATCH_SIZE=32
NUM_EPOCHS=15
BUCKET_WIDTH=30
NUM_BUCKETS=30


python bow_model.py \
    --train-file=${FULL_TRAIN_FILE} \
    --validation-file=${FULL_VALIDATION_FILE} \
    --test-file=${FULL_TEST_FILE} \
    --embedding-path=${FULL_EMBEDDING_PATH} \
    --embedding-ckpt=${FULL_EMBEDDING_CKPT} \
    --embedding-ckpt-name=${EMBEDDING_CKPT_NAME} \
    --embed-size=${EMBEDDING_SIZE} \
    --dropout=${DROPOUT_RATE} \
    --num-labels=${NUM_LABELS} \
    --num-units=${NUM_UNITS} \
    --weight-decay=${WEIGHT_DECAY} \
    --learning-rate=${LEARNING_RATE} \
    --batch-size=${BATCH_SIZE} \
    --num-epochs=${NUM_EPOCHS} \
    --bucket-width=${BUCKET_WIDTH} \
    --num-buckets=${NUM_BUCKETS}
