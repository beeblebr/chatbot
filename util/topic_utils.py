import math
import string
import difflib

import cPickle as pickle

from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz, process

from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer


print('Loading category list file...')
cats = map(lambda x : x.lower().encode('ascii', 'ignore'), pickle.load(open('topics3', 'rb')))
print('Loading Word2Vec model...')
# model = pickle.load(open('model.pickle', 'rb'))
model = {}

def w2v_similarity(a, b):
	if a in model and b in model:
		return cosine_similarity([model[a]], [model[b]])[0][0]
	return 0


def sentence_similarity(sent, word):
	a = 0
	count = 0
	for w in sent.split():
		si = w2v_similarity(w, word)
		if si == 0:
			continue
		a += si # * tfidf(w)
		count += 1
	a = a / float(max(1, count))
	return a


def get_top_categories(text):
	return map(lambda x : x[1], sorted(map(lambda x : (sentence_similarity(text, x), x), cats), reverse=True)[:5])


stop = set(stopwords.words('english'))
tokenizer = RegexpTokenizer(r'\w+')


def clean_text(sent):
    sent = sent.lower()
    res = map(lambda x : ' '.join(filter(lambda y : y not in stop, tokenizer.tokenize(x))), [sent])[0]
    return res


