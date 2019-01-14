import sys
import os
import io
import re
from argparse import ArgumentParser

import XmlUnpacker
import unzip

DEFAULT_WOT_DIR = '/c/Games/World_of_Tanks'


class WotXmlTree(object):

    def __init__(self, path):
        self.root = XmlUnpacker.getElementTree(path, True)

    def getElementAll(self, tag):
        elemList = self.root.findall('.//{}'.format(tag))
        return elemList

    def hasElement(self, tag):
        elemList = self.root.findall('.//{}'.format(tag))
        return len(elemList)

    def removeTagAll(self, tag):
        count = 0
        for parent in self.root.findall('.//{}/..'.format(tag)):
            for elem in parent.iterfind(tag):
                parent.remove(elem)
                count = count + 1
        return count

    def output(self, file):
        XmlUnpacker.outputElementTree(self.root, file)


def getWotVersion(base_dir=None):
    tree = WotXmlTree(os.path.join(base_dir or '', 'version.xml'))
    string = tree.getElementAll('version')[0].text
    match = re.match(r'\s*(v\.([\d.]+)\s+#([\d]+))\s*', string)
    version = {
        'string':   match.group(1),
        'version':  match.group(2),
        'build':    match.group(3)
    }
    return version


def fetchXmlData(file, base_dir=None, package=None):
    if package:
        zip = unzip.ZipPackage(os.path.join(base_dir, 'res/packages', package), mode='r')
        data = zip.read(file)
    else:
        with open(file, 'rb') as fp:
            data = fp.read() 
    xmlunpacker = XmlUnpacker.XmlUnpacker()
    tree = xmlunpacker.read(io.BytesIO(data), os.path.basename(file))
    if xmlunpacker.isPacked():
        text = XmlUnpacker.pretty_xml(tree)
    else:
        text = data
    return { 'data': tree, 'text': text }


def listPackageFile(package, base_dir=None):
    zip = unzip.ZipPackage(os.path.join(base_dir, 'res/packages', package), mode='r')
    return zip.namelist()


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('command', choices=['version', 'xml', 'list'])
    argparser.add_argument('-b', metavar='basedir', dest='base_dir', help='wot directory', default=DEFAULT_WOT_DIR)
    argparser.add_argument('-p', metavar='package', dest='package', help='package file')
    argparser.add_argument('file')
    settings = argparser.parse_args()

    if settings.command == 'version':
        print getWotVersion(base_dir=settings.base_dir)
    elif settings.command == 'xml':
        result = fetchXmlData(settings.file, base_dir=settings.base_dir, package=settings.package)
        print result['text']
    elif settings.command == 'list':
        for name in listPackageFile(settings.file, base_dir=settings.base_dir):
            print name
