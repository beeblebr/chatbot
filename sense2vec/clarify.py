from itertools import product
from pprint import pprint

import numpy as np

from sense import sense_vec_model

from sklearn.cluster import AffinityPropagation
from sklearn.metrics import silhouette_score


def find_most_representative_topic(
        candidate_topics,
        generality_threshold=1000,
        window_size=10,
        patience=300
):
    """Returns topic most representative of a set of topics.

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
    embeddings = map(
        lambda token: sense_vec_model[token][1],
        candidate_topics
    )
    candidate_topics = sense_vec_model.most_similar(sum(embeddings), 1000)[0]

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
    """Clusters a list of candidates (obtained from first-level filtering)
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


def find_optimal_cluster(
    query_topics,
    search_results_topics,
    summary_type='abstractive_summary'
):
    topic_combinations = product(*search_results_topics)
    clusters = []
    for comb in topic_combinations:
        comb = map(lambda x: unicode(x['topic']), comb)
        print(query_topics)
        print(comb)
        af = cluster_result_candidates(comb)
        # If only one cluster, then silhouette_score cannot be calculated,
        # so just use -1 for now. Ideally should be calculated using
        # intra-cluster distance.
        n_clusters = len(np.unique(af.labels_))
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
        clusters.append((cluster_score, af, comb))

    optimal_cluster = sorted(clusters, reverse=True)[0]
    _, af, all_topics = optimal_cluster
    print('Optimal cluster')
    print(all_topics)
    predicted = af.labels_

    def get_clusters(all_topics, predicted):
        clusters = []
        for i in range(len(set(predicted))):
            cluster = [
                all_topics[x]
                for x in range(len(predicted))
                if predicted[x] == i
            ]
            clusters.append(cluster)
        return clusters

    clusters = get_clusters(all_topics, predicted)
    pprint(clusters)

    if summary_type == 'extractive_summary':
        extractive_summary = [
            (all_topics[af.cluster_centers_indices_[i]], clusters[i])
            for i in range(len(clusters))
        ]
        return extractive_summary
    elif summary_type == 'abstractive_summary':
        abstractive_summary = [
            (find_most_representative_topic(cluster), cluster)
            for cluster in clusters
        ]
        return abstractive_summary
