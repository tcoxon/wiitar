
from wiimote import WIIMOTE_KEYS, CLASSIC_KEYS



class Guitar(object):
    """
    Guitar class remembers saved chord information, etc.
    """
    
    programs = [(24,"Nylon"),
                (26,"Jazz"),
                (29,"Overdrive"),
                (30,"Distortion"),
                (32,"Acoustic Bass"),
                (33,"Fingered Bass"),
                (28,"Muted")]
    
    def __init__(self, chord_seq):
        self.chord_seq = chord_seq
        ## TODO: load chords from conf?
        self.base_offset = 47
        self._note_offset = 0
#        self.chords = {1: [1,5,8], # C
#            2: [2, 6, 9], # C#
#            3: [3, 7, 10], # D
#            4: [4, 8, 11], # D#
#            5: [5, 9, 12], # E
#            6: [6, 10, 13], # F
#            7: [7, 11, 14], # F#
#            8: [8, 12, 15], # G
#            9: [9, 13, 16], # G#
#            10:[10, 14, 17], # A
#            11:[11, 15, 18], # A#
#            12:[12, 16, 19], # B
#        } # dict: chord_id -> note list
        self.chords = {1: [1,5,8], # C
            2: [3, 7, 10], # D
            3: [5, 9, 12], # E
            4: [6, 10, 13], # F
            5: [8, 12, 15], # G
            6:[10, 14, 17], # A
            7:[12, 16, 19], # B
        } # dict: chord_id -> note list
        self.program = 0
    
    def play_note(self, note):
        self.chord_seq.play_note(note + self.base_offset + self._note_offset)
    
    def stop_note(self, note):
        self.chord_seq.stop_note(note + self.base_offset + self._note_offset)
    
    def play_chord(self, chord, sharpen=False):
        chord = self.chords.get(chord)
        if chord is not None:
            sharpen_val = 1 if sharpen else 0
            self.chord_seq.play_chord([
                note + self.base_offset + self._note_offset + sharpen_val
                for note in chord])
    
    def stop_chord(self, chord):
        chord = self.chords.get(chord)
        if chord is not None:
            self.chord_seq.stop_chord([
                note + self.base_offset + self._note_offset
                for note in chord])
    
    def save_chord(self, chord_id, chord):
        # TODO: save speed information
        self.chords[chord_id] = chord
    
    def del_chord(self, chord_id):
        del self.chords[chord_id]
    
    def mute(self):
        self.chord_seq.mute()
    
    def get_offset_octaves(self):
        return self._note_offset/12
    
    def set_offset_octaves(self, v):
        self.mute()
        self._note_offset = v*12
        
    def get_program(self):
        return self._program
    
    def set_program(self, v):
        self._program = v % len(self.programs)
        self.chord_seq.program(self.programs[self._program][0])
        print "Program:", self.programs[self._program][1]
    
    def get_bend(self):
        return self.chord_seq.bend
    
    def set_bend(self, bend):
        self.chord_seq.bend = bend
    
    offset_octaves = property(fget=get_offset_octaves, fset=set_offset_octaves)
    program = property(fget=get_program, fset=set_program)
    bend = property(fget=get_bend, fset=set_bend)


table_octave8 = [0,2,4,5,7,9,11,12]
def octave8(note):
    """
    Algorithm for converting from an 8 note per octave scale to a 12 note per
    octave scale (i.e. binary scale to midi scale).
    """
    octave = (note - 1) / 8
    pos = (note - 1) % 8
    pos = table_octave8[pos]
    return octave * 12 + pos + 1

def fret_note_to_tab(note):
    if (note-1)%12 in [1,3,6,8,10]:
        note -= 1
        sharpen = True
    else:
        sharpen = False
        
    result = ""
    for i in xrange(5):
        if note & (1 << i):
            result += "o"
        else:
            result += "-"
            
    if sharpen:
        result += " #"
        
    return result

def fret_chord_to_tab(chord):
    result = ""
    for i in xrange(5):
        if chord & (1 << i):
            result += "o"
        else:
            result += "-"
    return result


class InvalidPlayingModeError(Exception):
    pass


class WiitarGuitarAdapter(object):
    
    def __init__(self, guitar, wiitar):
        self.wiitar = wiitar
        self.guitar = guitar
        wiitar.classic_events[CLASSIC_KEYS["down"]] = self.strum_event
        wiitar.classic_events[CLASSIC_KEYS["up"]] = self.strum_event
        for fret in ["a","b","x","y","zl"]:
            wiitar.classic_events[CLASSIC_KEYS[fret]] = self.fret_event
        wiitar.wiimote_events[WIIMOTE_KEYS["one"]] = self.one_event
        wiitar.wiimote_events[WIIMOTE_KEYS["two"]] = self.two_event
        wiitar.wiimote_events[WIIMOTE_KEYS["plus"]] = self.wplus_event
        wiitar.wiimote_events[WIIMOTE_KEYS["minus"]] = self.wminus_event
        wiitar.wiimote_events[WIIMOTE_KEYS["a"]] = self.record_event
        
        wiitar.whammy_event = self.whammy_event
        
        self.octave_mode = 8 # alternative is 12. to hit a sharp in mode 8,
            # hold the frets for the base note, and strum up. In mode 12,
            # the frets specify the binary code for the 12-per-octave midi note
        
        self.mode = 1 # 1 is single note mode, 2 is chord playing mode
    
    def _fret_to_note(self, fret_val, key):
        if self.octave_mode == 8:
            note = octave8(fret_val)
            if key == "up":
                #self.guitar.stop_note(note) ## hack
                self.guitar.mute() ## hack
                note += 1 # strum up to hit sharps
            else:
                #self.guitar.stop_note(note+1) ## hack
                self.guitar.mute() ## hack
            ## above two hacks necessary because there's no fret change event
            ## to cause guitar to mute between, e.g. C and C# 
            return note
        elif self.octave_mode == 12:
            return fret_val
    
    def record_event(self, wiitar, is_classic, key, status):
        if status: return
        if self.mode != 3:
            if  wiitar.fret_val == 0: return
            
            self.last_mode = self.mode
            self.mode = 3
            self.chord_pattern = wiitar.fret_val
            self.chord_notes = []
            print "Recording for chord", fret_chord_to_tab(wiitar.fret_val), ":"
        else:
            self.mode = self.last_mode
            print "Finished recording chord", fret_chord_to_tab(self.chord_pattern)
            self.guitar.chords[self.chord_pattern] = self.chord_notes
    
    def strum_event(self, wiitar, is_classic, key, status):
        if not status: return
        
        ## Tilting guitar moves up/down by 1 octave
        if wiitar.wiimote.tilt.y < -40: self.guitar.offset_octaves = 1
        elif wiitar.wiimote.tilt.y > 40: self.guitar.offset_octaves = -1
        else: self.guitar.offset_octaves = 0
                
        if CLASSIC_KEYS["plus"] not in wiitar.classic_keys_down:
            if self.mode in [1,3]:
                # Single note mode
                
                if wiitar.fret_val != 0:
                    note = self._fret_to_note(wiitar.fret_val, key)
                    self.guitar.play_note(note)
                    if self.mode == 3:
                        self.chord_notes.append(note)
                        print fret_chord_to_tab(wiitar.fret_val), \
                        ("#" if key == "up" and self.octave_mode != 12 else "")
                    
            elif self.mode == 2:
                # TODO: chord mode
                if wiitar.fret_val != 0:
                    self.guitar.play_chord(wiitar.fret_val, sharpen=(key=="up"))
                
            else:
                raise InvalidPlayingModeError()
        else:
            if key == "down":
                self.guitar.program -= 1
            else:
                self.guitar.program += 1
            wiitar.wiimote.leds = self.guitar.program + 1
    
    def fret_event(self, wiitar, is_classic, key, status):
        self.guitar.mute()
    
    def one_event(self, wiitar, is_classic, key, status):
        if status:
            ## single note mode
            self.mode = 1
            print "Switched to single-note mode."
    
    def two_event(self, wiitar, is_classic, key, status):
        if status:
            ## chord mode
            self.mode = 2
            print "Switched to chord-playing mode."
    
    def wplus_event(self, wiitar, is_classic, key, status):
        if status:
            ## plus on the WIIMOTE, not CLASSIC controller
            ## switch to 12 per octave mode
            self.octave_mode = 12
            print "Switched to 12 note per octave mode."
    
    def wminus_event(self, wiitar, is_classic, key, status):
        if status:
            ## minus on the WIIMOTE, not CLASSIC controller
            ## switch to 8 per octave mode
            self.octave_mode = 8
            print "Switched to 8 note per octave mode."
    
    def whammy_event(self, wiitar, whammy_val):
        # whammy_val ranges from 15 (fully up) to 26 (fully down)
        if whammy_val > 26: return # libwiimote bug
            ## another libwiimote bug sometimes makes bend -6554
            ##    when playing o-o--   :-S
            ##    workaround in wiimote.py event loop
        if whammy_val > 16:
            bend = (-8192*(whammy_val-16))/(26-16)
            #print "bend", bend
        else: bend = 0
        self.guitar.bend = bend
