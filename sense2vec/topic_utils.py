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


def find_valid_case_combination(topic):
    """If the originally entered case-variant is not available, it looks for the most frequently occuring valid case-variant. It is greedy towards lowercase variants. Returns None if none of them are valid."""
    topic = unicode(topic)
    # If original case combination is valid, return it
    if topic in sense_vec_model:
        return topic

    freqs = []
    # Generates all permutations of cases
    tokens = topic.split('|')[0].split('_')
    param_for_product = [[0, 1]] * len(tokens)

    for casing_combination in product(*param_for_product):
        casing = [tokens[i].title() if casing_combination[i] else tokens[i].lower() for i in range(len(tokens))]
        repr = '_'.join(casing) + '|NOUN'
        if repr in sens_vec_model:
            freqs.append((sense_vec_model[repr][0], repr))
    return max(freqs)[1] if freqs else None


def generate_variants(topic):
    if '|' not in topic:
        return []
    tokens = topic.split('|')[0].split('_')
    variants = []
    for i in range(len(tokens)):
        variants.append(tokens[i:])
        variants.append(tokens[:-i])
    variants = [find_valid_case_combination(merge_tokens(x)) for x in variants]
    variants = filter(lambda x : x and x != '|NOUN', variants)  # Remove empty strings
    variants = map(lambda topic : topic.split('|')[0].split('_'), variants)

    # Remove proper subsets
    proper_subsets = []
    for i in range(len(variants) - 1):
        for j in range(i + 1, len(variants)):
            if ' '.join(variants[j]).lower() in ' '.join(variants[i]).lower():
                proper_subsets.append(variants[j])
    unique = set(map(tuple, variants)) - set(map(tuple, proper_subsets))
    return sorted([unicode(merge_tokens(x)) for x in unique], key=lambda x : len(x.split('|')[0].split('_')), reverse=True)


def get_top_items(topic, n=1000):
    topic = find_valid_case_combination(unicode(topic))
    try:
        token = sense_vec_model[topic][1]
        related_items = sense_vec_model.most_similar(token, n)[0]
    except Exception as e:
        return []

    for i in range(len(related_items)):
        related_items[i] = {'text': prettify_topic(related_items[i]), 'similarity': sense_vec_model_similarity(topic, related_items[i]).similarity}
        if related_items[i]['similarity'] < 0.6:
            break

    return related_items[:i]





def topic_similarity_map(topics1, topics2, user_defined_taxonomy):
    """
    user_defined_taxonomy is referred to when either
    1. A topic in `topics1_variants` is not in sense2vec model.
    2. A topic in `topics1_variants` does not yield any matches."""

    print(user_defined_taxonomy)
    
    try:
        if not topics1 or not topics2:
            return [{'topic': t, 'score': '0', 'rank1': 0, 'rank2': 0} for t in topics1]

        # Divide query topics into valid and invalid sets (valid ones are those that are part of Sense2Vec)
        topics_from_query = []
        for t in topics1:
            variants = generate_variants(t)
            topics_from_query.extend([{'topic': variant, 'valid': True} for variant in variants])
        for t in user_defined_taxonomy:
            topics_from_query.append({'topic': t, 'valid': False})


        # Divide knowledge item topics into valid and invalid sets (valid ones are those that are part of Sense2Vec)
        topics_from_knowledge_item = []
        for t in topics2:
            variants = generate_variants(t)
            if variants:
                topics_from_knowledge_item.extend([{'topic': variant, 'valid': True} for variant in variants])
            else:
                topics_from_knowledge_item.append({'topic': prettify_topic(t), 'valid': False})


        CUSTOM_TOPIC_SIMILARITY = 0.95  # Custom relationships get a fixed similarity score

        # Calculate aggregate similarity score
        similarity_map = []
        for query_topic in topics_from_query:
            comparisons_against_current_knowledge_item = []

            for knowledge_item_topic in topics_from_knowledge_item:

                if query_topic['valid'] and knowledge_item_topic['valid']:
                    comparisons_against_current_knowledge_item.append(Comparison(score=sense_vec_model_similarity(query_topic['topic'], knowledge_item_topic['topic']), matched_topic=query_topic['topic'], matched_variant=knowledge_item_topic['topic']))

                elif not query_topic['valid'] and query_topic['topic'] in user_defined_taxonomy:
                    # If knowledge_item_topics is valid, convert it into pretty format
                    if knowledge_item_topic['valid']:
                        kt = prettify_topic(knowledge_item_topic['topic'])
                    else:
                        kt = knowledge_item_topic['topic']
                    if kt in user_defined_taxonomy[query_topic['topic']]:
                        comparisons_against_current_knowledge_item.append(Comparison(score=SimilarityAndRank(similarity=CUSTOM_TOPIC_SIMILARITY, rank1=1, rank2=1), matched_topic=query_topic['topic'], matched_variant=knowledge_item_topic['topic']))

            # Select pair (query_topic, knowledge_item_topic) that has the highest similarity score
            if not comparisons_against_current_knowledge_item:
                continue
            most_similar = sorted(comparisons_against_current_knowledge_item, key=lambda x: x.score, reverse=True)[0]
            most_similar_entry = {
                'topic': query_topic['topic'] if '|' in query_topic['topic'] else uglify_topic(query_topic['topic']),
                'score': str(most_similar.score.similarity),
                'rank1': most_similar.score.rank1, 
                'rank2': most_similar.score.rank2, 
                'matched_variant': most_similar.matched_variant
            }

            # If query_topic has already been matched with another topic, check if this is the highest (occurs when a topic is part of both Sense2Vec and custom taxonomy)
            for i in range(len(similarity_map)):
                match = similarity_map[i]
                if match['topic'] == most_similar_entry['topic']:
                    if float(match['score']) < most_similar.score.similarity:
                        similarity_map[i] = most_similar_entry
                    break
            else:            
                similarity_map.append(most_similar_entry)
                
        return similarity_map

    except Exception as e:
        print(e)
        return [{'topic': t, 'score': '0', 'rank1': 0, 'rank2': 0} for t in topics1]


def sense_vec_model_similarity(a, b):
    """Returns the cosine similarity between two Sense2Vec phrases and their Sense2Vec popularity ranks."""
    
    try:
        f1, v1 = sense_vec_model[unicode(a)]
        f2, v2 = sense_vec_model[unicode(b)]
        v1 = v1.reshape(1, -1)
        v2 = v2.reshape(1, -1)
        sim = cosine_similarity(v1, v2)[0][0]
        # print a, 'vs', b, '=', sim
        return SimilarityAndRank(similarity=round(sim * 100) / 100, rank1=float(f1), rank2=float(f2))
    except Exception as e:
        print('An exception occurred!!!')
        print(e)
        return SimilarityAndRank(similarity=0, rank1=float('inf'), rank2=float('inf'))


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