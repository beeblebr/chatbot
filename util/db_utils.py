from pymongo import MongoClient

client = MongoClient()
db = client.get_database('main')

def get_knowledge_corpus():
	k = db.knowledge.find()
	return k


def insert_knowledge(k):
	db.knowledge.insert_one(k)


def update_knowledge():
	import pickle
	kk = pickle.load(open('k', 'rb'))
	for i, k in enumerate(kk):
		db.knowledge.update_one({'eight_id': str(i).zfill(8)}, {'$set': {'text': k}}, upsert=False)


def get_name_from_id(id):
	return db.users.find_one({'eight_id': id})['name']