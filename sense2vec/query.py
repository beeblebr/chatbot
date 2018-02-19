import json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from clarify import find_most_representative_topic

from cluster import fit_affinity_propagation_model
from cluster import group_samples_by_label

from sense import stop_words

from topic_utils import find_best_casing
from topic_utils import generate_variants
from topic_utils import split_tokens


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
    logger.info(multi_word_topics)
    logger.info(len(stop_words))
    variants = generate_variants(multi_word_topics, stop_words)
    logger.info(variants)
    af = fit_affinity_propagation_model(variants)
    clusters = group_samples_by_label(variants, af.labels_)
    options = []
    # Not converged or useless clusters
    if af.n_iter_ == 200 or len(clusters) == len(variants):
        options = variants
    else:
        options = [cluster[0] for cluster in clusters]
    # Add MRT of options to options
    options.append(find_most_representative_topic(options))
    # Remove duplicates
    options = list(set(options))

    if options:
        return json.dumps({
            'result': 'QUERY_CLARIFICATION_NEEDED',
            'query_clarification_options': options
        })
    else:
        return json.dumps({
            'result': 'QUERY_SUCCESS'
        })


def process_query_clarification():
    pass