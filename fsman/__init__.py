from typing import TYPE_CHECKING
from .manager import FSManager as FSManager

if TYPE_CHECKING:
    import fsspec

def fsman(fs: 'fsspec.AbstractFileSystem', cwd='/', name=None):
    man = FSManager(fs, cwd=cwd)
    man.explore()
    return man
