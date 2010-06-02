
all: pywiimote.so pywiimote.py

pywiimote.py pywiimote_wrap.c: pywiimote.c pywiimote.h pywiimote.i
	swig -python -I../../libwiimote/src pywiimote.i

pywiimote.so: pywiimote_wrap.c pywiimote.c pywiimote.h
	gcc -shared -L../../libwiimote/lib -I/usr/include/python2.6 -lpython2.6 -lbluetooth -lcwiimote -I../../libwiimote/src pywiimote.c pywiimote_wrap.c -o _pywiimote.so

clean:
	rm *.so
	rm pywiimote.py pywiimote_wrap.c
