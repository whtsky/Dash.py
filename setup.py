from setuptools import setup, find_packages

import dash_py


setup(
    name='dash.py',
    version=dash_py.__version__,
    description=dash_py.__doc__.strip(),
    long_description=open('README.rst').read(),
    url='https://github.com/whtsky/Dash.py',
    license=dash_py.__license__,
    author=dash_py.__author__,
    author_email='whtsky@gmail.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'dash.py = dash_py.cli:main',
        ],
    },
    install_requires=open('requirements.txt').readlines(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Documentation',
        'Topic :: Software Development',
        'Topic :: Software Development :: Documentation',
        'Topic :: Text Processing',
    ],
    tests_require=['nose'],
    test_suite='nose.collector',
)
