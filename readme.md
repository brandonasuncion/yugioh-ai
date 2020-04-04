# Monte Carlo tree search AI for ocgcore

Initially based on https://github.com/tspivey/yugioh-game

The prototype will be written in Python 3 with the aim to have the final version in C++ for better performance.

`cli.py` is able to simulate a match between two AI that makes random moves.

To test it, install dependencies and execute `python3 cli.py --deck1 decks/normal46.ydk --deck2 decks/normal46.ydk`

# Automated setup
Requires a Linux environment with the following applications on the PATH: python3, pip3, g++, wget, tar, unzip, patch, make
```
make setup
```

# Verify setup

Test that the repo is setup correctly by running:
```
python3 cli.py --deck1 decks/normal46.ydk --deck2 decks/normal46.ydk
```

You should see text output showing two AI playing a duel by making random moves.

# Manual setup

## Install dependencies
Lua is needed for ygopro-core. To make sure a matching lua version is used, we will compile it on our own:
```
cd vendor
wget https://www.lua.org/ftp/lua-5.3.5.tar.gz
tar xf lua-5.3.5.tar.gz
cd lua-5.3.5
make linux CC=g++ CFLAGS='-O2 -fPIC'
```

Install Python dependencies:
```
pip3 install -r requirements.txt
```

## Building

lua-5.3.5, ygopro-core, and ygopro-scripts are put in vendor directory.

```
git clone https://github.com/Fluorohydride/ygopro-core vendor/ygopro-core
git clone https://github.com/Fluorohydride/ygopro-scripts vendor/ygopro-scripts
patch vendor/ygopro-core/playerop.cpp etc/ygopro-core.patch
g++ -shared -fPIC -o libygo.so vendor/ygopro-core/*.cpp -Ivendor/lua-5.3.5/src -Lvendor/lua-5.3.5/src -llua -std=c++14
python3 duel_build.py
ln -s vendor/ygopro-scripts script
```

## Card database

Obtain a copy of cards.cdb and put it in locale/en folder

```
wget https://gitlab.com/duelists-unite/cdb/-/raw/master/cards.cdb -O locale/en/cards.cdb
```
