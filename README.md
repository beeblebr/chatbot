Myndpool
=============

Service
-------------

The application consists of 3 dockerized services:
* Flask web server which runs the main application
* Sense server which runs the memory intensive Sense2Vec server
* MongoDB database server

Frontend is written in JavaScript (jQuery), backend is in Python (2.7)


### Requirements

* docker (tested on Docker version 17.12.0-ce)
* docker-compose (tested on docker-compose version 1.18.0)


### Start all services

The configuration of the service is done through `docker-compose.yml`.

`docker-compose up`


## High-level overview

web
-------------
The service named "web", which is the main Myndpool webapp, uses files from the following directories:
- / 
- util/
- templates/
- static/
- data/

It is strctured as a standard Python Flask project. 
The templates/ folder contains the HTML files.
The static/ folder contains Javascript, images and CSS files.
The data/ folder contains configuration and data files related to Rasa.AI (the chatbot framework in use).
The util/ folder contains utilities.

The main Python files in the root directory include 
- server.py (main file)
- actions.py (handles chatbot actions)
- conf.py contains constants
- lin.py contains WordNet similarity functions
- bot_wrapper.py is a supporting file for server.py 

There are also 2 shell scripts 
- train_nlu.sh
- train_dialogue.sh

They train the Keras (Tensroflow based) models for the chatbot using the training files in data/. This is a one-time operation taken care of by the docker file.


sense
-------------
The sense server is separated from the main project because:
1. It is too memory intensive to be run on a local, lightweight development machine.
2. A dependency conflicts with Spacy, which prevents both of them from being installed in the same Python environment together, so it had to be separated.


mongo
-------------
Vanilla MongoDB.

The file populate.py in the root directory populates the database with users and knowledge items for each of them. This data is a subset of the larger dataset that we received from the Myndpool team (after manual cleaning).

The way that the users / knowledge items are structured is that there is a one-to-one correspondence between the users and knowledge items. 

The user IDs follow the same 8-ID pattern starting from "00000000", "00000001", etc. to "00000355", each associated with a single knowledge item. The names of the users are the same as this number (without the leading zeros).



