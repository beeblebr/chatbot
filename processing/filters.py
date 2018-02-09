def DropItemsBelowSimilarityThreshold(similarity_map, return_values):
    return filter(lambda x : x['cosine_similarity'] > 0.65, similarity_map)
