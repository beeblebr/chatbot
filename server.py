from functools import wraps
from flask import *
from datetime import datetime

from util.db_utils import *
from util.sense_utils import get_closest_sense_items
from util.topic_utils import prettify_topic, uglify_topic

from bot_wrapper import handle_response, get_slots_of_user

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'super-secrfeet'

"""Admin routes"""

# import os
# os.system('./code/train_dialogue.sh')


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 's3cret'


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


"""Taxonomy related routes."""


@app.route('/admin/taxonomy')
@requires_auth
def taxonomy_builder():
    return render_template('admin/taxonomy.html')


@app.route('/admin/taxonomy/related', methods=['POST'])
@requires_auth
def fetch_related_topics():
    search_topic = request.form.get('topic')
    related_topics = get_closest_sense_items(search_topic)
    return jsonify([{'name': topic['text'], 'similarity': (1)} for topic in
                    related_topics])


@app.route('/admin/taxonomy/related_custom', methods=['POST'])
@requires_auth
def fetch_custom_topics():
    topic = request.form.get('topic')
    relations = [{'name': b, 'similarity': 1} for b in get_relations(topic)]
    return jsonify(relations)


@app.route('/admin/taxonomy/save_custom', methods=['POST'])
@requires_auth
def set_custom_topics():
    topic = request.form.get('topic')
    custom_related = request.form.get('custom_topics').split(';')
    update_relations(topic, custom_related)
    return jsonify({'success': True})


"""User related routes."""


@app.route('/admin/users/delete_knowledge_item', methods=['POST'])
@requires_auth
def remove_knowledge_item():
    user_id = request.form.get('id')
    item_text = request.form.get('text')
    delete_knowledge_item(user_id, item_text)
    return jsonify({'success': True})


@app.route('/admin/users/update_knowledge_item', methods=['POST'])
@requires_auth
def edit_knowledge_item():
    user_id = request.form.get('id')
    original_text = request.form.get('originalText')
    updated_text = request.form.get('updatedText')
    update_knowledge_item(user_id, original_text, updated_text)
    return jsonify({'success': True})


@app.route('/admin/users')
@requires_auth
def manage_users():
    users = get_all_users()
    return render_template('admin/users.html', users=users)


@app.route('/admin/users/user')
@requires_auth
def user_details():
    eight_id = request.args.get('id')
    user = get_user_from_eight_id(eight_id)
    user_knowledge = get_knowledge_list_by_eight_id(eight_id)
    for k in user_knowledge:
        k.pop('_id')
    user['knowledge'] = user_knowledge
    user.pop('_id')
    return jsonify(user)


@app.route('/admin/users/delete')
@requires_auth
def user_delete():
    eight_id = request.args.get('id')
    delete_user(eight_id)
    return jsonify({'success': True})


"""Webpage routes"""


@app.route('/admin')
@requires_auth
def admin():
    return render_template('admin/admin.html')


@app.route('/')
def index():
    return render_template('login2.html')


@app.route('/home')
def home():
    from trends.trending import identify_trending_topics
    trending_topics = identify_trending_topics()
    trending_topics = {
        topic.split('|')[0].replace('_', ' '): trending_topics[topic] for topic in
        trending_topics}
    trending_topics = dict(
        sorted(trending_topics.iteritems(), key=lambda (k, v): (v, k),
               reverse=True))
    return render_template('home2.html', trending_topics=trending_topics)


@app.route('/trending')
def trending():
    return render_template('trending.html')


@app.route('/ask')
def ask():
    return render_template('ask.html', action='ask')


@app.route('/share')
def share():
    return render_template('share.html', action='share')


@app.route('/admin/signup', methods=['GET', 'POST'])
@requires_auth
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        name = request.form.get('name')
        eight_id = request.form.get('eight_id')

        existing = db.users.find_one({'eight_id': eight_id})
        if existing:
            return redirect('/admin/signup')
        else:
            db.users.insert_one({'name': name, 'eight_id': eight_id})

        return redirect('/admin/users')


"""API Endpoints"""


@app.route('/api/users/<eight_id>')
def get_user_from_id(eight_id):
    user = get_user_from_eight_id(str(eight_id).zfill(8))
    user.pop('_id')
    if user:
        return jsonify(user)
    return None


@app.route('/api/knowledge/<eight_id>')
def get_user_knowledge(eight_id):
    knowledge = get_knowledge_by_eight_id(str(eight_id).zfill(8))
    return jsonify({
        'text': knowledge['text']
    })


@app.route('/api/knowledges/', methods=['POST'])
def add_to_k():
    k = request.get_json()
    k['timestamp'] = datetime.now()
    insert_knowledge(k)
    return jsonify({
        'success': True
    })


@app.route('/api/clarify')
def clarify():
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

    return jsonify({
        'type': 'found',
        'match': {
            'user_id': relevant_knowledge_items[0]['eight_id'],
            'knowledge': relevant_knowledge_items[0]['text']
        }
    })


@app.route('/api/query')
def query():
    q = request.args.get('text')
    user_id = request.args.get('user_id')

    response, slots = handle_response(
        user_id=user_id,
        query=q,
        intent='QUERY'
    )

    info = slots['response_metadata'].value
    logger.info(info)

    if info['result'] == 'QUERY_CLARIFICATION_NEEDED':
        query_clarification_options = map(
            prettify_topic,
            info['query_clarification_options']
        )
        return jsonify({
            'type': info['result'],
            'specify': query_clarification_options
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
        'type': 'unknown'
    })


app.run('0.0.0.0', port=8002, threaded=True, debug=True)
