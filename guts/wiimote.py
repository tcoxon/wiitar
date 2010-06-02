
import threading

from pywiimote import *



WIIMOTE_KEYS = {"left": 1, "right": 2, "down": 4, "up": 8,
    "plus": 16, "reserved1": 32, "two": 256, "one": 512,
    "b": 1024, "a": 2048, "minus": 4096, "reserved2": 8192,
    "home": 32768}


CLASSIC_KEYS = {"left":1, "right": 2, "up": 4, "down": 8,
    "l": 16, "r": 32, "zl": 64, "zr": 128,
    "minus": 256, "plus": 512, "home": 1024, "y": 2048,
    "x": 4096, "a": 8192, "b": 16384, "unused": 32768}



class WiimoteDisconnectedException(Exception):
    pass


class WiimoteCannotConnectException(Exception):
    pass


class Wiimote(object):
    
    def __init__(self):
        self.wiimote = None
        self.gkey_state = 0
        self.key_state = 0
        self.last_gkey_state = 0
        self.last_key_state = 0
    
    def open(self, bdaddr):
        self.gkey_state = 0
        self.key_state = 0
        self.last_gkey_state = 0
        self.last_key_state = 0

        # for some reason, this wiimote_discover() stuff doesn't work
#        self.wiimote = wiimote_t()
#        if wiimote_discover(self.wiimote,1) < 1:
#            raise WiimoteCannotConnectException()
#        
#        print self.wiimote.link.r_addr
#        
#        self.wiimote = wiimote_open(self.wiimote.link.r_addr)


        self.wiimote = wiimote_open(bdaddr)
        if self.wiimote == None:
            raise WiimoteCannotConnectException()
            
        self.wiimote.mode.items.acc = 1
        self.wiimote.mode.items.ext = 1
        wiimote_classic_init(self.wiimote)
    
    def close(self):
        wiimote_close(self.wiimote)
        self.wiimote = None
    
    def update(self):
        self.last_key_state = self.wiimote.keys.bits
        self.last_gkey_state = self.guitar.keys.bits
        if wiimote_update(self.wiimote) < 0 or classic_update(self.wiimote) < 0:
            raise WiimoteDisconnectedException()
        self.key_state = self.wiimote.keys.bits
        self.gkey_state = self.guitar.keys.bits
    
    def get_leds(self):
        return self.wiimote.led.bits
    
    def set_leds(self, bits):
        self.wiimote.led.bits = bits
    
    def get_guitar(self):
        return self.wiimote.ext.items.classic
    
    def is_open(self):
        return self.wiimote != None and wiimote_is_open(self.wiimote)
    
    def get_keys(self):
        return self.wiimote.keys.items
    
    def get_gkeys(self):
        return self.guitar.keys.items
    
    def get_tilt(self):
        return self.wiimote.tilt
    
    leds = property(fget=get_leds, fset=set_leds)
    guitar = property(fget=get_guitar)
    keys = property(fget=get_keys)
    gkeys = property(fget=get_gkeys)
    tilt = property(fget=get_tilt)



def get_fret_val(guitar):
    frets = ["a","b","x","y","zl"]
    result = 0
    for i in xrange(len(frets)):
        if guitar.keys.bits & CLASSIC_KEYS[frets[i]]:
            result |= 1 << i
    return result


class Wiitar(threading.Thread):
    
    def __init__(self, bdaddr, printing=True):
        threading.Thread.__init__(self, name="Wiitar-"+bdaddr)
        self.wiimote = Wiimote()
        self.bdaddr = bdaddr
        self.printing = printing
        self.classic_events = {}
        self.wiimote_events = {}
        self.whammy_event = None
        self.fret_val = 0
    
    def run(self):
        if self.printing:
            print "Press 1 and 2 on the wiimote now to connect to", self.bdaddr
            
        wiimote = self.wiimote
        wiimote.open(self.bdaddr)
        
        if self.printing:
            print "Connected to", self.bdaddr, "(Press Home to disconnect)"
            
        try:
            wiimote.leds = 1
            wiimote.update()
            guitar = wiimote.guitar
            
            while wiimote.is_open():
                try:
                    wiimote.update()
                except Exception, e:
                    print e
                    break
                
                if wiimote.keys.home:
                    break
                
                self.fret_val = get_fret_val(guitar)
                
                pressed = wiimote.key_state & ~wiimote.last_key_state
                released = wiimote.last_key_state & ~wiimote.key_state
                gpressed = wiimote.gkey_state & ~wiimote.last_gkey_state
                greleased = wiimote.last_gkey_state & ~wiimote.gkey_state
                
                self.classic_keys_down = set()
                for key in CLASSIC_KEYS.keys():
                    if wiimote.gkey_state & CLASSIC_KEYS[key]:
                        self.classic_keys_down.add(CLASSIC_KEYS[key])
                
                self.wiimote_keys_down = set()
                for key in WIIMOTE_KEYS.keys():
                    if wiimote.key_state & WIIMOTE_KEYS[key]:
                        self.wiimote_keys_down.add(WIIMOTE_KEYS[key])
                
                if pressed != 0 or released != 0:
                    for key in WIIMOTE_KEYS.keys():
                        if WIIMOTE_KEYS[key] & pressed and \
                                self.wiimote_events.has_key(WIIMOTE_KEYS[key]):
                            self.wiimote_events[WIIMOTE_KEYS[key]](self, False, key, 1)
                        if WIIMOTE_KEYS[key] & released and \
                                self.wiimote_events.has_key(WIIMOTE_KEYS[key]):
                            self.wiimote_events[WIIMOTE_KEYS[key]](self, False, key, 0)

                if gpressed != 0 or greleased != 0:
                    for key in CLASSIC_KEYS.keys():
                        if CLASSIC_KEYS[key] & gpressed and \
                                self.classic_events.has_key(CLASSIC_KEYS[key]):
                            self.classic_events[CLASSIC_KEYS[key]](self, True, key, 1)
                        if CLASSIC_KEYS[key] & greleased and \
                                self.classic_events.has_key(CLASSIC_KEYS[key]):
                            self.classic_events[CLASSIC_KEYS[key]](self, True, key, 0)
                
                if self.whammy_event is not None:
                    if wiimote.guitar.r != 24:
                        # libwiimote bug (?) makes whammy 24 sometimes while
                        # playing o-o--
                        self.whammy_event(self, wiimote.guitar.r)
                
            if self.printing: print "Closed connection to", self.bdaddr
        finally:
            wiimote.close()
