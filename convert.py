#! /usr/bin/python2

import sys
import os
import shutil
import argparse
from logging import getLogger, StreamHandler, INFO
from zipfile import ZipFile

from utils import wot
from utils import XmlUnpacker

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uncompyle2'))
import uncompyle2

logger = getLogger(__name__)
handler = StreamHandler()
logger.setLevel(INFO)
logger.addHandler(handler)

class Config:
    WD = 'tmp'
    package = ''
    outdir = WD

def extractZipfile(file, wdir):
    with ZipFile(file, 'r') as zip:
        list = zip.namelist()
        list = map(lambda n: n.split('/', 1)[0], list)
        list = sorted(set(list))
        for dir in list:
            target = os.path.join(wdir, dir)
            if os.path.exists(target):
                logger.info('# remove old dir, {}'.format(target))
                shutil.rmtree(target)
        logger.info('# extract {} to {}'.format(file, wdir))
        zip.extractall(wdir)
    return list

def uncompile(path, wdir):
    logger.info('# decpompile *.pyc files')
    showasm = showast = do_verify = 0
    codes = []
    list = []
    for root, dirs, files in os.walk(path):
        files = filter(lambda f: os.path.splitext(f)[1] in [ '.pyc', '.pyo' ], files)
        root = root.replace(wdir, '')[1:]
        list += map(lambda f: os.path.join(root, f), files)
    src_base = out_base = wdir
    files = list
    outfile = None
    result = uncompyle2.main(src_base, out_base, files, codes, outfile, showasm, showast, do_verify)
    logger.info('# decompiled %i files: %i okay, %i failed, %i verify failed' % result)

def rename(path):    
    print '# rename *.pyc_dis to *.py'
    for root, dirs, files in os.walk(path):
        files = filter(lambda f: os.path.splitext(f)[1] in [ '.pyc_dis' ], files)
        for f in files:
            file = os.path.join(root, f)
            os.rename(file, os.path.splitext(file)[0] + '.py')
            os.remove(os.path.splitext(file)[0] + '.pyc')

def convertXml(path):
    logger.info('# unpack XML files, *.xml and *.def, under {}'.format(path))
    for root, dirs, files in os.walk(path):
        for file in files:
            if os.path.splitext(file)[1] in [ '.xml', '.def' ]:
                target = os.path.join(root, file)
                result = wot.fetchXmlList(file=target, root='root')
                text = XmlUnpacker.pretty_xml(result[0][1], strip=True)
                try:
                    with open(target, 'w') as fp:
                        fp.write(text.encode('utf-8'))
                except Exception as e:
                    print text
                    print target, e
                    

if __name__ == '__main__':
    config = Config()
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', dest='outdir', help='output dir')
    parser.add_argument('-p', dest='pkgfile', help='pkg file')
    parser.parse_args(namespace=config)

    head, tail = os.path.split(config.outdir)
    config.outdir = os.path.join(head, tail) if tail else head
    
    if config.outdir != config.WD and os.path.exists(config.outdir):
        logger.info('# remove old dir, {}'.format(config.outdir))
        shutil.rmtree(config.outdir)

    list = extractZipfile(config.pkgfile, config.outdir)
    list = map(lambda x: os.path.join(config.outdir, x), list)
    for path in list:
        uncompile(path, config.outdir)
    for path in list:
        rename(path)
    for path in list:
        convertXml(path)
