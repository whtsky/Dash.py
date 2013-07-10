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

PACKAGES_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    "packages"
)

import dash_py
from parguments import Parguments
from .installer import install_package
from .utils import enable_pretty_logging, logger

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
        r = requests.head(url)
        if r.status_code == 200:
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

    from pyquery import PyQuery
    name = PyQuery(r.content)("title").html().split("|")[0].strip()

    for branch in ['stable', 'master', 'latest']:
        if branch not in r.content:
            continue
        url = "https://media.readthedocs.org/dash/" \
              "{0}/{1}/{2}.tgz".format(name.lower(), branch, name)
        if requests.head(url).status_code == 200:
            install_package({
                "name": name,
                "type": "docset",
                "url": url
            })
            return
    logger.error("Can't find package %s" % name)


def main():
    enable_pretty_logging()
    parguments.run()
