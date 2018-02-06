import requests
import json
import re
from pprint import pprint
import numpy as np
import warnings
import conf

from nltk import pos_tag


def _transform_doc_nltk(doc, maintain_case=False):  
    doc = re.sub(r'[^\w\s]', '', doc).lower()
    tagged = pos_tag(doc.split())
    print(tagged)
    tags = ' '.join([x[1] for x in tagged])
    print(tags)
    # Noun chaining with optional leading adjective
    matches = list(re.finditer('((JJ[A-Z]? )?)((NN[A-Z]? ?)+)', tags))
    noun_phrases = []
    for match in matches:
        chain_start_index = tags[:match.start() + 1].strip().count(' ')  # 4
        chain_end_index = tags[:match.end()].strip().count(' ')  #  
        print(tagged[chain_start_index:chain_end_index + 1])
        chain = tagged[chain_start_index : chain_end_index + 1]
        chain = '_'.join([x[0] for x in chain]) + '|NOUN'
        noun_phrases.append(chain)
    return ' '.join(noun_phrases)


def perform_batch_call(calls):
    headers = {'content-type': 'application/json'}
    url = conf.SENSE_SERVER_URL
    result = requests.post(url, data=json.dumps(calls), headers=headers).text
    res = json.loads(json.loads(result)['result'])
    return res


def get_closest_sense_items(topic):
    topic = topic.lower().replace(' ', '_') + '|NOUN'
    headers = {'content-type': 'application/json'}
    url = conf.SENSE_SERVER_URL
    result = requests.post(url + '/top_related_items', data=json.dumps({'topic': topic}), headers=headers).text
    res = json.loads(json.loads(result)['result'])
    return res

