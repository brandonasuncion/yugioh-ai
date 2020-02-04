## Compile language catalogues
This game supports multiple languages (english, spanish, german and french right now).
To compile the language catalogues, run the following:
```
./compile.sh de
./compile.sh es
./compile.sh fr
```

To update the plain text files into human-readable format, run the following:
```
./update.sh de
./update.sh es
./update.sh fr
```
The generated files in locale/<language code>/LC_MESSAGES/game.po can be given to translators afterwards.

## Card databases

You'll need to grab the card databases for all languages you'd like to enable on your server. You'll at least need the database for the primary language (mostly english).
Those can be found on various sources on the net, but it would be the best to checkout the official ygopro2 discord server, download and update the full package and use the files which can be found inside the cdb folder.

ATTENTION: the most up-to-date english databases can be found directly within the cdb folder (no sub-folder), so just grab all *.cdb files and copy them over into the locale/en/ folder to get the server up and running.

The YGOPRO2 discord server can be found [here](https://discordapp.com/invite/8S5KcMJ).

## Running
```
python3 ygo.py
```
The server will start on port 4000.

## Upgrading

### ygopro-scripts

When upgrading ygopro-scripts, always upgrade ygopro-core with it to prevent crashes. To do so, git pull the repositories cloned earlier and execute the build commands from above again.

### This game

We might change several basic things from time to time, like adding additional c-level helper functions or modify the database layout, so don't forget to run the following commands whenever pulling a major upgrade:
```
python3 duel_build.py
alembic upgrade head
```
Always remember that, even though we try to prevent it, upgrading the database might fail and leave your database in a broken state, so always back it up before proceeding.
