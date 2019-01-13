import os
import sys

import utils.path
from utils import unzip
from utils import XmlUnpacker
from utils import wotmod


ORG_PKG = '/c/games/World_of_Tanks_EU/res/packages/scripts.pkg'
PATTERN = '.*/item_defs/vehicles/.*\.xml'
WD_EXTRACT = 'tmp/orig'
WD_MODIFIED = 'tmp/dst'

if __name__ == '__main__':
    print 'extract fropm pkg'
    unzip.extractPattern(ORG_PKG, extract_dir=WD_EXTRACT, pattern=PATTERN)

    print 'modify XML files'
    for file in utils.path.getFileList([ 'scripts' ], base_dir=WD_EXTRACT):
        path = os.path.join(WD_EXTRACT, file)
        root = XmlUnpacker.getElementTree(path, True)
        elemlist = root.findall('.//gunCamPosition/..')
        if not len(elemlist):
            continue
        for elem in elemlist:
            for e in elem.iterfind('gunCamPosition'):
                elem.remove(e)
        dst = os.path.join(WD_MODIFIED, file)
        XmlUnpacker.outputElementTree(root, dst)

    print 'create wotmod package'
    wotmod.createSimplePackage('test.wotmod', base_dir=WD_MODIFIED, dest_dir='res')
 