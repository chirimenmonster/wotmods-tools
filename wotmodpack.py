from argparse import ArgumentParser
import zipfile
from datetime import datetime
import os

from utils import pathtools
from zip import wotmodtool


def do_command(options):
    wotmod = wotmodtool.WotmodPackage()
    for path in pathtools.getFileList([''], options['base_dir']):
        src = os.path.join(options['base_dir'], path)
        dst = os.path.join(options['dest_dir'], path)
        wotmod.add(src, dst)
    wotmod.list()
    wotmod.create(options['zipfile'], zipfile.ZIP_STORED)


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('-b', metavar='basedir', dest='base_dir', help='source base directory')
    argparser.add_argument('-d', metavar='destdir', dest='dest_dir', help='destination base directory')
    argparser.add_argument('zipfile')
    settings = argparser.parse_args()
    print settings
    do_command(vars(settings))
    