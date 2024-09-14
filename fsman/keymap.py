import curses
import os

def cursor_first(self, k):
    self.movecursor(0)

def cursor_page_up(self, k):
    self.movecursor(self.cursor-30)

def cursor_halfpage_up(self, k):
    self.movecursor(self.cursor-60)

def cursor_up(self, k):
    self.movecursor(self.cursor-1)

def cursor_down(self, k):
    self.movecursor(self.cursor+1)

def cursor_halfpage_down(self, k):
    self.movecursor(self.cursor+30)

def cursor_page_down(self, k):
    self.movecursor(self.cursor+60)

def cursor_last(self, k):
    self.movecursor(len(self.ls)-1)


def quit(self, k):
    self.stop = True

def enter(self, k):
    try:
        cur = self.ls[self.cursor]
        if cur['type'] == 'directory':
            self.cwd = cur['name']
            if not self.cwd.endswith('/'):
                self.cwd = self.cwd + '/'
            if not self.cwd.startswith('/'):
                self.cwd = '/' + self.cwd
            self.parent_cursor = self.cursor
            self.parent_wincursor = self.wincursor
            self.movecursor(0)
    except IndexError:
        pass

def cmd(self, k):
    pass

def dirup(self, k):
    if self.cwd != '/':
        self.cwd = os.path.dirname(self.cwd.rstrip('/'))
        if not self.cwd.endswith('/'):
            self.cwd = self.cwd + '/'
        if not self.cwd.startswith('/'):
            self.cwd = '/' + self.cwd
        self.cursor = self.parent_cursor
        self.wincursor = self.parent_wincursor
        self.parent_cursor = 0
        self.parent_wincursor = 0

def shell(self, k):
    curses.endwin()
    try:
        import IPython
    except ImportError:
        return
    user_ns = {
        'fs': self.fs,
        'fsman': self,
        'cwd': self.cwd,
        'path': self.ls[self.cursor]['name'],
        'ls': self.ls,
    }
    header = 'Available variables: ' + ', '.join(user_ns.keys())
    IPython.embed(colors='neutral', header=header, user_ns=user_ns)

DEFAULT_KEYMAP = {
    ord('w'): shell,
    ord('h'): dirup,
    ord(':'): cmd,
    ord('l'): enter,
    ord('q'): quit,
    ord('G'): cursor_last,
    6: cursor_page_down,          # ^F
    338: cursor_page_down,        # pagedown
    4: cursor_halfpage_down,      # ^D
    ord('j'): cursor_down,
    258: cursor_down,             # down
    ord('k'): cursor_up,
    259: cursor_up,               # up
    21: cursor_halfpage_up,       # ^U
    2: cursor_page_up,            # ^B
    339: cursor_page_up,          # pageup
    ord('g'): cursor_first,
}
