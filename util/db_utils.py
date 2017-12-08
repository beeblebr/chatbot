from pymongo import MongoClient


client = MongoClient()
db = client.get_database('main')


def get_knowledge_corpus():
	k = db.knowledge.find()
	return k


def insert_knowledge(k):
	db.knowledge.insert_one(k)