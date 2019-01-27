import os
import sys
import re
import io
import shutil
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import utils.path
from utils import unzip
from utils import wotmod
from utils import wot
from utils import XmlUnpacker

WD_EXTRACT = 'tmp/orig'
WD_MODIFIED = 'tmp/dst'


def remove_dirs(*args):
    for dir in args:
        try:
            shutil.rmtree(WD_EXTRACT)
        except:
            pass


def createmod_fontsize():
    BASE = '/c/games/World_of_Tanks/res'
    TARGET = 'gui/flash/fontconfig.xml'
    MOD_NAME = 'font.wotmod'
    
    remove_dirs(WD_EXTRACT, WD_MODIFIED)

    values = (('$TitleFont', '1.0'), ('$FieldFont', '1.0'), ('$TextFont', '1.1'),
            ('$PartnerCondensed', '1.1'), ('$PartnerLightCondensed', '1.1'))

    target = os.path.join(BASE, TARGET)
    print 'modify XML files...'
    print 'edit XML file: {}'.format(target)
    tree = wot.WotXmlTree(path=target)
    for tag, value in values:
        parent = tree.find('.//map/alias[embedded="{}"]'.format(tag))
        e = parent.find('scaleFactor')
        if e is not None:
            parent.remove(e)
        e = Element('scaleFactor')
        e.text = value
        parent.append(e)
    tree.output(os.path.join(WD_MODIFIED, TARGET))

    print 'create wotmod package: {}'.format(MOD_NAME)
    wotmod.createSimplePackage(MOD_NAME, base_dir=WD_MODIFIED, dest_dir='res')
    
    
def createmod_sniperview():
    ORG_PKG = '/c/games/World_of_Tanks_CT/res/packages/scripts.pkg'
    PATTERN = '.*/item_defs/vehicles/.*\.xml'
    MOD_NAME = 'sniperview.wotmod'
    
    remove_dirs(WD_EXTRACT, WD_MODIFIED)
    
    print 'extract from pkg: {}, pattern={}'.format(ORG_PKG, PATTERN)
    unzip.extractPattern(ORG_PKG, extract_dir=WD_EXTRACT, pattern=PATTERN)

    #print 'modify XML files...'
    print 'check XML files...'
    for file in utils.path.getFileList(base_dir=WD_EXTRACT, pattern=PATTERN):
        tree = wot.WotXmlTree(path=os.path.join(WD_EXTRACT, file))
        if tree.hasElement('gunCamPosition'):
            for e in tree.findall('.//gunCamPosition/..'):
                #print ElementTree.tostring(e.find('gunPosition'))
                #print ElementTree.tostring(e.find('gunCamPosition'))
                gunPosition = map(float, e.find('gunPosition').text.split())
                gunCamPosition = map(float, e.find('gunCamPosition').text.split())
                diff = [ w - v for v, w in zip(gunPosition, gunCamPosition) ]
                print '{:<40}: ( {: <18} {: <18} {: <18} )'.format(file.replace('scripts/item_defs/vehicles/', ''), *diff)
            tree.output(os.path.join(WD_MODIFIED, file))
        #if tree.removeTagAll('gunCamPosition'):
        #    print 'edit XML file: {}'.format(file)
        #    tree.output(os.path.join(WD_MODIFIED, file))

    #print 'create wotmod package: {}'.format(MOD_NAME)
    #wotmod.createSimplePackage(MOD_NAME, base_dir=WD_MODIFIED, dest_dir='res')


if __name__ == '__main__':
    createmod_sniperview()
    #createmod_fontsize()
    