import operator
import functools
import re

from util.db_utils import *
from util.sense_utils import _transform_doc_nltk

# Custom stopwords list
stop = map(lambda x : x.strip(), open('code/data/words.txt', 'rb').readlines())


def prettify_topic(x):
    return x.split('|')[0].replace('_', ' ')


def uglify_topic(x):
    return x.replace(' ', '_') + '|NOUN'


def get_all_topics(message, transformed=False):
    message = message.encode('ascii', 'ignore')
    if not transformed:
        pos = _transform_doc_nltk(message).split()
    else:
        pos = message.split()
    topics = filter(lambda x : x.split('|')[1] == 'NOUN', pos)
    topics = filter(lambda x : x.split('|')[0] not in stop, topics)
    return topics


def assemble_topic_wise_rankings(similarity_map, corpus):
    """Assemble separate rankings for each topic"""
    valid_variants = map(lambda x : x['topic'], similarity_map[0])

    topic_wise_ranking = {}

    for topic in valid_variants:
        ranking = []
        for i in range(len(corpus)):
            item = corpus[i].copy()
            try:
                current_topic = [x for x in similarity_map[i] if x['topic'] == topic][0]
                score = float(current_topic['score'])
                rank1 = float(current_topic['rank1'])
                rank2 = float(current_topic['rank2'])
                matched_variant = current_topic['matched_variant']
            except Exception as e:
                score = 0
                rank = float('inf')
                matched_variant = None
            item.update(score=score)
            item.update(rank1=rank1)
            item.update(rank2=rank2)
            item.update(matched_variant=matched_variant)
            ranking.append(item)
            
        topic_wise_ranking[topic] = ranking

    return topic_wise_ranking


def get_aggregate_scores(topic_wise_ranking, corpus):
    """Averages scores from topic wise rankings"""
    topics = topic_wise_ranking.keys()
    aggregate_ranking = []
    
    for i in range(len(corpus)):
        try:
            # Get similarity scores for same knowledge item from the perspective of all topics
            scores = [topic_wise_ranking[topic][i]['score'] for topic in topics]
            matched_variants = [topic_wise_ranking[topic][i]['matched_variant'] for topic in topics]
            # Get average similarity score (make it weighted?)
            avg_similarity = sum(scores) / max(1, float(len(scores)))

            item = corpus[i].copy()
            item.update(avg_score=avg_similarity)
            item.update(matched_variants=matched_variants)
            aggregate_ranking.append(item)
        except Exception as e:
            print(e)

    return aggregate_ranking


class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


def find_topic_intersection(combination, topic_wise_ranking):
    """Finds the knowledge items tagged with all these topics"""
    ids = [map(hashabledict, topic_wise_ranking[topic]) for topic in combination]
    common_items = list(functools.reduce(operator.and_, map(set, ids)))
    return common_items
