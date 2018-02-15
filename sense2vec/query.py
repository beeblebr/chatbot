import json


def process_query(params):
    return json.dumps({
        'result': 'QUERY_SUCCESS'
    })


def process_query_clarification():
    pass