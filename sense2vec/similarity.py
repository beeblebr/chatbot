from topic_utils import generate_variants, prettify_topic, vector_cosine_similarity, weighted_vector_sum
from sense import get_stop_words_list


QUERY = 1
KNOWLEDGE_ITEM = 2


stop_words = get_stop_words_list()


def populate_with_variants(
    topics,
    user_defined_taxonomy,
    query_or_knowledge_item
):
    """Fetch all possible variants for topics that are part of Sense2Vec vocabulary and populates topics necessary for user-defined taxonomy matching.

    Args:
        topics: List of topics directly extracted from either query or knowledge item sentence.
        user_defined_taxonomy: Dict mapping each query topic to list of user-defined connections.
        query_or_knowledge_item: `QUERY` if topics are from query and `KNOWLEDGE_ITEM` if topics are from knowledge item.

    Returns:
        List of dicts with each topic labelled as `in_vocab` or not.
    """
    all_topics = []
    for topic in topics:
        variants = generate_variants(topic, stop_words)
        all_topics.extend([{'topic': variant, 'in_vocab': True}
                           for variant in variants])
        if query_or_knowledge_item == KNOWLEDGE_ITEM and not variants:
            all_topics.append(
                {'topic': prettify_topic(topic), 'in_vocab': False})
    # Augment all_topics with user-defined taxonomy
    if query_or_knowledge_item == QUERY:
        all_topics.extend([{'topic': topic, 'in_vocab': False}
                           for topic in user_defined_taxonomy])
    return all_topics


def get_custom_topic_matches(
    user_defined_taxonomy,
    topics_from_query,
    topics_from_knowledge_item
):
    """Return topics in topics_from_knowledge_item that match any user-defined taxonomy matches."""
    matches = []
    for query_topic in topics_from_query:
        if not query_topic['in_vocab']:
            matches.extend([knowledge_item_topic['topic'] for knowledge_item_topic in topics_from_knowledge_item if
                            knowledge_item_topic['topic'] in user_defined_taxonomy[query_topic['topic']]])
    return matches


CUSTOM_TOPIC_SIMILARITY = 0.95  # Custom relationships get a fixed similarity score
NULL_ENTRY = {
    'ki_topics': [],
    'cosine_similarity': 0
}


def topic_similarity_map(
    topics_from_query,
    knowledge_item,
    user_defined_taxonomy
):
    """Augment each knowledge item with cosine similarity score calculated against query topics.

    Args:
        topics_from_query: list
            The list of topics from user's question.
        knowledge_item: dict
            A single knowledge item.
        user_defined_taxonomy: dict
            A mapping of each query topic to list of user-defined connections associated with it.

    Returns:
        dict: Dict containing knowledge item and similarity score.
    """
    topics_from_knowledge_item = knowledge_item['topics']

    topics_from_query = populate_with_variants(
        topics_from_query,
        user_defined_taxonomy,
        QUERY
    )
    topics_from_knowledge_item = populate_with_variants(
        topics_from_knowledge_item,
        user_defined_taxonomy,
        KNOWLEDGE_ITEM
    )
    if not (topics_from_query and topics_from_knowledge_item):
        return NULL_ENTRY

    custom_topic_matches = get_custom_topic_matches(
        user_defined_taxonomy,
        topics_from_query,
        topics_from_knowledge_item
    )
    custom_topic_similarity = CUSTOM_TOPIC_SIMILARITY if custom_topic_matches else 0

    topics_from_query = filter(lambda x: x['in_vocab'], topics_from_query)
    topics_from_knowledge_item = filter(
        lambda x: x['in_vocab'],
        topics_from_knowledge_item
    )

    if topics_from_query and topics_from_knowledge_item:
        model_similarity = vector_cosine_similarity(
            weighted_vector_sum(topics_from_query),
            weighted_vector_sum(topics_from_knowledge_item)
        )
    else:
        model_similarity = 0

    result = {
        'ki_topics': topics_from_knowledge_item,
        '_id': knowledge_item['_id'],
        'cosine_similarity': model_similarity
    }
    return result
