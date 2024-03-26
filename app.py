import requests
from flask import Flask

app = Flask(__name__)



@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/t")
def thing():
    return ""

song = {
    "song_id" : "thing",
    "name" : "The American Nightmare",
    "":"",
    "artist" : "Ice Nine Kills",
    "album" : "The Silver Scream"
}

band= {
    "band_id" : "thing",
    "artist" : "Motionless In White"
}

album= {
    "album_id" : "thing",
    "artist" : "Figure",
    "album" : "Monsters 5"
}