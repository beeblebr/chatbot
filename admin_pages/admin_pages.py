from flask import *
from functools import wraps

from util.db_utils import *
from util.sense_utils import get_closest_sense_items


admin_pages = Blueprint('admin_pages', 'admin_pages', url_prefix='/admin')


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


@admin_pages.route('/taxonomy')
@requires_auth
def taxonomy_builder():
    return render_template('admin/taxonomy.html')


@admin_pages.route('/taxonomy/related', methods=['POST'])
@requires_auth
def fetch_related_topics():
    search_topic = request.form.get('topic')
    related_topics = get_closest_sense_items(search_topic)
    return jsonify([{'name': topic['text'], 'similarity': (1)} for topic in
                    related_topics])


@admin_pages.route('/taxonomy/related_custom', methods=['POST'])
@requires_auth
def fetch_custom_topics():
    topic = request.form.get('topic')
    relations = [{'name': b, 'similarity': 1} for b in get_relations(topic)]
    return jsonify(relations)


@admin_pages.route('/taxonomy/save_custom', methods=['POST'])
@requires_auth
def set_custom_topics():
    topic = request.form.get('topic')
    custom_related = request.form.get('custom_topics').split(';')
    update_relations(topic, custom_related)
    return jsonify({'success': True})


"""User related routes."""


@admin_pages.route('/users/delete_knowledge_item', methods=['POST'])
@requires_auth
def remove_knowledge_item():
    user_id = request.form.get('id')
    item_text = request.form.get('text')
    delete_knowledge_item(user_id, item_text)
    return jsonify({'success': True})


@admin_pages.route('/users/update_knowledge_item', methods=['POST'])
@requires_auth
def edit_knowledge_item():
    user_id = request.form.get('id')
    original_text = request.form.get('originalText')
    updated_text = request.form.get('updatedText')
    update_knowledge_item(user_id, original_text, updated_text)
    return jsonify({'success': True})


@admin_pages.route('/users')
@requires_auth
def manage_users():
    users = get_all_users()
    return render_template('admin/users.html', users=users)


@admin_pages.route('/users/user')
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


@admin_pages.route('/users/delete')
@requires_auth
def user_delete():
    eight_id = request.args.get('id')
    delete_user(eight_id)
    return jsonify({'success': True})


"""Webpage routes"""


@admin_pages.route('/')
@requires_auth
def admin():
    return render_template('admin/admin.html')


@admin_pages.route('/signup', methods=['GET', 'POST'])
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
