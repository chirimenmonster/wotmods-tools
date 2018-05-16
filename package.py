import os
import re
import shutil
import py_compile
import zipfile
import ConfigParser
import json
from string import Template
from datetime import datetime

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

    
class Control(object):

    def __init__(self, config=CONFIG, hasBuildDir=False):
        self.setConfig(config)
        self.__buildDir = self.__params.get('build_dir', DEFAULT_BUILDDIR)
        self.__params['BUILDDIR'] = self.__buildDir
        self.__process = Process(self.__buildDir)
        if not hasBuildDir:
            self.makeBuildDir(self.__buildDir)
        self.__commitTime = committime.CommitTime()
        if isinstance(config, list):
            self.__configTimestamp = max([ self.__commitTime.getTimestamp(f) for f in config ])
        else:
            self.__configTimestamp = self.__commitTime.getTimestamp(config)
    
    def makeBuildDir(self, buildDir):
        try:
            shutil.rmtree(buildDir)
        except:
            pass
        os.makedirs(buildDir)

    def setConfig(self, config=CONFIG):
        inifile = ConfigParser.SafeConfigParser()
        inifile.read(config)
        params = dict(inifile.items(SECTION_WOTMOD))
        for section in inifile.sections():
            for k, v in inifile.items(section):
                params[section + '_' + k] = v
        self.__params = params
        return params

    def getParam(self, key):
        return self.__params[key]

    def setPackageDef(self, filename):
        with open(filename, 'r') as file:
            text = Template(file.read()).substitute(self.__params)
            packageDef = json.loads(text)
        self.__packageDef = packageDef
        return packageDef

    def makePackage(self, domain=SECTION_WOTMOD, compression=zipfile.ZIP_STORED):
        pkgsrcs = self.__params[PKGDEF[domain]]
        pkgname = os.path.join(self.__buildDir, self.__params[PKGNAME[domain]])
        packageDef = PackageDef(pkgsrcs, self.__params)
        package = Package()
        lastupdate = 0
        for recipe in packageDef.getRecipes():
            timestamp = self.__commitTime.getTimestamp(recipe.file)
            if 'apply' in recipe.method:
                recipe.timestamp = max(timestamp, self.__configTimestamp)
            else:
                recipe.timestamp = timestamp
            file = self.__process.command(recipe)
            release = os.path.join(recipe.root, recipe.reldir, os.path.basename(file))
            package.add(file, release, recipe.timestamp)
            lastupdate = max(lastupdate, recipe.timestamp)
            #print '{}: {} -> {} ({})'.format(recipe.method, recipe.file, file, recipe.timestamp)
        #package.list()
        package.setLastupdate(lastupdate)
        package.createZipfile(pkgname, compression)
        return pkgname


class PackageDef(object):

    def __init__(self, filename, params):
        self.__params = params
        with open(filename, 'r') as file:
            text = Template(file.read()).substitute(self.__params)
            packageDef = json.loads(text)
        self.__packageDef = packageDef

    def get(self, key):
        return self.__params[key]

    def getRecipes(self):
        self.__recipes = []
        for desc in self.__packageDef['sources']:
            recipes = self.parse(desc)
            self.__recipes.extend(recipes)
        return self.__recipes

    def parse(self, desc):
        recipes = []
        for file in desc.get('files', []):
            recipes.append(self.__parseSource(desc, file))
        for dir in desc.get('dirs', []):
            recipes.extend(self.__parseSrcDir(desc, dir))
        return recipes

    def __parseSource(self, desc, srcfile):
        recipe = Recipe(srcfile, desc.get('reldir', ''), desc, self.__params)
        return recipe

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
                recipes.append(Recipe(os.path.join(root, file), reldir, desc, self.__params))
        return recipes
 

class Process(object):

    def __init__(self, buildDir):
        self.__buildDir = buildDir
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
        dir, file = os.path.split(src)
        if splitpath(dir)[0] != self.__buildDir:
            dir = os.path.join(self.__buildDir, dir)
        name, ext = os.path.splitext(file)
        return os.path.join(dir, name + '.pyc')

    def __getFilename_apply(self, src):
        dir, file = os.path.split(src)
        if splitpath(dir)[0] != self.__buildDir:
            dir = os.path.join(self.__buildDir, dir)
        name, ext = os.path.splitext(file)
        if ext == '' or ext == '.in':
            dst = os.path.join(dir, name)
        else:
            inname, inext = os.path.splitext(name)
            if inext == '.in':
                dst = os.path.join(dir, inname + ext)
            else:
                dst = os.path.join(dir, name + ext)
        return dst

    def __feature_compile(self, src, recipe):
        dst = self.__getFilename_compile(src)
        makedirs(os.path.dirname(dst))
        vfile = os.path.join(recipe.reldir, os.path.basename(src))
        tmpfile = os.path.join(os.path.dirname(dst), os.path.basename(src))
        if src != tmpfile:
            shutil.copy(src, tmpfile)
        os.utime(tmpfile, (recipe.timestamp, recipe.timestamp))
        py_compile.compile(file=tmpfile, cfile=dst, dfile=vfile, doraise=True)
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
        self.__lastupdate = None

    def setLastupdate(self, lastupdate):
        self.__lastupdate = lastupdate

    def add(self, src, dst, timestamp):
        path = ''
        for dir in splitpath(dst)[0:-1]:
            path = os.path.join(path, dir)
            if path not in self.__dirs:
                self.__dirs[path] = True
                self.__list.append([ None, path + '/', None ])
        self.__list.append([src, dst, timestamp])

    def list(self):
        for source, target, timestamp in self.__list:
            print source, target, timestamp

    def createZipfile(self, pkgname, compression):
        with zipfile.ZipFile(pkgname, 'w', compression=compression) as file:
            for source, target, timestamp in self.__list:
                t = datetime.fromtimestamp(timestamp or self.__lastupdate)
                zipinfo = zipfile.ZipInfo(target, t.timetuple())
                if source:
                    with open(source, 'rb') as f:
                        file.writestr(zipinfo, f.read(), compression)
                    #file.write(source, target, compression)
                else:
                    file.writestr(zipinfo, '', zipfile.ZIP_STORED)


class Recipe(object):

    def __init__(self, file, reldir, target, params):
        self.file = file
        self.reldir = reldir
        self.method = target['method']
        self.root = target.get('root', '')
        self.params = params
 

def main():
    control = Control()
    file = control.makePackage()
    print 'create package: {}'.format(file)


if __name__ == "__main__":
    main()
