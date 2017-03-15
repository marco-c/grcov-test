import os
import subprocess
import time


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
cmd.extend(ordered_files[:14])
proc = subprocess.Popen(cmd, stdout=fout, stderr=ferr)
i = 0
while proc.poll() is None:
    print('Running grcov... ' + str(i))
    i += 1
    time.sleep(60)
