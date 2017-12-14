import requests
import json
import re
import spacy
from pprint import pprint
import numpy as np
import warnings
warnings.simplefilter("ignore", category=DeprecationWarning)

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


def _represent_word(word, maintain_case):
    if word.like_url:
        return '%%URL|X'
    text = re.sub(r'\s', '_', word.text)
    tag = LABELS.get(word.ent_type_, word.pos_)
    if not tag:
        tag = '?'

    return (text if maintain_case else text.lower()) + '|' + tag


def _transform_doc(doc, maintain_case=False):
    doc = nlp(unicode(doc))
    for ent in doc.ents:
        ent.merge(unicode(ent.root.tag_), unicode(ent.text), unicode(LABELS[ent.label_]))
    for np in doc.noun_chunks:
        while len(np) > 1 and np[0].dep_ not in ('advmod', 'amod', 'compound'):
            np = np[1:]
        np.merge(np.root.tag_, np.text, np.root.ent_type_)
    strings = []
    for sent in doc.sents:
        if sent.text.strip():
            strings.append(' '.join(_represent_word(w, maintain_case) for w in sent if not w.is_space))
    if strings:
        return '\n'.join(strings) + '\n'
    else:
        return ''


def transform_topics(nlu_topics):
    def transform(topic):
        return topic.lower().replace(' ', '_') + '|NOUN'
    return map(transform, nlu_topics)



SENSE_SERVER_URL = 'http://4c860dd8.ngrok.io'

def perform_batch_call(calls):
    print('Performing batch call')
    calls = {'calls': calls}
    headers = {'content-type': 'application/json'}
    url = SENSE_SERVER_URL
    result = requests.post(url, data=json.dumps(calls), headers=headers).text
    res = json.loads(json.loads(result)['result'])
    return res


def assemble_topic_wise_rankings(similarity_map, corpus):
    """Assemble separate rankings for each topic"""
    assert similarity_map
    valid_variants = map(lambda x : x['topic'], similarity_map[0])

    topic_wise_ranking = {}
    for topic in valid_variants:
        ranking = []
        for i in range(len(corpus)):
            item = corpus[i].copy()
            try:
                current_topic = [x for x in similarity_map[i] if x['topic'] == topic][0]
                score = float(current_topic['score'])
                rank = float(current_topic['rank'])
                matched_variant = current_topic['matched_variant']
            except Exception as e:
                score = 0
                rank = float('inf')
                matched_variant = None
            item.update(score=score)
            item.update(rank=rank)
            item.update(matched_variant=matched_variant)
            ranking.append(item)
        topic_wise_ranking[topic] = ranking

    for topic in topic_wise_ranking:
        topic_wise_ranking[topic].sort(key=lambda x : x['score'], reverse=True)

    return topic_wise_ranking
