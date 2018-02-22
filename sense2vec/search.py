from clarify import find_optimal_cluster
from similarity import topic_similarity_map

import json
import numpy as np
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def bucketize_into_similarity_intervals(
    results,
    min_score=0.75,
    interval_size=0.05
):
    # Divide (min_score, 1) into intervals of interval_size (in reverse order
    intervals = reversed(np.arange(min_score, 1.0, interval_size))
    buckets = []
    for lower_bound in intervals:
        bucket = [
            ki
            for ki in results
            if ki['normalized_cosine_similarity'] > lower_bound
        ]
        buckets.append(bucket)
        results = [ki for ki in results if ki not in bucket]
    return buckets


def fetch_search_results(
    query_topics,
    corpus_topics_map,
    user_defined_taxonomy
):
    knowledge_items_map = map(
        lambda knowledge_item: topic_similarity_map(
            query_topics['topics'],
            knowledge_item,
            user_defined_taxonomy
        ),
        corpus_topics_map
    )
    max_similarity_score = sorted(
        knowledge_items_map,
        key=lambda x: x['cosine_similarity'],
        reverse=True
    )[0]['cosine_similarity']
    for i in range(len(knowledge_items_map)):
        knowledge_items_map[i]['normalized_cosine_similarity'] = knowledge_items_map[i]['cosine_similarity'] / \
            min(1, max_similarity_score)

    top_bucket, clusters = order_knowledge_items_map(knowledge_items_map)
    return top_bucket, clusters


def order_knowledge_items_map(knowledge_items_map):
    buckets = bucketize_into_similarity_intervals(knowledge_items_map)
    non_empty_buckets = [bucket for bucket in buckets if bucket]
    if not non_empty_buckets:
        return [], []
    first_non_empty_bucket = non_empty_buckets[0]
    if len(first_non_empty_bucket) == 1:
        return first_non_empty_bucket, []
    else:
        clusters = find_optimal_cluster(
            map(lambda x: x['ki_topics'], first_non_empty_bucket[:6]),
            summary_type='abstractive_summary'
        )
        # Return a single element array if AF did not converge
        if not clusters or len(clusters) == 1:
            return [first_non_empty_bucket[0]], []
        return first_non_empty_bucket, clusters


def process_corpus_search(params):
    logger.info('Searching corpus')

    query_topics = params['query_topics']
    corpus_topics_map = params['corpus_topics_map']
    user_defined_taxonomy = params['user_defined_taxonomy']

    results, clusters = fetch_search_results(
        query_topics,
        corpus_topics_map,
        user_defined_taxonomy
    )

    logger.info(results)
    logger.info(clusters)

    for i in range(len(results)):
        results[i]['cosine_similarity'] = str(results[i]['cosine_similarity'])
        results[i]['normalized_cosine_similarity'] = str(
            results[i]['normalized_cosine_similarity'])

    return json.dumps({
        'result': 'CLARIFY_CORPUS' if clusters else 'FOUND',
        'results': json.dumps(results),
        'clusters': json.dumps(clusters)
    })


def process_corpus_clarification(params):
    relevant_knowledge_items = params['relevant_knowledge_items']
    clusters = find_optimal_cluster(
        relevant_knowledge_items,
        summary_type='abstractive_summary'
    )
    return json.dumps({

    })
