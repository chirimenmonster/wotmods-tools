import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../uncompyle2'))
import uncompyle2


def uncompile(path, wdir):
    if os.path.isfile(path):
        base = os.path.dirname(path)
        filelist = [ os.path.basename(path) ]
    elif os.path.isdir(path):
        base = path
        filelist = []
        for root, dirs, files in os.walk(path):
            files = filter(lambda x: os.path.splitext(x)[1] in [ '.pyc', '.pyo' ], files)
            root = os.path.relpath(root, start=path)
            if root == '.':
                root = ''
            filelist += map(lambda x: os.path.join(root, x), files)
    else:
        print 'not found: {}'.format(path)
        return
    do_uncompile(base, wdir, filelist)


def do_uncompile(src_base, out_base, files):
    codes = []
    outfile = None
    showasm = showast = do_verify = 0
    result = uncompyle2.main(src_base, out_base, files, codes, outfile, showasm, showast, do_verify)
    print '# decompiled %i files: %i okay, %i failed, %i verify failed' % result
    for file in files:
        srcfile = os.path.join(out_base, file)
        outfile = srcfile + '_dis'
        if not os.path.isfile(outfile):
            continue
        dstbase, ext = os.path.splitext(srcfile)
        if ext not in [ '.pyc', '.pyo' ]:
            continue
        dstfile = dstbase + '.py'
        if os.path.isfile(dstfile):
            os.rename(outfile, dstfile)
