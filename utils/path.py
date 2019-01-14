import os
import re

def getFileList(files=None, base_dir=None, pattern=None):
    if files is None:
        files = [ '' ]
    elif isinstance(files, str):
        files = [ files ]
    for path in files:
        abspath = os.path.join(base_dir, path) if base_dir else path
        if os.path.isdir(abspath):
            for root, dirs, files in os.walk(abspath):
                relroot = os.path.relpath(root, base_dir) if base_dir else root
                for file in files:
                    result = os.path.join(relroot, file)
                    if pattern:
                        if not re.match(pattern, result):
                            continue
                    yield result
        elif os.path.isfile(abspath):
            if pattern:
                if not re.match(pattern, path):
                    continue
            yield path
