import os
import shutil
import py_compile
import zipfile
import ConfigParser
import json
from string import Template

BUILD_DIR = 'build'
CONFIG = 'config.ini'

def get_config():
    inifile = ConfigParser.SafeConfigParser()
    inifile.read(CONFIG)

    parameters = dict(inifile.items('wotmod'))
    for section in inifile.sections():
        for k, v in inifile.items(section):
            parameters[section + '_' + k] = v
    return parameters


def makedirs(dir):
    try:
        os.makedirs(dir)
    except:
        pass


class Process(object):

    def __init__(self):
        self.__feature = {
            'apply+python': self.__apply_python,
            'python':       self.__python,
            'apply':        self.__apply,
            'plain':        self.__plain
        }

    def command(self, cmd, file, reldir, params):
        return self.__feature[cmd](file, reldir, params)

    def __apply_python(self, file, reldir, params):
        file = self.__apply(file, reldir, params)
        file = self.__python(file, reldir, params)
        return file

    def __python(self, file, reldir, params):
        file = self.feature_compile(file, reldir)
        return file

    def __apply(self, file, reldir, params):
        file = self.feature_apply(file, params)
        return file
    
    def __plain(self, file, reldir, params):
        return file

    def feature_compile(self, src, reldir):
        srcdir, srcfile = os.path.split(src)
        dstdir = os.path.join(BUILD_DIR, srcdir)
        name, ext = os.path.splitext(src)
        dst = os.path.join(dstdir, name + '.pyc')
        makedirs(os.path.dirname(dst))
        vfile = os.path.join(reldir, os.path.basename(src))
        py_compile.compile(file=src, cfile=dst, dfile=vfile, doraise=True)
        return dst

    def feature_apply(self, src, params):
        srcdir, srcfile = os.path.split(src)
        dstdir = os.path.join(BUILD_DIR, srcdir)
        name, ext = os.path.splitext(srcfile)
        if ext == '' or ext == '.in':
            dst = os.path.join(dstdir, name)
        else:
            inname, inext = os.path.splitext(name)
        if inext == '.in':
            dst = os.path.join(dstdir, inname + ext)
        else:
            dst = os.path.join(dstdir, name + ext)
        makedirs(os.path.dirname(dst))
        with open(src, 'r') as in_file, open(dst, 'w') as out_file:
            out_file.write(Template(in_file.read()).substitute(params))
        return dst


class Package(object):

    def __init__(self):
        self.__dirs = {}
        self.__list = []

    def __split(self, path):
        head, tail = os.path.split(path)
        if not head:
            return [ tail ]
        result = self.__split(head)
        result.append(path)
        return result
    
    def add(self, src, dst):
        for dir in self.__split(dst)[0:-1]:
            if dir not in self.__dirs:
                self.__dirs[dir] = True
                self.__list.append([ '.', dir ])
        self.__list.append([src, dst])

    def createZipfile(self, pkgname, compression):
        with zipfile.ZipFile(pkgname, 'w', compression=compression) as file:
            for source, target in self.__list:
                file.write(source, target, compression)


def makePackage(jsonfile, params, compression=zipfile.ZIP_STORED):
    with open(jsonfile, 'r') as f:
        desc = json.loads(Template(f.read()).substitute(params))
    package = Package()
    process = Process()
    for target in desc['files']:
        for file in target['source']:
            file = process.command(target['method'], file, target['reldir'], params)
            release = os.path.join(target['root'], target['reldir'], os.path.basename(file))
            package.add(file, release)
    pkgname = os.path.join(BUILD_DIR, desc['package'])
    package.createZipfile(pkgname, compression)


def main():
    params = get_config()
    try:
        shutil.rmtree(BUILD_DIR)
    except:
        pass
    os.makedirs(BUILD_DIR)

    makePackage(params['wotmod_files'], params)

    if 'release_files' in params and os.path.exists(params['release_files']):
        makePackage(params['release_files'], params, compression=zipfile.ZIP_DEFLATED)


if __name__ == "__main__":
    main()
