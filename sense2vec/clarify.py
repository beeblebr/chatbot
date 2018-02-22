"""Secondary questioning system.

This modules helps the user narrow down the target by clustering the initial search results into similar topics.
"""
from multiprocessing import Pool
from itertools import product
from pprint import pprint
import random

import numpy as np

from cluster import Cluster, cluster_combination, group_samples_by_label
from sense import sense_vec_model, get_stop_words_list


stop_words = get_stop_words_list()


def find_most_representative_topic(
        candidate_topics,
        generality_threshold=1000,
        patience=300
):
    """Return the topic most representative of a set of topics.

    Args:
        candidate_topics: List of topic names (typically obtained from
        sense_vec_model.most_similar).
        generality_threshold: Frequency score above which a topic is
        considered to be general enough to be potentially representative.
        patience: Number of topics examined before blindly returning the
        topic with the most frequency (even if it doesn't exceed the
        `generality_threshold`).

    Returns:
        str: Expected to return a topic which is either the most general
        among the candidates or a topic that roughly represents the general
        direction the vector is in.
    """
    # Find most general topic in the direction of sum vector of
    # candidate_topics
    embeddings = map(
        lambda token: sense_vec_model[token][1],
        candidate_topics
    )
    total = sum(embeddings)
    total /= np.linalg.norm(total)
    candidate_topics = sense_vec_model.most_similar(total, 600)[0]
    candidate_topics = filter(lambda x: '|' in x and x.split('|')[
                              1] == 'NOUN', candidate_topics)

    for i in range(min(len(candidate_topics), patience)):
        if sense_vec_model[candidate_topics[i]][0] > generality_threshold:
            flag = i
            break
    else:
        return max(map(
            lambda topic: (sense_vec_model[topic][0], topic),
            candidate_topics
        ))[1]

    results = map(
        lambda topic: (sense_vec_model[topic][0], topic),
        candidate_topics[:max(40, flag)]
    )
    # Remove stopwords
    results = filter(lambda x: x[1] not in stop_words, results)
    return max(results)[1]


def get_possible_clusterings(search_results_topics):
    """Return all possible clusterings by picking one topic from each knowledge item at a time.

    Args:
        search_results_topics: list of lists
            Each sublist contains all topics from a knowledge item.

    Returns:
        clusters: Possible clusterings.
    """
    topic_combinations = list(product(*search_results_topics))
    p = Pool()
    clusters = p.map(cluster_combination, topic_combinations)
    return sorted(
        clusters,
        key=lambda x: x.silhouette_score,
        reverse=True
    )[0]


def parochial_summary(clusters):
    abstractive_summary = []
    for cluster in clusters:
        if len(cluster) == 1:
            abstractive_summary.append((cluster[0], cluster[0]))
        else:
            abstractive_summary.append(
                (
                    find_most_representative_topic(cluster, stop_words),
                    cluster
                )
            )
    return abstractive_summary


def find_optimal_cluster(
    query_topics,
    search_results_topics,
    summary_type='abstractive_summary'
):
    """Return optimal cluster with an appropriate cluster head.

    This gives the cluster with the highest `cluster_score`.
    `cluster_score` is the equal to the `silhouette_score` of a cluster
    except in cases where `cluster_score` is not defined due to an inability
    to calculate `silhouette_score`.

    Args:
        query_topics: list
            Topics from query text.
        search_result_topics: list of lists
            Each sublist contains topics from a single knowledge item.
        summary_type: str
            `abstractive_summary` or `extractive_summary`.

    Returns:
        summary: tuple
            Tuple containing the cluster head and the topics under cluster.
    """
    possible_clusterings = get_possible_clusterings(search_results_topics)
    if not possible_clusterings:
        return None

    # Choose cluster with the highest score
    optimal_cluster = sorted(possible_clusterings, reverse=True)[0]
    cluster_score, af, samples = optimal_cluster

    clusters = group_samples_by_label(samples, af.labels_)

    if summary_type == 'extractive_summary':
        extractive_summary = [
            (samples[af.cluster_centers_indices_[i]], clusters[i])
            for i in range(len(clusters))
        ]
        return extractive_summary
    elif summary_type == 'abstractive_summary':
        abstractive_summary = parochial_summary(clusters)
        return abstractive_summary
