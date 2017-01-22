import flask
import flask_login
from flask import make_response
from functools import wraps, update_wrapper
from datetime import datetime
from db import users, properties

app = flask.Flask(__name__)
app.secret_key = 'notsecretstring'

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['pw'] == users[email]['pw']

    return user

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

@app.route('/')
def index():
    return flask.render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return flask.render_template("login.html")

    email = flask.request.form['email']
    if email in users and flask.request.form['pw'] == users[email]['pw']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        return flask.redirect(flask.url_for('home'))

    return 'Bad login'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if flask.request.method == 'GET':
        return flask.render_template("register.html")

    email = flask.request.form['username']
    pw = flask.request.form['pw']
    users[email] = {'pw' : pw}

    user = User()
    user.id = email
    flask_login.login_user(user)
    return flask.redirect(flask.url_for('home'))

@app.route('/home', methods=['GET'])
@flask_login.login_required
@nocache
def home():
    user = flask_login.current_user.id

    if flask.request.args.get('query'):
        properties_ = properties.values()
        return flask.render_template("search.html", properties=properties_)
    else:
        my_properties = []

        for prop_name, n_shares in users[user]["properties"]:
            prop = properties[prop_name]
            my_properties.append(
            {
                'name':prop_name,
                'n_shares':n_shares,
                'price':prop['price'],
                'change':prop['change']
            })

        return flask.render_template("home.html", username=user,
                                                  my_properties=my_properties
                                                  )

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'


if __name__ == "__main__":
    app.run(port=5000, debug=True)
