from flask import *

from datetime import datetime

from bot_wrapper import handle_response, get_slots_of_user
from util.db_utils import *
from util.topic_utils import prettify_topic, uglify_topic

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


api = Blueprint('api', 'api', url_prefix='/api')


@api.route('/users/<eight_id>')
def get_user_from_id(eight_id):
    user = get_user_from_eight_id(str(eight_id).zfill(8))
    user.pop('_id')
    if user:
        return jsonify(user)
    return None


@api.route('/knowledge/<eight_id>')
def get_user_knowledge(eight_id):
    knowledge = get_knowledge_by_eight_id(str(eight_id).zfill(8))
    return jsonify({
        'text': knowledge['text']
    })


@api.route('/knowledges/', methods=['POST'])
def add_to_k():
    k = request.get_json()
    k['timestamp'] = datetime.now()
    insert_knowledge(k)
    return jsonify({
        'success': True
    })


@api.route('/clarify_corpus')
def clarify_corpus():
    logger.info('clarify_corpus')
    user_id = request.args.get('user_id')
    selected_options = request.args.get('options').split('|')

    info = get_slots_of_user(user_id)['response_metadata'].value
    clusters = info['clusters']
    similarity_map = info['similarity_map']

    # Get all topics that come under selected clusters
    selected_options = map(uglify_topic, selected_options)
    relevant_topics = []
    for option in selected_options:
        cluster = [c for c in clusters if c[0] == option][0]
        topics = [topic for topic in cluster[1]]
        relevant_topics.extend(topics)

    # Iterate through similarity_map to find the knowledge items tagged with
    # any of relevant_topics
    relevant_knowledge_items = []
    for knowledge_item in similarity_map:
        topics = map(lambda x: x['topic'], knowledge_item['ki_topics'])
        if (set(topics) & set(relevant_topics)):
            relevant_knowledge_items.append(knowledge_item)

    # response, slots = handle_response(
    #     user_id=user_id,
    #     query=None,
    #     relevant_knowledge_items=relevant_knowledge_items,
    #     intent='CORPUS_CLARIFICATION'
    # )

    return jsonify({
        'type': 'FOUND',
        'match': {
            'user_id': relevant_knowledge_items[0]['eight_id'],
            'knowledge': relevant_knowledge_items[0]['text']
        }
    })


@api.route('/clarify_query', methods=['POST'])
def clarify_query():
    query_clarifications = dict(request.form)
    user_id = query_clarifications.pop('user_id')[0]
    logger.info('user_id: %s', user_id)
    response, slots = handle_response(
        user_id=user_id,
        query_clarifications=query_clarifications,
        query=None,
        intent='QUERY_CLARIFICATION'
    )
    info = slots['response_metadata'].value
    if info['result'] == 'CORPUS_CLARIFICATION_NEEDED':
        logger.info('CORPUS_CLARIFICATION_NEEDED')
        cluster_heads = [prettify_topic(x[0]) for x in info['clusters']]
        return jsonify({
            'type': info['result'],
            'specify': cluster_heads
        })
    elif info['result'] == 'FOUND':
        logger.info('FOUND')
        eight_id = info['similarity_map'][0]['eight_id']
        knowledge = info['similarity_map'][0]['text']
        return jsonify({
            'type': info['result'],
            'match': {
                'user_id': eight_id,
                'knowledge': knowledge
            }
        })
    return jsonify({
        'type': 'UNKNOWN'
    })


@api.route('/query')
def query():
    q = request.args.get('text')
    user_id = request.args.get('user_id')

    response, slots = handle_response(
        user_id=user_id,
        query=q,
        intent='QUERY'
    )

    info = slots['response_metadata'].value
    logger.info(info.keys())

    if info['result'] == 'QUERY_CLARIFICATION_NEEDED':
        query_clarifications = info['query_clarifications']
        query_clarifications = {
            topic: options
            for topic, options in query_clarifications.iteritems()
        }
        leading_message = 'Before I begin looking for a match, I need you to clarify %d thing(s) for me.' % len(
            query_clarifications)
        return jsonify({
            'type': info['result'],
            'leadingMessages': [leading_message],
            'queryClarifications': query_clarifications
        })

    elif info['result'] == 'CORPUS_CLARIFICATION_NEEDED':
        cluster_heads = [prettify_topic(x[0]) for x in info['clusters']]
        return jsonify({
            'type': info['result'],
            'specify': cluster_heads
        })

    elif info['result'] == 'FOUND':
        eight_id = info['similarity_map'][0]['eight_id']
        knowledge = info['similarity_map'][0]['text']
        return jsonify({
            'type': info['result'],
            'match': {
                'user_id': eight_id,
                'knowledge': knowledge
            }
        })

    elif info['result'] == 'NOTHING_FOUND':
        return jsonify({
            'type': info['result'],
            'before_message': 'Nothing found'
        })

    return jsonify({
        'type': 'UNKNOWN'
    })
