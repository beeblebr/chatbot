from collections import namedtuple
from itertools import product

from sklearn.metrics.pairwise import cosine_similarity

import sense2vec


sense_vec_model = sense2vec.load()


SimilarityAndRank = namedtuple('SimilarityAndRank', ['similarity', 'rank1', 'rank2'])
Comparison = namedtuple('Comparison', ['score', 'matched_topic', 'matched_variant'])


def prettify_topic(x):
    return x.split('|')[0].replace('_', ' ')

def uglify_topic(x):
    return x.replace(' ', '_') + '|NOUN'

def split_tokens(x):
    return x.split('|')[0].split('_')

def merge_tokens(x):
    return '_'.join(x) + '|NOUN'


def find_best_casing(topic):
    """If the originally entered case-variant is not available, it looks for te first valid case-variant. It is greedy towards lowercase variants. Returns None if none of them are valid."""
    topic = unicode(topic)
    if topic in sense_vec_model:
        return topic

    freqs = []
    # Generates all permutations of cases
    tokens = split_tokens(topic)
    param_for_product = [[0, 1]] * len(tokens)

    for casing_combination in product(*param_for_product):
        casing = [tokens[i].title() if casing_combination[i] else tokens[i].lower() for i in range(len(tokens))]
        repr = merge_tokens(casing)
        if repr in sense_vec_model:
            freqs.append((sense_vec_model[repr][0], repr))
    return max(freqs)[1] if freqs else None


def generate_variants(topic):
    if '|' not in topic:
        return []
    tokens = split_tokens(topic)
    variants = []
    for i in range(len(tokens)):
        variants.append(tokens[i:])
        variants.append(tokens[:-i])
    variants = [find_best_casing(merge_tokens(x)) for x in variants]
    variants = [x for x in variants if x and x != '|NOUN']
    variants = map(split_tokens, variants)

    # Remove proper subsets
    proper_subsets = []
    for i in range(len(variants) - 1):
        for j in range(i + 1, len(variants)):
            if ' '.join(variants[j]).lower() in ' '.join(variants[i]).lower():
                proper_subsets.append(variants[j])
    unique = set(map(tuple, variants)) - set(map(tuple, proper_subsets))
    return sorted([unicode(merge_tokens(x)) for x in unique], key=lambda x : len(split_tokens(x)), reverse=True)


def topic_similarity_map(topics1, topics2, user_defined_taxonomy):
    def populate_with_variants(topics):
        all_topics = []
        for t in topics:
            variants = generate_variants(t)
            all_topics.extend([{'topic': variant, 'valid': True} for variant in variants])
        return all_topics

    topics_from_query = populate_with_variants(topics1)
    topics_from_knowledge_item = populate_with_variants(topics2)

    print('Topics from query:')
    print(topics_from_query)

    print('Topics from knowledge item:')
    print(topics_from_knowledge_item)

    if not topics_from_query or not topics_from_knowledge_item:
        return str(0)

    def weighted_vector_sum(topics):
        topics = map(lambda x : x['topic'], topics)
        max_rank = max(map(lambda x : sense_vec_model[x][0], topics))
        result = sense_vec_model[topics[0]][1] / max_rank #sense_vec_model[topics[0]][0]
        for topic in topics[1:]:
            result += sense_vec_model[topic][1] / max_rank #sense_vec_model[topic][0]
        return result

    return str(cosine_similarity(
        weighted_vector_sum(topics_from_query).reshape(1, -1), 
        weighted_vector_sum(topics_from_knowledge_item).reshape(1, -1)
    )[0][0])


def sense_vec_model_similarity(a, b):
    """Returns the cosine similarity between two Sense2Vec phrases and their Sense2Vec popularity ranks."""
    try:
        f1, v1 = sense_vec_model[unicode(a)]
        f2, v2 = sense_vec_model[unicode(b)]
        v1 = v1.reshape(1, -1)
        v2 = v2.reshape(1, -1)
        sim = cosine_similarity(v1, v2)[0][0]
        return SimilarityAndRank(similarity=round(sim * 100) / 100, rank1=float(f1), rank2=float(f2))
    except Exception as e:
        return SimilarityAndRank(similarity=0, rank1=float('inf'), rank2=float('inf'))
