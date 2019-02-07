from argparse import ArgumentParser
import zipfile
import re


class ZipPackage(zipfile.ZipFile):
    options = {}

    def extractall(self, *args):
        if self.options['list']:
            members = self.namelist() if len(args) < 2 else args[1]
            print '\n'.join(members)
        else:
            super(ZipPackage, self).extractall(*args)

    def extract_pattern(self, path, pattern):
        members = self.list_pattern(pattern)
        self.extractall(path, members)

    def list_pattern(self, pattern=None):
        if pattern:
            return [ f for f in self.namelist() if re.match(pattern, f) ]
        return self.namelist()


def extractPattern(zipfile, extract_dir=None, pattern=None, opt_list=False):
    zip = ZipPackage(zipfile, mode='r')
    zip.options['list'] = opt_list
    if pattern:
        zip.extract_pattern(extract_dir, pattern)
    else:
        zip.extractall(extract_dir)

if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('-d', metavar='exdir', dest='extract_dir', help='extract files into exdir')
    argparser.add_argument('-l', dest='list', action='store_true', help='list files')
    argparser.add_argument('-p', dest='pattern', help='files pattern')
    argparser.add_argument('zipfile')
    argparser.add_argument('files', nargs='*')
    settings = argparser.parse_args()
    listPattern(settings.zipfile, extract_dir=settings.extract_dir, pattern=settings.pattern, opt_list=settings.list)
