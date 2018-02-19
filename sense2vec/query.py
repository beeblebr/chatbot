from clarify import find_most_representative_topic

from cluster import fit_affinity_propagation_model
from cluster import group_samples_by_label

from sense import stop_words

from topic_utils import find_best_casing
from topic_utils import generate_variants
from topic_utils import remove_proper_subsets
from topic_utils import split_tokens
from topic_utils import uglify_topic

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
    clarifications = {
        topic: get_possible_meanings(topic)
        for topic in multi_word_topics
    }
    clarifications = {
        topic: meanings
        for topic, meanings in clarifications.iteritems()
        if meanings
    }

    if clarifications:
        return json.dumps({
            'result': 'QUERY_CLARIFICATION_NEEDED',
            'query_clarifications': clarifications
        })
    else:
        return json.dumps({
            'result': 'QUERY_SUCCESS'
        })


def get_possible_meanings(topic):
    variants = generate_variants(topic, stop_words)
    logger.info(variants)
    if not variants:
        return []

    af = fit_affinity_propagation_model(variants)
    clusters = group_samples_by_label(variants, af.labels_)
    options = []

    # Not converged or trivially clustered
    if af.n_iter_ == 200 or len(clusters) == len(variants):
        options.extend(variants)
    else:
        options.extend([uglify_topic(cluster[0]) for cluster in clusters])

    # Add MRT of options to options
    options.append(find_most_representative_topic(options))

    # Add + chaining to options
    split_variants = map(split_tokens, variants)
    unique = remove_proper_subsets(split_variants)
    chains = map(lambda tokens: ' '.join(tokens), unique)
    options.append(' + '.join(chains))

    logger.info(options)
    # Remove duplicates
    options = list(set(options))
    logger.info(options)

    return options


def process_query_clarification():
    pass
