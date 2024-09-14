fsspec-manager
==============

Curses TUI for `fsspec` filesystems. 
Optimized for interactive use with the python repl and extensibility.
Looks made to mimic [lf](https://github.com/gokcehan/lf).

Goals:
- simple and easy to audit code
- easy extensibility through python to support custom filesystems

Non-goals:
- performance
- non-read-only features
- complicated operations - these should be added by the user

Installation
------------

```
pip install fsspec-manager
```

Basic usage
-----------

```
from fsman import fsman
from fsspec import filesystem

fs = filesystem('local')
man = fsman(fs)

# get state of manager when it exited
man.path
man.cwd
man.ls
```

To launch a IPython REPL from the manager, press 'w'.
