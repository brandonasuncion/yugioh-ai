cli:
	python3 cli.py --deck1 decks/normal46.ydk --deck2 decks/normal46.ydk

manual:
	 python3 cli.py --deck1 decks/70148.ydk --deck2 decks/normal46.ydk --p1 manual

ffi: libygo.so
	python3 duel_build.py
	rm _duel.cpp _duel.o

liblua.a:
	cd ../lua-5.3.5 && make linux CC=g++ MYCFLAGS='-O2 -fPIC'

libygo.so:
	cd ../ygopro-core && \
	git checkout -- . && \
	patch -p0 < ../yugioh-ai/etc/ygopro-core.patch
	g++ -shared -fPIC -o $@ ../ygopro-core/*.cpp -I../lua-5.3.5/src -L../lua-5.3.5/src -llua -std=c++14
