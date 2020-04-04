cli:
	python3 cli.py --deck1 decks/normal46.ydk --deck2 decks/normal46.ydk

manual:
	python3 cli.py --deck1 decks/70148.ydk --deck2 decks/normal46.ydk --p1 manual

setup: script ffi locale/en/cards.cdb
	pip3 install --user -r requirements.txt

script: vendor/ygopro-scripts
	ln -s vendor/ygopro-scripts script

ffi: libygo.so
	python3 duel_build.py
	rm _duel.cpp _duel.o

libygo.so: vendor/lua-5.3.5/src/liblua.a vendor/ygopro-core
	g++ -shared -fPIC -o $@ vendor/ygopro-core/*.cpp -Ivendor/lua-5.3.5/src -Lvendor/lua-5.3.5/src -llua -std=c++14

vendor/lua-5.3.5:
	wget https://www.lua.org/ftp/lua-5.3.5.tar.gz
	cd vendor; tar xvf ../lua-5.3.5.tar.gz
	rm lua-5.3.5.tar.gz

vendor/lua-5.3.5/src/liblua.a: vendor/lua-5.3.5
	cd vendor/lua-5.3.5 && make linux CC=g++ MYCFLAGS='-O2 -fPIC'

vendor/ygopro-core:
	wget https://github.com/Fluorohydride/ygopro-core/archive/master.zip
	unzip master.zip -d vendor; mv vendor/ygopro-core-master vendor/ygopro-core
	rm master.zip
	patch vendor/ygopro-core/playerop.cpp etc/ygopro-core.patch

vendor/ygopro-scripts:
	wget https://github.com/Fluorohydride/ygopro-scripts/archive/master.zip
	unzip master.zip -d vendor; mv vendor/ygopro-scripts-master vendor/ygopro-scripts
	rm master.zip

locale/en/cards.cdb:
	cd locale/en; wget https://gitlab.com/duelists-unite/cdb/-/raw/master/cards.cdb
