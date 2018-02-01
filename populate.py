import cPickle as pickle
import string
from random import *
from string import digits
from util.sense_utils import _transform_doc_nltk
import categorize
from datetime import datetime
from pymongo import MongoClient

k = pickle.load(open('k', 'rb'))
# q = pickle.load(open('q_processed', 'rb'))

N = len(k)
client = MongoClient('mongo')
#client = MongoClient('35.197.133.233', username='mongoadmin', password='3aw#Aq')
#client = MongoClient('35.185.96.31')
db = client.main


def create_users():
    db.users.remove({})
    def get_random_id():
        return ''.join(choice(digits) for i in range(8))

    users = []
    for i in range(N):
        users.append({'eight_id': str(i).zfill(8), 'name': str(i)})

    for u in users:
        db.users.insert_one(u)



def store_knowledge():

    db.knowledge.remove({})

    knowledge = []

    for i, text in enumerate(k):
        knowledge.append(
            {'text': text, 'timestamp': datetime.now(), 'eight_id': str(i).zfill(8)})

    for i in knowledge:
        db.knowledge.insert_one(i)


def cache_transformation_of_knowledge_items():

    corpus = db.knowledge.find()

    for k in corpus:
        try:
            print(k['_id'])
            transformed_text = _transform_doc_nltk(k['text'])
            db.knowledge.update_one(
                {'_id': k['_id']}, {'$set': {'transformed_text': transformed_text}})
        except Exception as e:
            print(e)

    print('Knowledge items transformed')

print('what')

# create_users()
# store_knowledge()
# cache_transformation_of_knowledge_items()