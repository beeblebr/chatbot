import requests
import json
import re
from pprint import pprint
import numpy as np
import warnings
import conf

from nltk import pos_tag
from util.topic_utils import uglify_topic


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

