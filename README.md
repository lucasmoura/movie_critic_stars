Movie Critic Stars
===================

One common problem for movie critics is, once the movie review is written, which
rating should they give it ?

This project aims to learn this rating process by looking at different rated
reviews and learn the rating process using machine learning techniques.

The reviews used in this project are all written in Brazilian Portuguese and
have a rating ranging from one to five stars.

Currently, the reviews come from three different websites:

* [Cinema Em Cena](http://cinemaemcena.cartacapital.com.br/)
* [Omelete](http://omelete.uol.com.br/)
* [Cineclick](http://cineclick.com.br/)


Data
------------------

In order to download the movie reviews, run the following command:

```sh
$ ./scripts/download_all_reviews.sh
```

The reviews will be stored in a folder named **data**. Inside this folder, every
website will possess a folder with the following hierarchy (Using Omelete
website as example):

```
data
└───omelete
│   └───movies
│       └───1
│       │   -   movie_review1.txt
│       │   -   ...
│       └───2
│       │   -   movie_review100.txt
│       │   -   ...
│       └───3
│       │   -   movie_review300.txt
│       │   -   ...
│       └───4
│       │   -   movie_review500.txt
│       │   -   ...
│       └───5
│       │   -   movie_review800.txt
│       │   -   ...
```

Folder such as **1** or **2** contain only reviews marked with that rating.


Movie Review
--------------------

Every review file have the following structure:

* First line: Name of the movie
* Second line: Director of the movie (If it was not possible to extract it from
  the website, the line will contain INVALID\_DIRECTOR)
* Third line: The name of the actors/actress in the movie separated by a comma
  (If it was not possible to extract the actors from the website, the line will
  contain INVALID\_ACTORS)
* Fourth line: The movie review
* Fifth line: The date the review was published


Data Pre-processing
----------------------

To pre-process the data, run the script:

```sh
$ ./scripts/run_dataset_preprocessing.sh
```

This script will produce five distinct datasets inside the "data/bag\_of\_words" folder:

* Full: Uses all movie reviews sources to create the dataset
* Full (Undersampling): Uses all movie reviews sources to create the dataset, but applies the 
                        undersampling technique to the training dataset.
* Omelete: Uses only Omelete reviews to create the dataset.
* Cineclick: Uses only Cineclick reviews to create the dataset.
* Cec: Uses only Cinema Em Cena reviews to create the dataset.

To better understand how the movies were pre-processed, please read the my [blog post](https://lucasmoura.github.io/blog/2018/01/31/automatic-star-rating-for-movie-reviews-part-2/)

Bag of Words models
----------------------

To run the Bag Of Words model, just run the script

```sh
$ ./scripts/run_bow_model.sh
```

It will run the model for all datasets produced by the preprocessing script.
The results will be saved inside "data/bag\_of\_words" folder. Inside, every dataset
will have a corresponding folder. For example, the full dataset will will be located in the folder
"data/bag\_of\_words/full". The results of running the model for each dataset will be located in the
"model" dir inside each dataset folder.
