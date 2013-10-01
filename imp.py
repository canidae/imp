from fnmatch import filter
from os import walk, path
from random import choice
from flask import Flask, render_template, send_file, jsonify
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/randomTrack")
def randomTrack():
    matches = []
    for root, dirnames, filenames in walk('music'):
        for filename in filter(filenames, '*.mp3'):
            matches.append(filename)
    return jsonify(song = choice(matches))

@app.route("/playTrack/<path>")
def playTrack(path):
    return send_file("music/" + path)

if __name__ == "__main__":
    app.debug = True
    app.run(threaded=True)
