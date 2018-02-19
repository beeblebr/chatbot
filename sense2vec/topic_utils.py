from itertools import product

import numpy as np

from nltk import pos_tag

from clarify import find_most_representative_topic
from cluster import Cluster, fit_affinity_propagation_model, group_samples_by_label
from sense import sense_vec_model

from sklearn.cluster import AffinityPropagation
from sklearn.metrics.pairwise import cosine_similarity


def prettify_topic(x):
    """Convert tokens in Sense2Vec compatible format to human readable format.

    For example, "machine_learning|NOUN" to "machine learning".
    """
    return x.split('|')[0].replace('_', ' ')


def uglify_topic(x):
    """Convert a phrase (or word) to Sense2Vec compatible format noun.

    For example, "machine learning" to "machine_learning|NOUN".
    NOTE: This method does not infer the POS tag. It always appends "|NOUN".
    """
    return x.replace(' ', '_') + '|NOUN'


def split_tokens(x):
    """Split token in Sense2Vec compatible format into individual words.

    For example, it splits "machine_learning|NOUN" into the list ["machine",
    "learning"].
    """
    return x.split('|')[0].split('_')


def merge_tokens(x):
    """Combine list of words into Sense2Vec compatible format noun.

    For example, it combines the list ["machine", "learning"] to
    "machine_learning|NOUN".
    NOTE: This method does not infer the POS tag. It always appends "|NOUN".
    """
    return '_'.join(x) + '|NOUN'


def weighted_vector_sum(topics):
    """Calculate sum of Sense2Vec embeddings of the topics.

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
    """Return casing variant of a topic that the user most likely meant.

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

    for binary_mask in product(*param_for_product):
        casing_combination = [
            tokens[i].title() if binary_mask[i] else tokens[i].lower()
            for i in range(len(tokens))
        ]
        repr = merge_tokens(casing_combination)
        if repr in sense_vec_model:
            freqs.append((sense_vec_model[repr][0], repr))
    return max(freqs)[1] if freqs else None


def remove_proper_subsets(subsets):
    proper_subsets = []
    for i in range(len(subsets) - 1):
        for j in range(i + 1, len(subsets)):
            if ' '.join(subsets[j]).lower() in ' '.join(subsets[i]).lower():
                proper_subsets.append(subsets[j])
    unique = set(map(tuple, subsets)) - set(map(tuple, proper_subsets))
    return unique


def generate_variants(topic, stop_words):
    """Generate topic variants.

    Args:
        topic: Topic in Sense2Vec compatible format.

    Returns:
        list: List of non-overlapping variants.
    """
    if '|' not in topic:
        return []
    if topic in sense_vec_model:
        return [topic]

    tokens = split_tokens(topic)

    variants = []
    for i in range(len(tokens)):
        variants.append(tokens[i:])
        variants.append(tokens[:-i])

    # Find best casing for whole phrase
    variants = map(lambda x: find_best_casing(merge_tokens(x)), variants)
    # Remove empty variants
    variants = filter(lambda x: x and x != '|NOUN', variants)
    # Remove stopwords
    variants = filter(
        lambda x: prettify_topic(x) not in stop_words,
        variants
    )
    adjectives_removed = []
    # Remove only adjectives
    for i in range(len(variants)):
        if len(split_tokens(variants[i])) == 1 and 'JJ' in pos_tag(prettify_topic(variants[i]).split())[0][1]:
            continue
        adjectives_removed.append(variants[i])
    variants = adjectives_removed
    return variants

    variants = map(split_tokens, variants)
    unique = remove_proper_subsets(variants)
    unique_merged = map(lambda x: merge_tokens, unique)
    return unique_merged


# def generate_variants(topic, stop_words):
#     potential_variants = generate_potential_variants(topic, stop_words)
#     af = fit_affinity_propagation_model(potential_variants)
#     converged = af.n_iter_ != 200
#     if not converged:
#         pass
#     n_clusters = len(np.unique(af.labels_))
#     clusters = group_samples_by_label(potential_variants, af.labels_)
#     if n_clusters > 1:
#         options = set([find_most_representative_topic(topics) for topics in clusters] + [])


def get_top_items(topic, n=1000):
    topic = find_best_casing(unicode(topic))
    try:
        token = sense_vec_model[topic][1]
        related_items = sense_vec_model.most_similar(token, n)[0]
    except Exception:
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
