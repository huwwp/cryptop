import curses
from curses import wrapper
import requests

def getPrice(coin, curr = 'USD'):
	'''Extend request to get the data on coins'''
	try:
		r = requests.get('https://min-api.cryptocompare.com/data/pricemulti?fsyms='+coin+'&tsyms='+curr)
	except requests.exceptions.RequestException as e:
		print(e)
		sys.exit(1)

	try:
		data = r.json()
		val = [v[curr] for k,v in data.items()]
		return val
	except:
		print('Could not find the coin currency pair(s)')
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
	stdscr.addstr('cryptop v0.1.0 - by huwwp', curses.color_pair(1))
	stdscr.addstr(1,0,'Coin    Price    Cap    High    Low', curses.color_pair(3))
	#Loop this, one request for speed

	coinvl = getPrice(','.join(coinl))

	for x,y in zip(coinl, coinvl):
		stdscr.addstr(coinl.index(x)+2,0,'{}    {}'.format(x, y), curses.color_pair(0))

	stdscr.addstr(stdscr.getmaxyx()[0]-1,0, '[A] Add coin [R] Remove coin [F] Set update frequency [0]Exit', curses.color_pair(2))

def main(stdscr):
	x = 1
	coinl = ['BTC','ETH','XMR']
	conf_scr()
	stdscr.clear()
	while x != 48 and x != 27:
		if x == 1:
			write_scr(stdscr, coinl)
		x = stdscr.getch()


wrapper(main)