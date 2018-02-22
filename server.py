from flask import *

from admin_pages.admin_pages import admin_pages
from user_pages.user_pages import user_pages
from api.api import api


app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'super-secrfeet'

app.register_blueprint(api)
app.register_blueprint(admin_pages)
app.register_blueprint(user_pages)

app.run('0.0.0.0', port=8002, threaded=True, debug=True)
