import glob
import os
import psycopg2
import shutil
import subprocess

from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis

#db = psycopg2.connect('host='localhost' dbname='imp' user='imp' password='imp'')

for filename in glob.glob('music/*/upload/*.*'):
    print ''
    print filename
    basename = filename[:filename.rfind('.')]
    print '--------------------------------------------------------------------------------'
    print 'Decoding'
    print '--------------------------------------------------------------------------------'
    # TODO: fetch metadata (artist, title, etc)
    maxbitrate = 999999999
    if filename.endswith('.flac'):
        audio = FLAC(filename)
        subprocess.call(['flac', '--decode', '-f', filename])
    elif filename.endswith('.ogg'):
        audio = OggVorbis(filename)
        maxbitrate = audio.info.bitrate
        subprocess.call(['oggdec', filename])
    elif filename.endswith('.mp3'):
        audio = MP3(filename)
        maxbitrate = audio.info.bitrate
        subprocess.call(['lame', '--decode', filename])
    else:
        print "don't know to handle this file"
        continue

    print '--------------------------------------------------------------------------------'
    print 'Normalizing'
    print '--------------------------------------------------------------------------------'
    # TODO: replaygain and normalize end up with different values. why?
    wavefile = basename + '.wav'
    wavefile_norm = basename + '-n.wav'
    shutil.copy(wavefile, wavefile_norm)
    subprocess.call(['normalize', wavefile_norm])

    try:
        os.mkdir(basename)
    except OSError:
        print "TODO"

    # TODO: no point creating copies with higher bitrate than original

    print '--------------------------------------------------------------------------------'
    print 'Encoding Ogg Vorbis'
    print '--------------------------------------------------------------------------------'
    subprocess.call(['oggenc', '-q', '9', '-o', os.path.join(basename, '2.ogg'), wavefile])
    subprocess.call(['oggenc', '-q', '9', '-o', os.path.join(basename, '2-n.ogg'), wavefile_norm])
    subprocess.call(['oggenc', '-q', '5', '-o', os.path.join(basename, '3.ogg'), wavefile])
    subprocess.call(['oggenc', '-q', '5', '-o', os.path.join(basename, '3-n.ogg'), wavefile_norm])
    subprocess.call(['oggenc', '-q', '1', '-o', os.path.join(basename, '4.ogg'), wavefile])
    subprocess.call(['oggenc', '-q', '1', '-o', os.path.join(basename, '4-n.ogg'), wavefile_norm])

    print '--------------------------------------------------------------------------------'
    print 'Encoding Lame MP3'
    print '--------------------------------------------------------------------------------'
    subprocess.call(['lame', '-V', '0', wavefile, os.path.join(basename, '2.mp3')])
    subprocess.call(['lame', '-V', '0', wavefile_norm, os.path.join(basename, '2-n.mp3')])
    subprocess.call(['lame', '-V', '4', wavefile, os.path.join(basename, '3.mp3')])
    subprocess.call(['lame', '-V', '4', wavefile_norm, os.path.join(basename, '3-n.mp3')])
    subprocess.call(['lame', '-V', '8', wavefile, os.path.join(basename, '4.mp3')])
    subprocess.call(['lame', '-V', '8', wavefile_norm, os.path.join(basename, '4-n.mp3')])

    # delete temporary wave files
    os.remove(wavefile)
    os.remove(wavefile_norm)

    # move original file (TODO: currently only copying for debugging purposes, just s/copy/move/ to fix)
    shutil.copy(filename, os.path.join(basename, '1' + filename[filename.rfind('.'):].lower()))
