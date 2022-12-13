//
// common.h
//
// Author:
//       Christopher "Zoggins" Mallery <zoggins@retro-spy.com>
//
// Copyright (c) 2020 RetroSpy Technologies
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.

#include "Arduino.h"

#if defined(__arm__) && defined(CORE_TEENSY)
#include "config_teensy.h"
#else
#include "config_arduino.h"
#endif

#define NES_BITCOUNT 8

#define PIN_READ PIND_READ

#define WAIT_FALLING_EDGE(pin) \
	while (!PIN_READ(pin))     \
		;                      \
	while (PIN_READ(pin))      \
		;
#define WAIT_LEADING_EDGE(pin) \
	while (PIN_READ(pin))      \
		;                      \
	while (!PIN_READ(pin))     \
		;

#define WAIT_FALLING_EDGEB(pin) \
	while (!PINB_READ(pin))     \
		;                       \
	while (PINB_READ(pin))      \
		;
#define WAIT_LEADING_EDGEB(pin) \
	while (PINB_READ(pin))      \
		;                       \
	while (!PINB_READ(pin))     \
		;

#define ZERO ((uint8_t)0) // Use a byte value of 0x00 to represent a bit with value 0.
#define ONE '1'			  // Use an ASCII one to represent a bit with value 1.  This makes Arduino debugging easier.
#define SPLIT '\n'		  // Use a new-line character to split up the controller state packets.

void common_pin_setup();
void sendTimeDiff();
