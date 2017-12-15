from flask import *
from datetime import datetime

import requests
from unidecode import unidecode

import categorize

from pymongo import MongoClient

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'super-secrfeet'


#client = MongoClient(username='mongoadmin', password='3aw#Aq')
client = MongoClient()
db = client.get_database('main')


"""Webpage routes"""
@app.route('/')
def index():
    return render_template('login2.html')

@app.route('/login', methods=['POST'])
def login():
    user = request.form.get('user')
    pwd = request.form.get('pass')

    user = db.users.find_one({'username': user, 'password': pwd})

    if user:
        return redirect('/home')

    return redirect('/')

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
    print eight_id
    user = db.users.find_one({'eight_id': str(eight_id).zfill(8)})
    # knowledge = db.knowledge.find_one({'eight_id': str(eight_id).zfill(8)})
    # user['knowledge'] = knowledge['text']
    user.pop('_id')
    if user:
        return jsonify(user)
    return None


@app.route('/api/knowledge/<eight_id>')
def get_user_knowledge(eight_id):
    knowledge = db.knowledge.find_one({'eight_id': str(eight_id).zfill(8)})
    return jsonify({'text': knowledge['text']})



from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.agent import Agent
from util.chat_utils import get_all_topics

agent = Agent.load("models/dialogue", interpreter=RasaNLUInterpreter("models/default/current"))


@app.route('/api/knowledges/', methods=['POST'])
def add_to_k():
    k = request.get_json()

    k['timestamp'] = datetime.now()
    k['text'] = k['text']
    k['type'] = 'text'
    db.knowledge.insert_one(k)
    return jsonify({'success': True})



from pprint import pprint
@app.route('/api/query')
def query():
    q = request.args.get('text')

    response = agent.handle_message(unicode(q))
    tracker = agent.tracker_store.get_or_create_tracker('default')
    print(tracker.slots)
    info = tracker.slots['response_metadata'].value

    if info['type'] == 'compromise':
        eight_id = info['top_matches'][0]['eight_id']
        return jsonify({'type': info['type'], 'before_message': response[0], 'match': {'user_id': eight_id}})
    elif info['type'] == 'found':
        eight_id = info['top_matches'][0]['eight_id']
        return jsonify({'type': info['type'], 'match': {'user_id': eight_id}})

    return jsonify({'type': 'unknown'})


app.run('0.0.0.0', port=8001, threaded=True, debug=True)
