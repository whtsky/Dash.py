import os
import sys
import time
import logging
import tempfile
import zipfile
import tarfile
import requests
import subprocess

try:
    import curses
    assert curses
except ImportError:
    curses = None

# Fake unicode literal support:  Python 3.2 doesn't have the u'' marker for
# literal strings, and alternative solutions like "from __future__ import
# unicode_literals" have other problems (see PEP 414).  u() can be applied
# to ascii strings that include \u escapes (but they must not contain
# literal non-ascii characters).
if type('') is not type(b''):
    def u(s):
        return s

    bytes_type = bytes
    unicode_type = str
    basestring_type = str
else:
    def u(s):
        return s.decode('unicode_escape')

    bytes_type = str
    unicode_type = unicode
    basestring_type = basestring

logger = logging.getLogger("dash.py")


def resource_exist(url):
    r = requests.head(url)
    try:
        r.raise_for_status()
        return True
    except requests.HTTPError:
        return False


def call(command, silence=True, **kwargs):
    if silence:
        kwargs["stderr"] = subprocess.PIPE
        kwargs["stdout"] = subprocess.PIPE
    kwargs.setdefault("shell", True)
    code = subprocess.call(command, **kwargs)
    return code == 0


def download_and_extract(package, extract_path):
    name = package["name"]
    url = package["url"]
    format = package["format"]
    if format == 'git':
        logger.info("Cloning package %s" % name)
        if not call("git clone %s %s" % (url, extract_path)):
            logger.error("Can't clone package %s" % name)
            sys.exit(5)
        return
    elif format == 'hg':
        logger.info("Cloning package %s" % name)
        if not call("hg clone %s %s" % (url, extract_path)):
            logger.error("Can't clone package %s" % name)
            sys.exit(5)
        return

    logger.info("Downloading package %s" % name)
    r = requests.get(url)
    if r.status_code != 200:
        logger.error("Can't download package %s" % name)
        sys.exit(5)
    downloaded_file_path = tempfile.mkstemp()[1]
    with open(downloaded_file_path, "wb") as f:
        f.write(r.content)

    file = None

    with open(downloaded_file_path, "r") as f:

        if format == 'zip':
            file = zipfile.ZipFile(f)
        elif format == 'tar':
            file = tarfile.open(fileobj=f)

        try:
            file.extractall(extract_path)
        except:
            logger.error("Can't extract package %s" % name)
            sys.exit(1)
    file.close()
    os.remove(downloaded_file_path)


def enable_pretty_logging(level='info'):
    """Turns on formatted logging output as configured.

    This is called automatically by `parse_command_line`.
    """
    logger.setLevel(getattr(logging, level.upper()))

    if not logger.handlers:
        # Set up color if we are in a tty and curses is installed
        color = False
        if curses and sys.stderr.isatty():
            try:
                curses.setupterm()
                if curses.tigetnum("colors") > 0:
                    color = True
            except Exception:
                pass
        channel = logging.StreamHandler()
        channel.setFormatter(_LogFormatter(color=color))
        logger.addHandler(channel)


class _LogFormatter(logging.Formatter):
    def __init__(self, color, *args, **kwargs):
        logging.Formatter.__init__(self, *args, **kwargs)
        self._color = color
        if color:

            # The curses module has some str/bytes confusion in
            # python3.  Until version 3.2.3, most methods return
            # bytes, but only accept strings.  In addition, we want to
            # output these strings with the logging module, which
            # works with unicode strings.  The explicit calls to
            # unicode_type() below are harmless in python2 but will do the
            # right conversion in python 3.
            fg_color = (curses.tigetstr("setaf") or
                        curses.tigetstr("setf") or "")
            if (3, 0) < sys.version_info < (3, 2, 3):
                fg_color = unicode_type(fg_color, "ascii")
            self._colors = {
                logging.DEBUG: unicode_type(curses.tparm(fg_color, 4),
                                            "ascii"),  # Blue
                logging.INFO: unicode_type(curses.tparm(fg_color, 2),
                                           "ascii"),  # Green
                logging.WARNING: unicode_type(curses.tparm(fg_color, 3),
                                              "ascii"),  # Yellow
                logging.ERROR: unicode_type(curses.tparm(fg_color, 1),
                                            "ascii"),  # Red
            }
            self._normal = unicode_type(curses.tigetstr("sgr0"), "ascii")

    def format(self, record):
        try:
            record.message = record.getMessage()
        except Exception as e:
            record.message = "Bad message (%r): %r" % (e, record.__dict__)
        record.asctime = time.strftime(
            "%y%m%d %H:%M:%S", self.converter(record.created))
        prefix = '[%(levelname)1.1s %(asctime)s]' % record.__dict__
        if self._color:
            prefix = (self._colors.get(record.levelno, self._normal) +
                      prefix + self._normal)
        formatted = prefix + " " + record.message
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            formatted = formatted.rstrip() + "\n" + record.exc_text
        return formatted.replace("\n", "\n    ")
