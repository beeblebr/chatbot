import cPickle as pickle
import string
from random import *
from string import digits
import names

import categorize

from pymongo import MongoClient

k = pickle.load(open('k', 'rb'))
# q = pickle.load(open('q_processed', 'rb'))

N = len(k)

client = MongoClient('35.197.133.233', username='mongoadmin', password='3aw#Aq')
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

from datetime import datetime

def store_knowledge():

	db.knowledge.remove({})

	knowledge = []

	for i, text in enumerate(k):
		knowledge.append({'text': text, 'timestamp': datetime.now(), 'eight_id': str(i).zfill(8)})

	for i in knowledge:
		db.knowledge.insert_one(i)

create_users()
store_knowledge()
