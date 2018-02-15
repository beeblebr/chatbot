import requests
import json
import conf


def _make_request(url, intent, data):
    headers = {'content-type': 'application/json'}
    data['intent'] = intent
    response = requests.post(
        url,
        data=json.dumps(data),
        headers=headers
    ).json()
    return response


def send_query(query_topics):
    response = _make_request(
        conf.SENSE_SERVER_URL,
        'QUERY',
        query_topics
    )
    result = json.loads(response['result'])
    return result


def send_query_clarification(
    query_topics,
    query_clarification_option_selected
):
    pass


def send_corpus_search(params):
    response = _make_request(
        conf.SENSE_SERVER_URL,
        'CORPUS_SEARCH',
        params
    )
    search_results = json.loads(response['results'])
    clusters = json.loads(response['clusters'])
    return search_results, clusters


def send_corpus_clarification():
    pass


def get_closest_sense_items(topic):
    response = _make_request(
        conf.SENSE_SERVER_URL + '/top_related_items',
        'CLOSEST_SENSE_ITEMS',
        json.dumps({'topic': topic})
    )
    response = json.loads(response)['result']
    return response
