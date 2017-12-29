import requests
import json
import re
import spacy
from pprint import pprint
import numpy as np
import warnings
import conf

from nltk import pos_tag

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


def _transform_doc_nltk(doc, maintain_case=False):
    doc = re.sub(r'[^\w\s]', '', doc)
    tagged = pos_tag(doc.split())
    # Chain noun tags
    noun_phrases = []
    i = 0
    while i < len(tagged):
        noun_phrase = []    
        while i < len(tagged) and tagged[i][1][0] == 'N':
            noun_phrase.append(tagged[i][0])
            i += 1
        if noun_phrase:
            noun_phrases.append('_'.join(noun_phrase) + '|NOUN')
        i += 1
    print(noun_phrases)
    return ' '.join(noun_phrases)


def _transform_doc(doc, maintain_case=False):
    doc = nlp(unicode(doc))
    for ent in doc.ents:
        ent.merge(unicode(ent.root.tag_), unicode(
            ent.text), unicode(LABELS[ent.label_]))
    for np in doc.noun_chunks:
        while len(np) > 1 and np[0].dep_ not in ('advmod', 'amod', 'compound'):
            np = np[1:]
        np.merge(np.root.tag_, np.text, np.root.ent_type_)
    strings = []
    for sent in doc.sents:
        if sent.text.strip():
            strings.append(' '.join(_represent_word(w, maintain_case)
                                    for w in sent if not w.is_space))
    if strings:
        return '\n'.join(strings) + '\n'
    else:
        return ''



def perform_batch_call(calls):
    print('Performing batch call')
    calls = {'calls': calls}
    headers = {'content-type': 'application/json'}
    url = conf.SENSE_SERVER_URL
    result = requests.post(url, data=json.dumps(calls), headers=headers).text
    res = json.loads(json.loads(result)['result'])
    return res
