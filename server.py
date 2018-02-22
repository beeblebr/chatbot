from functools import wraps
from flask import *

from util.db_utils import *
from util.sense_utils import get_closest_sense_items

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


from api.api import api

app.register_blueprint(api)

app.run('0.0.0.0', port=8002, threaded=True, debug=True)
