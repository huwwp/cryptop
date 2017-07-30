import curses
import os
import sys
import re
import shutil
import configparser

import requests
import requests_cache

#GLOBALS!
basedir = os.path.join(os.path.expanduser('~'), '.cryptop')
datafile = os.path.join(basedir, 'data')
conffile = os.path.join(basedir, 'config.ini')
config = configparser.ConfigParser()
p = re.compile('[A-Z]{3},\d{0,}\.?\d{0,}')


def read_configuration(confpath):
	# copy our default config file
	if not os.path.isfile(confpath):
		defaultconf = os.path.join(os.path.dirname(__file__), 'config.ini')
		shutil.copyfile(defaultconf, conffile)

	config.read(confpath)
	return config


def if_coin(coin):
	'''Check if coin exists'''
	t = requests.get('https://www.cryptocompare.com/api/data/coinlist/')
	data = t.json()
	if coin in data['Data'].keys():
		return True
	else:
		return False


def getPrice(coin, curr=None):
	'''Get the data on coins'''
	if not curr:
		curr = config['api'].get('currency', 'USD')

	try:
		r = requests.get(
			'https://min-api.cryptocompare.com/data/pricemultifull?fsyms='
			+coin+'&tsyms='+curr)
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


def get_theme_colors():
	''' Returns curses colors according to the config'''
	def get_curses_color(name_or_value):
		try:
			return getattr(curses, 'COLOR_' + name_or_value.upper())
		except AttributeError:
			return int(name_or_value)

	theme_config = config['theme']
	return get_curses_color(theme_config.get('text', 'yellow')), \
		get_curses_color(theme_config.get('banner', 'yellow')), \
		get_curses_color(theme_config.get('banner_text', 'black')), \
		get_curses_color(theme_config.get('background', -1))


def conf_scr():
	'''Configure the screen and colors/etc'''
	curses.curs_set(0)
	curses.start_color()
	curses.use_default_colors()
	text, banner, banner_text, background = get_theme_colors()
	curses.init_pair(2, text, background)
	curses.init_pair(3, banner_text, banner)


def write_scr(stdscr, coinl, heldl, y, x):
	'''Write text and formatting to screen'''
	if y >= 1:
		stdscr.addnstr(0,0,'cryptop v0.1.0', x, curses.color_pair(2))
	if y >= 2:
		stdscr.addnstr(1,0,
			'  COIN    PRICE         HELD        VAL     HIGH      LOW  ',
			x, curses.color_pair(3))

	total = 0
	if coinl:
		coinvl = getPrice(','.join(coinl))

		if y > 3:
			for coin,val,held in zip(coinl, coinvl, heldl):
				if coinl.index(coin)+2 < y:
					stdscr.addnstr(coinl.index(coin)+2,0,
						'  {}  {:8.2f} {:12.8f} {:10.2f} {:8.2f} {:8.2f}'
						.format(coin, val[0], float(held), float(held)*val[0],
							val[1], val[2]), x, curses.color_pair(2))
				total += float(held)*val[0]

	if y > len(coinl) + 3:
		stdscr.addnstr(y-2, 0, 'Total Holdings: {:10.2f}    '
			.format(total), x, curses.color_pair(3))
		stdscr.addnstr(y-1, 0,
			'[A] Add coin or update value [R] Remove coin [0]Exit', x,
			curses.color_pair(2))


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


def mainc(stdscr):
	inp = 0
	coinl, heldl = read_file()
	y, x = stdscr.getmaxyx()
	conf_scr()
	stdscr.bkgd(' ', curses.color_pair(2))
	stdscr.clear()
	stdscr.nodelay(1)
	while inp != 48 and inp != 27:
		while True:
			try:
				write_scr(stdscr, coinl, heldl, y, x)
			except curses.error:
				pass

			inp = stdscr.getch()
			if inp != curses.KEY_RESIZE:
				break
			stdscr.erase()
			y, x = stdscr.getmaxyx()

		if inp == 97 or inp == 65:
			if y > 2:
				data = get_string(stdscr,
					'Enter in format Symbol,Amount e.g. BTC,10')
				coinl, heldl = add_coin(data, coinl, heldl)

		if inp == 82 or inp == 114:
			if y > 2:
				data = get_string(stdscr,
					'Enter the symbol of coin to be removed, e.g. BTC')
				coinl, heldl = rem_coin(data, coinl, heldl)

	write_file(coinl, heldl)


def main():
	if os.path.isfile(basedir):
		sys.exit('Please remove your old configuration file at {}'.format(basedir))
	os.makedirs(basedir, exist_ok=True)

	global config
	config = read_configuration(conffile)

	requests_cache.install_cache(cache_name='api_cache', backend='memory',
		expire_after=int(config['api'].get('cache', 10)))

	curses.wrapper(mainc)


if __name__ == "__main__":
	main()
