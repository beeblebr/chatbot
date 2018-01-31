from flask import *
from datetime import datetime

import requests

from util.db_utils import *

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'super-secrfeet'


"""Webpage routes"""
@app.route('/')
def index():
    return render_template('login2.html')



@app.route('/home')
def home():
    return render_template('home2.html')


@app.route('/ask')
def ask():
    return render_template('ask.html', action='ask')

@app.route('/share')
def share():
    return render_template('share.html', action='share')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        name = request.form.get('name')
        eight_id = request.form.get('eight_id')

        existing = db.users.find_one({'eight_id': eight_id})
        if existing:
            return redirect('/signup')
        else:
            db.users.insert_one({'name': name, 'eight_id': eight_id})
        
        return redirect('/')


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
    return jsonify({'text': knowledge['text']})


from bot_wrapper import handle_message

@app.route('/api/knowledges/', methods=['POST'])
def add_to_k():
    k = request.get_json()
    k['timestamp'] = datetime.now()
    k['text'] = k['text']
    k['type'] = 'text'
    insert_knowledge(k)
    return jsonify({'success': True})



from pprint import pprint
@app.route('/api/query')
def query():
    print('yoooo')
    q = request.args.get('text')
    user_id = request.args.get('user_id')
    print(q)
    print(user_id)
    # Send message to bot, and retrieve response_metadata
    response, slots = handle_message(user_id, unicode(q))
    info = slots['response_metadata'].value

    try:
        if info['type'] == 'compromise':
            eight_id = info['top_matches'][0]['eight_id']
            return jsonify({'type': info['type'], 'before_message': response[0], 'match': {'user_id': eight_id}})
        elif info['type'] == 'found':
            eight_id = info['top_matches'][0]['eight_id']
            return jsonify({'type': info['type'], 'match': {'user_id': eight_id}})
        elif info['type'] == 'nothing_found':
            return jsonify({'type': info['type'], 'before_message': 'Nothing found'})
    except Exception as e:
        print(e)

    return jsonify({'type': 'unknown'})


app.run('0.0.0.0', port=8002, threaded=True, debug=True)
