import flask
import flask_login

users = {'rohanp': {'pw': 'secret'}}

app = flask.Flask(__name__)
app.secret_key = 'notsecretstring'

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

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

@app.route('/home')
@flask_login.login_required
def home():
    return flask.render_template("home.html", username=flask_login.current_user.id)


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'

if __name__ == "__main__":
    app.run(port=5000, debug=True)
