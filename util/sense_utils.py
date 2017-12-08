import requests
import json
import re
import spacy

import warnings
warnings.simplefilter("ignore", category=DeprecationWarning)

SENSE_SERVER = 'http://c70c1fcc.ngrok.io'
SENSE_SERVER_PORT = 8009

LABELS = {
    'ENT': 'ENT',
    'PERSON': 'ENT',
    'NORP': 'ENT',
    'FAC': 'ENT',
    'ORG': 'ENT',
    'GPE': 'ENT',
    'LOC': 'ENT',
    'LAW': 'ENT',
    'PRODUCT': 'ENT',
    'EVENT': 'ENT',
    'WORK_OF_ART': 'ENT',
    'LANGUAGE': 'ENT',
    'DATE': 'DATE',
    'TIME': 'TIME',
    'PERCENT': 'PERCENT',
    'MONEY': 'MONEY',
    'QUANTITY': 'QUANTITY',
    'ORDINAL': 'ORDINAL',
    'CARDINAL': 'CARDINAL'
}

nlp = spacy.load('en')


def _represent_word(word):
    if word.like_url:
        return '%%URL|X'
    text = re.sub(r'\s', '_', word.text)
    tag = LABELS.get(word.ent_type_, word.pos_)
    if not tag:
        tag = '?'
    return text + '|' + tag


def _transform_doc(doc):
    doc = nlp(unicode(doc))
    for ent in doc.ents:
        ent.merge(ent.root.tag_, ent.text, LABELS[ent.label_])
    for np in doc.noun_chunks:
        while len(np) > 1 and np[0].dep_ not in ('advmod', 'amod', 'compound'):
            np = np[1:]
        np.merge(np.root.tag_, np.text, np.root.ent_type_)
    strings = []
    for sent in doc.sents:
        if sent.text.strip():
            strings.append(' '.join(_represent_word(w) for w in sent if not w.is_space))
    if strings:
        return '\n'.join(strings) + '\n'
    else:
        return ''


def transform_topics(nlu_topics):
    transformed_topics = []
    for t in nlu_topics:
        transformed_topics.extend(_transform_doc(unicode(t)).split())

    def correct_case(t):
        pre, post = t.split('|')
        return pre.lower() + '|' + post.upper()

    return map(correct_case, transformed_topics)


def _sense_similarity(a, b):
    try:
        print('calling request')
        url = '{3}?a={1}&b={2}'.format(SENSE_SERVER_PORT, a, b, SENSE_SERVER)
        print(url)
        result = requests.get(url).text
        print(result)
        return float(json.loads(result)['sim'])
    except Exception as e:
        print(e)
        return 0


def sense_topic_similarity(topics1, topics2):
    score = 0
    similarities = []
    print('called')
    print(topics1)
    for i in topics1:
        print(i)
        most_similar = max([0] + map(lambda x : _sense_similarity(i, x), topics2))
        similarities.append(most_similar)

    return sum(similarities) / max(float(len(similarities)), 1.0)
