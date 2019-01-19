import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../uncompyle2'))
import uncompyle2

def uncompile_tree(path, wdir):
    print '# decpompile *.pyc files'
    showasm = showast = do_verify = 0
    codes = []
    list = []
    for root, dirs, files in os.walk(path):
        files = filter(lambda f: os.path.splitext(f)[1] in [ '.pyc', '.pyo' ], files)
        root = root.replace(wdir, '')[1:]
        list += map(lambda f: os.path.join(root, f), files)
    src_base = out_base = wdir
    files = list
    outfile = None
    result = uncompyle2.main(src_base, out_base, files, codes, outfile, showasm, showast, do_verify)
    print '# decompiled %i files: %i okay, %i failed, %i verify failed' % result
