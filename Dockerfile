# Use an official Python runtime as a parent image
FROM python:2.7-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN apt-get update && \
	apt-get -y upgrade && \
 	apt-get install -y gcc g++ && \
 	pip install -r requirements.txt --no-cache-dir && \
	python -m spacy download en && \
	python -c "import nltk; nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"

# Train Rasa NLU and Core models
RUN ./train_nlu.sh && \
    ./train_dialogue.sh


# Make port 8001 available outside
EXPOSE 8002

CMD python code/populate.py; python code/server.py