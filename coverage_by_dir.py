import os
import json
import re
import fnmatch
import requests

from libmozdata import hgmozilla


MAX_LEVEL = 3


def load_changesets(rev1, rev2):
    bug_pattern = re.compile('[\t ]*[Bb][Uu][Gg][\t ]*([0-9]+)')

    r = requests.get('https://hg.mozilla.org/mozilla-central/json-pushes?full&fromchange=' + rev1 + '&tochange=' + rev2)
    pushes = r.json()

    changesets = []

    for pushid, info in pushes.items():
        for changeset in info['changesets']:
            bug_id_match = re.search(bug_pattern, changeset['desc'])
            if not bug_id_match:
                continue

            bug_id = int(bug_id_match.group(1))

            changesets.append((bug_id, changeset['files']))

    return changesets


def get_related_bugs(changesets, directory):
    return [bug for bug, paths in changesets if any(fnmatch.fnmatch(path, directory + '/*') for path in paths)]


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
    changesets = load_changesets('01748a2b1a463f24efd9cd8abad9ccfd76b037b8', 'a551f534773cf2d6933f78ce7d82a7a33a99643e')

    directories = get_directories(rootDir, rootDir)

    data = dict()

    for directory in directories:
        d = get_coverage(directory)

        if d['selected_source_files_count'] == 0:
            continue

        data[directory] = {}
        data[directory]['cur'] = d['paths_covered_percent']
        data[directory]['prev'] = d['paths_previous_covered_percent']
        data[directory]['bugs'] = get_related_bugs(changesets, directory)

    with open('coverage_by_dir.json', 'w') as f:
        json.dump(data, f)
