/*
 * pywiimote.c
 *
 *  Created on: 30-Nov-2008
 *      Author: dingo
 */

#include "pywiimote.h"
#include <string.h>

// CLASSIC_MEM_START also defined in wiimote_classic.c
#define CLASSIC_MEM_START	0x04a40000
// mega hack because part of libwiimote seems to be (or was?) missing...
int classic_update(wiimote_t *wiimote)
{
	uint8_t data[16];
	uint8_t empty[8];
	int i;

	memset(empty, 0, 8);

	if (wiimote_read(wiimote, CLASSIC_MEM_START, data, 16) < 0) {
		wiimote_set_error("classic_update(): unable to read classic "
			"state: %s", wiimote_get_error());
		return WIIMOTE_ERROR;
	}

	// "decrypt" data
	for(i = 0; i < 16; i++) {
		data[i] = (data[i]^0x17)+0x17;
	}

	if (memcmp(data+8, empty, 8) == 0) {
		// weird wiimote bug?
		return 0;
	}

	return wiimote_classic_update(wiimote, data+8);
}


#undef wiimote_is_open
#undef wiimote_is_closed

int wiimote_is_open(wiimote_t *w) {
	return (w)->link.status == WIIMOTE_STATUS_CONNECTED;
}
int wiimote_is_closed(wiimote_t *w) {
	return !wiimote_is_open(w);
}

