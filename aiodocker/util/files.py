
import asyncio
import bz2
import gzip
import lzma
import io
import os.path
from tarfile import TarError, TarFile, TarInfo
from tempfile import NamedTemporaryFile

__all__ = ['make_dockerfile', 'validate_file']


class TarReader(io.IOBase):
    def __init__(self, content, encoding=None):
        self.content = content
        self.content.seek(0)
        self.content_type = 'application/tar'
        self.encoding = encoding

    def read(self):
        return self.content.read()


@asyncio.coroutine
def make_dockerfile(obj):
    """Transform obj to a docker tar.
    """

    if isinstance(obj, TarReader):
        return obj

    if isinstance(obj, str) and os.path.isfile(obj):
        archive = None
        ext = os.path.splitext(obj)
        if ext == '.tar':
            encoding = None
            archive = True
        elif ext in ('.tgz', '.gz'):
            encoding = 'gzip'
            archive = True
        elif ext in ('.tbz', '.tbz2', '.tb2', '.bz2'):
            encoding = 'bz2'
            archive = True
        elif ext in ('.tz', '.Z'):
            encoding = 'compress'
            archive = True
        elif ext in ('.tlz', '.lz', '.lzma'):
            encoding = 'lzma'
            archive = True
        elif ext in ('.txz', '.xz'):  # lzma & lzma2
            encoding = 'xz'
            archive = True

        with open(obj, 'rb') as file:
            if archive:
                return TarReader(file, encoding)

            # Let's pretend it's a single Dockerfile. Open it
            try:
                obj = TarFile.open(fileobj=file)
            except TarError:
                obj = io.BytesIO(file.read())

    if isinstance(obj, str) and os.path.isdir(obj):
        raise NotImplementedError('Currently not implemented')

    if isinstance(obj, str):
        raise ValueError('%r is not a Dockerfile' % obj)

    if isinstance(obj, io.StringIO):
        obj = io.BytesIO(obj.getvalue().encode('utf-8'))

    if isinstance(obj, io.BytesIO):
        out = io.BytesIO()
        info = TarInfo('Dockerfile')
        info.size = len(obj.getvalue())
        tar = TarFile.open(fileobj=out, mode='w')
        tar.addfile(info, obj)
        tar.close()
        obj = tar

    if isinstance(obj, str) and os.path.isdir(obj):
        # it's a docker context, Make a tar and compress it
        tar = TarFile.open(fileobj=NamedTemporaryFile(), mode='w:gz')
        tar.add(obj, arcname='.')
        tar.close()
        obj = tar.fileobj

    if isinstance(obj, TarFile):
        obj.close()
        obj = obj.fileobj

    if isinstance(obj, gzip.GzipFile):
        return TarReader(obj, 'gzip')

    if isinstance(obj, bz2.BZ2File):
        return TarReader(obj, 'bz2')

    if isinstance(obj, lzma.LZMAFile):
        return TarReader(obj, 'xz')

    return TarReader(obj)


@asyncio.coroutine
def validate_file(src):
    if isinstance(src, str):
        return src, None
    elif isinstance(src, io.BytesIo):
        return '-', src
    raise ValueError('src must be a filename')
