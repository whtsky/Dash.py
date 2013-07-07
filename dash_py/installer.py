import os
import shutil
import time

from .uncompress import uncompress
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
    command = 'doc2dash --name %s --destination "%s" --quiet' % (
        name, DEFAULT_DOCSET_PATH)
    if "icon" in package:
        icon_path = package["icon"]
        if "//" in icon_path:
            import requests
            r = requests.get(icon_path)
            if r.status_code == 200:
                icon_path = random_path() + '.png'
                with open(icon_path, "w") as f:
                    f.write(r.content)
                command += " --icon %s" % icon_path
        else:
            command += " --icon %s" % os.path.join(document_path, icon_path)
    command += " %s" % document_path
    os.system(command)

    shutil.rmtree(document_path)

    add_to_dash(docset_path)


def html_installer(package):
    name = package["name"]
    logger.info("Downloading package %s" % name)
    dirname = random_path()
    uncompress(package["url"], dirname, package.get("format", None))

    if "floder_name" not in package:
        files = os.listdir(dirname)
        if len(files) == 1:
            package["floder_name"] = files[0]

    document_path = os.path.join(dirname, package.get("floder_name", ""))
    return generate_docset(package, document_path)


def docset(package):
    name = package["name"]
    logger.info("Downloading package %s" % name)
    uncompress(package["url"], DEFAULT_DOCSET_PATH, "tar")

    docset_path = os.path.join(DEFAULT_DOCSET_PATH, name + '.docset')
    add_to_dash(docset_path)


INSTALLER = {
    'html': html_installer,
    'docset': docset,
}


def install_package(package):
    type = package["type"]
    if type not in INSTALLER:
        logger.error("Unknown type %s." % type)

    installer = INSTALLER[type]

    installer(package)
