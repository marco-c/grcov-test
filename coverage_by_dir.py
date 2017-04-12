import os
import json
import requests


def get_coverage(directory):
    r = requests.get('https://coveralls.io/jobs/24715266.json?paths=' + directory + '/*')
    return r.json()


rootDir = os.path.expanduser('~/Documenti/FD/mozilla-central')
maxLevel = 2
def get_directories(directory, curLevel=0):
    if curLevel == maxLevel or '.hg' in directory:
        return []

    dirs = [os.path.relpath(os.path.join(directory, d), rootDir) for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]

    subdirs = []
    for d in dirs:
        subdirs += get_directories(os.path.join(rootDir, d), curLevel + 1)

    return dirs + subdirs


def generate_data():
    directories = get_directories(rootDir)

    data = dict()

    for directory in directories:
        d = get_coverage(directory)

        if d['selected_source_files_count'] == 0:
            continue

        data[directory] = {}
        data[directory]['cur'] = d['paths_covered_percent']
        data[directory]['prev'] = d['paths_previous_covered_percent']

    with open('coverage-by-dir.json', 'w') as f:
        json.dump(data, f)
