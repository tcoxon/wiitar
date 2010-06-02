
#include <python2.5/Python.h>

#include "seq.h"


PyObject *wrap_open(PyObject *x, PyObject *args) {
	int client, port, channel, result;
	char *name;
    int ok = PyArg_ParseTuple( args, "iisi", &client, &port, &name, &channel);

    result = seq_open(client, port, name, channel);
    return Py_BuildValue("i",result);
}

PyObject *wrap_close(PyObject *x, PyObject *args) {

    seq_close();

    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *wrap_note_on(PyObject *x, PyObject *args) {
	int note, vel;
    int ok = PyArg_ParseTuple( args, "ii", &note, &vel);

    note_on(note, vel);

    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *wrap_note_off(PyObject *x, PyObject *args) {
	int note, vel;
    int ok = PyArg_ParseTuple( args, "ii", &note, &vel);

    note_off(note, vel);

    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *wrap_bender(PyObject *x, PyObject *args) {
	int bend;
    int ok = PyArg_ParseTuple( args, "i", &bend);

    bender(bend);

    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *wrap_control(PyObject *x, PyObject *args) {
	int type, val;
    int ok = PyArg_ParseTuple( args, "ii", &type, &val);

    control(type, val);

    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *wrap_program(PyObject *x, PyObject *args) {
	int bank, type;
    int ok = PyArg_ParseTuple( args, "ii", &bank, &type);

    program(bank, type);

    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *wrap_chorus_mode(PyObject *x, PyObject *args) {
	int mode;
    int ok = PyArg_ParseTuple( args, "i", &mode);

    chorus_mode(mode);

    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *wrap_reverb_mode(PyObject *x, PyObject *args) {
	int mode;
    int ok = PyArg_ParseTuple( args, "i", &mode);

    reverb_mode(mode);

    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *wrap_send_event(PyObject *x, PyObject *args) {
	int do_flush;
    int ok = PyArg_ParseTuple( args, "i", &do_flush);

    send_event(do_flush);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef methods[] = {
    { "open", wrap_open, METH_VARARGS,
      "open(int client, int port, string name, int channel) -> None.\n"
      "Opens a connection for playing MIDI to."},
    { "close", wrap_close,
      METH_VARARGS,
      "close() -> None.\n"
      "Closes MIDI connection"},
    { "note_on", wrap_note_on,
      METH_VARARGS,
      "note_on(note, vel) -> None.\n"
      "Plays a MIDI note."
    },
    { "note_off", wrap_note_off,
	  METH_VARARGS,
	  "note_off(note, vel) -> None.\n"
	  "Stops a playing MIDI note."
	},
    { "bender", wrap_bender,
	  METH_VARARGS,
	  "bender(bend) -> None."
	},
    { "program", wrap_program, METH_VARARGS, "program(bank, type) -> None." },
    { "control", wrap_control, METH_VARARGS, "control(type, val) -> None." },
    { "chorus_mode", wrap_chorus_mode, METH_VARARGS, "chorus_mode(mode) -> None." },
    { "reverb_mode", wrap_reverb_mode, METH_VARARGS, "chorus_mode(mode) -> None." },
    { "send_event", wrap_send_event, METH_VARARGS, "send_event(do_flush) -> None." },


    {NULL,NULL}
};


extern
#ifdef WIN32
__declspec(dllexport)
#endif
void initmidipy(void) {
    PyObject *m =
        Py_InitModule4(
            "midipy",   // name of the module
            methods,  // name of the method table
            "midi sounds", // doc string for module
            0,   // last two never change
            PYTHON_API_VERSION);
    return;
}
