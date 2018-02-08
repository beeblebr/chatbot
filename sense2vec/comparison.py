from itertools import chain, combinations

from sklearn.metrics.pairwise import cosine_similarity

from topic_utils import generate_variants, weighted_vector_sum, prettify_topic


def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1))


QUERY = 1
KNOWLEDGE_ITEM = 2
def populate_with_variants(topics, user_defined_taxonomy, query_or_knowledge_item):
    all_topics = []
    for topic in topics:
        variants = generate_variants(topic)
        all_topics.extend([{'topic': variant, 'in_vocab': True} for variant in variants])
        if query_or_knowledge_item == KNOWLEDGE_ITEM and not variants:
            all_topics.append({'topic': prettify_topic(topic), 'in_vocab': False})
    # Augment all_topics with user-defined taxonomy
    if query_or_knowledge_item == QUERY:
        all_topics.extend([{'topic': topic, 'in_vocab': False} for topic in user_defined_taxonomy])
    return all_topics


def get_custom_topic_matches(user_defined_taxonomy, topics_from_query, topics_from_knowledge_item):
    """Returns topics in topics_from_knowledge_item that match any user-defined taxonomy matches."""
    matches = []
    for query_topic in topics_from_query:
        if not query_topic['in_vocab']:
            matches.extend([knowledge_item_topic['topic'] for knowledge_item_topic in topics_from_knowledge_item if knowledge_item_topic['topic'] in user_defined_taxonomy[query_topic['topic']]])
    return matches


CUSTOM_TOPIC_SIMILARITY = 0.95  # Custom relationships get a fixed similarity score
def topic_similarity_map(topics1, topics2, user_defined_taxonomy):
    topics_from_query = populate_with_variants(topics1, user_defined_taxonomy, QUERY)
    topics_from_knowledge_item = populate_with_variants(topics2, user_defined_taxonomy, KNOWLEDGE_ITEM)
    if not (topics_from_query and topics_from_knowledge_item):
        return str(0)

    custom_topic_matches = get_custom_topic_matches(user_defined_taxonomy, topics_from_query, topics_from_knowledge_item)
    #custom_topic_similarity = CUSTOM_TOPIC_SIMILARITY if custom_topic_matches else 0
    model_similarity = cosine_similarity(
                            weighted_vector_sum(topics_from_query).reshape(1, -1), 
                            weighted_vector_sum(topics_from_knowledge_item).reshape(1, -1)
                        )[0][0]

    result = {
        'cosine_similarity': str(model_similarity)
    }
    return result
