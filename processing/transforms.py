from __future__ import print_function

import numpy as np
import sys

def ZipWithCorpus(similarity_map, *corpus):
    print('ok')
    try:
        for i in range(len(similarity_map)):
            corresponding_knowledge_item = [item for item in corpus if str(item['_id']) == similarity_map[i]['_id']][0]
            corresponding_knowledge_item.update(similarity_map[i])
            similarity_map[i] = corresponding_knowledge_item
    except Exception as e:
        print(e, file=sys.stderr)
        print('sorted', file=sys.stderr)
    return similarity_map


def ConvertSimilarityToFloat(similarity_map):
    print('okk')
    for i in range(len(similarity_map)):
        print(similarity_map[i], file=sys.stderr)
        similarity_map[i]['cosine_similarity'] = float(similarity_map[i]['cosine_similarity'])
    print(666, file=sys.stderr)
    return similarity_map


def SortBySimilarityDesc(similarity_map):
    similarity_map = sorted(similarity_map, key=lambda x : x['cosine_similarity'], reverse=True)
    return similarity_map


def BucketizeIntoSimilarityIntervals(similarity_map):
    intervals = reversed(np.arange(0.65, 1.0, 0.05))  # Divide (0.65, 1.0) into intervals of 0.05 (in reverse order)
    buckets = []
    for lower_bound in intervals:
        bucket = [ki for ki in similarity_map if ki['cosine_similarity'] > lower_bound]
        buckets.append(bucket)
        similarity_map = [ki for ki in similarity_map if ki not in bucket]
    return buckets
    