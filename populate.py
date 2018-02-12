import cPickle as pickle
import string
from random import *
from string import digits
from datetime import datetime

from pymongo import MongoClient

from util.topic_utils import transform_doc_nltk


k = pickle.load(open('k', 'rb'))
N = len(k)

client = MongoClient('mongo')
db = client.main


def create_users():
    db.users.remove({})
    for i in range(N):
        db.users.insert_one({
            'eight_id': str(i).zfill(8), 
            'name': str(i)
        })


def store_knowledge():
    db.knowledge.remove({})
    for i, text in enumerate(k):
        db.knowledge.insert_one({
            'text': text, 
            'timestamp': datetime.now(), 
            'eight_id': str(i).zfill(8)
        })


def cache_transformation_of_knowledge_items():
    corpus = db.knowledge.find()
    for k in corpus:
        try:
            print(k['_id'])
            transformed_text = transform_doc_nltk(k['text'])
            db.knowledge.update_one(
                {'_id': k['_id']}, {'$set': {'transformed_text': transformed_text}})
        except Exception as e:
            print(e)

    print('Knowledge items transformed')

# create_users()
# store_knowledge()
# cache_transformation_of_knowledge_items()