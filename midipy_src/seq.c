#include <unistd.h>
#include <ctype.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#ifdef USE_OLD_ALSA
#include <sys/asoundlib.h>
#else
#include <alsa/asoundlib.h>
#endif

#include "seq.h"

#if SND_LIB_MAJOR > 0 || SND_LIB_MINOR >= 6
#define snd_seq_flush_output(x) snd_seq_drain_output(x)
#define snd_seq_set_client_group(x,name) /*nop*/
#define my_snd_seq_open(seqp) snd_seq_open(seqp, "hw", SND_SEQ_OPEN_OUTPUT, 0)
#else
/* SND_SEQ_OPEN_OUT causes oops on early version of ALSA */
#define my_snd_seq_open(seqp) snd_seq_open(seqp, SND_SEQ_OPEN)
#endif

snd_seq_event_t ev;

snd_seq_t *seq_handle = NULL;
int my_client, my_port;
int seq_client = 128, seq_port = 0;
unsigned int caps;
char *my_name = NULL;
int chan_no = 0;

void send_event(int do_flush) {
	snd_seq_ev_set_direct(&ev);
	snd_seq_ev_set_source(&ev, my_port);
	snd_seq_ev_set_dest(&ev, seq_client, seq_port);

	snd_seq_event_output(seq_handle, &ev);
	if (do_flush)
		snd_seq_flush_output(seq_handle);
}

// eg. seq_open(128,0,"My Program", 0)
int seq_open(int client, int port, char *name, int channel) {
	seq_client = client;
	seq_port = port;
	my_name = name;
	chan_no = channel;

	my_snd_seq_open(&seq_handle);
	my_client = snd_seq_client_id(seq_handle);
	snd_seq_set_client_name(seq_handle, name);
	snd_seq_set_client_group(seq_handle, "input");
	caps = SND_SEQ_PORT_CAP_READ;
	if (seq_client == SND_SEQ_ADDRESS_SUBSCRIBERS)
		caps |= SND_SEQ_PORT_CAP_SUBS_READ;
	my_port = snd_seq_create_simple_port(seq_handle, name, caps,
					     SND_SEQ_PORT_TYPE_MIDI_GENERIC |
					     SND_SEQ_PORT_TYPE_APPLICATION);

	if (my_port < 0) {
		puts("can't create port\n");
		snd_seq_close(seq_handle);
		return 0;
	}

	if (seq_client != SND_SEQ_ADDRESS_SUBSCRIBERS) {
		if (snd_seq_connect_to(seq_handle, my_port, seq_client, seq_port) < 0) {
			printf("can't subscribe to MIDI port (%d:%d)\n", seq_client, seq_port);
			snd_seq_close(seq_handle);
			return 0;
		}
	}

	// some sensible defaults

	program(0,0);

	control(1,0);
	control(7,127);
	control(11,127);
	control(10,64);
	control(91,0);
	control(93,0);
	control(64,0);
	control(66,0);


	chorus_mode(0);

	reverb_mode(0);

	return 1;
}

void control(int type, int val) {
	snd_seq_ev_set_controller(&ev, chan_no, type, val);
	send_event(1);
}

void program(int bank, int preset) {
	snd_seq_ev_set_controller(&ev, 0, 0, bank);
	send_event(0);

	snd_seq_ev_set_pgmchange(&ev, chan_no, preset);
	send_event(1);
}


void note_on(int note, int vel) {
	snd_seq_ev_set_noteon(&ev, chan_no, note, vel);
	send_event(1);
}

void note_off(int note, int vel) {
	snd_seq_ev_set_noteoff(&ev, chan_no, note, 127);
	send_event(1);
}

void seq_close() {
	snd_seq_close(seq_handle);
}

void bender(int bend) {
	snd_seq_ev_set_pitchbend(&ev, chan_no, bend);
	send_event(1);
}

void chorus_mode(int mode) {
	static unsigned char sysex[11] = {
		0xf0, 0x41, 0x10, 0x42, 0x12, 0x40, 0x01, 0x38, 0, 0, 0xf7,
	};
	sysex[8] = mode;
	snd_seq_ev_set_sysex(&ev, 11, sysex);
	send_event(1);
	snd_seq_ev_set_fixed(&ev); /* reset */
}

void reverb_mode(int mode) {
	static unsigned char sysex[11] = {
		0xf0, 0x41, 0x10, 0x42, 0x12, 0x40, 0x01, 0x30, 0, 0, 0xf7,
	};
	sysex[8] = mode;
	snd_seq_ev_set_sysex(&ev, 11, sysex);
	send_event(1);
	snd_seq_ev_set_fixed(&ev); /* reset */
}

