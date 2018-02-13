from itertools import product
from collections import namedtuple
from pprint import pprint

import numpy as np

from sense import sense_vec_model

from sklearn.cluster import AffinityPropagation
from sklearn.metrics import silhouette_score


Cluster = namedtuple(
    'Cluster',
    ['converged', 'silhouette_score', 'af_model', 'topic_combination']
)


def find_most_representative_topic(
        candidate_topics,
        generality_threshold=1000,
        window_size=10,
        patience=300
):
    """Return the topic most representative of a set of topics.

    Args:
        candidate_topics: List of topic names (typically obtained from
        sense_vec_model.most_similar).
        generality_threshold: Frequency score above which a topic is
        considered to be "general".
        window_size: Size of window examined before returning most general
        topic.
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
    print(candidate_topics)
    embeddings = map(
        lambda token: sense_vec_model[token][1],
        candidate_topics
    )
    total = sum(embeddings)
    total /= np.linalg.norm(total)
    pprint(total)
    candidate_topics = sense_vec_model.most_similar(total, 600)[0]

    for i in range(min(len(candidate_topics), patience)):
        if sense_vec_model[candidate_topics[i]][0] > generality_threshold:
            flag = i
            break
    else:
        return max(map(
            lambda topic: (sense_vec_model[topic][0], topic),
            candidate_topics
        ))[1]
    return max(map(
        lambda topic: (sense_vec_model[topic][0], topic),
        candidate_topics[:max(40, flag)]
    ))[1]


def cluster_result_candidates(candidates):
    """Cluster a list of candidates (obtained from first-level filtering)
    into a set of top-level topics for secondary questioning.

    Args:
        candidates: Knowledge items classified as similar from (n-1)th pass.
        summary_type: 'abstractive_summary' can use a representative topic
        that is not part of the cluster.
        'extractive_summary' picks a representative topic from the cluster.

    Returns:
        list: List of tuples (representative topic, list of topics in the
        cluster).
    """
    candidates = map(lambda x: unicode(x), candidates)
    # Just filter out for now
    candidates = filter(lambda x: x in sense_vec_model, candidates)
    embeddings = map(lambda token: sense_vec_model[token][1], candidates)

    af = AffinityPropagation(verbose=True).fit(embeddings)
    return af


def get_possible_clusterings(search_results_topics):
    topic_combinations = product(*search_results_topics)
    clusters = []
    for comb in topic_combinations:
        comb = map(lambda x: unicode(x['topic']), comb)
        af = cluster_result_candidates(comb)
        converged = af.n_iter_ != 200
        if not converged:
            continue
        # If only one cluster, then silhouette_score cannot be calculated,
        # so just use -1 for now. Ideally should be calculated using
        # intra-cluster distance.
        n_clusters = len(np.unique(af.labels_))
        print('n_clusters = ' + str(n_clusters))
        # Order of precedence of situations is as follows:
        # Silhouette score calculatable > Number of clusters same as samples
        # > One cluster
        if not 1 < n_clusters < len(comb):
            if n_clusters > 1:
                cluster_score = 1
            else:
                cluster_score = -1
        else:
            embeddings = map(lambda x: sense_vec_model[x][1], comb)
            cluster_score = silhouette_score(
                embeddings,
                af.labels_,
                metric='cosine'
            )
        clusters.append(Cluster(
            converged=converged,
            silhouette_score=cluster_score,
            af_model=af,
            topic_combination=comb
        ))
        # clusters.append((cluster_score, af, comb))
    print('Clusters final')
    pprint(clusters)
    return clusters


def get_cluster_members(topic_combination, predicted):
    clusters = []
    for i in range(len(np.unique(predicted))):
        cluster = [
            topic_combination[x]
            for x in range(len(predicted))
            if predicted[x] == i
        ]
        clusters.append(cluster)
    return clusters


def find_optimal_cluster(
    query_topics,
    search_results_topics,
    summary_type='abstractive_summary'
):
    possible_clusterings = get_possible_clusterings(search_results_topics)

    # Choose cluster with the highest score
    optimal_cluster = sorted(possible_clusterings, reverse=True)[0]
    converged, cluster_score, af, topic_combination = optimal_cluster
    # Assume that non-convergence is due to single, repeated topic
    print('Optimal cluster')
    print(topic_combination)
    predicted = af.labels_
    clusters = get_cluster_members(topic_combination, predicted)
    pprint(clusters)

    if summary_type == 'extractive_summary':
        extractive_summary = [
            (topic_combination[af.cluster_centers_indices_[i]], clusters[i])
            for i in range(len(clusters))
        ]
        return extractive_summary
    elif summary_type == 'abstractive_summary':
        abstractive_summary = [
            (find_most_representative_topic(cluster), cluster)
            for cluster in clusters
        ]
        return abstractive_summary
