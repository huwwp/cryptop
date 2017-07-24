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
	curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)

def write_scr(stdscr, coinl, heldl, dim):
	'''Write text and formatting to screen'''
	if dim[0] >= 1:
		stdscr.addnstr(0,0,'cryptop v0.1.0', -1, curses.color_pair(2))
	if dim[0] >= 2:
		stdscr.addnstr(1,0,'  COIN      PRICE     HELD        VAL     HIGH      LOW  ', -1, curses.color_pair(3))

	coinvl = getPrice(','.join(coinl))
	total = 0

	if dim[0] > 2:
		for coin,val,held in zip(coinl, coinvl, heldl):
			if coinl.index(coin)+2 < dim[0]:
				stdscr.addnstr(coinl.index(coin)+2,0,'  {}    {:8.2f} {:8.2f} {:10.2f} {:8.2f} {:8.2f}'.format(coin, val[0], float(held), float(held)*val[0], val[1], val[2]), -1, curses.color_pair(2))
			total += float(held)*val[0]
	
	if dim[0] > len(coinl) + 4:
		stdscr.addnstr(dim[0]-2,0, 'Total Holdings: {:10.2f}    '.format(total), -1, curses.color_pair(3))
		stdscr.addnstr(dim[0]-1,0, '[A] Add coin [R] Remove coin [0]Exit', -1, curses.color_pair(2))
	#Comming from below causes issues

def read_file():
	'''Reads the data file'''
	with open(datafile, 'r') as f:
		data = f.readlines()
		data = [x.strip() for x in data]
		coinl, heldl = zip(*(s.split(',') for s in data))
		coinl = [x for x in coinl]
		heldl = [x for x in heldl]

	f.close()
	return coinl, heldl

def write_file(coinl, heldl):
	with open(datafile, 'w') as f:
		for x,y in zip(coinl, heldl):
			f.write('{},{}\n'.format(x,y))

	f.close()

def get_string(stdscr, prompt):
	stdscr.nodelay(0)
	curses.echo()
	stdscr.clear()
	stdscr.addnstr(0,0, prompt, -1)
	curses.curs_set(1)
	stdscr.refresh()
	input = stdscr.getstr(1, 0, 20)
	input = input.decode()
	curses.noecho()
	curses.curs_set(1)
	stdscr.clear()
	stdscr.nodelay(1)
	return input


def add_coin(input, coinl, heldl):
	input = input.split(',')
	coinl.append(input[0])
	heldl.append(input[1])
	return coinl, heldl

def rem_coin(input, coinl, heldl):
	heldl = [x for x in heldl if x.index(x) != coinl.index(input)]
	coinl = [x for x in coinl if x != input]
	return coinl, heldl


def main(stdscr):
	inp = 0
	coinl, heldl = read_file()
	dim = stdscr.getmaxyx()
	conf_scr()
	stdscr.clear()
	stdscr.nodelay(1)
	while inp != 48 and inp != 27:

		if dim != stdscr.getmaxyx():
			stdscr.clear()
			dim = stdscr.getmaxyx()

		if inp == 97 or inp == 65:
			data = get_string(stdscr, 'Enter in format Symbol,Ammount e.g. BTC,10')
			coinl, heldl = add_coin(data, coinl, heldl)

		if inp == 82 or inp == 114:
			data = get_string(stdscr, 'Enter the symbol of coin to be removed, e.g. BTC')
			coinl, heldl = rem_coin(data, coinl, heldl)


		write_scr(stdscr, coinl, heldl, dim)
		inp = stdscr.getch()

	write_file(coinl, heldl)

wrapper(main)