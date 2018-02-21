from clarify import find_most_representative_topic

from cluster import fit_affinity_propagation_model
from cluster import group_samples_by_label

from sense import stop_words

from topic_utils import find_best_casing
from topic_utils import generate_variants
from topic_utils import remove_proper_subsets
from topic_utils import split_tokens
from topic_utils import prettify_topic

import json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_query(params):
    query_topics = params['topics']
    logger.info(query_topics)
    # Find topics that do not have any casing-variant in the dictionary
    # and are multi-worded
    multi_word_topics = [
        topic for topic in query_topics
        if not find_best_casing(topic) and
        len(split_tokens(topic)) > 1
    ]

    clarifications = dict()
    for topic in multi_word_topics:
        meanings = get_possible_meanings(topic)
        if meanings:
            clarifications[prettify_topic(topic)] = meanings

    if clarifications:
        return json.dumps({
            'result': 'QUERY_CLARIFICATION_NEEDED',
            'query_topics': query_topics,
            'query_clarifications': clarifications
        })
    else:
        return json.dumps({
            'result': 'QUERY_SUCCESS',
            'query_topics': query_topics
        })


def get_possible_meanings(topic):
    variants = generate_variants(topic, stop_words)
    logger.info(variants)
    if not variants:
        return []

    af = fit_affinity_propagation_model(variants)
    clusters = group_samples_by_label(variants, af.labels_)
    logger.info(clusters)
    options = []
    # Not converged or trivially clustered
    if af.n_iter_ == 200 or len(clusters) == len(variants):
        options.extend(variants)
    else:
        options.extend([find_most_representative_topic(cluster) for cluster in clusters])
    # Add MRT of options to options
    options.append(find_most_representative_topic(options))

    # Add + chaining to options
    split_variants = map(split_tokens, variants)
    unique = remove_proper_subsets(split_variants)
    chains = map(lambda tokens: ' '.join(tokens), unique)
    options.append(' + '.join(chains))

    # Remove duplicates
    options = map(prettify_topic, options)
    options = list(set(options))

    return options


def process_query_clarification(params):
    query_topics = params['query_topics']
    query_clarifications = params['query_clarifications']

    # Assemble final list of topics from these
    search_topics = []
    for topic in query_topics:
        if topic in query_clarifications:
            search_topics.extend(query_clarifications[topic])
        else:
            search_topics.append(topic)

    return json.dumps({
        'result': 'QUERY_SUCCESS',
        'query_topics': query_topics
    })
