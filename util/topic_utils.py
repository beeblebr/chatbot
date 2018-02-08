import operator
import functools
import re

from util.db_utils import *
from util.sense_utils import _transform_doc_nltk

# Custom stopwords list
stop = map(lambda x : x.strip(), open('code/data/words.txt', 'rb').readlines())


def prettify_topic(x):
    return x.split('|')[0].replace('_', ' ')


def uglify_topic(x):
    return x.replace(' ', '_') + '|NOUN'


def get_all_topics(message, transformed=False):
    message = message.encode('ascii', 'ignore')
    if not transformed:
        pos = _transform_doc_nltk(message).split()
    else:
        pos = message.split()
    topics = filter(lambda x : x.split('|')[1] == 'NOUN', pos)
    topics = filter(lambda x : x.split('|')[0] not in stop, topics)
    return topics
