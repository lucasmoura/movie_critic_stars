#!/bin/bash

#usage: ./scripts/download_data.sh

set -e

DATA_DIR="data"
FASTTEXT_DIR="fasttext"
FASTTEXT_URL="https://s3-us-west-1.amazonaws.com/fasttext-vectors/wiki.pt.zip"
FASTEXT_ZIP="wiki.pt.zip"
FASTTEXT_FILE="wiki.pt.bin"

if [ ! -d "$DATA_DIR" ]; then
    mkdir "$DATA_DIR"
fi

cd "$DATA_DIR"

if [ ! -d "$FASTTEXT_DIR" ]; then
    mkdir "$FASTTEXT_DIR"
fi

cd "$FASTTEXT_DIR"

if [ ! -e "$FASTTEXT_FILE" ]; then
    wget "$FASTTEXT_URL"
    unzip "$FASTEXT_ZIP"
    rm "$FASTEXT_ZIP"
else
    echo "FastText file already downloaded!"
fi

cd ..

cd ..


