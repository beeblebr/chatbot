from flask import *

user_pages = Blueprint('user_pages', 'user_pages')


@user_pages.route('/')
def index():
    return render_template('login2.html')


@user_pages.route('/home')
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


@user_pages.route('/trending')
def trending():
    return render_template('trending.html')


@user_pages.route('/ask')
def ask():
    return render_template('ask.html', action='ask')


@user_pages.route('/share')
def share():
    return render_template('share.html', action='share')
