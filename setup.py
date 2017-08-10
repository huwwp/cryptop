# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst', encoding="utf-8") as f:
    readme = f.read()

setup(
    name='cryptop',
    version='0.1.7',
    description='Command line Cryptocurrency Portfolio',
    long_description=readme,
    author='huwwp',
    author_email='hpigott@gmail.com',
    url='https://github.com/huwwp/cryptop',
    license='MIT',
    keywords='crypto cli portfolio curses cryptocurrency bitcoin',
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
    install_requires=['requests', 'requests_cache'],
    package_data={'cryptop': ['config.ini']},
    entry_points = {
        'console_scripts': ['cryptop = cryptop.cryptop:main'],
    }
)
