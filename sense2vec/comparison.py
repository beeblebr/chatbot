from itertools import chain, combinations

from sklearn.metrics.pairwise import cosine_similarity

from topic_utils import generate_variants, weighted_vector_sum


def topic_similarity_map(topics1, topics2, user_defined_taxonomy):

    def populate_with_variants(topics):
        all_topics = []
        for t in topics:
            variants = generate_variants(t)
            all_topics.extend([{'topic': variant, 'valid': True} for variant in variants])
        return all_topics

    topics_from_query = populate_with_variants(topics1)
    topics_from_knowledge_item = populate_with_variants(topics2)

    if not (topics_from_query and topics_from_knowledge_item):
        return str(0)

    def powerset(iterable):
        s = list(iterable)
        return chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1))

    result = {
        'cosine_similarity': str(cosine_similarity(
            weighted_vector_sum(topics_from_query).reshape(1, -1), 
            weighted_vector_sum(topics_from_knowledge_item).reshape(1, -1)
        )[0][0])
    }

    return result
