import sys
import os
import unittest
from xml.etree import ElementTree

BASEDIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.join(BASEDIR, '..'))
from utils import wot


class TestTools(unittest.TestCase):

    def test_showversion(self):
        result = wot.getWotVersion(base_dir=os.path.join(BASEDIR, 'data'))
        expect = {'string': 'v.1.3.0.1 #1111', 'version': '1.3.0.1', 'build': '1111'}
        for k in expect.keys():
            self.assertEqual(result[k], expect[k])

    def test_fetchxml(self):
        result = wot.fetchXmlData('resources.xml', base_dir=os.path.join(BASEDIR, 'data'))
        expect = {}
        with open(os.path.join(BASEDIR, 'data/resources.xml'), 'r') as fp:
            expect['text'] = fp.read()
        expect['data'] = ElementTree.fromstring(expect['text'])
        self.assertEqual(result['text'], expect['text'])
        self.assertEqual(ElementTree.tostring(result['data']), ElementTree.tostring(expect['data']))

    def test_extractunzip(self):
        pass

    def test_packwotmod(self):
        pass

    def test_decompile(self):
        pass


if __name__ == '__main__':
    unittest.main()
