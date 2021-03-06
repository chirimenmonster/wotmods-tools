import sys
import os
import io
import re
from argparse import ArgumentParser
from xml.etree.ElementTree import ElementTree

import XmlUnpacker
import unzip
from exceptions import ApplicationError


class VPath(object):

    def __init__(self, baseDir=None, packageName=None):
        self.open(baseDir=baseDir, packageName=packageName)

    def open(self, baseDir=None, packageName=None):
        self.baseDir = baseDir
        if packageName:
            pkgPath = guessFilePath(packageName, base_dir=self.baseDir)
            if pkgPath is None:
                raise Exception('package is not found: {}'.format(packageName))
            try:
                self.zip = unzip.ZipPackage(pkgPath, mode='r')
            except:
                raise Exception('cannot open package: {}'.format(pkgPath))
        else:
            self.zip = None
    
    def readFile(self, file):
        if self.zip:
            return self.zip.read(file)
        path = guessFilePath(file, base_dir=self.baseDir)
        with open(path, 'rb') as fp:
            data = fp.read() 
        return data
    
    def listPattern(self, pattern=None):
        if self.zip:
            return self.zip.list_pattern(pattern)
        return None
        

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
    path = guessFilePath('version.xml', base_dir=base_dir)
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
    if base_dir is not None and not os.path.isdir(base_dir):
        raise IOError('base dir is not found: \'{}\''.format(base_dir))
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


def pickXmlElement(element, xpath=None):
    if xpath:
        return element.findall(xpath)
    return [ element ]


def fetchXmlList(base_dir=None, package=None, pattern=None, xpath=None, file=None, root=None):
    vpath = VPath(baseDir=base_dir, packageName=package)
    result = []
    if pattern:
        files = vpath.listPattern(pattern=pattern)
    elif file:
        files = [ file ]
    else:
        raise ApplicationError('require file or pattern')
    for f in files:
        data = vpath.readFile(f)
        xmlunpacker = XmlUnpacker.XmlUnpacker()
        rootName = os.path.basename(f) if root is None else root
        tree = xmlunpacker.read(io.BytesIO(data), rootName)
        list = [ (f, e) for e in pickXmlElement(tree, xpath) ]
        result.extend(list)
    return result
