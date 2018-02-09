#!/bin/bash

set -e

#usage
#./script/run_rnn_model.sh

FULL_TRAIN_FILE="data/rnn/full/train.tfrecord"
FULL_VALIDATION_FILE="data/rnn/full/validation.tfrecord"
FULL_TEST_FILE="data/rnn/full/test.tfrecord"
FULL_SAVE_PATH="data/rnn/full/model/"

FULL_UNDERSAMPLING_TRAIN_FILE="data/rnn/full/undersampling/train.tfrecord"
FULL_UNDERSAMPLING_VALIDATION_FILE="data/rnn/full/undersampling/validation.tfrecord"
FULL_UNDERSAMPLING_TEST_FILE="data/rnn/full/undersampling/test.tfrecord"
FULL_UNDERSAMPLING_SAVE_PATH="data/rnn/full/undersampling/model/"

OMELETE_TRAIN_FILE="data/rnn/omelete/train.tfrecord"
OMELETE_VALIDATION_FILE="data/rnn/omelete/validation.tfrecord"
OMELETE_TEST_FILE="data/rnn/omelete/test.tfrecord"
OMELETE_SAVE_PATH="data/rnn/omelete/model/"

CEC_TRAIN_FILE="data/rnn/cec/train.tfrecord"
CEC_VALIDATION_FILE="data/rnn/cec/validation.tfrecord"
CEC_TEST_FILE="data/rnn/cec/test.tfrecord"
CEC_SAVE_PATH="data/rnn/cec/model/"

CINECLICK_TRAIN_FILE="data/rnn/cineclick/train.tfrecord"
CINECLICK_VALIDATION_FILE="data/rnn/cineclick/validation.tfrecord"
CINECLICK_TEST_FILE="data/rnn/cineclick/test.tfrecord"
CINECLICK_SAVE_PATH="data/rnn/cineclick/model/"

FULL_EMBEDDING_PATH="data/rnn/full/fasttext.pkl"
FULL_UNDERSAMPLING_EMBEDDING_PATH="data/rnn/full/undersampling/fasttext.pkl"
OMELETE_EMBEDDING_PATH="data/rnn/omelete/fasttext.pkl"
CEC_EMBEDDING_PATH="data/rnn/cec/fasttext.pkl"
CINECLICK_EMBEDDING_PATH="data/rnn/cineclick/fasttext.pkl"

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

#echo "Run full model without undersampling"
#python rnn_model.py \
#    --train-file=${FULL_TRAIN_FILE} \
#    --validation-file=${FULL_VALIDATION_FILE} \
#    --test-file=${FULL_TEST_FILE} \
#    --save-path=${FULL_SAVE_PATH} \
#    --embedding-path=${FULL_EMBEDDING_PATH} \
#    --embed-size=${EMBEDDING_SIZE} \
#    --dropout=${DROPOUT_RATE} \
#    --num-labels=${NUM_LABELS} \
#    --num-units=${NUM_UNITS} \
#    --weight-decay=${WEIGHT_DECAY} \
#    --learning-rate=${LEARNING_RATE} \
#    --batch-size=${BATCH_SIZE} \
#    --num-epochs=${NUM_EPOCHS} \
#    --bucket-width=${BUCKET_WIDTH} \
#    --num-buckets=${NUM_BUCKETS}

echo "Run full model with undersampling"
python rnn_model.py \
    --train-file=${FULL_UNDERSAMPLING_TRAIN_FILE} \
    --validation-file=${FULL_UNDERSAMPLING_VALIDATION_FILE} \
    --test-file=${FULL_UNDERSAMPLING_TEST_FILE} \
    --save-path=${FULL_UNDERSAMPLING_SAVE_PATH} \
    --embedding-path=${FULL_UNDERSAMPLING_EMBEDDING_PATH} \
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

echo "Run omelete model"
python rnn_model.py \
    --train-file=${OMELETE_TRAIN_FILE} \
    --validation-file=${OMELETE_VALIDATION_FILE} \
    --test-file=${OMELETE_TEST_FILE} \
    --save-path=${OMELETE_SAVE_PATH} \
    --embedding-path=${OMELETE_EMBEDDING_PATH} \
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

echo "Run cineclick model"
python rnn_model.py \
    --train-file=${CINECLICK_TRAIN_FILE} \
    --validation-file=${CINECLICK_VALIDATION_FILE} \
    --test-file=${CINECLICK_TEST_FILE} \
    --save-path=${CINECLICK_SAVE_PATH} \
    --embedding-path=${CINECLICK_EMBEDDING_PATH} \
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

echo "Run Cinema em Cena model"
python rnn_model.py \
    --train-file=${CEC_TRAIN_FILE} \
    --validation-file=${CEC_VALIDATION_FILE} \
    --test-file=${CEC_TEST_FILE} \
    --save-path=${CEC_SAVE_PATH} \
    --embedding-path=${CEC_EMBEDDING_PATH} \
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
