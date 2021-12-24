import os
import pathlib
import datetime
import yaml
import requests
import json
import random
import math
import subprocess
import sys
import itertools
import string
import threading

import extra.load.load as load_py
load_py.cls() # replit console bug work-around
import extra.ytools.ytools as yt

loader = load_py.Loader()
thread = None


def cLoad(msg: str):
    global thread, loader
    thread = threading.Thread(target=loader.next, args=(msg, ))
    thread.start()


def sThread():
    global thread, loader
    loader.stop()


try:
    with open("extras.y", "r") as stream:
        toins = stream.read().split(", ")
        if toins == ['']:
            yt.log('Nothing to install')
        else:
            if type(toins) == list:
                for pkg in toins:
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", pkg])
            else:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", toins])
except:
    pass

yt.log("Checking for updates")
import extra.install.update

yt.log("Importing libs...")
from flask import Flask, render_template, redirect, flash, url_for, request, send_from_directory, abort, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, URLField
from wtforms.validators import InputRequired, Email, Length
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from wtforms.widgets import TextArea
from flask_migrate import Migrate
from oauthlib.oauth2 import WebApplicationClient
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_gzip import Gzip
from flask_talisman import Talisman, ALLOW_FROM

#import reset # resets login.db # use only if cannot upgrade db

cLoad("Initialising")

settings = None
with open("config.yaml", "r") as stream:
    try:
        settings = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        yt.warn(exc)

s_low = yt.Severity(
    name='Low Severity',
    desc=
    'A low severity, does not usualy require immediate resolution. Lowest severity.'
)

s_med = yt.Severity(
    name='Medium Severity',
    desc=
    'A medium severity, does not usualy require immediate resolution. Should be fixed as soon as possible though.'
)

s_high = yt.Severity(
    name='High Severity',
    desc='A high severity. Should be fixed as soon as possible.')


class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[InputRequired(),
                                       Length(min=4, max=34)])
    password = PasswordField(
        'Password', validators=[InputRequired(),
                                Length(min=7, max=70)])
    submit = SubmitField('Sign In')
    remember_me = BooleanField("Remember me", default=True)


class RegisterForm(FlaskForm):
    username = StringField('Username',
                           validators=[InputRequired(),
                                       Length(min=4, max=34)])
    email = EmailField('Email',
                       validators=[
                           InputRequired(),
                           Length(min=4, max=321),
                           Email(message="Invalid Email")
                       ])
    password = PasswordField('Password',
                             validators=[InputRequired(),
                                         Length(max=70)])


class ThreadForm(FlaskForm):
    title = StringField("Title",
                        validators=[Length(min=1, max=100),
                                    InputRequired()],
                        render_kw={"placeholder": "+!+13"})
    content = StringField(
        "Content",
        validators=[Length(min=1, max=2000),
                    InputRequired()],
        widget=TextArea(),
        render_kw={"placeholder": "Thread Content"})


class CommentForm(FlaskForm):
    content = StringField(
        "Content",
        validators=[Length(min=1, max=1500),
                    InputRequired()],
        widget=TextArea(),
        render_kw={"placeholder": "Comment Content"})


class AboutForm(FlaskForm):
    about = StringField("About",
                        validators=[Length(min=1, max=700),
                                    InputRequired()],
                        widget=TextArea())


class EditForm(FlaskForm):
    title_e = StringField("Title",
                          validators=[Length(min=1, max=100),
                                      InputRequired()],
        render_kw={"placeholder": "Change Title"})
    content_e = StringField(
        "Content",
        validators=[Length(min=1, max=2000),
                    InputRequired()],
        widget=TextArea(),
        render_kw={'class': 'aheight', 'placeholder': 'Change Content'})


class SettingsForm(FlaskForm):
    profile_pic = URLField('Profile picture',
                           validators=[Length(min=5, max=840)], render_kw={"placeholder": "Profile Picture URL"})
    delete = SubmitField('Delete Account')


class ShopForm(FlaskForm):
    item1 = SubmitField('Novice Role')
    item2 = SubmitField('Veteran Role')
    item3 = SubmitField('Expert Role')
    item4 = SubmitField('Hacker Role')
    item5 = SubmitField('Mythological Commenter Role')


class PWDResetForm(FlaskForm):
    username = StringField('Username',
                           validators=[InputRequired(),
                                       Length(min=4, max=34)])


app = Flask(__name__)

### config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + str(
    pathlib.Path(__file__).parent.resolve()) + '/login.db'  # db location
if settings['SQLALCHEMY_DATABASE_URI'] != 'default':
    app.config['SQLALCHEMY_DATABASE_URI'] = settings['SQLALCHEMY_DATABASE_URI']
    yt.log('Not default')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ['s-key']
app.config['SECURITY_PASSWORD_SALT'] = os.environ['pwd-salt']

mail = Mail(app)
app.config['APP_MAIL_USERNAME'] = os.environ['e-user']
app.config['APP_MAIL_PASSWORD'] = os.environ['e-pwd']
app.config['MAIL_USERNAME'] = os.environ['e-user']
app.config['MAIL_PASSWORD'] = os.environ['e-pwd']
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config["MAIL_DEFAULT_SENDER"] = settings['MAIL_DEFAULT_SENDER']

GOOGLE_CLIENT_ID = os.environ["c-id"]  # google client id
GOOGLE_CLIENT_SECRET = os.environ["c-sec"]  # google client sec
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration")
client = WebApplicationClient(GOOGLE_CLIENT_ID)

app.config['CACHE_TYPE'] = "SimpleCache"
app.config['CACHE_DEFAULT_TIMEOUT'] = 5

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=[
        "30 per second"
    ]  # if someone sends 30+ per second, its almost certainly a dos
)
csp = {
    'default-src': [
        '\'self\'', 'fonts.googleapis.com', 'cdn.jsdelivr.net',
        'cdnjs.cloudflare.com', 'fonts.gstatic.com', '\'unsafe-inline\'',
        'stackpath.bootstrapcdn.com', 'code.jquery.com', 'polyfill.io'
    ],
    'img-src':
    '*',
    'media-src': ['youtube.com']
}
### config

### inits
db = SQLAlchemy(app)
migrate = Migrate(app, db)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
Bootstrap(app)
mail = Mail(app)
admin = Admin(app)
cache = Cache(app)
Gzip(app)
talisman = Talisman(
    app,
    content_security_policy=csp,
    content_security_policy_nonce_in=['script-src', 'style-src'])
### inits


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(34), unique=True)
    email = db.Column(db.String(321), unique=True)
    password = db.Column(db.String(70))
    admin = db.Column(db.Boolean, nullable=False, default=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    registered_on = db.Column(db.DateTime, nullable=False)
    strike = db.Column(db.Boolean, nullable=False, default=False)
    banned = db.Column(db.Boolean, nullable=False, default=False)
    about = db.Column(db.String(370))
    coins = db.Column(db.Integer, default=0, nullable=False)
    role = db.Column(db.String(600))
    profile_pic = db.Column(db.String(900), default="/static/imgs/default.png")

    def like_post(self, post):
        if not self.has_liked_post(post):
            like = PostLike(user_id=self.id, post_id=post.id)
            db.session.add(like)
            db.session.commit()

    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(user_id=self.id, post_id=post.id).delete()
            db.session.commit()

    def has_liked_post(self, post):
        return PostLike.query.filter(PostLike.user_id == self.id,
                                     PostLike.post_id == post.id).count() > 0


class PostLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    post_id = db.Column(db.Integer)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    content = db.Column(db.String(2000))
    author_id = db.Column(db.Integer)
    created_on = db.Column(db.DateTime, nullable=False)
    comments = db.Column(db.Integer, default=0, nullable=False)

    def likes(self):
        return PostLike.query.filter(PostLike.post_id == self.id).count()

    def __lt__(self, other):
        return ratio_likes_age(self) < ratio_likes_age(other)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1500))
    author_id = db.Column(db.Integer)
    replyTo = db.Column(db.Integer)
    replyToPost = db.Column(db.Boolean, nullable=False, default=True)
    created_on = db.Column(db.DateTime, nullable=False)


class mModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.admin
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))


class Role:
    def __init__(self, name: str, desc: str):
        self.name = name
        self.desc = desc


def addCoins(author_id: int, n: int):
    usr = User.query.filter_by(id=author_id).first()
    usr.coins += n
    db.session.add(usr)
    db.session.commit()


def addRole(user_id: int, role_: Role):
    usr = User.query.filter_by(id=user_id).first()
    usr.role = role_.name
    db.session.add(usr)
    db.session.commit()


def deletePost(id):
    Post.query.filter_by(id=id).delete()
    for cmt in Comment.query.filter_by(replyTo=id).all():
        db.session.delete(cmt)
    db.session.commit()


def deleteUser(id):
    User.query.filter_by(id=id).delete()
    Post.query.filter_by(author_id=id).delete()
    PostLike.query.filter_by(user_id=id).delete()
    Comment.query.filter_by(author_id=id).delete()
    db.session.commit()


def addReply(content: str, toId: int, author_id: int, replyToPost=True):
    rep = Comment(content=content,
                  author_id=author_id,
                  replyTo=toId,
                  created_on=datetime.datetime.utcnow(),
                  replyToPost=replyToPost)
    pst = Post.query.filter_by(id=toId).first()
    pst.comments += 1
    db.session.add(rep)
    db.session.commit()
    addCoins(author_id, 5)


def createPost(title: str, content: str, author_id: int):
    pst = Post(title=title,
               content=content,
               author_id=author_id,
               created_on=datetime.datetime.utcnow())
    db.session.add(pst)
    db.session.commit()
    addCoins(author_id, 10)


def getPosts(id=-1):
    posts = Post.query.all()[-int(settings['postsPerPage']):]
    posts = list(reversed(posts))
    if id != -1:
        posts = [
            x for x in [x if x.author_id == id else None for x in posts]
            if x is not None
        ]
    authors = [
        User.query.filter_by(id=x.author_id).first().username
        for x in list(posts)
    ]
    return zip(posts, authors)


def sendEmail(to, subject, template):
    msg = Message(subject,
                  recipients=[to],
                  html=template,
                  sender=app.config['MAIL_DEFAULT_SENDER'])
    mail.send(msg)


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=settings['email_expiration']):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token,
                                 salt=app.config['SECURITY_PASSWORD_SALT'],
                                 max_age=expiration)
    except:
        return False
    return email


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


def ratio_likes_age(poste):
    age, likes = (poste.created_on - datetime.datetime.utcnow()
                  ).total_seconds() / 60 / 24, poste.likes() + 1  # age in days
    return (100 * math.log(10 * likes**2, 10)) / age  # 100log(10x^2)/a


def getHot():  # gets hot posts
    posts = Post.query.all()
    posts.sort()
    posts = posts[::-1][-int(settings['postsPerPage']):]
    authors = [
        User.query.filter_by(id=x.author_id).first().username
        for x in list(posts)
    ]
    return zip(posts, authors)


def days_between(d1):
    d2 = datetime.datetime.utcnow()
    secs = (d2 - d1).total_seconds()
    mins = math.floor(secs / 60)
    hours = math.floor(mins / 60)
    days = math.floor(hours / 24)
    months = math.floor(days / 60)
    years = math.floor(months / 12)

    if abs(mins) < 1:
        return str(round(secs)) + ' second(s)'
    if abs(hours) < 1:
        return str(round(mins)) + ' minute(s)'
    if abs(days) < 1:
        return str(round(hours)) + ' hour(s)'
    if abs(months) < 1:
        return str(round(days)) + ' day(s)'
    if abs(years) < 1:
        return str(round(months)) + ' month(s)'
    if abs(years) > 1:
        return str(round(years)) + ' year(s)'


settings['d_b'] = days_between


def getULikes(id):
    post_ids = [post.id for post in Post.query.filter_by(author_id=id).all()]
    likes = 0
    for ide in post_ids:
        likes += PostLike.query.filter_by(post_id=ide).count()
    return likes


settings['gul'] = getULikes


def gUserPosts(id):
    return Post.query.filter_by(author_id=id).count()


settings['gup'] = gUserPosts


def cRandPwd():
    z = ''
    for x in range(random.randrange(10, 20)):
        z += random.choice([
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C',
            'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
            'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c',
            'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
            'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '!', '@', '#',
            '$', '%', '^', '&', '*'
        ])
    return z


def cName(name):
    tname = name
    chars = string.ascii_lowercase + string.digits
    for z in range(1, 4):
        for nxt in itertools.product(chars, repeat=z):
            tname = ''.join(nxt)
            if User.query.filter_by(username=tname).first() != None:
                return tname
    return None


def hf(num):
    if int(num) == 0: return 0
    units = ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
    magnitude = int(math.floor(math.log(num, 1000.0)))
    return '%.0f%s' % (num / 1000.0**magnitude, units[magnitude])


settings['hf'] = hf


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@talisman(frame_options=ALLOW_FROM,
          frame_options_allow_from='*',
          content_security_policy={
              **csp, 'frame-ancestors': ['*']
          })
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


zed = [100, 500, 1500, 5000, 20000]


def getPrice(index):
    global zed
    return zed[index]


shop_items = [
    'Novice', 'Veteran', 'Expert', 'Hacker', 'Mythological Commenter'
]


@app.route('/shop', methods=['GET', 'POST'])
@login_required
def shop():
    form = ShopForm()
    if form.validate_on_submit():
        index = 0
        if form.item1.data == True: index = 0
        elif form.item2.data == True: index = 1
        elif form.item3.data == True: index = 2
        elif form.item4.data == True: index = 3
        elif form.item5.data == True: index = 4
        else:
            flash(f"Invalid Item! {form.item1}")
            return redirect(url_for("shop"))

        price = getPrice(index)

        if current_user.coins >= price:
            addCoins(current_user.id, -price)
            global shop_items
            addRole(current_user.id, Role(name=shop_items[index],
                                          desc="Unset"))
        else:
            flash("You do not have sufficient coin.")

    global zed
    return render_template("shop.html", form=form, z=zed)


@app.route('/cpost', methods=['GET', 'POST'])
@login_required
def cpost():
    form = ThreadForm()
    if form.validate_on_submit():
        title = form.title.data
        content = (form.content.data).replace('\n', '<br />')
        author_id = current_user.id
        if not any(x in content.lower()
                   for x in settings['prohibited_words']) and not any(
                       x in title.lower()
                       for x in settings['prohibited_words']):
            createPost(title, content, author_id)
            flash("Created post with title '{}'".format(title))
        return redirect(url_for('home'))
    return render_template('cpost.html', form=form)


@app.route('/profile/<user>', methods=["GET", 'POST'])
@cache.cached(timeout=15)
@login_required
def profile(user):
    usr = User.query.filter_by(username=user).first()
    form = AboutForm()
    if form.validate_on_submit():
        flash('Attempting about section change for {}'.format(user))
        usr.about = form.about.data
        db.session.add(usr)
        db.session.commit()
        return redirect(url_for(
            "profile", user=user))  # may cause too many redirects error

    if usr == None:
        abort(404)
    return render_template("profile.html",
                           user=usr,
                           posts=getPosts(usr.id),
                           form=form)


@app.route('/profile/del', methods=['POST'])
@login_required
def deleteAc():
    deleteUser(current_user.id)
    flash("Deleted account. :(")
    return redirect(url_for("home"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Attempting login for {}'.format(form.username.data))
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect(url_for('index'))
            elif user.password == form.password.data:
                login_user(user, remember=form.remember_me.data)
                return redirect(url_for('index'))
            else:
                flash("Invalid Credentials")
                return redirect(url_for('login'))
        return redirect('/')
    return render_template('login.html', form=form)


@limiter.limit("5/day")
@app.route('/confirmReset/<token>')
def confirmReset(token):
    try:
        email = confirm_token(token)
    except:
        flash("Link has expired or is invalid.")

    user = User.query.filter_by(email=email).first_or_404()
    pwd = cRandPwd()
    user.password = pwd
    if user:
        return f"Your password has been set to {pwd}."


@limiter.limit("5/day")
@app.route('/pwdrst/<uid>')
def pwdrst(uid):
    usr = User.query.filter_by(username=uid).first()
    if usr:
        token = generate_confirmation_token(usr.email)
        url = url_for('confirmReset', token=token, _external=True)
        html = render_template('cpemail.html', confirm_url=url)
        subject = "Reset your Password"
        sendEmail(usr.email, subject, html)
    else:
        flash("User does not exist.")
    return redirect(url_for("login"))


@limiter.limit("5/day")
@app.route('/pwdrst', methods=['GET', 'POST'])
def pwdrst_callback():
    form = PWDResetForm()
    if form.validate_on_submit():
        return redirect(url_for("pwdrst", uid=form.username.data))
    return render_template("reset.html", form=form)


@app.route('/loginG')
def loginG():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url.replace('http', 'https') + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route('/loginG/callback')
def loginGcb():
    global client, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url.replace('http', 'https'),
        redirect_url=request.base_url.replace('http', 'https'),
        code=code)
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    if userinfo_response.json().get("email_verified"):
        email = userinfo_response.json()["email"]
        if not User.query.filter_by(email=email).first():
            name = userinfo_response.json()["given_name"]
            if User.query.filter_by(username=name).first() != None:
                name = cName(name)
                if name == None: abort(500)
            newUser = User(username=name,
                           email=email,
                           password=cRandPwd(),
                           registered_on=datetime.datetime.utcnow(),
                           confirmed=True)
            db.session.add(newUser)
            db.session.commit()
            login_user(newUser, remember=True)
        else:
            newUser = User.query.filter_by(email=email).first()
            login_user(newUser, remember=True)
        flash("Logged in!")
        return redirect(url_for("profile", user=current_user.username))
    else:
        return "Email not avalible.", 400


@app.route('/reg', methods=["GET", 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        h_pwd = generate_password_hash(form.password.data, method='sha256')
        flash('Attempting reg for {}'.format(form.username.data))
        newUser = User(username=form.username.data,
                       email=form.email.data,
                       password=h_pwd,
                       registered_on=datetime.datetime.utcnow(),
                       confirmed=False)
        db.session.add(newUser)
        db.session.commit()

        token = generate_confirmation_token(newUser.email)

        url = url_for('confirm_email', token=token, _external=True)
        html = render_template('email.html', confirm_url=url)
        subject = "Activate your acount"

        sendEmail(newUser.email, subject, html)
        login_user(newUser)
        flash(
            'A confirmation email has been sent to your email. Please check your spam forlder in case you cannot find it. (Google abhorres automated emails)'
        )
        return redirect(url_for('index'))

    return render_template('reg.html', form=form)


@app.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash("Link has expired or is invalid.")

    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash("Already confirmed.")
    else:
        user.confirmed = True
        user.confirmed_on = datetime.datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account successfully.')
        addCoins(user.id, 100)
    return redirect(url_for('index'))


@app.route('/threads')
@app.route('/general')
@app.route('/cont')
@app.route('/feed')
@app.route('/home')
@cache.cached(timeout=3)
def home():
    return render_template('home.html', posts=getHot())


@app.route('/vote/<id>')
@login_required
def vote(id):
    pst = Post.query.filter_by(id=id).first()
    if not current_user.has_liked_post(pst):
        flash("Liked post. (may take up to 5 seconds to register)")
        current_user.like_post(pst)
    else:
        flash("Unliked post. (may take up to 5 seconds to register)")
        current_user.unlike_post(pst)
    return redirect(url_for("thread", thread=id))


@app.route('/thread/<thread>', methods=["GET", 'POST'])
@cache.cached(timeout=1)
def thread(thread):
    comments = Comment.query.filter_by(replyTo=thread)
    cauts = [
        User.query.filter_by(id=x.author_id).first().username for x in comments
    ]
    pst = Post.query.filter_by(id=thread).first()
    if pst == None:
        return render_template('404.html'), 404
    auth = User.query.filter_by(id=pst.author_id).first().username

    form = CommentForm()
    if form.validate_on_submit():
        datae = form.content.data
        if not any(x in datae.lower() for x in settings['prohibited_words']):
            addReply((form.content.data).replace('\n', '<br />'), thread,
                     current_user.id)
        return redirect(url_for('thread', thread=thread))

    forme = EditForm(title=pst.title, content=pst.content)

    if forme.validate_on_submit():
        pst.title = forme.title_e.data
        pst.content = forme.content_e.data
        db.session.add(pst)
        db.session.commit()

    return render_template("thread.html",
                           post=pst,
                           auth=auth,
                           form=form,
                           comments=zip(comments, cauts),
                           pid=thread,
                           forme=forme)


@app.route('/thread/<thread>/del')
@login_required
def delThread(thread):
    pst = Post.query.filter_by(id=thread).first()
    if pst.author_id == current_user.id:
        deletePost(thread)
        flash("Deleted thread.")
        return redirect(url_for("home"))
    else:
        return redirect(url_for("thread", thread=thread))


def is_url_image(image_url):
    image_formats = ("image/png", "image/jpeg", "image/jpg")
    r = requests.head(image_url)
    if r.headers["content-type"] in image_formats:
        return True
    return False


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings_():
    form = SettingsForm()
    if not form.validate_on_submit():
        form.profile_pic.data = current_user.profile_pic
    if form.validate_on_submit():
        if form.delete.data == True:
            return redirect(url_for("deleteAc"), code=307)
        usr = User.query.filter_by(id=current_user.id).first()
        print(form.profile_pic.data)
        if is_url_image(form.profile_pic.data):
            usr.profile_pic = form.profile_pic.data
        else:
            usr.profile_pic = request.base_url.replace(
                'http', 'https') + '/static/imgs/default.png'
        db.session.add(usr)
        db.session.commit()
        return redirect(url_for('profile', user=current_user.username))
    return render_template('settings.html', form=form)


@app.route('/loadmore')
def getMorePosts():  # slower than default load
    if request.args:
        ctr = int(request.args.get("ctr"))
        indx = Post.query.filter().count() - ctr

        pst = Post.query.filter_by(id=indx).first()
        if pst == None: return '[]'  # no more posts
        return make_response(
            jsonify([
                pst.title,
                User.query.filter_by(id=pst.author_id).first().username,
                days_between(pst.created_on), pst.content[:100] +
                (pst.content[100:] and '...'), pst.comments, pst.id
            ], 200))
    return '[]'  # no args


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    global s_med
    yt.warn(str(e))
    # rep = yt.Rep(title='500', content=str(e), severity=s_med)
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Roboto&display=swap" rel="stylesheet"><link rel="stylesheet" href="/static/style.css"><script src="/static/scripts.js"></script> <link rel="shortcut icon" href="/static/favicon.ico"></head><title>500 :P</title><h2 class='center'>500 - An error seems to have occured on the serverside.</h2><a href="/"><strong class='center'>Back to index?</strong></a><br><img src="https://thumbs.gfycat.com/AgileBoldBandicoot-size_restricted.gif" width="500" class='center-image'><i>Image gotten from <a href="https://thumbs.gfycat.com/AgileBoldBandicoot-size_restricted.gif">https://thumbs.gfycat.com/AgileBoldBandicoot-size_restricted.gif</a></i><a href="mailto:{settings['contactEmail']}"><p class='center'>Report this error?</p></a><div class="loader"><div></body></html>''', 500


@app.errorhandler(401)
def unauth(e):
    flash(e)
    return redirect(url_for('login'))


@app.errorhandler(400)
def bad_request(e):
    flash(e)
    return redirect(url_for('index'))


@app.errorhandler(408)
def time_out_error(e):
    flash(e)
    return redirect(url_for('index'))


@app.errorhandler(501)
def unimpl(e):
    return f'<h2>Your browser does not seem to support this website or one of its features.</h2><br><p>{e}</p>'


@app.errorhandler(429)
def ratelimit_handler(e):
    return "We would appreciate if you wouldn't DoS us."


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico')


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


@app.route('/terms')
def terms():
    return render_template('terms.html')


@app.route('/ver')
def version():
    return '2'


sThread()

if __name__ == "__main__":
    admin.add_view(mModelView(User, db.session))
    admin.add_view(mModelView(Post, db.session))
    admin.add_view(mModelView(Comment, db.session))
    app.jinja_env.globals.update(settings=settings)
    from waitress import serve
    yt.log("Starting.")
    serve(app, host='0.0.0.0', port=8080, threads=8)  # for ie10 :P
