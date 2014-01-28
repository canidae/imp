import glob
import os
import psycopg2
import shutil
import subprocess

import acoustid
from musicbrainz2.webservice import Query, TrackIncludes, WebServiceError

from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis

db = psycopg2.connect("host='localhost' dbname='imp' user='imp' password='imp'")
mb = Query()
acoustid_apikey = '8XaBELgH' # TODO: 'k5TfSNsw' is our api key, but it doesn't work yet (maybe some delay in servers?)

for filename in glob.glob('music/*/upload/*.*'):
    print ''
    print 'File:', filename
    print '================================================================================'
    member_id = filename[len('music/'):filename.find('/upload')]
    basename = filename[:filename.rfind('.')]
    original_format = filename[filename.rfind('.') + 1:].lower()

    print 'Fetching metadata from file'
    print '--------------------------------------------------------------------------------'
    if filename.endswith('.flac'):
        audio = FLAC(filename)
        decode_command = ['flac', '--decode', '-f', filename]
    elif filename.endswith('.ogg'):
        audio = OggVorbis(filename)
        decode_command = ['oggdec', filename]
    elif filename.endswith('.mp3'):
        audio = EasyID3(filename)
        decode_command = ['lame', '--decode', filename]
    else:
        print "Don't know to handle this file"
        continue

    artist = audio['artist'][0] if 'artist' in audio else ''
    title = audio['title'][0] if 'title' in audio else ''

    print artist
    print title

    print 'Looking up track on AcoustID/MusicBrainz'
    print '--------------------------------------------------------------------------------'
    acoustid_duration, acoustid_fingerprint = acoustid.fingerprint_file(filename) # TODO: use fingerprint & duration to check for duplicates in database
    acoustid_result = acoustid.parse_lookup_result(acoustid.lookup(acoustid_apikey, acoustid_fingerprint, acoustid_duration))
    mb_track_id = ''
    for a in acoustid_result:
        mb_track_id = a[1]
        try:
            track = mb.getTrackById(mb_track_id, TrackIncludes(artist=True))
            mb_track_title = track.getTitle()
            mb_track_artist = track.getArtist().getName()
        except WebServiceError, e:
            print 'Error:', e

        print 'Track ID:', mb_track_id
        print 'Title   :', mb_track_title
        print 'Artist  :', mb_track_artist
        print

        # TODO: match track id with files in database to check for duplicates

        # just pick first found track for now, we'll probably need to handle this somehow
        break

    if mb_track_id == '':
        print 'Track not found in MusicBrainz database'

    print 'Decoding to wav'
    print '--------------------------------------------------------------------------------'
    subprocess.call(decode_command)

    print 'Applying ReplayGain'
    print '--------------------------------------------------------------------------------'
    wavefile = basename + '.wav'
    soxfile = basename + '.sox.wav'
    subprocess.call(['sox', wavefile, '-b', '16', soxfile]) # convert to 16bit (wavegain bugs out on 24bit)
    shutil.move(soxfile, wavefile)
    wavefile_norm = basename + '_n.wav'
    shutil.copy(wavefile, wavefile_norm)
    subprocess.call(['wavegain', '-y', wavefile_norm])

    try:
        os.mkdir(basename)
    except OSError, e:
        print 'Error:', e

    print 'Encoding to Ogg Vorbis'
    print '--------------------------------------------------------------------------------'
    subprocess.call(['oggenc', '-q', '8', '-o', os.path.join(basename, '2.ogg'), wavefile])
    subprocess.call(['oggenc', '-q', '8', '-o', os.path.join(basename, '2_n.ogg'), wavefile_norm])
    subprocess.call(['oggenc', '-q', '5', '-o', os.path.join(basename, '3.ogg'), wavefile])
    subprocess.call(['oggenc', '-q', '5', '-o', os.path.join(basename, '3_n.ogg'), wavefile_norm])
    subprocess.call(['oggenc', '-q', '2', '-o', os.path.join(basename, '4.ogg'), wavefile])
    subprocess.call(['oggenc', '-q', '2', '-o', os.path.join(basename, '4_n.ogg'), wavefile_norm])

    print 'Encoding to Lame MP3'
    print '--------------------------------------------------------------------------------'
    subprocess.call(['lame', '--noreplaygain', '-V', '0', wavefile, os.path.join(basename, '2.mp3')])
    subprocess.call(['lame', '--noreplaygain', '-V', '0', wavefile_norm, os.path.join(basename, '2_n.mp3')])
    subprocess.call(['lame', '--noreplaygain', '-V', '4', wavefile, os.path.join(basename, '3.mp3')])
    subprocess.call(['lame', '--noreplaygain', '-V', '4', wavefile_norm, os.path.join(basename, '3_n.mp3')])
    subprocess.call(['lame', '--noreplaygain', '-V', '8', wavefile, os.path.join(basename, '4.mp3')])
    subprocess.call(['lame', '--noreplaygain', '-V', '8', wavefile_norm, os.path.join(basename, '4_n.mp3')])

    # delete temporary wave files
    os.remove(wavefile)
    os.remove(wavefile_norm)

    # copy original file into directory with encoded files
    shutil.copy(filename, os.path.join(basename, '1.' + original_format))

    # get track_id from database
    cursor = db.cursor()
    cursor.execute("select nextval('track_track_id_seq')")
    result = cursor.fetchone()
    track_id = str(result[0])
    cursor.close()

    # move directory with tracks
    shutil.move(basename, os.path.join('music', member_id, track_id))

    # update database
    cursor = db.cursor()
    cursor.execute("insert into track(track_id, member_id, artist, title, original_format) values (%s, %s, %s, %s, %s)", (track_id, member_id, artist, title, original_format))
    db.commit()
    cursor.close()

    # delete original file
    os.remove(filename)

db.close()
