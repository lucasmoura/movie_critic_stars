#!/bin/bash

set -e

#usage
#./script/run_dataset_preprocessing.sh

OMELETE_REVIEWS_FOLDER="data/omelete/movies/"

PREPROCESSING_TYPE="bag_of_words"
STOPWORDS_PATH="preprocessing/files/stopwords.txt"

python preprocess_dataset.py \
    --reviews-folder=${OMELETE_REVIEWS_FOLDER} \
    --preprocessing-type=${PREPROCESSING_TYPE} \
    --stopwords-path=${STOPWORDS_PATH}
