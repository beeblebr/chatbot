import json

from flask import Flask, request

from comparison import topic_similarity_map, fetch_search_results


app = Flask(__name__)


@app.route('/', methods=['POST'])
def index():
    """Route to handle questions."""
    params = json.loads(request.data)

    query_topics = params['query_topics']
    corpus_topics_map = params['corpus_topics_map']
    user_defined_taxonomy = params['user_defined_taxonomy']

    results, clusters = fetch_search_results(query_topics, corpus_topics_map, user_defined_taxonomy)
    # Map float to string for JSON conversion
    for i in range(len(results)):
        results[i]['cosine_similarity'] = str(results[i]['cosine_similarity'])
    return json.dumps({
        'results' : json.dumps(results), 
        'clusters': json.dumps(clusters)
    })


@app.route('/top_related_items', methods=['POST'])
def top_items():
    """Route to get related topics for Smart Taxonomy Builder."""
    params = json.loads(request.data)
    topic = params['topic']
    results = get_top_items(topic)
    return json.dumps({'result': json.dumps(results)})


if __name__ == '__main__':
    app.run('0.0.0.0', port=8011, debug=True)