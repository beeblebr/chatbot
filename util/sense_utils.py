import requests
import json
import re
from pprint import pprint
import numpy as np
import warnings
import conf

from nltk import pos_tag
from util.topic_utils import uglify_topic


def _transform_doc_nltk(doc, maintain_case=False):  
    doc = re.sub(r'[^\w\s]', '', doc).lower()
    tagged = pos_tag(doc.split())
    tags = ' '.join([x[1] for x in tagged])
    # Noun chaining with optional leading adjective
    matches = list(re.finditer('((JJ[A-Z]? )?)((NN[A-Z]? ?)+)', tags))
    noun_phrases = []
    for match in matches:
        chain_start_index = tags[:match.start() + 1].strip().count(' ')  # 4
        chain_end_index = tags[:match.end()].strip().count(' ')  #  
        chain = tagged[chain_start_index : chain_end_index + 1]
        chain = '_'.join([x[0] for x in chain]) + '|NOUN'
        noun_phrases.append(chain)
    return ' '.join(noun_phrases)


def perform_batch_call(calls):
    headers = {'content-type': 'application/json'}
    url = conf.SENSE_SERVER_URL
    response = json.loads(requests.post(url, data=json.dumps(calls), headers=headers).text)
    results = json.loads(response['results'])
    clusters = json.loads(response['clusters'])
    return results, clusters


def get_closest_sense_items(topic):
    headers = {'content-type': 'application/json'}
    url = conf.SENSE_SERVER_URL
    topic = uglify_topic(topic.lower())
    response = requests.post(url + '/top_related_items', data=json.dumps({'topic': topic}), headers=headers).text
    response = json.loads(json.loads(response)['result'])
    return response

