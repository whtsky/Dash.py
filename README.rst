Dash.py
=======

Dash.py is a tool that helps you install python documents to Dash easily.

Usage
-------------

Installing python documents to Dash via Dash.py is easy ::

    dash.py install flask
    dash.py install tornado jinja2 sqlalchemy


Installation
--------------

You can install dash.py via pip ::

    pip install dash.py

If you don't have pip, you should install it first ::

    curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python

Adding a package
------------------

.. note:: You don't need to add a package which is hosted on rtfd.org . Dash.py can download docset from rtfd.org automatically.


It's pretty easy to add a new package in Dash.py :

* Fork the project
* Add a new file in dash_py/packages folder.

Filename should be ``package_name.yaml`` . Now that package name should be lower case.

It should be a vailed yaml file.

It looks like ::

    name: Jinja2 # Package name
    type: html # Type. Supported types are ``html`` and ``sphinx``
    format: zip  # Format. Should be either ``zip``, ``tar`` or ``git``. Note that Gzipped Tar file should be ``tar``
    url: http://jinja.pocoo.org/docs/jinja-docs.zip  # URL to download the file or to clone the git repo.
    icon: _static/jinja-small.png  # OPTIONAL. path to icon file.
    sphinx_doc_path: doc  # OPTIONAL. If the type is sphinx and sphinx conf file isn't in the root path, you need to provide this.


* git add && git commit
* Send a pull request.