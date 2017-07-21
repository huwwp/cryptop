import curses
from curses import wrapper
import requests
import sys
import time


#GLOBALS!
datafile = '.cryptop'


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
	curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_RED)

def write_scr(stdscr, coinl, heldl):
	'''Write text and formatting to screen'''
	height, width = stdscr.getmaxyx()
	stdscr.addstr(0,0,'cryptop v0.1.0', curses.color_pair(0))
	stdscr.addstr(1,0,'  COIN      PRICE     HELD        VAL     HIGH      LOW  ', curses.color_pair(3))
	coinvl = getPrice(','.join(coinl))
	total = 0
	for coin,val,held in zip(coinl, coinvl, heldl):
		stdscr.addstr(coinl.index(coin)+2,0,'  {}    {:8.2f} {:8.2f} {:10.2f} {:8.2f} {:8.2f}'.format(coin, val[0], float(held), float(held)*val[0], val[1], val[2]), curses.color_pair(2))
		total += float(held)*val[0]
	stdscr.addstr(height-2,0, 'Total Holdings: {:8.2f}'.format(total), curses.color_pair(2))
	stdscr.addstr(height-1,0, '[A] Add coin [R] Remove coin [0]Exit', curses.color_pair(2))

def read_file():
	'''Reads the data file'''
	with open(datafile) as f:
		data = f.readlines()
		data = [x.strip() for x in data]
		coinl, heldl = zip(*(s.split(',') for s in data))

	f.close()
	return coinl, heldl

def write_file():
	with open(datafile, 'w') as f:
		print('')

	f.close()
	print('')


def main(stdscr):
	inp = 0
	coinl, heldl = read_file()
	conf_scr()
	stdscr.clear()
	stdscr.nodelay(1)
	while inp != 48 and inp != 27:
		write_scr(stdscr, coinl, heldl)
		inp = stdscr.getch()

wrapper(main)