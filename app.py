import requests
from flask import Flask, render_template, url_for, redirect, request, session
from wtforms import Form, StringField, PasswordField, BooleanField ,validators, SelectMultipleField, SubmitField
import json
import DAL
import Insert
import UserHandler

app = Flask(__name__)
app.secret_key = b'4d08d4a53d0fd770975f622163928fc2f87e13bde753c5cb9d4a3afedd0c2169'

# @app.before_request
# def setup():

@app.route("/", methods=['GET'])
def index():
    session.permanent = False
    bands = DAL.DAL.getBands(5)
    albums = DAL.DAL.getAlbums(5)
    songs = DAL.DAL.getSongs(5)
    loggedIn = False
    if 'username' in session:
        loggedIn= True
    return render_template('index.html',value1=bands, value2 = albums, value3 = songs, value4=loggedIn)

@app.route("/insertItem", methods=['GET', 'POST'])
def insertItem():
    loggedIn = False
    if 'username' in session:
        loggedIn = True
        form = InputForm(request.form)
        if request.method == 'POST' and form.validate():
            item = Insert.input.insertItem(form.band.data, form.album.data, form.song.data, session.get('username'))
            if item == {}:
                return render_template('input.html', loggedIn=loggedIn, form=form)
            else:
                return redirect(url_for("index"))
        return render_template('input.html', loggedIn=loggedIn, form=form)
    else:
        return render_template('loggedOut.html')

@app.route("/user", methods=['GET'])
def userPage():
    if 'username' in session:
        favs = DAL.DAL.getAllFavorites(session.get('username'))
        return render_template('user.html', user=session.get('username'), items=favs)
    else:
        return render_template('loggedOut.html')

@app.route("/concerts", methods=['GET', 'POST'])
def concerts():
    form = ConcertForm(request.form)
    status = 1
    concerts = DAL.DAL.getConcerts()
    if 'username' in session:
        if request.method == 'POST' and form.validate():
            status = Insert.input.insertConcert(session.get('username'), form.band.data, form.location.data)
            if(status == 1):
                return redirect(url_for("userPage"))
        return render_template('concerts.html', form=form, status=status, concerts=concerts)
    else:
        return render_template('loggedOut.html')

@app.route("/related", methods=['GET', 'POST'])
def related():
    if 'username' in session:
        form = RelatedForm(request.form)
        favs = DAL.DAL.getAllFavorites(session.get('username'))
        bands = [band for band in favs]
        fNames = []
        form.bands.choices = fNames
        sBands = []
        rBands = []
        for band in bands:
            if(band.get('type') == "artist"):
                # print(band)
                fNames.append(band.get('name'))
        if request.method == 'POST' and form.validate():
            sBands = form.bands.data
            rBands = DAL.DAL.insertRelated(sBands)
            # print(rBands)
        return render_template('related.html', favs=favs, form=form, sBands=sBands, rBands=rBands)
    else:
        return render_template('loggedOut.html')

@app.route("/visual", methods=['GET'])
def visual():
    if 'username' in session:
        bands = DAL.DAL.getAllBands()
        albums = DAL.DAL.getAllAlbums()
        songs = DAL.DAL.getAllSongs()
        genres = DAL.DAL.getGenres()
        for b in bands:
            DAL.DAL.insertGenres(b.get('name'))
        favs = DAL.DAL.getAllFavorites(session.get('username'))
        return render_template('visual.html', favs=favs, bands=bands, albums=albums, songs=songs, genres=genres)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        rg = UserHandler.UserHandler.register(form.username.data, form.email.data, form.password.data)
        if(not rg):
            return redirect(url_for("register"))
        DAL.DAL.insertUser(form.username.data, form.email.data, form.password.data)
        return redirect(url_for("login"))
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        users = DAL.DAL.getUsers()
        lg = UserHandler.UserHandler.login(form.input.data, form.password)
        for user in users:
            if(lg.get('username') == user.get('username') and lg.get('password') == user.get('password')):
                session['username'] = lg.get('username')
        return redirect(url_for("index"))
    return render_template('login.html', form=form)

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for("index"))

class InputForm(Form):
    band = StringField('Band')
    album = StringField('Album')
    song = StringField('Song')

class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=5, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])

class LoginForm(Form):
    input = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password')

class ConcertForm(Form):
    band = StringField('Band', [validators.Length(min=4, max=25)])
    location = StringField('City', [validators.Length(min=4, max=25)])

class RelatedForm(Form):
    b = []
    bands = SelectMultipleField('', choices=b)
    submit = SubmitField('Choose Bands')