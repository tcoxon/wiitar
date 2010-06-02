
all: midipy.so

midipy.so: midipy.c seq.c seq.h
	gcc -shared -lpython2.6 -lasound midipy.c seq.c -o midipy.so

clean:
	rm *.o *.so
