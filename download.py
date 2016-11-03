# -*- coding: utf-8 -*-
import os


def check_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def download_file(url, save_to, session):
    '''
        Adapted from http://stackoverflow.com/a/16696317
    '''
    r = session.get(url, stream=True)
    with open(save_to, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def download_files(files, directory, session):
    check_dir(directory)
    for file in files:
        filename = file.split('/')[-1]
        path = os.path.join(directory, filename)
        download_file(file, path, session)
