from flask import Flask, render_template, send_file, jsonify, request
from os import path, makedirs
import psycopg2
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# TODO: replace parameter "member_id" with some "session_id" (when we got such a thing)
@app.route('/uploadFiles/<int:member_id>', methods = ['POST'])
def uploadFiles(member_id):
    for uploadFile in request.files.getlist('files'):
        if uploadFile.mimetype not in ['audio/flac', 'audio/mp3', 'audio/wav', 'audio/ogg']:
            # file is not a type we support, discard it
            return ''
        extension = uploadFile.mimetype[uploadFile.mimetype.find('/') + 1:]
        uploadDir = 'music/' + str(member_id) + '/upload/'
        if not path.exists(uploadDir):
            makedirs(uploadDir)
        connection = getDatabaseConnection()
        cursor = connection.cursor()
        cursor.execute("select nextval('track_track_id_seq')")
        result = cursor.fetchone()
        uploadFile.save(uploadDir + str(result[0]) + '.' + extension)
        # TODO: convert to quality 2-4 ogg/mp3, move files, add to database, etc
        # TODO: run this outside of flask? i.e. cronjob-ish? it's multithreaded so not a big issue, yet...
        # TODO: on the other hand, the client is waiting for a response...
    return ''

@app.route('/randomTrack')
def randomTrack():
    connection = getDatabaseConnection()
    cursor = connection.cursor()
    cursor.execute('select member_id, track_id, original_format, artist, title from track order by random() limit 1')
    result = cursor.fetchone()
    #return jsonify(member_id = result[0], track_id = result[1], original_format = result[2], artist = result[3], title = result[4])
    return jsonify(track = result)

@app.route('/searchTrack/<text>')
def searchTrack(text):
    # TODO: use tsvector and nice stuff in postgres
    # - should create an own "search" table
    # - also put all metadata in it's own table
    connection = getDatabaseConnection()
    cursor = connection.cursor()
    cursor.execute('select member_id, track_id, original_format, artist, title from track where artist ilike %s or title ilike %s', (text, text))
    result = cursor.fetchall()
    return jsonify(tracks = result)

@app.route('/playTrack/<int:member_id>/<int:track_id>/<int:quality>/<extension>')
def playTrack(member_id, track_id, quality, extension):
    # quality: 1 (original), 2 (~320 kbit), 3 (~160 kbit), 4 (~80 kbit)
    # extension: flac, ogg (vorbis), mp3
    # NOTE:
    # - there will only be one valid extension for quality 1 (original)
    # - for the lower qualities, ogg vorbis and mp3 files are created, but no flac
    if len(extension) > 5:
        return # simplistic protection for the time being, the other values are integers and likely safe
    return send_file('music/' + str(member_id) + '/' + str(track_id) + '/' + str(quality) + '.' + extension)

def getDatabaseConnection():
    # TODO: remember database connection over requests
    # TODO: pooling
    return psycopg2.connect("host='localhost' dbname='imp' user='imp' password='imp'")

if __name__ == '__main__':
    app.debug = True
    app.run(threaded = True)
