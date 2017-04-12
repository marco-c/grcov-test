import os
import json
import requests


MAX_LEVEL = 2


def get_coverage(directory):
    r = requests.get('https://coveralls.io/jobs/24715266.json?paths=' + directory + '/*')
    return r.json()


def get_directories(directory, rootDir, curLevel=0):
    if curLevel == MAX_LEVEL or '.hg' in directory:
        return []

    dirs = [os.path.relpath(os.path.join(directory, d), rootDir) for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]

    subdirs = []
    for d in dirs:
        subdirs += get_directories(os.path.join(rootDir, d), rootDir, curLevel + 1)

    return dirs + subdirs


def generate_data(rootDir):
    directories = get_directories(rootDir, rootDir)

    data = dict()

    for directory in directories:
        d = get_coverage(directory)

        if d['selected_source_files_count'] == 0:
            continue

        data[directory] = {}
        data[directory]['cur'] = d['paths_covered_percent']
        data[directory]['prev'] = d['paths_previous_covered_percent']

    with open('coverage_by_dir.json', 'w') as f:
        json.dump(data, f)
