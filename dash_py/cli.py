"""
Dash.py

Usage:
    dash.py install <name>...
    dash.py --version

Options:
    -h --help             Show this screen and exit.
"""

import os
import yaml
import requests
import dash_py

PACKAGES_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    "packages"
)

from bs4 import BeautifulSoup
from parguments import Parguments
from .installer import install_package
from .utils import enable_pretty_logging, logger, resource_exist

parguments = Parguments(__doc__, version=dash_py.__version__)


@parguments.command
def install(name):
    """
    Usage:
        dash.py install <name>...

    Options:
        -h --help             Show this screen and exit.
    """
    if isinstance(name, list):
        return [install(n) for n in name]

    content = ""
    name = name.lower()
    if os.path.exists(name):
        content = open(name, "r").read()
    else:
        if '//' in name:
            url = name
        else:
            url = "https://raw.github.com/whtsky/Dash.py/" \
                  "master/dash_py/packages/%s.yaml" % name
        if resource_exist(url):
            r = requests.get(url)
            content = r.content

    if content:
        package = yaml.load(content)
        install_package(package)
        return

    # Try to download document from rtfd
    r = requests.get("https://readthedocs.org/projects/%s/downloads/" % name)
    if r.status_code != 200:
        logger.error("Can't find package %s" % name)
        return

    name = BeautifulSoup(r.content).title.string.split("|")[0].strip()
    html_content = str(r.content)

    for branch in ['stable', 'master', 'latest']:
        if branch not in html_content:
            continue
        docset_url = "https://media.readthedocs.org/dash/" \
                     "{0}/{1}/{2}.tgz".format(name.lower(), branch, name)
        zip_url = "https://media.readthedocs.org/htmlzip/" \
                  "{0}/{1}/{0}.zip".format(name.lower(), branch)
        if resource_exist(docset_url):
            install_package({
                "name": name,
                "type": "docset",
                "url": docset_url,
                "format": "tar"
            })
            return
        elif resource_exist(zip_url):
            install_package({
                "name": name,
                "type": "html",
                "url": zip_url,
                "format": "zip"
            })
            return

    logger.error("Can't find package %s" % name)
    return -1


def main():
    enable_pretty_logging()
    parguments.run()
