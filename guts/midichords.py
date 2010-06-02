
import sys
import midipy as midi

# TODO: take other midi arguments off sys.argv[]
midi.open(128, 0, sys.argv[0], 0)

note_vel = 127

class ChordSequencerClass(object):
    
    def __init__(self):
        # TODO: use chord save information etc. ?
        self.playing = []
        self._bend = 0
    
    def play_note(self, note):
        if self.is_playing_note(note):
            self.stop_note(note)
        self.playing.append(set([note]))
        midi.note_on(note, note_vel)
    
    def stop_note(self, note):
        to_remove = []
        for i in xrange(len(self.playing)):
            if note in self.playing[i]:
                self.playing[i].remove(note) # remove note from playing chord
                if len(self.playing[i]) == 0: # if chord's empty, remove it
                    to_remove.append(i)
        for i in to_remove: del self.playing[i]
        midi.note_off(note, note_vel)
    
    def is_playing_note(self, note):
        for chord in self.playing:
            if note in chord: return True
        return False
    
    def play_chord(self, chord):
        """
        Chord should be an ordered iterable container of notes
        """
        if self.is_playing_chord(chord):
            self.stop_chord(chord)
        self.playing.append(set(chord))
        for note in chord:
            # TODO: timing & stopping note_on when chord already stopped
            midi.note_on(note, note_vel)
    
    def stop_chord(self, chord):
        if self.is_playing_chord(chord):
            self.playing.remove(set(chord))
            for note in chord:
                midi.note_off(note, note_vel)
    
    def is_playing_chord(self, chord):
        return set(chord) in self.playing
    
    def mute(self):
        muted = set()
        for chord in self.playing:
            for note in chord:
                if note not in muted:
                    muted.add(note)
                    midi.note_off(note, note_vel)
        self.playing = []
    
    def program(self, prog):
        midi.program(0,prog)
        
    def set_bend(self, bend):
        if self._bend != bend:
            self._bend = bend
            midi.bender(bend)
    
    def get_bend(self):
        return self._bend
    
    bend = property(fget=get_bend, fset=set_bend)
    

# ChordSequencer is currently singleton because the midipy library is singleton
seq = ChordSequencerClass()
def ChordSequencer():
    return seq
