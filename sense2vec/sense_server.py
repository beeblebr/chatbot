import json
import pickle

from collections import namedtuple
from itertools import product

from flask import Flask, request
from sklearn.metrics.pairwise import cosine_similarity

import sense2vec


app = Flask(__name__)


WORD2VEC_MODEL_PATH = '../web/model.pickle'
TEXT_RAZOR_TOPICS_PATH = '../topics3'

sense_vec_model = sense2vec.load()
word_vec_model = dict() #pickle.load(open(WORD2VEC_MODEL_PATH, 'rb'))
topic_corpus = [] #pickle.load(open(TEXT_RAZOR_TOPICS_PATH, 'rb'))


def generate_variants(topic):
    tokens = topic.split('|')[0].split('_')
    variants = set([topic])
    variants.update(generate_case_variants(topic))
    for i in range(1, len(tokens)):
        variants.add('_'.join(tokens[i:]) + '|NOUN')
        variants.add('_'.join(tokens[:-i]) + '|NOUN')
        variants.update(generate_case_variants('_'.join(tokens[i:]) + '|NOUN'))
        variants.update(generate_case_variants('_'.join(tokens[:-i]) + '|NOUN'))
    print(variants)
    return variants


def binary_string_to_lowercase(text, binary_string):
    text = text.split('|')[0]
    assert(len(text.split('_')) == len(binary_string))
    tokens = text.split('_')
    transformed = [tokens[i].lower() if binary_string[i] else tokens[i] for i in range(len(binary_string))]
    return '_'.join(transformed) + '|NOUN'


def generate_case_variants(topic):
    n_tokens = len(topic.split('|')[0].split('_'))
    variants = []
    for binary_string in product(*([[1, 0]] * n_tokens)):
        variants.append(binary_string_to_lowercase(topic, binary_string))
    return variants
    

def get_longest_variants(variants):
    lengths = map(lambda x : len(x.split('|')[0].split('_')), variants)
    longest_variants = filter(lambda x : len(x.split('|')[0].split('_')) == max(lengths), variants)
    return longest_variants


def get_most_relevant_variant(variants):
    variants = filter(lambda x : x in sense_vec_model, list(variants))
    variants.sort(key=lambda variant : sense_vec_model[variant][0])
    return variants[0]


def get_index_in_rankings(token, search_term, n=100000):
    token = sense_vec_model[unicode(token)][1]
    try:
        index = sense_vec_model.most_similar(token, n)[0].index(unicode(search_term))
        return index
    except ValueError as e:
        return float('inf')


def topic_similarity_map(topics1, topics2):
    Comparison = namedtuple('Comparison', ['score', 'matched_topic', 'matched_variant'])
    Importance = namedtuple('Importance', ['topic', 'importance'])
    try:
        if not topics1 or not topics2:
            return [{'topic': t, 'score': '0', 'rank1': 0, 'rank2': 0} for t in topics1]
            
        # Generate all variants for both sets of topics
        topics2_variants = []
        for t in topics2:
            if t not in sense_vec_model:
                # topics2_variants.append(get_most_relevant_variant(generate_variants(t)))
                topics2_variants.extend(get_longest_variants(generate_variants(t)))
            else:
                topics2_variants.append(t)

        topics1_variants = []
        for t in topics1:
            if t not in sense_vec_model:
                variants = filter(lambda x : x in sense_vec_model, generate_variants(t))
                longest_variants = get_longest_variants(variants)
                most_relevant_variant = sorted(longest_variants, key=lambda x : sense_vec_model[x][0])[0]
                print(most_relevant_variant)
                topics1_variants.append(most_relevant_variant)
            else:
                topics1_variants.append(t)

        # Calculate aggregate similarity score
        similarity_map = []
        for i in topics1_variants:
            current_topic_sims = []
            for j in topics2_variants:
                current_topic_sims.append(Comparison(score=sense_vec_model_similarity(i, j), matched_topic=i, matched_variant=j))
            most_similar = sorted(current_topic_sims, key=lambda x : x.score, reverse=True)[0]
            similarity_map.append({'topic': i, 'score': str(most_similar.score.similarity), 'rank1': most_similar.score.rank1, 'rank2': most_similar.score.rank2, 'matched_variant': most_similar.matched_variant})

        # Average sum of similarities over number of topics in topics1
        # avg = sum(map(lambda x : x['score'], similarities)) / float(len(topics1))
        # print('Avg:' + str(avg) + '\n')
        
        return similarity_map
    except Exception as e:
        print(e)
        return [{'topic': t, 'score': '0', 'rank1': 0, 'rank2': 0} for t in topics1]


def sense_vec_model_similarity(a, b):
    SimilarityAndRank = namedtuple('SimilarityAndRank', ['similarity', 'rank1', 'rank2'])
    try:
        f1, v1 = sense_vec_model[unicode(a)]
        f2, v2 = sense_vec_model[unicode(b)]
        v1 = v1.reshape(1, -1)
        v2 = v2.reshape(1, -1)
        sim = cosine_similarity(v1, v2)[0][0]
        print a, 'vs', b, '=', sim
        return SimilarityAndRank(similarity=round(sim * 100) / 100, rank1=float(f1), rank2=float(f2))
    except Exception as e:
        print(e)
        return SimilarityAndRank(similarity=0, rank1=float('inf'), rank2=float('inf'))


def word_vec_similarity(a, b):
    try:
        a = word_vec_model[a].reshape(1, -1)
        b = word_vec_model[b].reshape(1, -1)
        return cosine_similarity(a, b)[0][0]
    except Exception as e:
        return 0


def closest_word2vec_word(noun_phrase, n_candidates=10):
    top_ten = sense_vec_model.most_similar(sense_vec_model[noun_phrase][1], n_candidates)[0]
    print(top_ten)
    for candidate in top_ten:
        candidate = candidate.split('|')[0].lower()
        if candidate in word_vec_model:
            return candidate
    return None


def disambiguate_topic(topic):
    variants = generate_variants(topic)
    candidates = []
    for variant in variants:
        if variant in sense_vec_model:
            candidates.append(variant)
    w2v_candidates = map(closest_word2vec_word, candidates)

    closest_topics = []

    # Map each Word2Vec candidate to closest topic
    for candidate in w2v_candidates:
        closest_topic = sorted(map(lambda x : (word_vec_similarity(candidate, x), x), topic_corpus), reverse=True)[0]
        closest_topics.append(closest_topic)

    return closest_topics


@app.route('/', methods=['POST'])
def index():
    calls = json.loads(request.data)['calls']
    print('\n\n\n\n')

    results = []

    for c in calls:
        try:
            topics1 = c['topics1']
            topics2 = c['topics2']

            similarity_map = topic_similarity_map(topics1, topics2)
            results.append(similarity_map)
        except KeyError as ke:
            results.append(str(0))

    return json.dumps({'result' : json.dumps(results)})


if __name__ == '__main__':
    app.run('0.0.0.0', port=8010, debug=True)
