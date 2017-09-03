import curses
import os
import sys
import re
import shutil
import configparser
import json
import pkg_resources
import locale
import datetime
import requests
import requests_cache


# GLOBALS!
BASEDIR = os.path.join(os.path.expanduser('~'), '.cryptop')
WALLETFILE = os.path.join(BASEDIR, 'wallet.json')
LEDGERFILE = os.path.join(BASEDIR, 'ledger.json')
CONFFILE = os.path.join(BASEDIR, 'config.ini')
CONFIG = configparser.ConfigParser()
COIN_FORMAT = re.compile('[A-Z]{2,5},\d{0,}\.?\d{0,}')

SORT_FNS = { 'coin' : lambda item: item[0],
             'price': lambda item: float(item[1][0]),
             'held' : lambda item: float(item[2]),
             'val'  : lambda item: float(item[1][0]) * float(item[2]) }
SORTS = list(SORT_FNS.keys())
COLUMN = SORTS.index('val')
ORDER = True

VIEW = 'WALLET'
FIAT = 'EUR'
CURRENCYLIST = [FIAT, 'ETH', 'BTC']
CURRENCYCOUNTER = 0
CURRENCY = FIAT
NROFDECIMALS = 2

KEY_ESCAPE = 27
KEY_ZERO = 48
KEY_A = 65
KEY_F = 70
KEY_Q = 81
KEY_R = 82
KEY_S = 83
KEY_C = 67
KEY_T = 84
KEY_V = 86
KEY_a = 97
KEY_f = 102
KEY_q = 113
KEY_r = 114
KEY_s = 115
KEY_c = 99
KEY_t = 116
KEY_v = 118

def read_configuration(confpath):
    # copy our default config file
    if not os.path.isfile(confpath):
        defaultconf = pkg_resources.resource_filename(__name__, 'config.ini')
        shutil.copyfile(defaultconf, CONFFILE)

    CONFIG.read(confpath)
    return CONFIG


def if_coin(coin, url='https://www.cryptocompare.com/api/data/coinlist/'):
    '''Check if coin exists'''
    return coin in requests.get(url).json()['Data']


def get_price(coin, curr=None):
    '''Get the data on coins'''
    # curr = curr or CONFIG['api'].get('currency', 'USD')
    global CURRENCY
    curr = CURRENCY
    fmt = 'https://min-api.cryptocompare.com/data/pricemultifull?fsyms={}&tsyms={}'

    try:
        r = requests.get(fmt.format(coin, curr))
    except requests.exceptions.RequestException:
        sys.exit('Could not complete request')

    try:
        data_raw = r.json()['RAW']
        return [(data_raw[c][curr]['PRICE'],
                data_raw[c][curr]['LOW24HOUR'],
                data_raw[c][curr]['HIGH24HOUR'],
                data_raw[c][curr]['CHANGEPCT24HOUR']) for c in coin.split(',')]
    except:
        sys.exit('Could not parse data')


def get_theme_colors():
    ''' Returns curses colors according to the config'''
    def get_curses_color(name_or_value):
        try:
            return getattr(curses, 'COLOR_' + name_or_value.upper())
        except AttributeError:
            return int(name_or_value)

    theme_config = CONFIG['theme']
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
    curses.init_pair(1, banner_text, banner)
    curses.init_pair(2, text, -1)
    curses.init_pair(3, text, 234)
    curses.init_pair(4, getattr(curses, 'COLOR_GREEN'), -1)
    curses.init_pair(5, getattr(curses, 'COLOR_GREEN'), 234)
    curses.init_pair(6, getattr(curses, 'COLOR_RED'), -1)
    curses.init_pair(7, getattr(curses, 'COLOR_RED'), 234)
    curses.halfdelay(10)

def str_formatter(coin, val, held):
    '''Prepare the coin strings as per ini length/decimal place values'''
    return '{:<5} {:>15.2f} {:>15.{prec}f} {} {:>15.{prec}f} {} {:>15.{prec}f} {} {:>15.{prec}f} {}'.format(
        coin, float(held), val[0], CURRENCY, float(held)*val[0], CURRENCY, val[1], CURRENCY, val[2], CURRENCY, prec=NROFDECIMALS)


def write_scr(stdscr, wallet, y, x):
    '''Write text and formatting to screen'''
    stdscr.erase()
    if y >= 1:
        stdscr.addnstr(0, 0, 'cryptop v0.1.9', x, curses.color_pair(2))
    if y >= 2:
        header = '{:<5} {:>15} {:>19} {:>19} {:>19} {:>19} {:>15}'.format(
            'COIN', 'HODLING', 'CURRENT PRICE', 'TOTAL VALUE', '24H LOW', '24H HIGH', '24H CHANGE')
        stdscr.addnstr(1, 0, header, x, curses.color_pair(1))
    
    total = 0
    coinl = list(wallet.keys())
    heldl = list(wallet.values())
    if coinl:
        coinvl = get_price(','.join(coinl))

        if y > 3:
            s = sorted(list(zip(coinl, coinvl, heldl)), key=SORT_FNS[SORTS[COLUMN]], reverse=ORDER)
            coinl = list(x[0] for x in s)
            coinvl = list(x[1] for x in s)
            heldl = list(x[2] for x in s)
            counter = 0            
            for coin, val, held in zip(coinl, coinvl, heldl):
                if coinl.index(coin) + 2 < y:
                    
                    stdscr.addnstr(coinl.index(coin) + 2, 0, str_formatter(coin, val, held), x, curses.color_pair(2 + counter % 2))

                    if val[3] > 0:
                        stdscr.addnstr(coinl.index(coin) + 2, 5 + 16 + 4 * 20,
                        '  {:>12.2f} %'.format(val[3]), x, curses.color_pair(4 + counter % 2))
                    elif val[3] < 0:
                        stdscr.addnstr(coinl.index(coin) + 2, 5 + 16 + 4 * 20,
                        '  {:>12.2f} %'.format(val[3]), x, curses.color_pair(6 + counter % 2))
                    else:
                        stdscr.addnstr(coinl.index(coin) + 2, 5 + 16 + 4 * 20,
                        '  {:>12.2f} %'.format(val[3]), x, curses.color_pair(2 + counter % 2))
                total += float(held) * val[0]
                counter += 1

    if y > len(coinl) + 3:
        stdscr.addnstr(y - 2, 0, 'Total Holdings: {:10.2f} {}    '
            .format(total, CURRENCY), x, curses.color_pair(1))
        stdscr.addnstr(y - 1, 0,
            '[A] Add coin [R] Remove coin [T] Add transaction [F] Switch FIAT/ETH [V] View ledger [S] Sort [C] Cycle sort [Q] Exit', x,
            curses.color_pair(2))


def read_wallet():
    ''' Reads the wallet data from its json file '''
    try:
        with open(WALLETFILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        # missing or malformed wallet
        write_wallet({})
        return {}

def read_ledger():
    ''' Reads the transaction ledger data from its json file '''
    try:
        with open(LEDGERFILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        # missing or malformed wallet
        write_ledger({})
        return {}

def write_wallet(wallet):
    ''' Writes the wallet data to its json file '''
    with open(WALLETFILE, 'w') as f:
        json.dump(wallet, f)

def write_ledger(ledger):
    ''' Writes the ledger data to its json file '''
    with open(LEDGERFILE, 'w') as f:
        json.dump(ledger, f)


def get_string(stdscr, prompt):
    '''Requests and string from the user'''
    curses.echo()
    stdscr.clear()
    stdscr.addnstr(0, 0, prompt, -1, curses.color_pair(2))
    curses.curs_set(1)
    stdscr.refresh()
    in_str = stdscr.getstr(1, 0, 20).decode()
    curses.noecho()
    curses.curs_set(0)
    stdscr.clear()
    curses.halfdelay(10)
    return in_str


def add_coin(coin_amount, wallet):
    ''' Add a coin and its amount to the wallet '''
    coin_amount = coin_amount.upper()
    if not COIN_FORMAT.match(coin_amount):
        return wallet

    coin, amount = coin_amount.split(',')
    if not if_coin(coin):
        return wallet

    wallet[coin] = amount
    return wallet

def add_transaction(transaction, wallet, ledger):
    ''' Add a transaction to ledger and update wallet accordingly '''

    transaction = transaction.upper()
    if not COIN_FORMAT.match(transaction):
        return wallet, ledger

    coin_out, amount_out, coin_in, amount_in = transaction.split(',')
    if (not if_coin(coin_out)) or (not if_coin(coin_out)):
        return wallet, ledger

    # Add transaction to ledger
    now = datetime.datetime.now()
    ledger[now.strftime("%Y-%m-%d %H:%M")] = transaction

    # Update wallet 
    current_amount_coin_out = float(wallet[coin_out])
    current_amount_coin_in = float(wallet[coin_in])
    wallet[coin_out] = current_amount_coin_out - float(amount_out)
    wallet[coin_in] = current_amount_coin_in + float(amount_in)

    return wallet, ledger


def remove_coin(coin, wallet):
    ''' Remove a coin and its amount from the wallet '''
    # coin = '' if window is resized while waiting for string
    if coin:
        coin = coin.upper()
        wallet.pop(coin, None)
    return wallet

def view_ledger(stdscr, ledger, x, y):
    '''Write transactions to screen'''
    stdscr.erase()

    if y >= 1:
        stdscr.addnstr(0, 0, 'cryptop v0.1.9', x, curses.color_pair(2))
    if y >= 2:
        header = '{:<23} {:<12} {:<14} {:<11} {:<17} {:<23} {:>9}'.format(
            'DATE', 'OUT', 'AMOUNT', 'IN', 'AMOUNT', 'RATE OUT/IN', 'RATE  IN/OUT')
        stdscr.addnstr(1, 0, header, x, curses.color_pair(1))
    
    
    dates = list(ledger.keys())
    transactions = list(ledger.values())

    if transactions:

        if y > 3:
            counter = 0
            for date, transaction in list(zip(dates, transactions)):
                info = transaction.split(',')
                printme = '{:<15} {:>10} {:>15.6f} {:>10} {:>15.6f} {:>15.6f} {}/{} {:>15.6f} {}/{}'.format(
                    date, info[0], float(info[1]), info[2], float(info[3]), 
                    float(info[1])/float(info[3]), info[0], info[2], 
                    float(info[3])/float(info[1]), info[2], info[0])
                stdscr.addnstr(dates.index(date) + 2, 0, printme, x, curses.color_pair(2 + counter % 2))
                counter += 1

    if y > len(transactions) + 3:
        stdscr.addnstr(y - 1, 0,
            '[V] View wallet [T] Add transaction [Q] Exit', x,
            curses.color_pair(2))


def mainc(stdscr):
    inp = 0
    wallet = read_wallet()
    ledger = read_ledger()
    y, x = stdscr.getmaxyx()
    conf_scr()
    stdscr.bkgd(' ', curses.color_pair(2))
    stdscr.clear()
    #stdscr.nodelay(1)
    # while inp != 48 and inp != 27 and inp != 81 and inp != 113:
    while inp not in {KEY_ZERO, KEY_ESCAPE, KEY_Q, KEY_q}:
        global VIEW
        while True:
            try:
                if VIEW is 'WALLET':
                    write_scr(stdscr, wallet, y, x)
                elif VIEW is 'LEDGER':
                    view_ledger(stdscr, ledger, x, y)
            except curses.error:
                pass

            inp = stdscr.getch()
            if inp != curses.KEY_RESIZE:
                break
            y, x = stdscr.getmaxyx()

        if inp in {KEY_a, KEY_A}:
            if y > 2:
                data = get_string(stdscr,
                    'Enter in format Symbol,Amount e.g. BTC,10')
                wallet = add_coin(data, wallet)
                write_wallet(wallet)

        if inp in {KEY_r, KEY_R}:
            if y > 2:
                data = get_string(stdscr,
                    'Enter the symbol of coin to be removed, e.g. BTC')
                wallet = remove_coin(data, wallet)
                write_wallet(wallet)

        if inp in {KEY_s, KEY_S}:
            if y > 2:
                global ORDER
                ORDER = not ORDER

        if inp in {KEY_c, KEY_C}:
            if y > 2:
                global COLUMN
                COLUMN = (COLUMN + 1) % len(SORTS)

        if inp in {KEY_f, KEY_F}:
            if y > 2:
                global CURRENCY, NROFDECIMALS, FIAT, CURRENCYCOUNTER, CURRENCYLIST
                CURRENCYCOUNTER = (CURRENCYCOUNTER + 1) % 3
                CURRENCY = CURRENCYLIST[CURRENCYCOUNTER]
                
                if CURRENCY is FIAT:
                    NROFDECIMALS = 2
                else:
                    NROFDECIMALS = 6

        if inp in {KEY_t, KEY_T}:
            if y > 2:
                data = get_string(stdscr,
                    'Enter transaction (Out,Amount,In,Amount), e.g. BTC,10,ETH,10')
                wallet, ledger = add_transaction(data, wallet, ledger)
                write_wallet(wallet)
                write_ledger(ledger)

        if inp in {KEY_v, KEY_V}:
            if VIEW is 'WALLET':
                VIEW = 'LEDGER'
            elif VIEW is 'LEDGER':
                VIEW = 'WALLET'
                    

def main():
    if os.path.isfile(BASEDIR):
        sys.exit('Please remove your old configuration file at {}'.format(BASEDIR))
    os.makedirs(BASEDIR, exist_ok=True)

    global CONFIG
    CONFIG = read_configuration(CONFFILE)
    # locale.setlocale(locale.LC_MONETARY, CONFIG['locale'].get('monetary', ''))
    # locale.setlocale(locale.LC_ALL, 'en_US')

    requests_cache.install_cache(cache_name='api_cache', backend='memory',
        expire_after=int(CONFIG['api'].get('cache', 10)))

    curses.wrapper(mainc)


if __name__ == "__main__":
    main()
