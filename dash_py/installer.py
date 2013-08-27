import os
import tempfile
import shutil
import requests

from .utils import download_and_extract, logger, call

DEFAULT_DOCSET_PATH = os.path.expanduser(
    '~/Library/Application Support/dash.py/DocSets'
)


def add_to_dash(docset_path):
    logger.info("Adding package to Dash")
    call('open -a dash "%s"' % docset_path)


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
            r = requests.get(icon_path)
            if r.status_code == 200:
                icon_path = tempfile.mkstemp('.png')[1]
                with open(icon_path, "w") as f:
                    f.write(r.content)
                command += " --icon %s" % icon_path
        else:
            command += " --icon %s" % os.path.join(document_path, icon_path)
    command += " %s" % document_path
    if call(command):
        add_to_dash(docset_path)
    else:
        logger.error("Can't generate docset for package %s" % name)

    shutil.rmtree(document_path)


def html_installer(package):
    dirname = tempfile.mkdtemp()
    download_and_extract(package, dirname)

    if "floder_name" not in package:
        files = os.listdir(dirname)
        if len(files) == 1:
            package["floder_name"] = files[0]

    document_path = os.path.join(dirname, package.get("floder_name", ""))
    generate_docset(package, document_path)


def docset(package):
    name = package["name"]
    package["type"] = "tar"
    download_and_extract(package, DEFAULT_DOCSET_PATH)

    docset_path = os.path.join(DEFAULT_DOCSET_PATH, name + '.docset')
    add_to_dash(docset_path)


def sphinx(package):
    repo_path = tempfile.mkdtemp()
    download_and_extract(package, repo_path)
    doc_path = package.get("sphinx_doc_path", "docs")
    doc_path = os.path.join(repo_path, doc_path)

    document_path = tempfile.mkdtemp()
    command = "sphinx-build -b html %s %s" % (doc_path, document_path)
    if call(command):
        generate_docset(package, document_path)
        shutil.rmtree(repo_path)
    else:
        logger.error("Can't build doc for package %s" % package["name"])


INSTALLER = {
    'html': html_installer,
    'docset': docset,
    'sphinx': sphinx
}


def install_package(package):
    type = package["type"]
    if type not in INSTALLER:
        logger.error("Unknown type %s." % type)

    installer = INSTALLER[type]

    installer(package)
