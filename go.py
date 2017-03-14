import os
import shutil
import subprocess
import requests


def get_last_task():
    r = requests.get('https://index.taskcluster.net/v1/task/gecko.v2.mozilla-central.latest.firefox.linux64-ccov-opt')
    last_task = r.json()
    return last_task['taskId']


def get_task_details(task_id):
    r = requests.get('https://queue.taskcluster.net/v1/task/' + task_id)
    return r.json()


def get_task_artifacts(task_id):
    r = requests.get('https://queue.taskcluster.net/v1/task/' + task_id + '/artifacts')
    return r.json()['artifacts']


def get_tasks_in_group(group_id):
    r = requests.get('https://queue.taskcluster.net/v1/task-group/' + group_id + '/list', params={
        'limit':200
    })
    reply = r.json()
    tasks = reply['tasks']
    while 'continuationToken' in reply:
        r = requests.get('https://queue.taskcluster.net/v1/task-group/' + group_id + '/list', params={
            'limit': 200,
            'continuationToken': reply['continuationToken']
        })
        reply = r.json()
        tasks += reply['tasks']
    return tasks


def get_artifact(task_id, artifact):
    file_name = task_id + '_' + os.path.basename(artifact['name'])
    r = requests.get('https://queue.taskcluster.net/v1/task/' + task_id + '/artifacts/' + artifact['name'], stream=True)
    with open(file_name, 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)
    return file_name


def get_github_commit(mercurial_commit):
    r = requests.get("https://api.pub.build.mozilla.org/mapper/gecko-dev/rev/hg/" + mercurial_commit)

    return r.text.split(" ")[0]



last_task_id = get_last_task()
task_data = get_task_details(last_task_id)
revision = task_data["payload"]["env"]["GECKO_HEAD_REV"]

artifacts = get_task_artifacts(last_task_id)
for artifact in artifacts:
    if 'target.code-coverage-gcno.zip' in artifact['name']:
        get_artifact(last_task_id, artifact)

test_tasks = [t for t in get_tasks_in_group(task_data['taskGroupId']) if t['task']['metadata']['name'].startswith('test-linux64-ccov')]
for test_task in test_tasks:
    artifacts = get_task_artifacts(test_task['status']['taskId'])
    for artifact in artifacts:
        if 'code-coverage-gcda.zip' in artifact['name']:
            get_artifact(test_task['status']['taskId'], artifact)


files = os.listdir(".")
ordered_files = []
for fname in files:
    if not fname.endswith('.zip'):
        continue

    if 'gcno' in fname:
        ordered_files.insert(0, fname)
    else:
        ordered_files.append(fname)

print(len(ordered_files))

fout = open("output.info", 'w')
ferr = open("error", 'w')
cmd = ['grcov', '-z', '-t', 'lcov', '-s', '/home/worker/workspace/build/src/']
cmd.extend(ordered_files)
proc = subprocess.Popen(cmd, stdout=fout, stderr=ferr)
proc.wait()

if not os.path.isdir("gecko-dev"):
    subprocess.call(["git", "clone", "https://github.com/mozilla/gecko-dev.git"])

os.chdir("gecko-dev")

subprocess.call(["git", "pull"])

git_commit = get_github_commit(revision)

subprocess.call(["git", "checkout", git_commit])
subprocess.call(["genhtml", "-o", "../report", "--show-details", "--highlight", "--ignore-errors", "source", "--legend", "../output.info"])
subprocess.call(["git", "checkout", "master"])
