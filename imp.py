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
    cursor.execute("select track_id, member_id, artist, title, original_format from track order by random() limit 1")
    result = cursor.fetchone()
    return jsonify(track_id = result[0], member_id = result[1], artist = result[2], title = result[3], original_format = result[4])

@app.route("/searchTrack/<text>")
def searchTrack():
    # TODO
    return ''

@app.route("/playTrack/<int:member_id>/<int:track_id>/<int:quality>/<extension>")
def playTrack(member_id, track_id, quality, extension):
    # quality: 1 (original), 2 (~320 kbit), 3 (~160 kbit), 4 (~80 kbit)
    # extension: flac, ogg (vorbis), mp3
    # NOTE:
    # - there will only be one valid extension for quality 1 (original)
    # - for the lower qualities, ogg vorbis and mp3 files are created, but no flac
    if len(extension) > 5:
        return # simplistic protection for the time being, the other values are integers and likely safe
    return send_file('music/' + str(member_id) + '/' + str(track_id) + '/' + str(quality) + '.' + extension)

if __name__ == "__main__":
    app.debug = True
    app.run(threaded = True)
