
int seq_open(int client, int port, char *name, int channel);
void seq_close();
void note_on(int note, int vel);
void note_off(int note, int vel);
void control(int type, int val);
void program(int bank, int type);
void bender(int bend);
void chorus_mode(int mode);
void reverb_mode(int mode);
void send_event(int do_flush);
