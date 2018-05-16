
import os
import commands
import re
from datetime import *


def getFileList():
    return commands.getoutput('git ls-files -z').split('\0')[:-1]

def getGitCommitLogs():
    return commands.getoutput('git log -m -r --name-only --no-color --pretty=raw -z').split('\0\0')


class CommitTime(object):

    def __init__(self):
        filelist = getFileList()
        logs = getGitCommitLogs()
        self.__timestamp = {}
        self.setCommitTime(logs, filelist)
        self.lastupdate = max(self.__timestamp.values())

    def __getCommitTime(self, log):
        lines = log.split('\n')
        timestamp = None
        for s in lines:
            match = re.match(r'^committer .*? (\d+) (?:[\-+]\d+)$', s)
            if match:
                timestamp = int(match.group(1))
                break
        files = lines[-1].split('\0')
        return (timestamp, files)

    def setCommitTime(self, logs, filelist):
        for log in logs:
            (timestamp, files) = self.__getCommitTime(log)
            for f in files:
                if f in filelist:
                    self.__timestamp[f] = timestamp
                    filelist.remove(f)
                    if len(filelist) == 0:
                        return

    def getTimestamp(self, file):
        return self.__timestamp.get(file, None)

