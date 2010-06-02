/*
 * pywiimote.h
 *
 *  Created on: 30-Nov-2008
 *      Author: dingo
 */

#ifndef PYWIIMOTE_H_
#define PYWIIMOTE_H_

#include "wiimote.h"
#include "wiimote_api.h"

int classic_update(wiimote_t *wiimote);

#undef wiimote_is_open
#undef wiimote_is_closed

int wiimote_is_open(wiimote_t *w);
int wiimote_is_closed(wiimote_t *w);


#endif /* PYWIIMOTE_H_ */
