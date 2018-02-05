from pymongo import MongoClient
from datetime import datetime

from util.topic_utils import get_all_topics
from util.sense_utils import _transform_doc_nltk

import conf


client = MongoClient('mongo', username=conf.MONGO_USERNAME, password=conf.MONGO_PASSWORD)

db = client.get_database('main')

def get_knowledge_corpus(exclude_user=None):
	filter = {}
	if exclude_user:
		filter = {'eight_id': {'$ne': exclude_user}}
	k = db.knowledge.find(filter)
	return k


def insert_knowledge(k, transform_text=True):
	if transform_text:
		transformed_text = _transform_doc_nltk(k['text'])
		k['transformed_text'] = transformed_text
	db.knowledge.insert_one(k)


def delete_knowledge_item(eight_id, item_text):
	db.knowledge.remove({'eight_id': eight_id, 'text': item_text})


def get_knowledge_by_eight_id(eight_id):
	return db.knowledge.find_one({'eight_id': eight_id})


def get_knowledge_list_by_eight_id(eight_id):
	return list(db.knowledge.find({'eight_id': eight_id}))


def get_name_from_id(id):
	return db.users.find_one({'eight_id': id})['name']


def attempt_login(username, password):
	return db.users.find_one({'username': username, 'password': password})


def get_user_from_eight_id(eight_id):
	return db.users.find_one({'eight_id': eight_id})


def get_all_users():
	return sorted(list(db.users.find({})), key=lambda x: x['eight_id'])


def delete_user(id):
	db.users.remove({'eight_id': id})
	db.knowledge.remove({'eight_id': id})


def add_user(eight_id, **kwargs):
	user_details = kwargs
	user_details.update(eight_id=eight_id)
	db.users.insert_one(user_details)
	

def add_question_to_user_history(eight_id, question_text):
	question = {
		'eight_id': eight_id,
		'text': question_text,
		'transformed_text': ' '.join(get_all_topics(question_text)),
		'timestamp': datetime.now()
	}
	db.history.insert(question)


def clear_questions_history_for_user(eight_id):
	db.users.update({'eight_id': eight_id}, {'$unset': {'questions': 1}}, multi=True, upsert=True)


def clear_questions_history():
	db.users.update({}, {'$unset': {'questions': 1}}, multi=True, upsert=True)	


def get_questions_since(start_time):
	return db.history.find({'timestamp': {'$gt': start_time}}).sort('timestamp')