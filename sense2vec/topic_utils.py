from collections import namedtuple
from itertools import product

from sklearn.metrics.pairwise import cosine_similarity

import sense2vec

sense_vec_model = sense2vec.load()


def find_valid_case_combination(topic):
    topic = unicode(topic)
    tokens = topic.split('|')[0].split('_')
    param_for_product = [[1, 0]] * len(tokens)
    case_variants = []
    for comb in product(*param_for_product):
        variant = [tokens[i].title() if comb[i] else tokens[i].lower() for i in range(len(tokens))]
        repr = '_'.join(variant) + '|NOUN'
        if repr in sense_vec_model:
            return repr
    return None


def generate_variants(topic):
    tokens = topic.split('|')[0].split('_')
    variants = []
    for i in range(len(tokens)):
        variants.append(tokens[i:])
        variants.append(tokens[:-i])
    variants = [find_valid_case_combination('_'.join(x) + '|NOUN') for x in variants]
    variants = filter(lambda x : x and x != '|NOUN', variants)  # Remove empty strings
    variants = map(lambda topic : topic.split('|')[0].split('_'), variants)

    # Remove proper subsets
    proper_subsets = []
    for i in range(len(variants) - 1):
        for j in range(i + 1, len(variants)):
            if ' '.join(variants[j]) in ' '.join(variants[i]):
                proper_subsets.append(variants[j])
    unique = set(map(tuple, variants)) - set(map(tuple, proper_subsets))
    return sorted([unicode('_'.join(x)) + '|NOUN' for x in unique], key=lambda x : len(x.split('|')[0].split('_')), reverse=True)


def get_top_items(topic, n=1000):
    topic = unicode(topic)
    try:
        token = sense_vec_model[topic][1]
        related_items = sense_vec_model.most_similar(token, n)[0]
    except Exception as e:
        print(e)

    prettify_topic = lambda x : x.split('|')[0].replace('_', ' ')

    for i in range(len(related_items)):
        related_items[i] = {'text': prettify_topic(related_items[i]), 'similarity': sense_vec_model_similarity(topic, related_items[i]).similarity}
        if related_items[i]['similarity'] < 0.6:
            break

    return related_items[:i]


# def get_index_in_rankings(token, search_term, nearest_items, n=20000):
#     token = sense_vec_model[unicode(token)][1]
#     try:
#         index = nearest_items.index(unicode(search_term))
#         return index
#     except ValueError as e:
#         return float('inf')


# def get_index_ranking_product(a, b, nearest_a):
#     result = get_index_in_rankings(a, b, nearest_a) * get_index_in_rankings(b, a, nearest_b)
#     return result


def topic_similarity_map(topics1, topics2):
    Comparison = namedtuple('Comparison', ['score', 'matched_topic', 'matched_variant'])
    
    try:
        if not topics1 or not topics2:
            return [{'topic': t, 'score': '0', 'rank1': 0, 'rank2': 0} for t in topics1]
            
        flatten = lambda l: [item for sublist in l for item in sublist]
        # Generate all variants for both sets of topics
        topics1_variants = flatten([generate_variants(t) for t in topics1])
        topics2_variants = flatten([generate_variants(t) for t in topics2])

        # Calculate aggregate similarity score
        similarity_map = []
        for i in topics1_variants:
            current_topic_sims = []
            for j in topics2_variants:
                current_topic_sims.append(Comparison(score=sense_vec_model_similarity(i, j), matched_topic=i, matched_variant=j))
            most_similar = sorted(current_topic_sims, key=lambda x : x.score, reverse=True)[0]
            similarity_map.append({
                'topic': i, 
                'score': str(most_similar.score.similarity), 
                'rank1': most_similar.score.rank1, 
                'rank2': most_similar.score.rank2, 
                'matched_variant': most_similar.matched_variant
            })

        return similarity_map
    except Exception as e:
        return [{'topic': t, 'score': '0', 'rank1': 0, 'rank2': 0} for t in topics1]


def sense_vec_model_similarity(a, b):
    SimilarityAndRank = namedtuple('SimilarityAndRank', ['similarity', 'rank1', 'rank2'])
    try:
        f1, v1 = sense_vec_model[unicode(a)]
        f2, v2 = sense_vec_model[unicode(b)]
        v1 = v1.reshape(1, -1)
        v2 = v2.reshape(1, -1)
        sim = cosine_similarity(v1, v2)[0][0]
        print a, 'vs', b, '=', sim
        return SimilarityAndRank(similarity=round(sim * 100) / 100, rank1=float(f1), rank2=float(f2))
    except Exception as e:
        print(e)
        return SimilarityAndRank(similarity=0, rank1=float('inf'), rank2=float('inf'))