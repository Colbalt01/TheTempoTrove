import requests
from flask import Flask, render_template, url_for, redirect, request
from wtforms import Form, StringField, PasswordField, validators
import json
import DAL
import Insert

app = Flask(__name__)

@app.route("/", methods=['GET'])
def index():  
    # songs = DAL.DAL.getSongs().get('name')
    bands = DAL.DAL.getBands(5)
    albums = DAL.DAL.getAlbums(5)
    songs = DAL.DAL.getSongs(5)
    return render_template('index.html',value1=bands, value2 = albums, value3 = songs)

@app.route("/insertItem", methods=['GET', 'POST'])
def insertItem():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        # song = DAL.DAL.insertSong("Funeral Derangements")
        item = Insert.input.insertItem(form.band.data, form.album.data, form.song.data)
        # flash('Submitted!')
        return redirect(url_for("index"))
    return render_template('input.html', form=form)

class RegistrationForm(Form):
    band = StringField('Band', [validators.Length(min=4, max=25)])
    album = StringField('Album', [validators.Length(min=6, max=35)])
    song = StringField('Song', [validators.Length(min=6, max=35)])