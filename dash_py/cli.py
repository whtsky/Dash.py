"""
Dash.py

Usage:
    dash.py install <name>
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
        dash.py install <name>

    Options:
        -h --help             Show this screen and exit.
    """
    name = name.lower()
    

    # Try to download document from rtfd
    import requests
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
                "type": "rtfd_docset",
                "url": url
            })
            return


def main():
    enable_pretty_logging()
    parguments.run()
