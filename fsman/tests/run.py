import fsspec
from fsman import fsman

def run_local():
    fs = fsspec.filesystem('local')
    fsman(fs)

if __name__ == '__main__':
    run_local()
