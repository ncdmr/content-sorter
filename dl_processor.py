#!/usr/bin/env python3

import os
import re
import shutil
import sys
from pprint import pprint
import logging

root_folder = '/volumes/Downloads'
source_folder = root_folder + '/incoming'
skip_folders = ['.DS_Store', ]

def fetch_incoming():
    l_candidates = []
    for candidate in os.listdir(source_folder):
        if candidate in skip_folders:
            continue
        l_candidates.append(candidate)
    return l_candidates
        
def check_mount():
    if not os.path.exists(root_folder):
        # logger.error(f'folder {root_folder} not found.')    
        print(f'Folder {root_folder} not found.  Try mounting it.')
        sys.exit()
    l_dirs = os.listdir(root_folder)
    if not 'Series' in l_dirs or not 'Films' in l_dirs:
        print(f"Something wrong with the {root_folder}'s content.  Expected 'Series', 'Books' and 'Films', but none were found.")
        sys.exit()

def process_candidates(l_candidates):
    for candidate in l_candidates:
        # logger.info(f'Processing {candidate}')
        print(f'Processing "{candidate}"')
        for file in os.listdir(f'{source_folder}/{candidate}'):
            if re.search(r'[sS]\d{1,2}[eE]\d{1,2}', file) and (file.endswith('.mkv') or file.endswith('.mp4') or file.endswith('.avi')):
                file_name, file_extension = os.path.splitext(file)
                new_file_name = file_name.replace('.', ' ') + file_extension
                os.rename(f'{source_folder}/{candidate}/{file}', f'{source_folder}/{candidate}/{new_file_name}')
                file = re.sub(r'.', '\s', file)
                wb = {}
                params = re.match(r'(?P<show>[a-zA-Z0-9\.\s]*)[sS](?P<season>\d{1,2})[eE](?P<episode>\d{1,2})',l)
                wb = params.groupdict()

def main():
    check_mount()
    l_candidates = fetch_incoming()
    process_candidates(l_candidates)

def telegram_report():
    import telepot

if __name__ == '__main__':
    logger = logging.basicConfig()
    main()