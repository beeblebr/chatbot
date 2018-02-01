import pickle
import re

from nltk.corpus import stopwords

from util.sense_utils import _transform_doc_nltk
import os

# Custom stopwords list
stop = map(lambda x : x.strip(), open('code/words.txt', 'rb').readlines())

def get_all_topics(message, transformed=False):
    message = message.encode('ascii', 'ignore')
    if not transformed:
    	pos = _transform_doc_nltk(message).split()
    else:
    	pos = message.split()
    topics = filter(lambda x : x.split('|')[1] == 'NOUN', pos)
    topics = filter(lambda x : x.split('|')[0] not in stop, topics)
    return topics

