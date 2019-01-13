import os
import sys

import utils.path
from utils import unzip
from utils import XmlUnpacker
from utils import wotmod


if __name__ == '__main__':
    print 'extract fropm pkg'
    unzip.extractPattern('/c/games/World_of_Tanks_EU/res/packages/scripts.pkg', extract_dir='tmp/orig', pattern='.*/item_defs/vehicles/.*\.xml')

    print 'modify XML files'
    fileopt = {
        'base_dir':      'tmp/orig',
        'extract_dir':   'tmp/dst',
        'files':        [ 'scripts' ]
    }
    for file in utils.path.getFileList(fileopt['files'], base_dir=fileopt['base_dir']):
        path = os.path.join(fileopt['base_dir'], file)
        root = XmlUnpacker.getElementTree(path, True)
        elemlist = root.findall('.//gunCamPosition/..')
        if not len(elemlist):
            continue
        for elem in elemlist:
            for e in elem.iterfind('gunCamPosition'):
                elem.remove(e)
        dst = os.path.join(fileopt['extract_dir'], file)
        XmlUnpacker.outputElementTree(root, dst)

    print 'create wotmod package'
    wotmod.createSimplePackage('test.wotmod', base_dir='tmp/dst', dest_dir='res')
 