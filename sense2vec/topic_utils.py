from itertools import product

import numpy as np

from sense import sense_vec_model, stop

from sklearn.metrics.pairwise import cosine_similarity


def prettify_topic(x):
    """Converts tokens in Sense2Vec compatible format to human readable format.

    For example, "machine_learning|NOUN" to "machine learning".
    """
    return x.split('|')[0].replace('_', ' ')


def uglify_topic(x):
    """Converts a phrase (or word) to Sense2Vec compatible format noun.

    For example, "machine learning" to "machine_learning|NOUN".
    NOTE: This method does not infer the POS tag. It always appends "|NOUN".
    """
    return x.replace(' ', '_') + '|NOUN'


def split_tokens(x):
    """Splits token in Sense2Vec compatible format into individual words.

    For example, it splits "machine_learning|NOUN" into the list ["machine",
    "learning"].
    """
    return x.split('|')[0].split('_')


def merge_tokens(x):
    """Combines list of words into Sense2Vec compatible format noun.

    For example, it combines the list ["machine", "learning"] to
    "machine_learning|NOUN".
    NOTE: This method does not infer the POS tag. It always appends "|NOUN".
    """
    return '_'.join(x) + '|NOUN'


def weighted_vector_sum(topics):
    """Calculates sum of Sense2Vec embeddings of the topics.

    Args:
        topics: List of dicts, each topic represented by a dict.

    Returns:
        Vector sum of embeddings.
    """
    topics = map(lambda x: x['topic'], topics)
    weight_term = lambda topic: sense_vec_model[topic][1]
    result = sum(map(weight_term, topics))
    norm = np.linalg.norm(result)
    if norm != 0:
        result /= norm
    return result


def find_best_casing(topic):
    """Returns casing variant of a topic that the user most likely meant.

    If the originally entered casing is not in Sense2Vec, it looks for the
    casing that's most frequently occuring.

    Args:
        topic: Topic in Sense2Vec compatible format.

    Returns:
        Most frequently occuring valid variant. None if no valid variants.
    """
    topic = unicode(topic)
    if topic in sense_vec_model:
        return topic

    freqs = []
    # Generates all permutations of cases
    tokens = split_tokens(topic)
    param_for_product = [[0, 1]] * len(tokens)

    for casing_combination in product(*param_for_product):
        casing = [
            tokens[i].title() if casing_combination[i] else tokens[i].lower()
            for i in range(len(tokens))
        ]
        repr = merge_tokens(casing)
        if repr in sense_vec_model:
            freqs.append((sense_vec_model[repr][0], repr))
    return max(freqs)[1] if freqs else None


def generate_variants(topic):
    """Generates topic variants.

    Args:
        topic: Topic in Sense2Vec compatible format.

    Returns:
        list: List of non-overlapping variants.
    """
    if '|' not in topic:
        return []
    tokens = split_tokens(topic)
    variants = []
    for i in range(len(tokens)):
        variants.append(tokens[i:])
        variants.append(tokens[:-i])
    variants = map(lambda x: find_best_casing(merge_tokens(x)), variants)
    variants = filter(lambda x: x and x != '|NOUN', variants)
    variants = map(split_tokens, variants)

    # Remove proper subsets
    proper_subsets = []
    for i in range(len(variants) - 1):
        for j in range(i + 1, len(variants)):
            if ' '.join(variants[j]).lower() in ' '.join(variants[i]).lower():
                proper_subsets.append(variants[j])
    unique = set(map(tuple, variants)) - set(map(tuple, proper_subsets))
    unique_merged = sorted(
        [unicode(merge_tokens(x)) for x in unique],
        key=lambda x: len(split_tokens(x)),
        reverse=True
    )
    # Remove stopwords
    unique_merged = filter(
        lambda x: prettify_topic(x) not in stop,
        unique_merged
    )
    return unique_merged


def get_top_items(topic, n=1000):
    topic = find_valid_case_combination(unicode(topic))
    try:
        token = sense_vec_model[topic][1]
        related_items = sense_vec_model.most_similar(token, n)[0]
    except Exception as e:
        return []

    for i in range(len(related_items)):
        related_items[i] = {'text': prettify_topic(related_items[i]), 'similarity': sense_vec_model_similarity(topic, related_items[i]).similarity}
        if related_items[i]['similarity'] < 0.6:
            break

    return related_items[:i]


def vector_cosine_similarity(vector1, vector2):
    return cosine_similarity(
        vector1.reshape(1, -1),
        vector2.reshape(1, -1)
    )[0][0]


def topic_cosine_similarity(topic1, topic2):
    return vector_cosine_similarity(
        sense_vec_model[unicode(topic1)][1],
        sense_vec_model[unicode(topic2)][1]
    )
