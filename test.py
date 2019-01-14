import os
import sys
import re
import io

import utils.path
from utils import unzip
from utils import XmlUnpacker
from utils import wotmod


ORG_PKG = '/c/games/World_of_Tanks_EU/res/packages/scripts.pkg'
PATTERN = '.*/item_defs/vehicles/.*\.xml'
WD_EXTRACT = 'tmp/orig'
WD_MODIFIED = 'tmp/dst'


def getWotVersion(base_dir=None):
    tree = WotXmlTree(os.path.join(base_dir, 'version.xml'))
    string = tree.getElementAll('version')[0].text
    match = re.match(r'\s*(v\.([\d.]+)\s+#([\d]+))\s*', string)
    version = {
        'string':   match.group(1),
        'version':  match.group(2),
        'build':    match.group(3)
    }
    return version
        
class WotXmlTree(object):

    def __init__(self, path):
        self.root = XmlUnpacker.getElementTree(path, True)

    def getElementAll(self, tag):
        elemList = self.root.findall('.//{}'.format(tag))
        return elemList

    def hasElement(self, tag):
        elemList = self.root.findall('.//{}'.format(tag))
        return len(elemList)

    def removeTagAll(self, tag):
        count = 0
        for parent in self.root.findall('.//{}/..'.format(tag)):
            for elem in parent.iterfind(tag):
                parent.remove(elem)
                count = count + 1
        return count

    def output(self, file):
        XmlUnpacker.outputElementTree(self.root, file)
    

if __name__ == '__main__':
    print getWotVersion('/c/games/World_of_Tanks_EU')

    zip = unzip.ZipPackage(ORG_PKG, mode='r')
    data = zip.read('scripts/entity_defs/Account.def')
    
    xmlunpacker = XmlUnpacker.XmlUnpacker()
    tree = xmlunpacker.read(io.BytesIO(data))
    e = tree.find(".//Properties/requiredVersion_13000")
    sys.stdout.write(XmlUnpacker.pretty_xml(e))
    sys.exit()

    print 'extract from pkg'
    unzip.extractPattern(ORG_PKG, extract_dir=WD_EXTRACT, pattern=PATTERN)

    print 'modify XML files'
    for file in utils.path.getFileList(base_dir=WD_EXTRACT, pattern=PATTERN):
        tree = WotXmlTree(os.path.join(WD_EXTRACT, file))
        if tree.removeTagAll('gunCamPosition'):
            tree.output(os.path.join(WD_MODIFIED, file))

    print 'create wotmod package'
    wotmod.createSimplePackage('test.wotmod', base_dir=WD_MODIFIED, dest_dir='res')
 