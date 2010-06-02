/*
 * pywiimote.i
 *
 *  Created on: 30-Nov-2008
 *      Author: dingo
 */

%module pywiimote
%{
  /* Includes the header in the wrapper code */
  #include "pywiimote.h"
%}

/* Some hacks */
#define uint64_t unsigned long
#define uint32_t unsigned int
#define uint16_t unsigned short
#define uint8_t unsigned char

#define __attribute__(foo) 

/* Parse the header files to generate wrappers */
%include "pywiimote.h"
%include "wiimote.h"
%include "wiimote_api.h"
%include "wiimote_link.h"
%include "wiimote_io.h"
%include "wiimote_event.h"
%include "wiimote_ir.h"
%include "wiimote_error.h"
%include "wiimote_util.h"
%include "wiimote_report.h"
%include "wiimote_speaker.h"
%include "wiimote_mii.h"
%include "wiimote_nunchuk.h"
%include "wiimote_classic.h"
