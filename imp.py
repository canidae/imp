from fnmatch import filter
from os import walk, path
from random import choice
from flask import Flask, render_template, send_file, jsonify
import psycopg2
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/randomTrack")
def randomTrack():
    connection = psycopg2.connect("host='localhost' dbname='imp' user='imp' password='imp'")
    cursor = connection.cursor()
    cursor.execute("select track_id, member_id, artist, title from track order by random() limit 1")
    result = cursor.fetchone()
    print "Artist: " + result[2] + ", Title: " + result[3]

    matches = []
    for root, dirnames, filenames in walk('music'):
        for filename in filter(filenames, '*.mp3'):
            matches.append(filename)
    return jsonify(song = choice(matches))

@app.route("/playTrack/<member_id>/<track_id>/<source>")
def playTrack(path):
    # TODO: source is a predefined list of "original", "320mp3", "q9ogg", etc
    #       although we don't know what format "original" is, and we don't want
    #       to convert 128mp3 to 320mp3, and we won't know format of original
    #       file by just "original".
    #       need to think this through.
    #       also need to sanitize input values
    return send_file("music/" + member_id + "/" + track_id + "/" + source)

if __name__ == "__main__":
    app.debug = True
    app.run(threaded=True)
