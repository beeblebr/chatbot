import numpy as np

from sense import sense_vec_model


def find_most_representative_topic(candidate_topics):
    """Returns topic with the highest frequency from list of topic strings.

    Args:
        candidate_topics: List of topic names (typically obtained from sense_vec_model.most_similar)

    Returns:
        str: Expected to return a topic which is either the most general among the candidates or a topic that roughly represents the general direction the vector is in.
    """
    return max(map(lambda topic : (sense_vec_model[topic], topic)))[1]


def topic_sum_unit_vector(topics):
    """Returns unit vector in the direction of sum of all topic vectors.

    Args:
        topics: List of topic names

    Returns:
        numpy.ndarray: Resultant vector
    """
    result = sum(sense_vec_model[topic][1] for topic in topics)
    return result / np.linalg.norm(result)


def vector_difference(a, b):
    """Returns a - b.

    Args:
        a: Vector 1
        b: Vector 2

    Returns:
        Unit vector in the direction of (a - b).
    """
    diff = a - b
    return diff / np.linalg.norm(diff)


def find_omitted_topic(query_topics, knowledge_item_topics):
    diff = vector_difference(topic_sum_unit_vector(query_topics), topic_sum_unit_vector(knowledge_item_topics))
    return find_most_representative_topic(sense_vec_model.most_similar(diff, 1000)[0])