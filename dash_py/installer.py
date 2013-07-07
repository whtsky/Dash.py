import os
import shutil
import time

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

import requests
from .utils import logger

DEFAULT_DOCSET_PATH = os.path.expanduser(
    '~/Library/Application Support/dash.py/DocSets'
)

random_path = lambda: os.path.join("/tmp", str(time.time()))


def add_to_dash(docset_path):
    logger.info("Adding package to Dash")
    os.system('open -a dash "%s"' % docset_path)


def generate_docset(package, document_path):
    name = package["name"]
    logger.info("Creating docset for package %s" % name)
    docset_path = os.path.join(DEFAULT_DOCSET_PATH, "%s.docset" % name)
    if os.path.exists(docset_path):
        shutil.rmtree(docset_path)
    command = 'doc2dash --name %s --destination "%s" --quiet' % (name, DEFAULT_DOCSET_PATH)
    if "icon" in package:
        command += " --icon %s" % os.path.join(document_path, package["icon"])
    command += " %s" % document_path
    os.system(command)

    shutil.rmtree(document_path)

    add_to_dash(docset_path)


def zip_installer(package):
    name = package["name"]
    import requests
    logger.info("Downloading package %s" % name)
    dirname = random_path()

    zip_content = requests.get(package["url"]).content

    f = StringIO()
    f.write(zip_content)

    logger.info("Unzipping package %s" % name)
    import zipfile
    with zipfile.ZipFile(f) as z:
        z.extractall(dirname)
    f.close()

    if "floder_name" not in package:
        files = os.listdir(dirname)
        if len(files) == 1:
            package["floder_name"] = files[0]

    document_path = os.path.join(dirname, package.get("floder_name", ""))
    return generate_docset(package, document_path)


def rtfd_docset_installer(package):
    name = package["name"]
    logger.info("Downloading package %s" % name)
    import requests
    r = requests.get(package["url"])

    f = StringIO()
    f.write(r.content)
    f.seek(0)

    import tarfile
    with tarfile.open(fileobj=f) as t:
        t.extractall(DEFAULT_DOCSET_PATH)
    f.close()

    docset_path = os.path.join(DEFAULT_DOCSET_PATH, name+'.docset')
    add_to_dash(docset_path)


INSTALLER = {
    'zip': zip_installer,
    'rtfd_docset': rtfd_docset_installer,
}


def install_package(package):
    name = package["name"]
    type = package["type"]
    if type not in INSTALLER:
        logger.error("Unknown type %s." % type)
    
    installer = INSTALLER[type]
    
    installer(package)

