from collections import namedtuple

import numpy as np

from sklearn.cluster import AffinityPropagation
from sklearn.metrics import silhouette_score

from sense import sense_vec_model


Cluster = namedtuple(
    'Cluster',
    ['silhouette_score', 'af_model', 'topic_combination']
)


def fit_affinity_propagation_model(candidates):
    """Fit an Affinity Propagation model to the list of topics.

    The topics' Sense2Vec embeddings are used for clustering.

    Args:
        candidates: list
            List of topics to cluster.

    Returns:
        af: The AffinityPropagation model fitted on the list.
    """
    candidates = map(lambda x: unicode(x), candidates)
    # Just filter out for now
    candidates = filter(lambda x: x in sense_vec_model, candidates)
    embeddings = map(lambda token: sense_vec_model[token][1], candidates)

    af = AffinityPropagation().fit(embeddings)
    return af


def group_samples_by_label(samples, labels):
    """Group samples by their cluster labels.

    Args:
        samples: list
            List of topics.
        labels: list
            Label map.

    Returns:
        clusters: list of lists
            Each sublist contains members of a cluster.
    """
    clusters = []
    for i in range(len(np.unique(labels))):
        cluster = [
            samples[x]
            for x in range(len(labels))
            if labels[x] == i
        ]
        clusters.append(cluster)
    return clusters


def cluster_topic_combination(comb):
    comb = map(lambda x: unicode(x['topic']), comb)
    af = fit_affinity_propagation_model(comb)
    converged = af.n_iter_ != 200
    if not converged:
        return Cluster(
            silhouette_score=-1
        )
    n_clusters = len(np.unique(af.labels_))
    # Cannot calculate silhouette score
    if not 1 < n_clusters < len(comb):
        cluster_score = 1 if n_clusters > 1 else -1
    else:
        embeddings = map(lambda x: sense_vec_model[x][1], comb)
        cluster_score = silhouette_score(
            embeddings,
            af.labels_,
            metric='cosine'
        )
    return Cluster(
        silhouette_score=cluster_score,
        af_model=af,
        topic_combination=comb
    )
