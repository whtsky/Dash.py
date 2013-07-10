import os
import yaml

from dash_py.cli import PACKAGES_PATH
from dash_py.installer import DEFAULT_DOCSET_PATH
from dash_py.utils import call


def assert_docset_exists(name):
    plist_path = os.path.join(DEFAULT_DOCSET_PATH, '%s.docset' % name,
                              'Contents/Info.plist')
    assert os.path.exists(plist_path), name


def test():
    for f in os.listdir(PACKAGES_PATH):
        if not f.endswith('.yaml'):
            continue
        path = os.path.join(PACKAGES_PATH, f)
        package = yaml.load(open(path, "r").read())
        name = package["name"]
        call("dash.py install %s" % name.lower())
        assert_docset_exists(name)

    # Download from RTFD
    call("dash.py install requests")
    assert_docset_exists("requests")
