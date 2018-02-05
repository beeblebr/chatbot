from db.db import get_connection

db = get_connection()

def add_relation(a, b):
	db.custom_relations.insert({'a': a, 'b': b})
