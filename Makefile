.PHONY: install clean

install:
	chmod +x go2web.py
	ln -sf $(PWD)/go2web.py /usr/local/bin/go2web

clean:
	rm -f /usr/local/bin/go2web 