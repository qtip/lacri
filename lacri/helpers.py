import time
import tarfile
from io import BytesIO
from collections import OrderedDict

class TarWriter(object):
    def __init__(self, fileobj):
        self.fileobj = fileobj
        self.tar = tarfile.open(fileobj=fileobj, mode='w')

    def add(self, name, file_bytes):
        data = BytesIO()
        data.write(file_bytes)
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

def create_form(form_class, request, **kwargs):
    kwargs = kwargs.copy()
    if request.method in ('POST', 'PUT'):
        kwargs.update({
            'data': request.POST,
            'files': request.FILES,
        })
    form = form_class(**kwargs)
    if all(form.add_prefix(field) in request.POST for field, value in form.fields.items() if value.required):
        form = form_class(**kwargs)
    return form
