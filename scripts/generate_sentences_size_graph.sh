#!/bin/bash

set -e

#usage: ./scripts/generate_sentences_size_graph.sh

GRAPH_FOLDER="data_analysis/graphs/sentences_size"

OMELETE_MOVIES_FOLDER="data/omelete/movies"
OMELETE_GRAPH_NAME="omelete_sentences_size.png"
OMELETE_WEBSITE="Omelete"
OMELETE_GRAPH_COLOR="y"

echo "Generating $OMELETE_WEBSITE sentence size graph"
python data_analysis/sentence_size.py \
  --website-name=${OMELETE_WEBSITE} \
  --movies-folder=${OMELETE_MOVIES_FOLDER} \
  --graph-folder=${GRAPH_FOLDER} \
  --graph-name=${OMELETE_GRAPH_NAME} \
  --graph-color=${OMELETE_GRAPH_COLOR}

CINEMA_EM_CENA_MOVIES_FOLDER="data/cinema_em_cena/movies"
CINEMA_EM_CENA_GRAPH_NAME="cinema_em_cena_sentences_size.png"
CINEMA_EM_CENA_WEBSITE="Cinema Em Cena"
CINEMA_EM_CENA_GRAPH_COLOR="r"

echo "Generating $CINEMA_EM_CENA_WEBSITE sentence size graph"
python data_analysis/sentence_size.py \
  --website-name="$CINEMA_EM_CENA_WEBSITE" \
  --movies-folder=${CINEMA_EM_CENA_MOVIES_FOLDER} \
  --graph-folder=${GRAPH_FOLDER} \
  --graph-name=${CINEMA_EM_CENA_GRAPH_NAME} \
  --graph-color=${CINEMA_EM_CENA_GRAPH_COLOR}

CINECLICK_MOVIES_FOLDER="data/cineclick/movies"
CINECLICK_GRAPH_NAME="cineclick_sentences_size.png"
CINECLICK_WEBSITE="Cineclick"
CINECLICK_GRAPH_COLOR="b"

echo "Generating $CINECLICK_WEBSITE sentence size graph"
python data_analysis/sentence_size.py \
  --website-name=${CINECLICK_WEBSITE} \
  --movies-folder=${CINECLICK_MOVIES_FOLDER} \
  --graph-folder=${GRAPH_FOLDER} \
  --graph-name=${CINECLICK_GRAPH_NAME} \
  --graph-color=${CINECLICK_GRAPH_COLOR}
