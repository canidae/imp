from flask import Flask, render_template, send_file, jsonify, request
from os import listdir, makedirs, path

import psycopg2

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# TODO: replace parameter "member_id" with some "session_id" (when we got such a thing)
@app.route('/uploadFiles/<int:member_id>', methods = ['POST'])
def uploadFiles(member_id):
    for uploadFile in request.files.getlist('files'):
        if uploadFile.mimetype not in ['audio/flac', 'audio/mp3', 'audio/ogg']:
            # file is not a type we support, discard it
            return ''
        extension = uploadFile.mimetype[uploadFile.mimetype.find('/') + 1:]
        uploadDir = 'music/' + str(member_id) + '/upload/'
        if not path.exists(uploadDir):
            makedirs(uploadDir)
        upload_num = 1
        for existing_file in listdir(uploadDir):
            tmp_num = int(existing_file[:existing_file.find('.')])
            if tmp_num >= upload_num:
                upload_num = tmp_num + 1
        filename = uploadDir + str(upload_num) + '.' + extension
        uploadFile.save(filename)
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

@app.route('/playTrack/<int:member_id>/<int:track_id>/<filename>')
def playTrack(member_id, track_id, filename):
    if len(filename) > 8:
        return # simplistic protection for the time being, the other values are integers and likely safe. # TODO: regex match filename with '^\w+\.\w+$' (\w = a-zA-Z0-9_)
    return send_file('music/' + str(member_id) + '/' + str(track_id) + '/' + filename)

def getDatabaseConnection():
    # TODO: remember database connection over requests
    # TODO: pooling
    return psycopg2.connect("host='localhost' dbname='imp' user='imp' password='imp'")

if __name__ == '__main__':
    app.debug = True
    app.run(threaded = True)
