import curses
import os
import sys
import re
import shutil
import configparser
import json

import requests
import requests_cache

# GLOBALS!
basedir = os.path.join(os.path.expanduser('~'), '.cryptop')
datafile = os.path.join(basedir, 'wallet.json')
conffile = os.path.join(basedir, 'config.ini')
config = configparser.ConfigParser()
p = re.compile('[A-Z]{2,5},\d{0,}\.?\d{0,}')


def read_configuration(confpath):
	# copy our default config file
	if not os.path.isfile(confpath):
		defaultconf = os.path.join(os.path.dirname(__file__), 'config.ini')
		shutil.copyfile(defaultconf, conffile)

	config.read(confpath)
	return config


def if_coin(coin, url='https://www.cryptocompare.com/api/data/coinlist/'):
	'''Check if coin exists'''
	return coin in requests.get(url).json()['Data']


def get_price(coin, curr=None):
	'''Get the data on coins'''
	curr = curr or config['api'].get('currency', 'USD')
	fmt = 'https://min-api.cryptocompare.com/data/pricemultifull?fsyms={}&tsyms={}'

	try:
		r = requests.get(fmt.format(coin, curr))
	except requests.exceptions.RequestException:
		sys.exit('Could not complete request')

	try:
		data_raw = r.json()['RAW']
		return [(data_raw[c][curr]['PRICE'],
				data_raw[c][curr]['HIGH24HOUR'],
				data_raw[c][curr]['LOW24HOUR']) for c in coin.split(',')]
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
	return (get_curses_color(theme_config.get('text', 'yellow')),
		get_curses_color(theme_config.get('banner', 'yellow')),
		get_curses_color(theme_config.get('banner_text', 'black')),
		get_curses_color(theme_config.get('background', -1)))


def conf_scr():
	'''Configure the screen and colors/etc'''
	curses.curs_set(0)
	curses.start_color()
	curses.use_default_colors()
	text, banner, banner_text, background = get_theme_colors()
	curses.init_pair(2, text, background)
	curses.init_pair(3, banner_text, banner)


def write_scr(stdscr, wallet, y, x):
	'''Write text and formatting to screen'''
	if y >= 1:
		stdscr.addnstr(0, 0,'cryptop v0.1.2', x, curses.color_pair(2))
	if y >= 2:
		header = '  COIN      PRICE          HELD        VAL     HIGH      LOW  '
		stdscr.addnstr(1, 0, header, x, curses.color_pair(3))

	total = 0
	coinl = list(wallet.keys())
	heldl = list(wallet.values())
	if coinl:
		coinvl = get_price(','.join(coinl))

		if y > 3:
			for coin,val,held in zip(coinl, coinvl, heldl):
				if coinl.index(coin)+2 < y:
					stdscr.addnstr(coinl.index(coin)+2,0,
						'  {:<5}  {:8.2f} {:>13.8f} {:10.2f} {:8.2f} {:8.2f}'
						.format(coin, val[0], float(held), float(held)*val[0],
							val[1], val[2]), x, curses.color_pair(2))
				total += float(held)*val[0]

	if y > len(coinl) + 3:
		stdscr.addnstr(y-2, 0, 'Total Holdings: {:10.2f}    '
			.format(total), x, curses.color_pair(3))
		stdscr.addnstr(y-1, 0,
			'[A] Add coin or update value [R] Remove coin [0\Q]Exit', x,
			curses.color_pair(2))


def read_wallet():
	''' Reads the wallet data from its json file '''
	try:
		with open(datafile, 'r') as f:
			return json.load(f)
	except (FileNotFoundError, ValueError):
		# missing or malformed wallet
		write_wallet({})
		return {}


def write_wallet(wallet):
	''' Reads the wallet data to its json file '''
	with open(datafile, 'w') as f:
		json.dump(wallet, f)


def get_string(stdscr, prompt):
	'''Requests and string from the user'''
	stdscr.nodelay(0)
	curses.echo()
	stdscr.clear()
	stdscr.addnstr(0,0, prompt, -1, curses.color_pair(2))
	curses.curs_set(1)
	stdscr.refresh()
	in_str = stdscr.getstr(1, 0, 20).decode()
	curses.noecho()
	curses.curs_set(0)
	stdscr.clear()
	stdscr.nodelay(1)
	return in_str


def add_coin(coin_amount, wallet):
	''' Remove a coin and its amount to the wallet '''
	if not p.match(coin_amount):
		return wallet

	coin, amount = coin_amount.split(',')
	wallet[coin] = amount

	return wallet


def remove_coin(coin, wallet):
	''' Remove a coin and its amount from the wallet '''
	# coin = '' if window is resized while waiting for string
	if coin:
		return wallet.pop(coin, None)
	return wallet


def mainc(stdscr):
	inp = 0
	wallet = read_wallet()
	y, x = stdscr.getmaxyx()
	conf_scr()
	stdscr.bkgd(' ', curses.color_pair(2))
	stdscr.clear()
	stdscr.nodelay(1)
	while inp != 48 and inp != 27 and inp != 81 and inp != 113:
		while True:
			try:
				write_scr(stdscr, wallet, y, x)
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
				wallet = add_coin(data, wallet)

		if inp == 82 or inp == 114:
			if y > 2:
				data = get_string(stdscr,
					'Enter the symbol of coin to be removed, e.g. BTC')
				wallet = remove_coin(data, wallet)

	write_wallet(wallet)


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
