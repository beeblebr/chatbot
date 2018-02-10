import numpy as np
from sklearn.cluster import AffinityPropagation

from sense import sense_vec_model


def find_most_representative_topic(candidate_topics, generality_threshold=1000, window_size=10, patience=300):
    """Returns topic most representative of a set of topics.

    Args:
        candidate_topics: List of topic names (typically obtained from sense_vec_model.most_similar).
        generality_threshold: Frequency score above which a topic is considered to be "general".
        window_size: Size of window examined before returning most general topic.
        patience: Number of topics examined before blindly returning the topic with the most frequency (even if it doesn't exceed the `generality_threshold`).

    Returns:
        str: Expected to return a topic which is either the most general among the candidates or a topic that roughly represents the general direction the vector is in.
    """
    for i in range(min(len(candidate_topics), patience)):
        if sense_vec_model[candidate_topics[i]][0] > generality_threshold:
            flag = i
            break
    else:
        return max(map(lambda topic : (sense_vec_model[topic][0], topic), candidate_topics))[1]
    return max(map(lambda topic : (sense_vec_model[topic][0], topic), candidate_topics[:max(40, flag)]))[1]


def cluster_result_candidates(candidates, summary_type='abstractive_summary'):
    """Clusters a list of candidates (obtained from first-level filtering) into a set of top-level topics for secondary questioning.

    Args:
        candidates: Knowledge items classified as similar from (n-1)th pass.
        summary_type: 'abstractive_summary' can use a representative topic that is not part of the cluster. 
                      'extractive_summary' picks a representative topic from the cluster.

    Returns:
        list: List of tuples (representative topic, list of topics in the cluster).
    """
    flatten_list = lambda l: [item for sublist in l for item in sublist]
    get_embedding = lambda token: sense_vec_model[token][1]

    all_topics = flatten_list(candidates)
    all_topics = map(lambda x : unicode(x['topic']), all_topics)
    # Just filter out for now
    all_topics = filter(lambda x : x in sense_vec_model, all_topics)
    embeddings = map(get_embedding, all_topics)
    
    af = AffinityPropagation().fit(embeddings)
    predicted = af.labels_

    def get_clusters(all_topics, predicted):
        clusters = []                                                    
        for i in range(len(set(predicted))):
            cluster = [all_topics[x] for x in range(len(predicted)) if predicted[x] == i]
            clusters.append(cluster)
        return clusters

    clusters = get_clusters(all_topics, predicted)

    # Two possible approaches to finding representative topics
    # 1. Extractive
    # 2. Abstractive
    if summary_type == 'extractive_summary':
        extractive_summary = map(lambda i : (all_topics[af.cluster_centers_indices_[i]], clusters[i]), range(len(clusters)))
        return extractive_summary
    elif summary_type == 'abstractive_summary':
        abstractive_summary = map(lambda x : (find_most_representative_topic(x), x), clusters)
        return abstractive_summary
