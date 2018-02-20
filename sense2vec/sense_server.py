"""Endpoints for all computations that the require Sense2Vec model."""

import json

from search import process_corpus_search, process_corpus_clarification
from query import process_query, process_query_clarification

from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['POST'])
def index():
    """Route to handle questions."""
    params = json.loads(request.data)

    intent_handlers = {
        'QUERY': process_query,
        'QUERY_CLARIFICATION': process_query_clarification,
        'CORPUS_SEARCH': process_corpus_search,
        'CORPUS_CLARIFICATION': process_corpus_clarification
    }

    response = intent_handlers[params['intent']](params)
    return response


@app.route('/top_related_items', methods=['POST'])
def top_items():
    """Route to get related topics for Smart Taxonomy Builder."""
    params = json.loads(request.data)
    topic = params['topic']
    results = get_top_items(topic)
    return json.dumps({'result': json.dumps(results)})


if __name__ == '__main__':
    import pip
    pip.main(['install', 'nltk'])
    # import nltk
    # nltk.download('averaged_perceptron_tagger')
    app.run('0.0.0.0', port=8011, debug=True)
