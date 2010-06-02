
all: pywiimote.so midipy.so

pywiimote.so:
	cd pywiimote_src && make && mv pywiimote.so .. && mv pywiimote.py ..

midipy.so:
	cd midipy_src && make && mv midipy.so ..

clean:
	rm *.so
	rm pywiimote.py
	cd pywiimote_src && make clean
	cd midipy_src && make clean

