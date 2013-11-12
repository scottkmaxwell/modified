__author__ = 'Scott Maxwell'
__version__ = "1.04"
__project_url__ = "https://github.com/codecobblers/modified"

# Copyright (C) 2013 by Scott Maxwell
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
modified tracks the files of the currently running application and facilitates
restart if any files have changed. By default it will track all Python files,
including all modules loaded by the app. If there are additional files you
need to track such as config files, templates, etc., you can add those using
the track function.

The simplest usage is to simply run the hup_hook. By default, this will build
a dict of all currently loaded code files with their timestamps and register
a handler for `signal.SIGHUP`. When the application receives `signal.SIGHUP`,
the hook will check to see if any of the files have been modified, and issue
`signal.SIGTERM`, if so.

@note: If a file ends in `.pyc`, `modified` will attempt to retrieve
the timestamp from the `.py` file instead.


"""

import sys
import os
import signal

_process_files = {}
_scanned = False
if sys.version_info[0] == 3 and sys.version_info[1] < 3:
    from collections import Callable

    #noinspection PyShadowingBuiltins
    def callable(o):
        return isinstance(o, Callable)


def _get_filename_and_modified(filename):
    path = filename
    while path:
        try:
            if path.endswith('.pyc'):
                try:
                    return path[:-1], os.stat(path[:-1]).st_mtime
                except Exception:
                    pass
            return path, os.stat(path).st_mtime
        except Exception:
            path = os.path.dirname(path)
            if os.path.isdir(path):
                break
    return None, 0


def _get_modified(filename):
    try:
        return os.stat(filename).st_mtime
    except Exception:
        return 0


def module_files(module, dependencies_dict=None):
    """
    Scan a module and its entire dependency tree to create a dict of all files
    and their modified time.

    @param module: A <module> object
    @param dependencies_dict: Pass an existing dict to add only unscanned
        files or None to create a new file dict
    @return: A dict containing filenames as keys with their modified time
        as value
    """
    if dependencies_dict is None:
        dependencies_dict = dict()
    if hasattr(module, '__file__'):
        filename = module.__file__
        if filename not in dependencies_dict:
            realname, modified_time = _get_filename_and_modified(filename)
            if realname and realname not in dependencies_dict:
                dependencies_dict[realname] = modified_time
                for name in dir(module):
                    try:
                        item = getattr(module, name)
                        if hasattr(item, '__file__'):
                            module_files(item, dependencies_dict)
                        elif hasattr(item, '__module__'):
                            item = sys.modules[getattr(item, '__module__')]
                            if hasattr(item, '__file__'):
                                module_files(item, dependencies_dict)
                    except (AttributeError, KeyError):
                        pass
    return dependencies_dict


def files():
    """
    Scan all modules in the currently running app to create a dict of all
    files and their modified time.

    @note The scan only occurs the first time this function is called.
        Subsequent calls simply return the global dict.

    @return: A dict containing filenames as keys with their modified time
        as value
    """
    if not _scanned:
        if not module_files(sys.modules['__main__'], _process_files):
            for module in sys.modules.values():
                if hasattr(module, '__file__'):
                    filename = module.__file__
                    if filename not in _process_files:
                        realname, modified_time = _get_filename_and_modified(filename)
                        if realname and realname not in _process_files:
                            _process_files[realname] = modified_time
    return _process_files


def modified():
    """
    Get the modified list.

    @return: A list of all tracked files that have been modified since the
        initial scan.
    """
    return [filename for filename, modified_timestamp in _process_files.items() if modified_timestamp != _get_modified(filename)]


def track(*args):
    """
    Track additional files. It is often useful to use glob.glob here.
    For instance:

        track('config.ini', glob.glob('templates/*.pt'), glob.glob('db/*.db'))

    @param args: A list where each element is either a filename or an
        iterable of filenames
    """
    for arg in args:
        if isinstance(arg, str):
            arg = [arg]
        for filename in arg:
            realname, modified_time = _get_filename_and_modified(filename)
            if realname and realname not in _process_files:
                _process_files[realname] = modified_time


def hup_hook(signal_or_callable=signal.SIGTERM, verbose=False):
    """
    Register a signal handler for `signal.SIGHUP` that checks for modified
    files and only acts if at least one modified file is found.

    @type signal_or_callable: str, int or callable
    @param signal_or_callable: You can pass either a signal or a callable.
        The signal can be specified by name or number. If specifying by name,
        the 'SIG' portion is optional. For example, valid values for SIGINT
        include 'INT', 'SIGINT' and `signal.SIGINT`.

        Alternatively, you can pass a callable that will be called with the list
        of changed files. So the call signature should be `func(list)`. The return
        value of the callable is ignored.
    @type verbose: bool or callable
    @param verbose: Defaults to False. True indicates that a message should be
        printed. You can also pass a callable such as log.info.
    """

    #noinspection PyUnusedLocal
    def handle_hup(signum, frame):
        changed = modified()
        if changed:
            if callable(signal_or_callable):
                func = signal_or_callable
                args = (changed,)
                op = 'Calling'
                try:
                    name = signal_or_callable.__name__
                except Exception:
                    name = str(signal_or_callable)
            else:
                if isinstance(signal_or_callable, int):
                    name = str(signal_or_callable)
                    signum = signal_or_callable
                    if verbose:
                        for item in dir(signal):
                            if item.startswith('SIG') and getattr(signal, item) == signal_or_callable:
                                name = item
                                break
                else:
                    name = signal_or_callable if signal_or_callable.startswith('SIG') else 'SIG' + signal_or_callable
                    signum = getattr(signal, name)
                func = os.kill
                args = (os.getpid(), signum)
                op = 'Sending'
            if verbose:
                more = ' and {0} other files'.format(len(changed)) if len(changed) > 1 else ''
                message = '{0} {1} because {2}{3} changed'.format(op, name, changed[0], more)
                if callable(verbose):
                    #noinspection PyCallingNonCallable
                    verbose(message)
                else:
                    print(message)
            func(*args)

    files()
    signal.signal(signal.SIGHUP, handle_hup)
    signal.siginterrupt(signal.SIGHUP, False)
