import curses
from curses import wrapper

def conf_scr():
	curses.curs_set(0)
	curses.start_color()
	curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)

def write_scr(stdscr):
	stdscr.addstr('cryptop v0.1.0 - by huwwp', curses.color_pair(1))
	stdscr.addstr(stdscr.getmaxyx()[0]-1,0, '[0]Exit')

def main(stdscr):
	x = 1
	conf_scr()
	stdscr.clear()
	while x != 48 and x != 27:
		if x == 1:
			write_scr(stdscr)
		x = stdscr.getch()


wrapper(main)