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


def compile_python(src, dst, virtualdir):
    makedirs(os.path.dirname(dst))
    vfile = os.path.join(virtualdir, os.path.basename(src))
    py_compile.compile(file=src, cfile=dst, dfile=vfile, doraise=True)


def apply_template(src, dst, parameters):
    makedirs(os.path.dirname(dst))
    with open(src, 'r') as in_file, open(dst, 'w') as out_file:
        out_file.write(Template(in_file.read()).substitute(parameters))


def feature_apply(src, params):
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
    apply_template(src, dst, params)
    return dst


def feature_compile(src, reldir):
    srcdir, srcfile = os.path.split(src)
    dstdir = os.path.join(BUILD_DIR, srcdir)
    name, ext = os.path.splitext(src)
    dst = os.path.join(dstdir, name + '.pyc')
    compile_python(src, dst, reldir)
    return dst


def process_file(method, file, reldir, params):
    if method == 'apply+python':
        file = feature_apply(file, params)
        file = feature_compile(file, reldir)
    elif method == 'python':
        file = feature_compile(file, reldir)
    elif method == 'apply':
        file = feature_apply(file, params)
    elif method == 'plain':
        pass
    else:
        raise ValueError('unknown methd: {}'.format(target['method']))
    return file


def split(path):
    head, tail = os.path.split(path)
    if not head:
        return [ tail ]
    result = split(head)
    result.append(path)
    return result


def create_zipfile(package, paths, compression=zipfile.ZIP_DEFLATED):
    donelist = []
    with zipfile.ZipFile(package, 'w', compression=compression) as file:
        for source, target in paths:
            for dir in split(target)[0:-1]:
                if dir not in donelist:
                    file.write('.', dir, compression)
                    donelist.append(dir)
            file.write(source, target, compression)
            donelist.append(target)


def package(jsonfile, params, compression=zipfile.ZIP_STORED):
    with open(jsonfile, 'r') as f:
        desc = json.loads(Template(f.read()).substitute(params))   
    paths = []
    for target in desc['files']:
        for file in target['source']:
            file = process_file(target['method'], file, target['reldir'], params)
            release = os.path.join(target['root'], target['reldir'], os.path.basename(file))
            paths.append([ file, release ])
    package = os.path.join(BUILD_DIR, desc['package'])
    create_zipfile(package, paths, compression)


def main():
    params = get_config()
    try:
        shutil.rmtree(BUILD_DIR)
    except:
        pass
    os.makedirs(BUILD_DIR)

    package(params['wotmod_files'], params)

    if 'release_files' in params and os.path.exists(params['release_files']):
        package(params['release_files'], params, compression=zipfile.ZIP_DEFLATED)


if __name__ == "__main__":
    main()
