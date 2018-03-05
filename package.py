import os
import re
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
            'python':       self.__feature_compile,
            'apply':        self.__feature_apply
        }
        self.__getFilename = {
            'python':       self.__getFilename_compile,
            'apply':        self.__getFilename_apply
        }

    def command(self, recipe):
        file = recipe.file
        for method in recipe.method.split('+'):
            if method != 'plain':
                file = self.__feature[method](file, recipe)
        return file

    def getFilename(self, method, file):
        for m in method.split('+'):
            if m != 'plain':
                file = self.__getFilename[m](file)
        return file


    def __getFilename_compile(self, src):
        srcdir, srcfile = os.path.split(src)
        dstdir = os.path.join(BUILD_DIR, srcdir)
        name, ext = os.path.splitext(srcfile)
        return os.path.join(dstdir, name + '.pyc')

    def __getFilename_apply(self, src):
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
        return dst

    def __feature_compile(self, src, recipe):
        dst = self.__getFilename_compile(src)
        makedirs(os.path.dirname(dst))
        vfile = os.path.join(recipe.reldir, os.path.basename(src))
        py_compile.compile(file=src, cfile=dst, dfile=vfile, doraise=True)
        return dst

    def __feature_apply(self, src, recipe):
        dst = self.__getFilename_apply(src)
        makedirs(os.path.dirname(dst))
        with open(src, 'r') as in_file, open(dst, 'w') as out_file:
            out_file.write(Template(in_file.read()).substitute(recipe.params))
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

    def list(self):
        for source, target in self.__list:
            print source, target

    def createZipfile(self, pkgname, compression):
        with zipfile.ZipFile(pkgname, 'w', compression=compression) as file:
            for source, target in self.__list:
                file.write(source, target, compression)

                
class Recipe(object):

    def __init__(self, file, reldir, target, params):
        self.file = file
        self.reldir = reldir
        self.method = target['method']
        self.root = target.get('root', '')
        self.params = params
        self.cooked = Process().getFilename(self.method, self.file) 
 

def parsePackage(target, params):
    list = []
    for file in target.get('source', []):
        desc = Recipe(file, target.get('reldir', ''), target, params)
        list.append(desc) 
    for dir in target.get('srcdir', []):
        for root, dirs, files in os.walk(dir):
            relpath = os.path.relpath(root, dir)
            if relpath == '.':
                relpath = ''
            reldir = os.path.join(target.get('reldir', ''), relpath)
            for file in sorted(files):
                if 'include' in target and not re.search(target['include'], file):
                    continue
                if 'exclude' in target and re.search(target['exclude'], file):
                    continue
                desc = Recipe(os.path.join(root, file), reldir, target, params)
                list.append(desc) 
    return list


def makePackage(jsonfile, params, compression=zipfile.ZIP_STORED):
    with open(jsonfile, 'r') as f:
        desc = json.loads(Template(f.read()).substitute(params))
    package = Package()
    list = []
    for target in desc['files']:
        list.extend(parsePackage(target, params))
    process = Process()
    for recipe in list:
        file = process.command(recipe)
        release = os.path.join(recipe.root, recipe.reldir, os.path.basename(file))
        package.add(file, release)
        # print '{}: {} -> {}'.format(recipe.method, recipe.file, recipe.cooked)
    pkgname = os.path.join(BUILD_DIR, desc['package'])
    package.createZipfile(pkgname, compression)       
    return pkgname


def main():
    params = get_config()
    try:
        shutil.rmtree(BUILD_DIR)
    except:
        pass
    os.makedirs(BUILD_DIR)

    file = makePackage(params['wotmod_files'], params)
    print 'create package: {}'.format(file)

    if 'release_files' in params and os.path.exists(params['release_files']):
        file = makePackage(params['release_files'], params, compression=zipfile.ZIP_DEFLATED)
        print 'create package: {}'.format(file)


if __name__ == "__main__":
    main()
