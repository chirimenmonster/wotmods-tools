import os
import sys

from utils import pathtools
from zip import ziptool
from zip import wotmodtool
from xmltool import XmlUnpacker


if __name__ == '__main__':
    ziptool.do_command({
        'extract_dir':  'tmp/orig',
        'pattern':      '.*/item_defs/vehicles/.*\.xml',
        'zipfile':      '/c/games/World_of_Tanks_EU/res/packages/scripts.pkg'
    })

    fileopt = {
        'base_dir':      'tmp/orig',
        'extract_dir':   'tmp/dst',
        'files':        [ 'scripts' ]
    }
    
    for file in pathtools.getFileList(fileopt['files'], base_dir=fileopt['base_dir']):
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

    wotmodtool.do_command({
        'base_dir': 'tmp/dst',
        'dest_dir': 'res',
        'zipfile':  'test.wotmod'
    })
 