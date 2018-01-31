import requests
import json
import re
from pprint import pprint
import numpy as np
import warnings
import conf

from nltk import pos_tag


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
    return ' '.join(noun_phrases)


def perform_batch_call(calls):
    print('Performing call')
    headers = {'content-type': 'application/json'}
    url = conf.SENSE_SERVER_URL
    result = requests.post(url, data=json.dumps(calls), headers=headers).text
    res = json.loads(json.loads(result)['result'])
    return res


def get_closest_sense_items(calls):
    print('Performing call')
    headers = {'content-type': 'application/json'}
    url = conf.SENSE_SERVER_URL
    result = requests.post(url + '/top', data=json.dumps(calls), headers=headers).text
    res = json.loads(json.loads(result)['result'])
    print(res)
    return res
