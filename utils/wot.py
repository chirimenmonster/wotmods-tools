import sys
import os
import io
import re
from argparse import ArgumentParser
from xml.etree.ElementTree import ElementTree

import XmlUnpacker
import unzip


class WotXmlTree(ElementTree):

    def __init__(self, data=None, path=None, rootName=None):
        xmlunpacker = XmlUnpacker.XmlUnpacker()
        if data:
            root = xmlunpacker.read(io.BytesIO(data), rootName)
        elif path:
            with open(path, 'rb') as fp:
                data = fp.read()
            root = xmlunpacker.read(io.BytesIO(data), os.path.basename(path))
        else:
            root = None
        super(WotXmlTree, self).__init__(root)
        self.__data = data
        self.__isPacked = xmlunpacker.isPacked()

    def getElementAll(self, tag):
        elemList = self.findall('.//{}'.format(tag))
        return elemList

    def hasElement(self, tag):
        elemList = self.findall('.//{}'.format(tag))
        return len(elemList)

    def removeTagAll(self, tag):
        count = 0
        for parent in self.findall('.//{}/..'.format(tag)):
            for elem in parent.iterfind(tag):
                parent.remove(elem)
                count = count + 1
        return count

    def output(self, file=None):
        if self.isPacked():
            data = XmlUnpacker.pretty_xml(self.getroot())
        else:
            data = self.__data
        if file:
            dstdir = os.path.dirname(file)
            if not os.path.exists(dstdir):
                os.makedirs(dstdir)
            with open(file, 'w') as fp:
                fp.write(data)
        else:
            sys.stdout.write(data)

    def isPacked(self):
        return self.__isPacked


def getWotVersion(base_dir=None):
    path = os.path.join(base_dir or '', 'version.xml')
    tree = WotXmlTree(path=path)
    string = tree.getElementAll('version')[0].text
    match = re.match(r'\s*(v\.([\d.]+[^#]*)\s+#([\d]+))\s*', string)
    version = {
        'string':   match.group(1),
        'version':  match.group(2),
        'build':    match.group(3)
    }
    return version



def guessFilePath(name, base_dir=None):
    if os.path.isfile(name):
        return name
    _, ext = os.path.splitext(name)
    if ext == '.pkg':
        path = os.path.join(base_dir, 'res/packages', name)
        if os.path.isfile(path):
            return path
    path = os.path.join(base_dir, name)
    if os.path.isfile(path):
        return path
    path = os.path.join(base_dir, 'res', name)
    if os.path.isfile(path):
        return path
    return None


def fetchXmlData(file, base_dir=None, package=None):
    if package:
        _, ext = os.path.splitext(package)
        if ext == '.wotmod':
            target = package
        elif ext == '.pkg':
            if os.path.isfile(package):
                tatrget = package
            else:
                target = os.path.join(base_dir, 'res/packages', package)
        else:
            target = package
        zip = unzip.ZipPackage(target, mode='r')
        data = zip.read(file)
    else:
        if os.path.isfile(file):
            target = file
        elif os.path.isfile(os.path.join(base_dir, file)):
            target = os.path.join(base_dir, file)
        elif os.path.isfile(os.path.join(base_dir, 'res', file)):
            target = os.path.join(base_dir, 'res', file)
        else:
            target = file
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

