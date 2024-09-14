import curses
import os.path
from datetime import datetime

from .cmd import DEFAULT_CMD
from .keymap import DEFAULT_KEYMAP

class FSManager():

    keymap = DEFAULT_KEYMAP
    cmd = DEFAULT_CMD

    def __init__(self, fs, *, url=None, cwd='/'):
        # copy the dict so that when it is updated on an instance,
        # the classvar is untouched
        self.keymap = self.keymap.copy()
        self.cmd = self.cmd.copy()

        self.fs = fs
        if url is None:
            url = self.besteffort_url()
        self.url = url
        if not cwd.endswith('/'):
            cwd = cwd + '/'
        if not cwd.startswith('/'):
            cwd = '/' + cwd
        self.cwd = cwd

        self.cursor = 0
        self.wincursor = 0
        self.parent_cursor = 0
        self.parent_wincursor = 0

    def besteffort_url(self):
        protocol = self.fs.protocol
        if isinstance(protocol, tuple):
            protocol = protocol[0]
        if self.fs.protocol in ('local', 'file'):
            import getpass
            import platform
            user = getpass.getuser()
            host = platform.node()
            return f'file://{user}@{host}'
        elif self.fs.protocol in ('az', 'abfs'):
            account_name = self.fs.account_name
            return f'az://{account_name}'
        return f'{protocol}:'

    def update(self):
        self.ls = sorted(self.fs.listdir(self.cwd, detail=True), key=lambda f: (f['type'], f['name']))
        self.parent_ls = sorted(self.fs.listdir(os.path.dirname(self.cwd.rstrip('/'))), key=lambda f: (f['type'], f['name'])) if self.cwd != '/' else []

    def explore(self):
        return curses.wrapper(self.main)

    def main(self, stdscr):
        self.init(stdscr)
        self.stop = False

        while not self.stop:
            self.update()
            self.drawdir()
            self.drawparent()
            self.drawhead()
            self.drawstatus()

            k = stdscr.getch()
            try:
                action = self.keymap[k]
            except KeyError:
                curses.endwin()
                print(k)
                input()
                continue
            action(self, k)

    def cmdmode(self):
        ...

    def movecursor(self, where):
        height, _ = self.win_r.getmaxyx()
        where = min(len(self.ls) - 1, where)
        where = max(0, where)
        self.cursor = where
        self.wincursor = max(self.wincursor, where - height + 1)
        self.wincursor = min(self.wincursor, where)

    def drawstatus(self):
        self.win_status.erase()
        _, width = self.win_status.getmaxyx()
        try:
            cur = self.ls[self.cursor]
        except IndexError:
            return
            self.win_status.refresh()
        try:
            size = cur['size']
            if size is None:
                size = ''
            else:
                size = str(size)+'B'
        except KeyError:
            size = ''
        self.win_status.addstr(0, 0, size)
        try:
            mtime = datetime.fromtimestamp(cur['mtime']).strftime('%c')
        except KeyError:
            mtime = ''
        self.win_status.addstr(0, len(size)+2, mtime)
        if self.cursor < len(self.ls):
            pos = f'{self.cursor+1}/{len(self.ls)}'
            try:
                self.win_status.addstr(0, width-len(pos), pos)
            except curses.error:
                pass  # curses bug
        self.win_status.refresh()


    def drawls(self, win, items, wincursor, cursor):
        win.erase()
        height, width = win.getmaxyx()
        for i, f in enumerate(items[wincursor:wincursor+height]):
            if f['type'] == 'directory':
                col = self.color_dir
            else:
                col = self.color_file
            if i + wincursor == cursor:
                col |= curses.A_REVERSE
            try:
                win.addstr(i, 0, self.pad(os.path.basename(f['name']), width), col)
            except curses.error:
                pass  # curses bug
        win.refresh()

    def drawdir(self):
        self.drawls(self.win_r, self.ls, self.wincursor, self.cursor)

    def drawparent(self):
        self.drawls(self.win_l, self.parent_ls, self.parent_wincursor, self.parent_cursor)

    def drawhead(self):
        # TODO err if too many
        self.win_head.erase()
        self.win_head.addstr(0, 0, self.url, self.color_url)
        self.win_head.addstr(0, len(self.url), self.cwd, self.color_dir)
        try:
            self.win_head.addstr(0, len(self.url) + len(self.cwd), os.path.basename(self.ls[self.cursor]['name']), self.color_file)
        except IndexError:
            pass
        self.win_head.refresh()


    def pad(self, s, width):
        if len(s) > width-2:
            s = s[:width-3] + '~'
        return (' ' + s).ljust(width)

    def mkwins(self):
        height, width = self.stdscr.getmaxyx()
        self.win_head = curses.newwin(1, width, 0, 0)
        self.win_status = curses.newwin(1, width, height-1, 0)

        split = width // 3
        self.win_l = curses.newwin(height-2, split, 1, 1)
        self.win_r = curses.newwin(height-2, width - split - 4, 1, split + 3)


    def init(self, stdscr):
        self.stdscr = stdscr

        curses.start_color()
        curses.use_default_colors()
        curses.curs_set(0)

        curses.init_pair(1, curses.COLOR_WHITE, -1)
        curses.init_pair(2, curses.COLOR_BLUE, -1)
        curses.init_pair(3, curses.COLOR_GREEN, -1)

        self.color_file = curses.color_pair(1)
        self.color_dir = curses.color_pair(2)
        self.color_url = curses.color_pair(3)

        stdscr.erase()
        stdscr.refresh()

        self.mkwins()
