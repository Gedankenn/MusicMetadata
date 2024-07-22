#!/usr/bin/env python
'''
This script is used to get and set metadata of mp3 files and verify if the mp3 files are valid.
It uses the eyed3 library to get and set metadata of mp3 files.
It uses the ffmpeg library to verify if the mp3 files are valid.
If the mp3 files are not valid, it converts them to valid mp3 files.

Usage:
python mmdata.py <mp3_file> <option> <value>
Options:
1. get_mp3_info
2. set_mp3_info
3. verify_files
Example:
python mmdata.py test.mp3 get_mp3_info
python mmdata.py test.mp3 set_mp3_info "Test Title" "Test Artist" "Test Album" 1
python mmdata.py verify_files /home/user/music

Author: Fabio Slika Stella
Date: 15/07/2024
Version: 1.0

'''

import sys
import eyed3 as ed
import ffmpeg
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

CLIENT_ID = 'a410478f90754145ad7d91537f1b9537'
CLIENT_SECRET = '2c0884b4a1444c5c808dd9fc78d52df2'

bcolors = {
    'HEADER': '\033[95m',
    'OKBLUE': '\033[94m',
    'OKGREEN': '\033[92m',
    'WARNING': '\033[93m',
    'FAIL': '\033[91m',
    'ENDC': '\033[0m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m'
}

def get_mp3_info(mp3_file):
    try:
        audiofile = ed.load(mp3_file)
        print(f"{bcolors['OKGREEN']}Title: ", audiofile.tag.title)
        print("Artist: ", audiofile.tag.artist)
        print("Album: ", audiofile.tag.album)
        print("Track Number: ", audiofile.tag.track_num[0])
        print(f"{bcolors['ENDC']}")
    except Exception as e:
        print('Error: ', str(e))

def set_mp3_info(mp3_file, title, artist, album, track_num):
    try:
        audiofile = ed.load(mp3_file)
        audiofile.tag.title = title
        audiofile.tag.artist = artist
        audiofile.tag.album = album
        audiofile.tag.track_num = track_num
        audiofile.tag.save()
        print(f"{bcolors['OKGREEN']}"+mp3_file, ' metadata updated successfully'+f"{bcolors['ENDC']}")
    except Exception as e:
        print('Error: ', str(e))

def convert_mp3(file):
    try:
        input_file = ffmpeg.input(file)
        output_file = file.replace('.mp3', '_converted.mp3')
        ffmpeg.output(input_file, output_file).run()
        print(f"{bcolors['OKGREEN']}"+file, ' converted successfully'+f"{bcolors['ENDC']}")
        os.remove(file)
        os.rename(output_file, file)
    except Exception as e:
        print('Error: ', str(e))

def verify_files_dir_func(dir):
    try:
        files = os.listdir(dir)
        for file in files:
            #run ffprobe on file to verify if it is a valid mp3 file
            print('Verifying file: ', file)
            try:
                probe = ffmpeg.probe(dir+'/'+file)
                if probe['streams'][0]['codec_type'] == 'audio' and probe['streams'][0]['codec_name'] == 'mp3':
                    print(f"{bcolors['OKGREEN']}"+file, ' is a valid mp3 file'+f"{bcolors['ENDC']}")
                else:
                    print(f"{bcolors['FAIL']}"+file, ' is not a valid mp3 file'+f"{bcolors['ENDC']}")
                    convert_mp3(dir+'/'+file)
            except Exception as e:
                print('Error: ', str(e))

    except Exception as e:
        print('Error: ', str(e))

def verify_files_file_func(file):
    try:
        #run ffprobe on file to verify if it is a valid mp3 file
        print('Verifying file: ', file)
        try:
            probe = ffmpeg.probe(file)
            if probe['streams'][0]['codec_type'] == 'audio' and probe['streams'][0]['codec_name'] == 'mp3':
                print(f"{bcolors['OKGREEN']}"+file, ' is a valid mp3 file'+f"{bcolors['ENDC']}")
            else:
                print(f"{bcolors['FAIL']}"+file, ' is not a valid mp3 file, converting it'+f"{bcolors['ENDC']}")
                convert_mp3(file)
        except Exception as e:
            print('Error: ', str(e))
    except Exception as e:
        print('Error: ', str(e))

def verify_files(dir):
    # Verify if dir is a valid directory or a file
    if os.path.isdir(dir):
        verify_files_dir_func(dir)

    elif os.path.isfile(dir):
        verify_files_file_func(dir)

    else:
        print('Invalid directory or file')

def get_song_info(song):
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))
        result = sp.search(song)
        song_info = {}
        if result['tracks']['total'] == 0:
            print('Song not found')
            return
        song_info['title'] = result['tracks']['items'][0]['name']
        song_info['artist'] = result['tracks']['items'][0]['artists'][0]['name']
        song_info['album'] = result['tracks']['items'][0]['album']['name']
        song_info['cover'] = result['tracks']['items'][0]['album']['images'][0]['url']
        song_info['track'] = result['tracks']['items'][0]['track_number']
        return song_info
    except Exception as e:
        print('Error: ', str(e))

def print_song_cover_in_terminal(cover):
    download_dir = '/tmp'
    cover_file = download_dir+'/cover.jpg'
    os.system('wget -O '+cover_file+' '+cover)
    os.system('catimg '+cover_file)
    os.remove(cover_file)

def set_mp3_info_func(argv):
    if len(argv) != 6 and len(argv) != 1:
        print('Usage: python mmdata.py <mp3_file> set_mp3_info <title> <artist> <album> <track_num>')
        print('Example: python mmdata.py test.mp3 set_mp3_info "Test Title" "Test Artist" "Test Album" 1')
        return

    if len(argv) == 1:
        mp3_file = input('Enter mp3 file: ')
        title = input('Enter title: ')
        artist = input('Enter artist: ')
        album = input('Enter album: ')
        track_num = input('Enter track number: ')

    else:
        mp3_file = argv[0]
        title = argv[2]
        artist = argv[3]
        album = argv[4]
        track_num = argv[5]

    set_mp3_info(mp3_file, title, artist, album, track_num)

def verify_files_func(argv):
    if len(argv) != 2:
        print('Usage: python mmdata.py verify_files <dir>')
        print('Example: python mmdata.py verify_files /home/user/music')
        return
    dir = argv[1]
    verify_files(dir)

def get_song_info_func(argv):
    if len(argv) != 2:
        print('Usage: python mmdata.py get_song_info <song>')
        print('Example: python mmdata.py get_song_info "song name"')
        return
    song = argv[0]
    song_info = get_song_info(song)
    if song_info:
        print(f"{bcolors['OKGREEN']}Title: ", song_info['title'])
        print("Artist: ", song_info['artist'])
        print("Album: ", song_info['album'])
        print_song_cover_in_terminal(song_info['cover'])

def print_help():
    print('Usage: python mmdata.py <mp3_file> <option> <value>')
    print('Options:')
    print('1. get_mp3_info')
    print('2. set_mp3_info')
    print('3. verify_files')
    print('4. get_song_info')
    print('Example: python mmdata.py test.mp3 get_mp3_info')


def func_write_song_info_to_file(mp3_file):
    song_info = get_song_info(mp3_file)
    
    if song_info:
        set_mp3_info(mp3_file, song_info['title'], song_info['artist'], song_info['album'], song_info['track'])
    
    else:
        print('Song not found')

def func_wirte_song_info_all_files(dir):
    files = os.listdir(dir)
    for file in files:
        if file.endswith('.mp3'):
            func_write_song_info_to_file(dir+'/'+file)

    else:
        print('Invalid directory')

def main(argv):
    if len(argv) < 2:
        mp3_file = input('Enter mp3 file: ')
        option = input('Enter option: ')

    else:
        mp3_file = argv[0]
        option = argv[1]

    if option == 'get_mp3_info':
        get_mp3_info(mp3_file)

    elif option == 'set_mp3_info':
        set_mp3_info_func(argv)

    elif mp3_file == 'verify_files':
        verify_files_func(argv)

    elif option == 'get_song_info':
        get_song_info_func(argv)

    elif option == 'update_song_info':
        func_write_song_info_to_file(mp3_file)

    elif option == 'update_all':
        func_wirte_song_info_all_files(mp3_file)

    else:
        print_help()

if __name__ == '__main__':
    main(sys.argv[1:])
