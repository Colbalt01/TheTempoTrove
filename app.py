import requests
from flask import Flask, render_template, url_for, redirect, request, session
from wtforms import Form, StringField, PasswordField, BooleanField ,validators, SelectMultipleField, SubmitField, FileField
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
import json
import DAL
import Insert
import UserHandler
import os
import webbrowser

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = b'4d08d4a53d0fd770975f622163928fc2f87e13bde753c5cb9d4a3afedd0c2169'
app.config['UPLOADED_FOLDER'] = 'static'

@app.route("/", methods=['GET'])
def index():
    session.permanent = False
    bands = DAL.DAL.getBands(7)
    albums = DAL.DAL.getAlbums(7)
    songs = DAL.DAL.getSongs(7)
    loggedIn = False
    if 'username' in session:
        loggedIn= True
    return render_template('index.html',value1=bands, value2 = albums, value3 = songs, loggedIn=loggedIn, username=session.get('username'))

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
        return render_template('input.html', loggedIn=loggedIn, form=form, username=session.get('username'))
    else:
        return render_template('loggedOut.html')

@app.route("/user", methods=['GET'])
def userPage():
    if 'username' in session:
        favs = DAL.DAL.getAllFavorites(session.get('username'))
        for f in favs:
            if(f.get('type') == "album"):
                print(f.get('cover'))
        u = DAL.DAL.getUser(session.get('username'))
        return render_template('user.html', user=u, items=favs, username=session.get('username'))
    else:
        return render_template('loggedOut.html')

@app.route("/visual", methods=['GET'])
def visual():
    if 'username' in session:
        bands = DAL.DAL.getAllBands()
        albums = DAL.DAL.getAllAlbums()
        songs = DAL.DAL.getAllSongs()
        for b in bands:
            DAL.DAL.insertGenres(b.get('name'))
        genres = DAL.DAL.getGenres()
        favs = DAL.DAL.getAllFavorites(session.get('username'))
        return render_template('visual.html', favs=favs, bands=bands, albums=albums, songs=songs, genres=genres, username=session.get('username'))
    else:
        return render_template('loggedOut.html')

@app.route('/visual/<name>')
def visualItem(name):
    if 'username' in session:
        favs = DAL.DAL.getAllFavorites(session.get('username'))
        genres = DAL.DAL.getGenres()
        print("Don't")
        item = {}
        info = {}
        tracks = {}
        for f in favs:
            if f.get('name').lower() == name.lower():
                if(f.get('type') == "track"):
                    item = DAL.DAL.getSong(name)
                    info = DAL.DAL.getSongLyrics(name)
                elif(f.get('type') == "album"):
                    item = DAL.DAL.getAlbum(name)
                    info = DAL.DAL.getAlbumInfo(name)
                    tracks = DAL.DAL.getAlbumTracks(name)
                    print(item)
                elif(f.get('type') == "artist"):
                    item = DAL.DAL.getBand(name)
                    info = DAL.DAL.getBandInfo(name)
                if(item != {}):
                    return render_template('item.html', item=item, username=session.get('username'), genres=genres, info=info, tracks=tracks)
        return render_template('item.html', item=item, username=session.get('username'))
    else:
        return render_template('loggedOut.html')

@app.route("/extra", methods=['GET', 'POST'])
def extra():
    if 'username' in session:
        formC = ConcertForm(request.form)
        status = 1
        formR = RelatedForm(request.form)
        favs = DAL.DAL.getAllFavorites(session.get('username'))
        fNames = []
        formR.bands.choices = fNames
        sBands = []
        rBands = []
        concert = {}
        for band in favs:
            if(band.get('type') == "artist"):
                fNames.append(band.get('name'))
        if request.method == 'POST' and formC.submitC.data and formC.validate():
            status = Insert.input.insertConcert(session.get('username'), formC.band.data, formC.location.data)
            print(status)
            if(status == 1):
                return redirect(url_for("userPage"))
            elif(status == 4):
                concert = DAL.DAL.getConcert(formC.band.data, formC.location.data)
        elif request.method == 'POST' and formR.submitR.data and formR.validate():
            sBands = formR.bands.data
            rBands = DAL.DAL.insertRelated(sBands)
        return render_template('con-rel.html', formC=formC, status=status, favs=favs, formR=formR, sBands=sBands, rBands=rBands,concert=concert, username=session.get('username'))
    else:
        return render_template('loggedOut.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm2()
    print(form.validate_on_submit())
    file = form.username
    print(file)
    if form.is_submitted():
        print("submitted")
    if form.validate_on_submit():
        rg = UserHandler.UserHandler.register(form.username.data, form.email.data, form.password.data)
        if(not rg):
            return redirect(url_for("register"))
        file = form.picture.data
        print(file)
        print("Test file")
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOADED_FOLDER'],secure_filename(file.filename)))
        DAL.DAL.insertUser(form.name.data, form.username.data, form.email.data, form.password.data)
        return redirect(url_for("login"))
    else:
        print("Why?")
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
        return redirect(url_for("login"))
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
    name = StringField('First & Last Name', [validators.Length(min=5, max=25)])
    username = StringField('Username', [validators.Length(min=5, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    picture = FileField()
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])

class RegistrationForm2(FlaskForm):
    name = StringField('First & Last Name', [validators.Length(min=5, max=25)], render_kw={"placeholder": "First & Last Name"})
    username = StringField('Username', [validators.Length(min=5, max=25)], render_kw={"placeholder": "Username"})
    email = StringField('Email Address', [validators.Length(min=6, max=35)], render_kw={"placeholder": "Email"})
    picture = FileField()
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')], render_kw={"placeholder": "Confirm Password"})
    confirm = PasswordField('Confirm Password', render_kw={"placeholder": "Confirm Password"})
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])
    submit = SubmitField("Submit")

class LoginForm(Form):
    input = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password')

class ConcertForm(Form):
    band = StringField('Band', [validators.Length(min=4, max=25)])
    location = StringField('City', [validators.Length(min=4, max=25)])
    submitC = SubmitField('Submit')

class RelatedForm(Form):
    b = []
    bands = SelectMultipleField('', choices=b)
    submitR = SubmitField('Choose Bands')