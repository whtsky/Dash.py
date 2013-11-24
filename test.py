import os
import yaml

from dash_py.cli import PACKAGES_PATH
from dash_py.installer import DEFAULT_DOCSET_PATH
from dash_py.utils import call


def assert_docset_exists(name):
    plist_path = os.path.join(DEFAULT_DOCSET_PATH, '%s.docset' % name,
                              'Contents/Info.plist')
    assert os.path.exists(plist_path), name


def test_packages():
    for f in os.listdir(PACKAGES_PATH):
        if not f.endswith('.yaml'):
            continue
        path = os.path.join(PACKAGES_PATH, f)
        package = yaml.load(open(path, "r").read())
        name = package["name"]
        call("dash.py install %s" % name.lower(), silence=False)
        assert_docset_exists(name)


def test_download_docset_from_rtfd():
    call("dash.py install requests", silence=False)
    assert_docset_exists("requests")


def test_download_zip_from_rtfd():
    call("dash.py install chump", silence=False)
    assert_docset_exists("Chump")
