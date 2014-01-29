import glob
import os
import psycopg2
import shutil
import subprocess
import sys
import time

import acoustid
from musicbrainz2.webservice import Query, TrackIncludes, WebServiceError

from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis

db = psycopg2.connect("host='localhost' dbname='imp' user='imp' password='imp'")
mb = Query()
acoustid_apikey = '8XaBELgH' # TODO: 'k5TfSNsw' is our api key, but it doesn't work yet (maybe some delay in servers?)

for filename in glob.glob('music/*/upload/*.*'):
    try:
        print ''
        print 'File:', filename
        print '================================================================================'
        member_id = filename[len('music/'):filename.find('/upload')]
        basename = filename[:filename.rfind('.')]
        original_format = filename[filename.rfind('.') + 1:].lower()
        wavefile = os.path.join(basename, 'original.wav')
        wavefile_norm = os.path.join(basename, 'replaygain.wav')
        soxfile = os.path.join(basename, 'sox.wav')
        delete_tmp_dir = False

        print 'Fetching metadata from file'
        print '--------------------------------------------------------------------------------'
        if filename.endswith('.flac'):
            file_metadata = FLAC(filename)
            decode_command = ['flac', '--decode', '-f', filename, '-o', wavefile]
        elif filename.endswith('.ogg'):
            file_metadata = OggVorbis(filename)
            decode_command = ['oggdec', filename, '-o', wavefile]
        elif filename.endswith('.mp3'):
            file_metadata = EasyID3(filename)
            decode_command = ['lame', '--decode', filename, wavefile]
        else:
            print "Don't know to handle this file"
            continue

        print 'Looking up track on AcoustID/MusicBrainz'
        print '--------------------------------------------------------------------------------'
        # TODO: max 3 requests/sec to AcoustID/MusicBrainz, just sleeping a sec for the time being
        time.sleep(1)
        acoustid_duration, acoustid_fingerprint = acoustid.fingerprint_file(filename) # TODO: use fingerprint & duration to check for duplicates in database? seems like matching fingerprints is not trivial
        acoustid_result = acoustid.parse_lookup_result(acoustid.lookup(acoustid_apikey, acoustid_fingerprint, acoustid_duration))
        mb_metadata = {}
        for result in acoustid_result:
            mb_metadata['musicbrainz_track_id'] = [result[1]]
            try:
                track = mb.getTrackById(mb_metadata['musicbrainz_track_id'][0], TrackIncludes(artist=True, releases=True))
                mb_metadata['artist'] = [track.getArtist().getName()]
                mb_metadata['title'] = [track.getTitle()]
                mb_metadata['musicbrainz_artist_id'] = [track.getArtist().getId()[track.getArtist().getId().rfind('/') + 1:]]
                for release in track.getReleases():
                    if 'album' not in mb_metadata:
                        mb_metadata['album'] = []
                        mb_metadata['tracknumber'] = []
                        mb_metadata['musicbrainz_release_id'] = []
                    mb_metadata['album'].append(release.getTitle())
                    mb_metadata['tracknumber'].append(release.getTracksOffset() + 1)
                    mb_metadata['musicbrainz_release_id'].append(release.getId()[release.getId().rfind('/') + 1:])
                    if release.getArtist() is not None:
                        if 'albumartist' not in mb_metadata:
                            mb_metadata['albumartist'] = []
                            mb_metadata['musicbrainz_release_id'] = []
                        mb_metadata['albumartist'].append(release.getArtist().getName())
                        mb_metadata['musicbrainz_albumartist_id'].append(release.getArtist().getId()[release.getArtist().getId().rfind('/') + 1:])

            except WebServiceError, e:
                print 'Error:', e

            # TODO: match track id with files in database to check for duplicates

            # just pick first found track for now, we'll probably need to handle this somehow
            break

        if 'musicbrainz_track_id' not in mb_metadata:
            print 'Track not found in MusicBrainz database'

        print 'Decoding to wav'
        print '--------------------------------------------------------------------------------'
        if not os.path.exists(basename):
            os.mkdir(basename)
        delete_tmp_dir = True
        subprocess.call(decode_command)

        print 'Applying ReplayGain'
        print '--------------------------------------------------------------------------------'
        subprocess.call(['sox', wavefile, '-b', '16', soxfile]) # convert to 16bit (wavegain bugs out on 24bit)
        shutil.move(soxfile, wavefile)
        shutil.copy(wavefile, wavefile_norm)
        subprocess.call(['wavegain', '-y', wavefile_norm])

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
        delete_tmp_dir = False

        # update database
        cursor = db.cursor()
        cursor.execute("insert into track(track_id, member_id, original_format, duration, fingerprint) values (%s, %s, %s, %s, %s)", (track_id, member_id, original_format, acoustid_duration, acoustid_fingerprint))
        if 'musicbrainz_track_id' in mb_metadata:
            for field, values in mb_metadata.iteritems():
                cursor.execute("insert into metadata(track_id, field, values) values (%s, %s, %s)", (track_id, field, values))
        else:
            if 'artist' in file_metadata:
                cursor.execute("insert into metadata(track_id, field, values) values (%s, %s, %s)", (track_id, 'artist', file_metadata['artist']))
            if 'title' in file_metadata:
                cursor.execute("insert into metadata(track_id, field, values) values (%s, %s, %s)", (track_id, 'title', file_metadata['title']))
            if 'album' in file_metadata:
                cursor.execute("insert into metadata(track_id, field, values) values (%s, %s, %s)", (track_id, 'album', file_metadata['album']))
            if 'tracknumber' in file_metadata:
                cursor.execute("insert into metadata(track_id, field, values) values (%s, %s, %s)", (track_id, 'tracknumber', file_metadata['tracknumber']))
        db.commit()
        cursor.close()

        # delete original file
        #os.remove(filename)
    except:
        raise
        e = sys.exc_info()[0]
        print "Error:", e
        if delete_tmp_dir:
            shutil.rmtree(basename)

db.close()
