import taskcluster


task_id = taskcluster.get_last_task()
task_data = taskcluster.get_task_details(task_id)
revision = task_data["payload"]["env"]["GECKO_HEAD_REV"]

artifacts = taskcluster.get_task_artifacts(task_id)
for artifact in artifacts:
    if 'target.code-coverage-gcno.zip' in artifact['name']:
        taskcluster.get_artifact(task_id, artifact)

test_tasks = [t for t in taskcluster.get_tasks_in_group(task_data['taskGroupId']) if t['task']['metadata']['name'].startswith('test-linux64-ccov')]
for test_task in test_tasks:
    artifacts = taskcluster.get_task_artifacts(test_task['status']['taskId'])
    for artifact in artifacts:
        if 'code-coverage-gcda.zip' in artifact['name']:
            taskcluster.get_artifact(test_task['status']['taskId'], artifact)
