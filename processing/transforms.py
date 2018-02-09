def ZipWithCorpus(similarity_map, *corpus):
    for i in range(len(corpus)):
        similarity_map[i].update(corpus[i])
	assert len(similarity_map) > 300
    return similarity_map


def ConvertSimilarityToFloat(similarity_map):
    for i in range(len(similarity_map)):
        similarity_map[i]['cosine_similarity'] = float(similarity_map[i]['cosine_similarity'])
    return similarity_map


def SortBySimilarityDesc(similarity_map):
    similarity_map = sorted(similarity_map, key=lambda x : x['cosine_similarity'], reverse=True)
    return similarity_map