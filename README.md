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
website will possess a folder with the following hierarchy (Using omelete
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
