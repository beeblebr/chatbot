from itertools import combinations

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AffinityPropagation
import numpy as np

from sense import sense_vec_model


def find_most_representative_topic(candidate_topics, generality_threshold=1000, window_size=10, patience=500):
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
        print('no flag')
        return max(map(lambda topic : (sense_vec_model[topic][0], topic), candidate_topics))[1]
    return max(map(lambda topic : (sense_vec_model[topic][0], topic), candidate_topics[:max(40, flag)]))[1]


def topic_sum_unit_vector(topics):
    """Returns unit vector in the direction of sum of all topic vectors.

    Args:
        topics: List of topic names.

    Returns:
        numpy.ndarray: Resultant vector.
    """
    result = sum(sense_vec_model[topic][1] for topic in topics)
    return result / np.linalg.norm(result)


def vector_difference(a, b):
    """Returns a - b.

    Args:
        a: Vector 1.
        b: Vector 2.

    Returns:
        Unit vector in the direction of (a - b).
    """
    diff = a - b
    return diff / np.linalg.norm(diff)


def cluster_result_candidates(candidates):
    """Clusters a list of candidates (obtained from first-level filtering) into a set of top-level topics for secondary questioning."""
    flatten_list = lambda l: [item for sublist in l for item in sublist]
    def get_embedding(token):
        print(token)
        return sense_vec_model[token][1].reshape(1, -1)
    all_topics = flatten_list(candidates)
    all_topics = map(lambda x : unicode(x['topic']), all_topics)
    # Just filter out for now
    all_topics = filter(lambda x : x in sense_vec_model, all_topics)
    print('all_topics')
    print(all_topics)
    embeddings = map(get_embedding, all_topics)
    
    af = AffinityPropagation().fit(embeddings)
    predicted = af.labels_

    def get_clusters(all_topics, predicted):
        clusters = []                                                    
        for i in range(len(set(pred))):
            cluster = [all_topics[x] for x in range(len(pred)) if pred[x] == i]
            clusters.append(cluster)
        return clusters

    clusters = get_clusters(all_topics, predicted)

    # Two possible approaches to finding representative topics
    # 1. Extractive
    # 2. Abstractive
    extractive_summary = map(lambda i : (all_topics[af.cluster_center_indices_[i]], clusters[i]), range(len(clusters)))
    abstractive_summary = map(lambda x : (find_most_representative_topic(x), x), clusters)

    return {
        'extractive_summary': extractive_summary,
        'abstractive_summary': abstractive_summary
    }


def find_omitted_topic(query_topics, knowledge_item_topics):
    query_topics = map(unicode, query_topics)
    knowledge_item_topics = map(unicode, knowledge_item_topics)
    diff = vector_difference(topic_sum_unit_vector(query_topics), topic_sum_unit_vector(knowledge_item_topics))
    return find_most_representative_topic(sense_vec_model.most_similar(diff, 1000)[0])


def uglify_topic(x):
    return x.replace(' ', '_') + '|NOUN'


if __name__ == '__main__':
    while True:
        try:
            a = raw_input('a >> ')
            b = raw_input('b >> ')
            print(find_omitted_topic(map(uglify_topic, a.split(', ')), map(uglify_topic, b.split(', '))))
        except Exception as e:
            print(e)
            continue