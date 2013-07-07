def test_types_support():
    from dash_py.cli import load_packages, PACKAGES
    load_packages()
    from dash_py.installer import INSTALLER

    for package in PACKAGES:
        assert package["type"] in INSTALLER
