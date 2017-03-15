import os
import subprocess
import requests
import taskcluster


def get_github_commit(mercurial_commit):
    r = requests.get("https://api.pub.build.mozilla.org/mapper/gecko-dev/rev/hg/" + mercurial_commit)

    return r.text.split(" ")[0]


if not os.path.isdir("gecko-dev"):
    subprocess.call(["git", "clone", "https://github.com/mozilla/gecko-dev.git"])

os.chdir("gecko-dev")

subprocess.call(["git", "pull"])

task_id = taskcluster.get_last_task()
task_data = taskcluster.get_task_details(task_id)
revision = task_data["payload"]["env"]["GECKO_HEAD_REV"]
git_commit = get_github_commit(revision)

subprocess.call(["git", "checkout", git_commit])
subprocess.call(["genhtml", "-o", "../report", "--show-details", "--highlight", "--ignore-errors", "source", "--legend", "../output.info", "--prefix", os.getcwd()])
subprocess.call(["git", "checkout", "master"])
