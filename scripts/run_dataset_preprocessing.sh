#!/bin/bash

set -e

#usage
#./script/run_dataset_preprocessing.sh

OMELETE_REVIEWS_FOLDER="data/omelete/movies/"
CINECLICK_REVIEWS_FOLDER="data/cineclick/movies"
CINEMA_EM_CENA_REVIEWS_FOLDER="data/cinema_em_cena/movies"

PREPROCESSING_TYPE="bag_of_words"
STOPWORDS_PATH="preprocessing/files/stopwords.txt"

FASTTEXT_FILE="data/fasttext/wiki.pt.bin"
EMBEDDING_PATH="data/fasttext/fasttext.pkl"
EMBEDDING_WORDINDEX_PATH="data/fasttext/fasttext_word_index.pkl"
EMBED_SIZE=300

python preprocess_dataset.py \
    --omelete-folder=${OMELETE_REVIEWS_FOLDER} \
    --cec-folder=${CINEMA_EM_CENA_REVIEWS_FOLDER} \
    --cineclick-folder=${CINECLICK_REVIEWS_FOLDER} \
    --preprocessing-type=${PREPROCESSING_TYPE} \
    --stopwords-path=${STOPWORDS_PATH} \
    --embedding-file=${FASTTEXT_FILE} \
    --embedding-path=${EMBEDDING_PATH} \
    --embedding-wordindex-path=${EMBEDDING_WORDINDEX_PATH} \
    --embed-size=${EMBED_SIZE}
