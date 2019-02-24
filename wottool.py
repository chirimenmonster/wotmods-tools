#! /usr/bin/python2
# -*- coding: utf-8; -*-
import os
import sys
import logging
from argparse import ArgumentParser
from xml.etree import ElementTree
from abc import ABCMeta, abstractmethod

from utils import wot
from utils import XmlUnpacker
from utils import wotmod
from utils import unzip
from utils import uncompile
from utils.exceptions import ApplicationError, FileNotFound


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

DEFAULT_WOT_DIR = 'C:/Games/World_of_Tanks'


class SubCommand():
    __metaclass__ = ABCMeta

    def __init__(self, parser):
        self.setParser(parser)
        parser.set_defaults(func=self.command)
        self.parser = parser
    
    @abstractmethod
    def setParser(self, parser):
        pass

    @abstractmethod
    def command(self):
        pass

        
class SubCommandVersion(SubCommand):
    def setParser(self, parser):
        parser.add_argument('-s', action='store_true', dest='name', help='show version name (folder name)')
        parser.add_argument('-b', action='store_true', dest='build', help='show build number')
        return parser

    def command(self, args):
        result = wot.getWotVersion(base_dir=args.base_dir)
        if args.name:
            print result['version']
        elif args.build:
            print result['build']
        else:
            print result['string']


class SubCommandXml(SubCommand):
    def setParser(self, parser):
        parser.add_argument('-p', metavar='package', dest='package', help='package file')
        parser.add_argument('-e', metavar='regex', dest='regex', help='file match pattern')
        parser.add_argument('-x', metavar='xpath', dest='xpath', help='xpath')
        parser.add_argument('-H', action='store_true', dest='withfilename', help='print file name with output lines')
        parser.add_argument('-s', action='store_true', dest='simple', help='output simple xml (not pretty)')
        parser.add_argument('file', nargs='?')
        return parser

    def command(self, args):
        result = wot.fetchXmlList(base_dir=args.base_dir, package=args.package, pattern=args.regex, xpath=args.xpath, file=args.file)
        for data in result:
            if args.simple:
                text = [ ElementTree.tostring(data[1]) ]
            else:
                text = XmlUnpacker.pretty_xml(data[1]).rstrip('\n').split('\n')
            header = data[0] + ': ' if args.withfilename else '' 
            for line in text:
                print header + line


class SubCommandUnzip(SubCommand):
    def setParser(self, parser):
        parser.add_argument('-d', metavar='destdir', dest='dest_dir', help='dest base dir')
        parser.add_argument('-e', metavar='regex', dest='regex', help='match pattern')
        parser.add_argument('-l', action='store_true', dest='list', help='view file list')
        parser.add_argument('file')

    def command(self, args):
        path = wot.guessFilePath(args.file, base_dir=args.base_dir)
        if path is None:
            raise FileNotFound('file is not found: {}'.format(args.file))
        if not args.dest_dir and not args.list:
            raise ApplicationError('required option -d or -l')
        unzip.extractPattern(path, extract_dir=args.dest_dir, pattern=args.regex, opt_list=args.list)


class SubCommandWotmod(SubCommand):
    def setParser(self, parser):
        parser.add_argument('target', help='base directory of target files')
        parser.add_argument('file', help='wotmod package name')

    def command(self, args):
        wotmod.createSimplePackage(args.file, base_dir=args.target, dest_dir='res')
        print 'created wotmod: {}'.format(args.file)


class SubCommandDecompile(SubCommand):
    def setParser(self, parser):
        parser.add_argument('target', help='base of target files')
        parser.add_argument('dest', help='dest base dir')

    def command(self, args):
        uncompile.uncompile(args.target, args.dest)


def create_parser():
    parser = ArgumentParser()
    parser.add_argument('-b', metavar='basedir', dest='base_dir', help='wot directory', default=DEFAULT_WOT_DIR)
    subparsers = parser.add_subparsers(dest='subparser_name')
    template = {
        'version':      SubCommandVersion,
        'xml':          SubCommandXml,
        'unzip':        SubCommandUnzip,
        'wotmod':       SubCommandWotmod,
        'decompile':    SubCommandDecompile,
    }
    subcmds = {}
    for key, cmd in template.items():
        subcmds[key] = cmd(subparsers.add_parser(key))
    return parser, subcmds


if __name__ == '__main__':
    try:
        parser, subcmds = create_parser()
        args = parser.parse_args()
        args.func(args)
    except FileNotFound as e:
        logger.error(e)
        sys.exit(1)
    except ApplicationError as e:
        logger.error(e)
        parser.print_usage()
        subcmds[args.subparser_name].parser.print_usage()
        sys.exit(1)
    except Exception as e:
        import traceback
        logger.debug(traceback.format_exc())
        logger.error(e)
        sys.exit(1)
