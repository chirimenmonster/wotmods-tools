import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../uncompyle2'))
import uncompyle2

def uncompile_tree(path, wdir):
    print '# decompile *.pyc files'
    showasm = showast = do_verify = 0
    codes = []
    list = []
    for root, dirs, files in os.walk(path):
        files = filter(lambda f: os.path.splitext(f)[1] in [ '.pyc', '.pyo' ], files)
        root = os.path.relpath(root, start=path)
        if root == '.':
            root = ''
        list += map(lambda f: os.path.join(root, f), files)
    src_base = path
    out_base = wdir
    files = list
    outfile = None
    result = uncompyle2.main(src_base, out_base, files, codes, outfile, showasm, showast, do_verify)
    print '# decompiled %i files: %i okay, %i failed, %i verify failed' % result
    for file in list:
        tmp = os.path.join(wdir, file) + '_dis'
        dst, ext = os.path.splitext(os.path.join(wdir, file))
        if not ext == '.pyc':
            continue
        dst = dst + '.py'
        if os.path.isfile(tmp) and not os.path.isfile(dst):
            os.rename(tmp, dst)
