import json

from flask import Flask, request

from topic_utils import *


app = Flask(__name__)


@app.route('/', methods=['POST'])
def index():
    params = json.loads(request.data)

    query_topics = params['query_topics']
    corpus_topics_map = params['corpus_topics_map']

    results = []
    for item_topics in corpus_topics_map:
        try:
            similarity_map = topic_similarity_map(query_topics['text'], item_topics['text'])
            results.append(similarity_map)
        except KeyError as ke:
            results.append(str(0))

    return json.dumps({'result' : json.dumps(results)})


@app.route('/top', methods=['POST'])
def top_items():
    print('received')
    params = json.loads(request.data)
    topics = params['topics']
    results = {topic: get_top_items(topic) for topic in topics}
    return json.dumps({'result': json.dumps(results)})


if __name__ == '__main__':
    app.run('0.0.0.0', port=8000, debug=True)