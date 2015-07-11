import time
import tarfile
from io import StringIO
from collections import OrderedDict

class TarWriter(object):
    def __init__(self, fileobj):
        self.fileobj = fileobj
        self.tar = tarfile.open(fileobj=fileobj, mode='w')

    def add(self, name, text):
        data = StringIO()
        data.write(text)
        info = tarfile.TarInfo(name)
        info.size = data.tell()
        info.mtime = int(time.time())
        info.mode = 0o640
        info.type = tarfile.REGTYPE
        data.seek(0)
        self.tar.addfile(info, data)
        data.close()

    def dir(self, name):
        info = tarfile.TarInfo(name)
        info.mtime = int(time.time())
        info.mode = 0o640
        info.type = tarfile.DIRTYPE
        self.tar.addfile(info)

    def close(self, *args, **kwargs):
        self.tar.close(*args, **kwargs)

