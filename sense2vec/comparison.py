import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from topic_utils import generate_variants, weighted_vector_sum, prettify_topic
from clarify import cluster_result_candidates

QUERY = 1
KNOWLEDGE_ITEM = 2


def populate_with_variants(topics, user_defined_taxonomy, query_or_knowledge_item):
    """Fetches all possible variants for topics that are part of Sense2Vec vocabulary and populates topics necessary for user-defined taxonomy matching.

    Args:
        topics: List of topics directly extracted from either query or knowledge item sentence.
        user_defined_taxonomy: Dict mapping each query topic to list of user-defined connections.
        query_or_knowledge_item: `QUERY` if topics are from query and `KNOWLEDGE_ITEM` if topics are from knowledge item.

    Returns:
        List of dicts with each topic labelled as `in_vocab` or not.
    """
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
            matches.extend([knowledge_item_topic['topic'] for knowledge_item_topic in topics_from_knowledge_item if
                            knowledge_item_topic['topic'] in user_defined_taxonomy[query_topic['topic']]])
    return matches


CUSTOM_TOPIC_SIMILARITY = 0.95  # Custom relationships get a fixed similarity score
NULL_ENTRY = {
    'ki_topics': [],
    'cosine_similarity': 0
}


def topic_similarity_map(topics_from_query, knowledge_item, user_defined_taxonomy):
    """Augments each knowledge item with cosine similarity score calculated against query topics.

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
    topics_from_knowledge_item = knowledge_item['text']

    topics_from_query = populate_with_variants(topics_from_query, user_defined_taxonomy, QUERY)
    topics_from_knowledge_item = populate_with_variants(topics_from_knowledge_item, user_defined_taxonomy,
                                                        KNOWLEDGE_ITEM)
    if not (topics_from_query and topics_from_knowledge_item):
        return NULL_ENTRY

    custom_topic_matches = get_custom_topic_matches(user_defined_taxonomy, topics_from_query,
                                                    topics_from_knowledge_item)
    custom_topic_similarity = CUSTOM_TOPIC_SIMILARITY if custom_topic_matches else 0

    topics_from_query = filter(lambda x: x['in_vocab'], topics_from_query)
    topics_from_knowledge_item = filter(lambda x: x['in_vocab'], topics_from_knowledge_item)
    model_similarity = cosine_similarity(
        weighted_vector_sum(topics_from_query).reshape(1, -1),
        weighted_vector_sum(topics_from_knowledge_item).reshape(1, -1)
    )[0][0]

    result = {
        'ki_topics': topics_from_knowledge_item,
        '_id': knowledge_item['_id'],
        'cosine_similarity': model_similarity
    }
    return result


def bucketize_into_similarity_intervals(results, min_score=0.65, interval_size=0.05):
    intervals = reversed(np.arange(min_score, 1.0, interval_size))  # Divide (min_score, 1) into intervals of interval_size (in reverse order)
    buckets = []
    for lower_bound in intervals:
        bucket = [ki for ki in results if ki['cosine_similarity'] > lower_bound]
        buckets.append(bucket)
        results = [ki for ki in results if ki not in bucket]
    return buckets


def fetch_search_results(query_topics, corpus_topics_map, user_defined_taxonomy):
    all_results = []
    for knowledge_item in corpus_topics_map:
        similarity_map = topic_similarity_map(query_topics['text'], knowledge_item, user_defined_taxonomy)
        all_results.append(similarity_map)

    buckets = bucketize_into_similarity_intervals(all_results)
    first_non_empty_bucket = [bucket for bucket in buckets if bucket][0]
    clusters = cluster_result_candidates(map(lambda x: x['ki_topics'], first_non_empty_bucket))
    return first_non_empty_bucket, clusters
