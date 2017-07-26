import curses
from curses import wrapper
import requests
import os
import sys
import re

#GLOBALS!
datafile = os.path.expanduser('~') + '/.cryptop'
#datafile = '.cryptop'
p = re.compile('[A-Z]{3},\d{0,}\.?\d{0,}')

def if_coin(coin):
	'''Check if coin exists'''
	t = requests.get('https://www.cryptocompare.com/api/data/coinlist/')
	data = t.json()
	if coin in data['Data'].keys():
		return True
	else:
		return False

def getPrice(coin, curr = 'USD'):
	'''Get the data on coins'''
	try:
		r = requests.get('https://min-api.cryptocompare.com/data/pricemultifull?fsyms='+coin+'&tsyms='+curr)
	except requests.exceptions.RequestException as e:
		sys.exit('Could not complete request')

	try:
		data = r.json()
		val= [(data['RAW'][c][curr]['PRICE'],
			data['RAW'][c][curr]['HIGH24HOUR'],
			data['RAW'][c][curr]['LOW24HOUR']) for c in coin.split(',')]
		return val
	except:
		sys.exit('Could not parse data')

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
		stdscr.addnstr(0,0,'cryptop v0.1.0', dim[1], curses.color_pair(2))
	if dim[0] >= 2:
		stdscr.addnstr(1,0,'  COIN    PRICE         HELD        VAL     HIGH      LOW  ', dim[1], curses.color_pair(3))

	total = 0
	if coinl:
		coinvl = getPrice(','.join(coinl))
		
		if dim[0] > 3:
			for coin,val,held in zip(coinl, coinvl, heldl):
				if coinl.index(coin)+2 < dim[0]:
					stdscr.addnstr(coinl.index(coin)+2,0,'  {}  {:8.2f} {:12.8f} {:10.2f} {:8.2f} {:8.2f}'.format(coin, val[0], float(held), float(held)*val[0], val[1], val[2]), dim[1], curses.color_pair(2))
				total += float(held)*val[0]
	
	if dim[0] > len(coinl) + 3:
		stdscr.addnstr(dim[0]-2,0, 'Total Holdings: {:10.2f}    '.format(total), dim[1], curses.color_pair(3))
		stdscr.addnstr(dim[0]-1,0, '[A] Add coin [R] Remove coin [0]Exit', dim[1], curses.color_pair(2))

def read_file():
	'''Reads the data file'''
	coinl = []
	heldl = []

	try:
		with open(datafile, 'r') as f:
			data = f.readlines()
			data = [x.strip() for x in data]
			coinl, heldl = zip(*(s.split(',') for s in data))
			coinl = [x for x in coinl]
			heldl = [x for x in heldl]

		f.close()
		return coinl, heldl

	except:
		with open(datafile, 'w') as f:
			print('')
		f.close()
		return coinl,heldl

def write_file(coinl, heldl):
	'''Writes the lists to the data file'''
	with open(datafile, 'w') as f:
		for x,y in zip(coinl, heldl):
			f.write('{},{}\n'.format(x,y))

	f.close()

def get_string(stdscr, prompt):
	'''Requests and string from the user'''
	stdscr.nodelay(0)
	curses.echo()
	stdscr.clear()
	stdscr.addnstr(0,0, prompt, -1, curses.color_pair(2))
	curses.curs_set(1)
	stdscr.refresh()
	input = stdscr.getstr(1, 0, 20)
	input = input.decode()
	curses.noecho()
	curses.curs_set(0)
	stdscr.clear()
	stdscr.nodelay(1)
	return input


def add_coin(input, coinl, heldl):
	'''Adds a coin and amount held'''
	if not p.match(input):
		return coinl, heldl
	else:
		input = input.split(',')
		
		if input[0] in coinl:
			heldl[coinl.index(input[0])] = input[1]
		else:
			if if_coin(input[0]):
				coinl.append(input[0])
				heldl.append(input[1])

				
		
		return coinl, heldl

def rem_coin(input, coinl, heldl):
	'''Remove coin and ammount held from list'''
	#input = '' if window is resized while waiting for string
	if input == '':
		return coinl,heldl
	else:
		try:
			heldl = [x for x in heldl if x.index(x) != coinl.index(input)]
			coinl = [x for x in coinl if x != input]
		except:
			pass
		
		return coinl, heldl

def main(stdscr):
	inp = 0
	coinl, heldl = read_file()
	dim = stdscr.getmaxyx()
	conf_scr()
	stdscr.clear()
	stdscr.nodelay(1)
	while inp != 48 and inp != 27:
		while True:
			try:
				write_scr(stdscr, coinl, heldl, dim)
			except curses.error:
				pass

			inp = stdscr.getch()
			if inp != curses.KEY_RESIZE:
				break
			stdscr.erase()
			dim = stdscr.getmaxyx()
			
		if inp == 97 or inp == 65:
			if dim[0] > 2:
				data = get_string(stdscr, 'Enter in format Symbol,Ammount e.g. BTC,10')
				coinl, heldl = add_coin(data, coinl, heldl)

		if inp == 82 or inp == 114:
			if dim[0] > 2:
				data = get_string(stdscr, 'Enter the symbol of coin to be removed, e.g. BTC')
				coinl, heldl = rem_coin(data, coinl, heldl)

	write_file(coinl, heldl)

wrapper(main)