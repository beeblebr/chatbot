import requests
import json
import conf

from util.topic_utils import uglify_topic


def _make_request(url, data):
    headers = {'content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(data), headers=headers).json()
    return response


def perform_batch_call(calls):
    response = _make_request(conf.SENSE_SERVER_URL, calls)
    results = json.loads(response['results'])
    clusters = json.loads(response['clusters'])
    return results, clusters


def get_closest_sense_items(topic):
    response = _make_request(conf.SENSE_SERVER_URL + '/top_related_items', json.dumps({'topic': topic}))
    response = json.loads(response)['result']
    return response
