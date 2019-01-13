import os
from argparse import ArgumentParser

from utils import pathtools
from xmltool import XmlUnpacker


def do_command(options):
    for path in pathtools.getFileList(options.files, options.base_dir, pattern=options.pattern):
        src = os.path.join(options.base_dir, path) if options.base_dir else path
        dst = os.path.join(options.extract_dir, path) if options.extract_dir else None
        XmlUnpacker.convert(src, dst, True)


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('-b', metavar='basedir', dest='base_dir', help='base directory')
    argparser.add_argument('-d', metavar='exdir', dest='extract_dir', help='extract files into exdir')
    argparser.add_argument('-p', dest='pattern', help='files pattern')
    argparser.add_argument('files', nargs='+')
    settings = argparser.parse_args()
    do_command(settings)
