import requests
from flask import Flask, render_template, url_for, redirect, request, session
from wtforms import Form, StringField, PasswordField, BooleanField ,validators
import json
import DAL
import Insert
import UserHandler

app = Flask(__name__)
app.secret_key = b'4d08d4a53d0fd770975f622163928fc2f87e13bde753c5cb9d4a3afedd0c2169'

@app.route("/", methods=['GET'])
def index():  
    # songs = DAL.DAL.getSongs().get('name')
    bands = DAL.DAL.getBands(5)
    albums = DAL.DAL.getAlbums(5)
    songs = DAL.DAL.getSongs(5)
    loggedIn = False
    if 'username' in session:
        loggedIn= True
    print(session.get('username'))
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
        favs = DAL.DAL.getFavorites(session.get('username'))
        for fav in favs: 
            typeF = fav.get('type')
            for key, value in fav.items():
                if(key == "name" and typeF == "artist"):
                    print(key, ":" ,value)
        return render_template('user.html', user=session.get('username'), items=favs)
    else:
        return render_template('loggedOut.html')

@app.route("/concerts", methods=['GET', 'POST'])
def concerts():
    form = ConcertForm(request.form)
    if 'username' in session:        
        if request.method == 'POST' and form.validate():
            favs = DAL.DAL.getFavorites(session.get('username'))
            for fav in favs:
                if(fav.get('type') == "artist"):
                    DAL.DAL.insertConcerts(session.get('username'), fav.get("name"))
        return render_template('concerts.html', form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        rg = UserHandler.UserHandler.register(form.username.data, form.email.data, form.password.data)
        print(rg)
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
                print("Logged in success")
                print(lg.get('username'))
                session['username'] = lg.get('username')
        return redirect(url_for("index"))
    return render_template('login.html', form=form)

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for("index"))

class InputForm(Form):
    band = StringField('Band')
    album = StringField('Album')
    song = StringField('Song')

class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
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
    location = StringField('City', [validators.Length(min=4, max=25)]) 