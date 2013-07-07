import zipfile
import tarfile
import requests

from .utils import logger

try:
    from cStringIO import StringIO
    assert StringIO
except ImportError:
    try:
        from StringIO import StringIO
        assert StringIO
    except ImportError:
        from io import StringIO
        assert StringIO


def uncompress(url, extract_path, type=None):
    f = StringIO()
    f.write(requests.get(url).content)
    f.seek(0)

    file = None

    if type == 'zip':
        file = zipfile.ZipFile(f)
    elif type == 'tar':
        file = tarfile.open(fileobj=f)

    if not file:
        try:
            file = tarfile.open(fileobj=f)
            assert file
        except tarfile.ReadError:
            try:
                file = zipfile.ZipFile(f)
            except zipfile.BadZipfile:
                logger.error("Unknown type for %s" % url)
                import sys
                sys.exit(4)

    file.extractall(extract_path)
    file.close()
    f.close()
