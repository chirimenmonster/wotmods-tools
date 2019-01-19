from argparse import ArgumentParser

from utils import wot
from utils import XmlUnpacker

DEFAULT_WOT_DIR = 'C:/Games/World_of_Tanks'


def show_version(args):
    print wot.getWotVersion(base_dir=args.base_dir)


def fetch_xml(args):
    result = wot.fetchXmlData(args.file, base_dir=args.base_dir, package=args.package)
    if args.xpath:
        for e in result['data'].findall(args.xpath):
            print XmlUnpacker.pretty_xml(e)
    else:
        print result['text']


def list(args):
    for name in wot.listPackageFile(args.package, base_dir=args.base_dir):
        print name


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-b', metavar='basedir', dest='base_dir', help='wot directory', default=DEFAULT_WOT_DIR)
    
    subparsers = parser.add_subparsers()
    
    parser_version = subparsers.add_parser('version')
    parser_version.set_defaults(func=show_version)

    parser_xml = subparsers.add_parser('xml')
    parser_xml.add_argument('-p', metavar='package', dest='package', help='package file')
    parser_xml.add_argument('-x', metavar='xpath', dest='xpath', help='xpath')
    parser_xml.add_argument('file')
    parser_xml.set_defaults(func=fetch_xml)
    
    parser_xml = subparsers.add_parser('list')
    parser_xml.add_argument('-p', metavar='package', dest='package', help='package file')
    parser_xml.set_defaults(func=list)
    
    args = parser.parse_args()
    args.func(args)
