import curses
from curses import wrapper
import requests
import sys
import time



def getPrice(coin, curr = 'USD'):
	'''Extend request to get the data on coins'''
	try:
		r = requests.get('https://min-api.cryptocompare.com/data/pricemultifull?fsyms='+coin+'&tsyms='+curr)
	except requests.exceptions.RequestException as e:
		print(e)
		sys.exit(1)

	try:
		data = r.json()
		val= [(data['RAW'][c][curr]['PRICE'],
			data['RAW'][c][curr]['MKTCAP'],
			data['RAW'][c][curr]['HIGH24HOUR'],
			data['RAW'][c][curr]['LOW24HOUR']) for c in coin.split(',')]
		return val
	except:
		print('Could not parse data')
		sys.exit(1)

def conf_scr():
	'''Configure the screen and colors/etc'''
	curses.curs_set(0)
	curses.start_color()
	curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
	curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
	curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_CYAN)

def write_scr(stdscr, coinl):
	'''Write text and formatting to screen'''

	height, width = stdscr.getmaxyx()
	stdscr.addstr(0,0,'cryptop v0.1.0 - by huwwp', curses.color_pair(1))
	stdscr.addstr(1,0,'  COIN     PRICE            CAP    HIGH     LOW                                 ', curses.color_pair(3))
	coinvl = getPrice(','.join(coinl))
	for x,y in zip(coinl, coinvl):
		stdscr.addstr(coinl.index(x)+2,0,'  {}    {:7.2f} {:14.2f} {:7.2f} {:7.2f}'.format(x, y[0], y[1], y[2], y[3]), curses.color_pair(0))

	stdscr.addstr(height-1,0, '[A] Add coin [R] Remove coin [F] Set update frequency [0]Exit', curses.color_pair(2))

def main(stdscr):
	inp = 0
	coinl = ['BTC','ETH','XMR']
	conf_scr()
	stdscr.clear()
	stdscr.nodelay(1)
	while inp != 48 and inp != 27:
		if inp == 102:
			curses.halfdelay(50)

		write_scr(stdscr, coinl)
		inp = stdscr.getch()

wrapper(main)