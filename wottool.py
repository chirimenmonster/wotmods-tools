import os
from argparse import ArgumentParser

from utils import wot
from utils import XmlUnpacker
from utils import wotmod
from utils import unzip
from utils import uncompile

DEFAULT_WOT_DIR = 'C:/Games/World_of_Tanks'


def show_version(args):
    result = wot.getWotVersion(base_dir=args.base_dir)
    if args.name:
        print result['version']
    elif args.build:
        print result['build']
    else:
        print result['string']


def fetch_xml(args):
    result = wot.fetchXmlData(args.file, base_dir=args.base_dir, package=args.package)
    if args.xpath:
        for e in result['data'].findall(args.xpath):
            print XmlUnpacker.pretty_xml(e)
    else:
        print result['text']


def extract_zipfile(args):
    path = wot.guessFilePath(args.file, base_dir=args.base_dir)
    if path is None:
        print 'unknwon file: ', path
        return
    if not args.dest_dir and not args.list:
        print 'required option -d or -l'
        return
    unzip.extractPattern(path, extract_dir=args.dest_dir, pattern=args.regex, opt_list=args.list)


def create_wotmod(args):
    wotmod.createSimplePackage(args.file, base_dir=args.target, dest_dir='res')
    print 'created wotmod: {}'.format(args.file)

    
def decompile(args):
    uncompile.uncompile_tree(args.target, args.dest)
    

def main(arg_list=None):
    parser = ArgumentParser()
    parser.add_argument('-b', metavar='basedir', dest='base_dir', help='wot directory', default=DEFAULT_WOT_DIR)
    
    subparsers = parser.add_subparsers()
    
    parser_version = subparsers.add_parser('version')
    parser_version.add_argument('-s', action='store_true', dest='name', help='show version name (folder name)')
    parser_version.add_argument('-b', action='store_true', dest='build', help='show build number')
    parser_version.set_defaults(func=show_version)

    parser_xml = subparsers.add_parser('xml')
    parser_xml.add_argument('-p', metavar='package', dest='package', help='package file')
    parser_xml.add_argument('-x', metavar='xpath', dest='xpath', help='xpath')
    parser_xml.add_argument('file')
    parser_xml.set_defaults(func=fetch_xml)
       
    parser_xml = subparsers.add_parser('unzip')
    parser_xml.add_argument('-d', metavar='destdir', dest='dest_dir', help='dest base dir')
    parser_xml.add_argument('-e', metavar='regex', dest='regex', help='match pattern')
    parser_xml.add_argument('-l', action='store_true', dest='list', help='view file list')
    parser_xml.add_argument('file')
    parser_xml.set_defaults(func=extract_zipfile)

    parser_wotmod = subparsers.add_parser('wotmod')
    parser_wotmod.add_argument('target', help='base directory of target files')
    parser_wotmod.add_argument('file', help='wotmod package name')
    parser_wotmod.set_defaults(func=create_wotmod)

    parser_decompile = subparsers.add_parser('decompile')
    parser_decompile.add_argument('target', help='base of target files')
    parser_decompile.add_argument('dest', help='dest base dir')
    parser_decompile.set_defaults(func=decompile)
        
    args = parser.parse_args(arg_list)
    args.func(args)


if __name__ == '__main__':
    main()
