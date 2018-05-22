
import os
import commands
import re
from datetime import *


def getFileList():
    return commands.getoutput('git ls-files -z').split('\0')[:-1]

def getGitCommitLogs():
    return commands.getoutput('git log -r --name-only --no-color --pretty=raw -z').split('\0\0')

def getChangeFiles():
    result = commands.getoutput('git diff --ignore-cr-at-eol --numstat').split('\n')
    result = filter(lambda s: not re.match(r'0\t0\t.*$', s), result)
    result = map(lambda s: s.split('\t')[2], result)
    return result

class CommitTime(object):

    def __init__(self):
        filelist = getFileList()
        logs = getGitCommitLogs()
        changefiles = getChangeFiles()
        self.__timestamp = {}
        self.setCommitTime(logs, filelist)
        self.setChangeTime(changefiles)
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

    def setChangeTime(self, files):
        for f in files:
            mtime = int(os.stat(f).st_mtime)
            self.__timestamp[f] = mtime
 
    def getTimestamp(self, file):
        return self.__timestamp.get(file, int(os.stat(file).st_mtime))

    def setTimestamp(self, file, timestamp):
        self.__timestamp[file] = int(timestamp)

    def dump(self):
        for k, v in self.__timestamp.items():
            print '{} {}'.format(datetime.fromtimestamp(v), k)

if __name__ == "__main__":
    ct = CommitTime()
    ct.dump()
