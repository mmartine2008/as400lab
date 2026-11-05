
import curses


class Screen:

    WIDTH = 80
    HEIGHT = 24

    def __init__(self, stdscr):
        self.stdscr = stdscr

        curses.start_color()
        curses.use_default_colors()
        curses.curs_set(1)

        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        self.green = curses.color_pair(1)
        self.white = curses.color_pair(2)
        self.yellow = curses.color_pair(3)

        self.stdscr.keypad(True)
        self.stdscr.timeout(-1)

    def clear(self):
        self.stdscr.erase()
        self.stdscr.bkgd(" ", self.green)

    def write(self, row, col, text, color=None):
        if color is None:
            color = self.green

        height, width = self.stdscr.getmaxyx()

        if row < height and col < width:
            try:
                self.stdscr.addnstr(
                    row, col, str(text),
                    max(0, width - col),
                    color
                )
            except curses.error:
                pass

    def refresh(self):
        self.stdscr.refresh()

    def function_keys(self):
        self.write(
            22, 0,
            "F1=Help  F2=Status  F3=Exit  F4=Prompt",
            self.yellow
        )

        self.write(
            23, 0,
            "F5=Refresh  F9=Retrieve  F12=Cancel",
            self.yellow
        )

