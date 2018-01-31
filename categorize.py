import math
import string
import difflib

import cPickle as pickle

from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz, process


def preprocess(cats):
	cats = map(lambda x : x.translate(None, string.punctuation).split()[0], cats)

	present = filter(lambda x : x in model, cats)
	return present
	# not_present = filter(lambda x : x not in model, cats)
	# closest_matches = []
	# for i, np in enumerate(not_present):
	# 	closest_matches.append(difflib.get_close_matches(np, model.wv.vocab.keys()))
	# closest_matches = filter(lambda x : x[1] > 85, closest_matches)
	# closest_matches = map(lambda x : x[0], closest_matches)

	# cats = present + closest_matches

	# return cats


def sim(a, b):
	if a not in model:
		matches = difflib.get_close_matches(a, model.wv.vocab)
		print matches
		if matches:
			a = matches[0]
			print 'Fixed to', a
	if b not in model:
		matches = difflib.get_close_matches(b, model.wv.vocab)
		print matches
		if matches:
			b = matches[0]
			print 'Fixed to', b
	if a in model and b in model:
		return cosine_similarity([model[a]], [model[b]])[0][0]
	return 0


def avg(sent, word):
	a = 0
	count = 0
	for w in sent.split():
		si = sim(w, word)
		if si == 0:
			continue
		a += si # * tfidf(w)
		count += 1
	a = a / float(max(1, count))
	return a


def get_top_categories(text):
	return map(lambda x : x[1], sorted(map(lambda x : (avg(text, x), x), cats), reverse=True)[:10])


# if __name__ == '__main__'
# 	#PREPROCESS = True
# 	print 'Loading Word2Vec...'
# 	model = pickle.load(open('model.pickle', 'rb'))

# 	cats = map(lambda x : x.lower().encode('ascii', 'ignore'), pickle.load(open('topics3', 'rb')))
# 	# if PREPROCESS:
# 	# 	preprocess(cats)
# 	#pickle.dump(cats, open('topics3', 'wb'))
