import os
import sys
import re
import io

import utils.path
from utils import unzip
from utils import XmlUnpacker
from utils import wotmod
from utils import wot

ORG_PKG = '/c/games/World_of_Tanks_EU/res/packages/scripts.pkg'
PATTERN = '.*/item_defs/vehicles/.*\.xml'
WD_EXTRACT = 'tmp/orig'
WD_MODIFIED = 'tmp/dst'

        
if __name__ == '__main__':
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
        tree = wot.WotXmlTree(os.path.join(WD_EXTRACT, file))
        if tree.removeTagAll('gunCamPosition'):
            tree.output(os.path.join(WD_MODIFIED, file))

    print 'create wotmod package'
    wotmod.createSimplePackage('test.wotmod', base_dir=WD_MODIFIED, dest_dir='res')
 