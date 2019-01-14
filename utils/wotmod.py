from argparse import ArgumentParser
import zipfile
from datetime import datetime
import os

import path as pathtool

def _splitpath(path):
    head, tail = os.path.split(path)
    if not head:
        return [ tail ]
    return _splitpath(head) + [ tail ]


class WotmodPackage(object):

    def __init__(self):
        self.__dirs = {}
        self.__list = []

    def add(self, src, dst, timestamp=None):
        if not timestamp:
            timestamp = os.stat(src).st_mtime
        path = ''
        for dir in _splitpath(dst)[0:-1]:
            path = os.path.join(path, dir)
            if path not in self.__dirs:
                self.__dirs[path] = True
                self.__list.append([ None, path + '/', timestamp ])
            else:
                for i, d in enumerate(self.__list):
                    if path + '/' == d[1]:
                        self.__list[i][2] = max(d[2], timestamp)
        self.__list.append([src, dst, timestamp])

    def list(self):
        for source, target, timestamp in self.__list:
            print source, target, timestamp

    def create(self, pkgname, compression):
        with zipfile.ZipFile(pkgname, 'w', compression=compression) as file:
            for source, target, timestamp in self.__list:
                t = datetime.fromtimestamp(timestamp)
                zipinfo = zipfile.ZipInfo(target, t.timetuple())
                if source:
                    with open(source, 'rb') as f:
                        file.writestr(zipinfo, f.read(), compression)
                else:
                    file.writestr(zipinfo, '', zipfile.ZIP_STORED)
        timestamp = max([ d[2] for d in self.__list ])
        return timestamp


def createSimplePackage(filename, base_dir='', dest_dir=''):
    wotmod = WotmodPackage()
    for path in pathtool.getFileList([''], base_dir):
        src = os.path.join(base_dir, path)
        dst = os.path.join(dest_dir, path)
        wotmod.add(src, dst)
    wotmod.create(filename, zipfile.ZIP_STORED)


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('-b', metavar='basedir', dest='base_dir', help='source base directory')
    argparser.add_argument('-d', metavar='destdir', dest='dest_dir', help='destination base directory')
    argparser.add_argument('zipfile')
    settings = argparser.parse_args()

    createSimplePackage(settings.zipfile, base_dir=settings.base_dir, dest_dir=settings.dest_dir)