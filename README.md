Summary
=======

modified tracks the files of the currently running application and facilitates
restart if any files have changed. By default it will track all Python files,
including all modules loaded by the app. If there are additional files you
need to track such as config files, templates, etc., you can add those using
a glob pattern.

The simplest usage is to simply run the hup_hook. By default, this will build
a dict of all currently loaded code files with their timestamps and register
a handler for `signal.SIGHUP`. When the application receives `signal.SIGHUP`,
the hook will check to see if any of the files have been modified, and issue
`signal.SIGTERM`, if so.

**IMPORTANT**: If a file ends in **.pyc**, `modified` will attempt to retrieve
the timestamp from the **.py** file instead.

    >>> import modified
    >>> modified.hup_hook()


Installation
============

    $> pip install modified


Functions
=========

`files()`
---------

Scan all modules in the currently running app to create a dict of all files
and their modified time.

The scan only occurs the first time this function is called. Subsequent calls
simply return the global dict.

    >>> import modified
    >>> modified.files()
    {'.../env32/lib/python3.2/copyreg.py': 1368477498.0,
     '.../env32/lib/python3.2/_weakrefset.py': 1368477497.0,
     '.../env32/lib/python3.2/os.py': 1368477498.0,
     'modified.py': 1384228495.0,
     '.../env32/lib/python3.2/genericpath.py': 1368477498.0,
     '.../env32/lib/python3.2/abc.py': 1368477497.0,
     '.../env32/lib/python3.2/posixpath.py': 1368477498.0,
     '.../env32/lib/python3.2/stat.py': 1368477498.0,
     '.../env32/lib/python3.2/_abcoll.py': 1368477497.0}

`module_files(module, dependencies_dict=None)`
----------------------------------------------

Scan a module and its entire dependency tree to create a dict of all files
and their modified time.

Pass an existing dict to add only unscanned files or None to create a new
file dict

    >>> import modified
    >>> import sh
    >>> modified.module_files(sh)
    {'.../env32/lib/python3.2/site-packages/sh-1.09-py3.2.egg/sh.py': 1384230023.0}

`modified()`
------------

Return the list of files modified since the initial scan.

    >>> import modified
    >>> modified.files()
    {'.../env32/lib/python3.2/copyreg.py': 1368477498.0,
     '.../env32/lib/python3.2/_weakrefset.py': 1368477497.0,
     '.../env32/lib/python3.2/os.py': 1368477498.0,
     'modified.py': 1384228495.0,
     '.../env32/lib/python3.2/genericpath.py': 1368477498.0,
     '.../env32/lib/python3.2/abc.py': 1368477497.0,
     '.../env32/lib/python3.2/posixpath.py': 1368477498.0,
     '.../env32/lib/python3.2/stat.py': 1368477498.0,
     '.../env32/lib/python3.2/_abcoll.py': 1368477497.0}
    >>> open('modified.py', 'a+').close()
    >>> modified.modified()
    ['modified.py']

`track(*args)`
--------------

Track additional files. It is often useful to use glob.glob here.
For instance:

    >>> import modified
    >>> import glob
    >>> modified.track('config.ini', glob.glob('templates/*.pt'), glob.glob('db/*.db'))

`hup_hook(signal_or_callable=signal.SIGTERM, verbose=False)`
------------------------------------------------------------

Register a signal handler for `signal.SIGHUP` that checks for modified
files and only acts if at least one modified file is found.

You can pass either a signal or a callable for `signal_or_callable`.
The signal can be specified by name or number. If specifying by name,
the 'SIG' portion is optional. For example, valid values for SIGINT
include 'INT', 'SIGINT' and `signal.SIGINT`.

Alternatively, you can pass a callable that will be called with the list
of changed files. So the call signature should be `func(list)`. The return
value of the callable is ignored.

The `verbose` parameter can be True, False or a callable. True indicates that
a message should be printed. A callable will be called with the message to
print.

    >>> import modified
    >>> import logging
    >>> modified.hup_hook('INT', logging.info)
    ...
    Sending SIGINT because modified.py and 3 other files changed.

With a callable:

    >>> import modified
    >>> import logging
    >>> shutting_down = False
    >>> def set_shutdown():
    ...     global shutting_down
    ...     shutting_down = True
    >>> modified.hup_hook(set_shutdown)
    ...
    Calling set_shutdown because modified.py and 3 other files changed.
