from pymongo import MongoClient
from datetime import datetime

import conf

client = MongoClient(username=conf.MONGO_USERNAME, password=conf.MONGO_PASSWORD)
#client = MongoClient(username='mongoadmin', password='3aw#Aq')
db = client.get_database('main')

def get_knowledge_corpus(exclude_user=None):
	filter = {}
	if exclude_user:
		filter = {'eight_id': {'$ne': exclude_user}}
	k = db.knowledge.find(filter)
	return k


def insert_knowledge(k, transform_text=True):
	from util.sense_utils import _transform_doc
	if transform_text:
		transformed_text = _transform_doc(k['text'])
		k['transformed_text'] = transformed_text
	db.knowledge.insert_one(k)


def update_knowledge():
	import pickle
	kk = pickle.load(open('k', 'rb'))
	for i, k in enumerate(kk):
		db.knowledge.update_one({'eight_id': str(i).zfill(8)}, {'$set': {'text': k}}, upsert=False)


def get_knowledge_by_eight_id(eight_id):
	return db.knowledge.find_one({'eight_id': eight_id})


def get_name_from_id(id):
	return db.users.find_one({'eight_id': id})['name']


def attempt_login(username, password):
	return db.users.find_one({'username': username, 'password': password})


def get_user_from_eight_id(eight_id):
	return db.users.find_one({'eight_id': eight_id})


def add_user(eight_id, **kwargs):
	user_details = kwargs
	user_details.update(eight_id=eight_id)
	db.users.insert_one(user_details)
	

def add_question_to_user_history(eight_id, question_text):
	question = {
		'text': question_text,
		'timestamp': datetime.now()
	}
	db.users.update({'eight_id': eight_id}, {'$push': {'questions': question}})


def clear_questions_history_for_user(eight_id):
	db.users.update({'eight_id': eight_id}, {'$unset': {'questions': 1}}, multi=True, upsert=True)


def clear_questions_history():
	db.users.update({}, {'$unset': {'questions': 1}}, multi=True, upsert=True)	