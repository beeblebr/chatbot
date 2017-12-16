import math
import string
import difflib
import operator
import functools

import cPickle as pickle

from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz, process

from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

from util.db_utils import *

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


def assemble_topic_wise_rankings(similarity_map, corpus):
    """Assemble separate rankings for each topic"""
    assert similarity_map
    valid_variants = map(lambda x : x['topic'], similarity_map[0])

    topic_wise_ranking = {}
    for topic in valid_variants:
        ranking = []
        for i in range(len(corpus)):
            item = corpus[i].copy()
            try:
                current_topic = [x for x in similarity_map[i] if x['topic'] == topic][0]
                score = float(current_topic['score'])
                rank = float(current_topic['rank'])
                matched_variant = current_topic['matched_variant']
            except Exception as e:
                score = 0
                rank = float('inf')
                matched_variant = None
            item.update(score=score)
            item.update(rank=rank)
            item.update(matched_variant=matched_variant)
            ranking.append(item)

        from pprint import pprint
        topic_wise_ranking[topic] = ranking

    return topic_wise_ranking


def get_aggregate_scores(topic_wise_ranking, corpus):
    """Averages scores from topic wise rankings"""
    aggregate_ranking = []

    for i in range(len(corpus)):
        topics = topic_wise_ranking.keys()
        # Get similarity scores for same knowledge item from the perspective of all topics
        scores = [topic_wise_ranking[topic][i]['score'] for topic in topics]
        matched_variants = [topic_wise_ranking[topic][i]['matched_variant'] for topic in topics]
        # Get average similarity score (make it weighted?)
        avg_similarity = sum(scores) / float(len(scores))

        item = corpus[i].copy()
        item.update(avg_score=avg_similarity)
        item.update(matched_variants=matched_variants)
        aggregate_ranking.append(item)

    return aggregate_ranking


class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))

def find_topic_intersection(combination, topic_wise_ranking):
    """Finds the knowledge items tagged with all these topics"""
    ids = [map(hashabledict, topic_wise_ranking[topic]) for topic in combination]
    common_items = list(functools.reduce(operator.and_, map(set, ids)))
    
    # common_items = map(set, common_items)
    # common_items = []
    # if common_item_ids:
    #     common_items = list(db.knowledge.find({'$or': [{'_id': id} for id in common_item_ids]}))
    return common_items
