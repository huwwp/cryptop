cryptop
=======
cryptop is a lightweight command line based cryptocurrency portfolio.
Built on Python 3 and ncurses with simplicity in mind, cryptop updates in realtime.

.. image:: img\cryptop.png

Installation
------------

cryptop requires Python 3 to run, and has only been tested in Python 3.6 so far.

The easiest way to install cryptop is through pip

.. code:: bash

    sudo pip install cryptop

You may need to force pip3 depending on your python install

.. code:: bash

    sudo pip3 install cryptop

cryptop can be installed manually, download the repo and run

.. code:: bash

    sudo python setup.py install

pip and setup.py can be run with a --user flag if you would prefer not to sudo. Both require setuptools which is included in most python installs and many distros by default

Usage
-----

Start from a terminal.

.. code:: bash

    cryptop

Follow the on screen instructions to add/remove cryptocurrencies from your portfolio.

Customisation
-------------

Cryptop creates two config files in a .cryptop folder in your home directory.

.crypto/config.ini contains theme configuration (text/background colors) and
options to change the output currency (default USD), update frequency, number of decimal places to display and maximum width for float values.

.. image:: img\fall.png

.. image:: img\aesth.png

.cryptop/wallet.json contains the coins and amounts you hold, you shouldn't need to edit it manually

Exchange support
----------------

You can also automatically fetch balances from your exchange accounts.
Currently the supported exchanges are Bitfinex, Bittrex, Cryptopia and Poloniex.
You will have to get your personal api-keys from the respective exchanges.
Simply add your api keys to config.ini to enable exchange balance synching:

.. code:: ini

    [bitfinex]
    key=my-key
    secret=my-secret

    [bittrex]
    key=my-key
    secret=my-secret

    [cryptopia]
    key=my-key
    secret=my-secret

    [poloniex]
    key=my-key
    secret=my-secret

You can add all or just a selection of supported exchanges. Your manually added balances that are stored
in wallet.json are not affected by this feature. This allows you to manually maintain your offline wallet balances
while cryptop shows you the full balances (wallet.json + balances from exchanges).

Credits
-------

Uses the `cryptocompare.com API
<http://www.cryptocompare.com/>`_.

Tipjar
------

Help me reach my goal of becoming a blockchain developer.

BTC: 15wNW29q7XAEbC8yus49CWvt91JkhcdkoW

Disclaimer
----------

I am not liable for the accuracy of this program’s output nor actions
performed based upon it.
