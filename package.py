#! /bin/python2

import sys
import os
import re
import shutil
import py_compile
import zipfile
import ConfigParser
import json
from string import Template
from datetime import datetime
import traceback

import committime

CONFIG = 'config.ini'
DEFAULT_BUILDDIR = 'build'

SECTION_WOTMOD = 'wotmod'
SECTION_RELEASE = 'release'

PKGDEF = {
    SECTION_WOTMOD:     SECTION_WOTMOD + '_pkgdef',
    SECTION_RELEASE:    SECTION_RELEASE + '_pkgdef'
}

PKGNAME = {
    SECTION_WOTMOD:     SECTION_WOTMOD + '_package',
    SECTION_RELEASE:    SECTION_RELEASE + '_package'
}


def makedirs(dir):
    try:
        os.makedirs(dir)
    except:
        pass

def splitpath(path):
    head, tail = os.path.split(path)
    if not head:
        return [ tail ]
    return splitpath(head) + [ tail ]


class Config(object):

    def __init__(self, config=CONFIG):
        inifile = ConfigParser.SafeConfigParser()
        inifile.read(config)
        try:
            self.__params = dict(inifile.items(SECTION_WOTMOD))
        except:
            sys.stderr.write('not found section "{}" in "{}"'.format(SECTION_WOTMOD, config))
            sys.exit(1)
        for section in inifile.sections():
            for k, v in inifile.items(section):
                self.__params[section + '_' + k] = v

    def get(self, name, default=None):
        return self.__params.get(name, default)

    def getDict(self):
        return self.__params

    @property
    def dict(self):
        return self.__params

    @property
    def buildDir(self):
        return self.__params.get('build_dir', DEFAULT_BUILDDIR)


class Control(object):

    def __init__(self, config=CONFIG):
        self.__commitTime = committime.CommitTime()
        self.setConfig(config)
        self.makeBuildDir()
    
    def setConfig(self, config=CONFIG):
        self.__params = Config(config)
        if isinstance(config, list):
            timestamp = max([ self.__commitTime.getTimestamp(f) for f in config ])
        else:
            timestamp = self.__commitTime.getTimestamp(config)
        self.__params.timestamp = timestamp

    def makeBuildDir(self):
        try:
            shutil.rmtree(self.__params.buildDir)
        except:
            pass
        os.makedirs(self.__params.buildDir)

    def makePackage(self, domain=SECTION_WOTMOD, compression=zipfile.ZIP_STORED):
        pkgsrcs = self.__params.get(PKGDEF[domain])
        if not pkgsrcs:
            sys.stderr.write('not def "{}"'.format(PKGDEF[domain]))
            sys.exit(1)
        pkgname = os.path.join(self.__params.buildDir, self.__params.get(PKGNAME[domain]))
        resources = Resources(pkgsrcs, self.__params, self.__commitTime)
        #resources.dump()
        zipPackage = ZipPackage()
        for recipe in resources.getRecipes():
            file, vpath, timestamp = Process().command(recipe)
            zipPackage.add(file, vpath, timestamp)
        timestamp = zipPackage.create(pkgname, compression)
        self.__commitTime.setTimestamp(pkgname, timestamp)
        return pkgname


class Resources(object):

    def __init__(self, filename, params, commitTime):
        self.__commitTime = commitTime
        self.__params = params
        try:
            with open(filename, 'r') as file:
                text = Template(file.read()).substitute(self.__params.dict)
        except Exception as e:
            sys.stderr.write(traceback.format_exc())
            sys.stderr.write('cannot open file: "{}"'.format(filename))
            sys.exit(1)
        self.__resource = json.loads(text)
        self.__recipes = []
        for desc in self.__resource['sources']:
            recipes = self.parse(desc)
            self.__recipes.extend(recipes)

    def get(self, key):
        return self.__params[key]

    def getRecipes(self):
        return self.__recipes

    def dump(self):
        for recipe in self.__recipes:
            print '{}: {}: {} -> {}'.format(datetime.fromtimestamp(recipe.timestamp), recipe.method,
                    recipe.file, recipe.vpath)

    def parse(self, desc):
        recipes = []
        for file in desc.get('files', []):
            reldir = desc.get('reldir', '')
            recipes.append(self.__getRecipe(file, reldir, desc))
        for dir in desc.get('dirs', []):
            recipes.extend(self.__parseSrcDir(desc, dir))
        return recipes

    def __parseSrcDir(self, desc, srcdir):
        recipes = []
        for root, dirs, files in os.walk(srcdir):
            relpath = os.path.relpath(root, srcdir)
            if relpath == '.':
                relpath = ''
            reldir = os.path.join(desc.get('reldir', ''), relpath)
            for file in sorted(files):
                if 'include' in desc and not re.search(desc['include'], file):
                    continue
                if 'exclude' in desc and re.search(desc['exclude'], file):
                    continue
                src = os.path.join(root, file)
                recipes.append(self.__getRecipe(src, reldir, desc))
        return recipes

    def __getRecipe(self, src, reldir, desc):
        timestamp = self.__commitTime.getTimestamp(src)
        recipe = Recipe(src, reldir, desc, timestamp, self.__params, desc)
        return recipe


class Process(object):

    def __init__(self):
        self.__feature = {
            'python':       self.__feature_compile,
            'apply':        self.__feature_apply,
            'copy':         self.__feature_copy
        }
        self.__getFilename = {
            'python':       self.__getFilename_compile,
            'apply':        self.__getFilename_apply,
            'copy':         self.__getFilename_copy
        }

    def command(self, recipe):
        file = recipe.file
        for p in recipe.process:
            file = self.__feature[p.method](p.src, p.dst, recipe)
        return file, recipe.vpath, recipe.timestamp

    def getFilename(self, method, file, buildDir, desc):
        process = []
        for m in method.split('+'):
            if m != 'plain':
                newfile = self.__getFilename[m](file, buildDir, desc)
                process.append(ProcessDesc(m, file, newfile))
                file = newfile
        return process

    def getTimestamp(self, method, timestamp, configTimestamp):
        if 'apply' in method:
            timestamp = max(timestamp, configTimestamp)
        return timestamp

    def __getDstdir(self, dir, buildDir):
        if splitpath(dir)[0] != buildDir:
            dir = os.path.join(buildDir, dir)
        return dir

    def __getFilename_compile(self, src, buildDir, desc):
        dir, file = os.path.split(src)
        dstdir = self.__getDstdir(dir, buildDir)
        name, ext = os.path.splitext(file)
        return os.path.join(dstdir, name + '.pyc')

    def __getFilename_apply(self, src, buildDir, desc):
        dir, file = os.path.split(src)
        dstdir = self.__getDstdir(dir, buildDir)
        name, ext = os.path.splitext(file)
        if ext == '' or ext == '.in':
            dst = os.path.join(dstdir, name)
        else:
            inname, inext = os.path.splitext(name)
            if inext == '.in':
                dst = os.path.join(dstdir, inname + ext)
            else:
                dst = os.path.join(dstdir, name + ext)
        return dst

    def __getFilename_copy(self, src, buildDir, desc):
        dir_, file = os.path.split(src)
        dstdir = self.__getDstdir(dir_, buildDir)
        if 'replace' in desc:
            pattern, string = desc.get('replace')
            file = re.sub(pattern, string, file)
        dst = os.path.join(dstdir, file)
        return dst

    def __feature_compile(self, src, dst, recipe):
        makedirs(os.path.dirname(dst))
        vfile = os.path.join(recipe.reldir, os.path.basename(src))
        tmpfile = os.path.join(os.path.dirname(dst), os.path.basename(src))
        if src != tmpfile:
            shutil.copy(src, tmpfile)
        os.utime(tmpfile, (recipe.timestamp, recipe.timestamp))
        py_compile.compile(file=tmpfile, cfile=dst, dfile=vfile, doraise=True)
        return dst

    def __feature_apply(self, src, dst, recipe):
        makedirs(os.path.dirname(dst))
        with open(src, 'r') as in_file, open(dst, 'w') as out_file:
            out_file.write(Template(in_file.read()).substitute(recipe.params.dict))
        return dst

    def __feature_copy(self, src, dst, recipe):
        makedirs(os.path.dirname(dst))
        shutil.copyfile(src, dst)
        os.utime(dst, (recipe.timestamp, recipe.timestamp))
        return dst


class ZipPackage(object):

    def __init__(self):
        self.__dirs = {}
        self.__list = []

    def add(self, src, dst, timestamp):
        path = ''
        for dir in splitpath(dst)[0:-1]:
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


class Recipe(object):

    def __init__(self, file, reldir, target, timestamp, params, desc):
        self.file = file
        self.reldir = reldir
        self.target = target
        self.params = params
        self.process = Process().getFilename(self.method, file, params.buildDir, desc)
        self.timestamp = Process().getTimestamp(self.method, timestamp, params.timestamp)
 
    @property
    def method(self):
        return self.target['method']

    @property
    def root(self):
        return self.target.get('root', '')

    @property
    def vpath(self):
        return os.path.join(self.root, self.reldir, os.path.basename(self.dst))

    @property
    def dst(self):
        if self.process:
            return self.process[-1].dst
        return self.file


class ProcessDesc(object):

    def __init__(self, method, src, dst):
        self.method = method
        self.src = src
        self.dst = dst


def main():
    control = Control()
    file = control.makePackage()
    print 'create package: {}'.format(file)


if __name__ == "__main__":
    main()
