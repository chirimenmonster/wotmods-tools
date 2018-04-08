
import os
import commands
import re
from datetime import *

files = None
commitTimeDict = {}

def getFileList():
    return commands.getoutput('git ls-files -z').split('\0')[:-1]

def getGitCommitLogs():
    return commands.getoutput('git log -m -r --name-only --no-color --pretty=raw -z').split('\0\0')

def setCommitTime(log):
    lines = log.split('\n')
    timestamp = None
    for s in lines:
        match = re.match(r'^committer .*? (\d+) (?:[\-+]\d+)$', s)
        if match:
            timestamp = match.group(1)
            break
    for f in lines[-1].split('\0'):
        if f in files:
            commitTimeDict[f] = int(timestamp)
            files.remove(f)

def getCommitTimeDict():
    global files
    files = getFileList()
    logs = getGitCommitLogs()
    for log in logs:
        setCommitTime(log)
        if len(files) == 0:
            break
    return commitTimeDict
