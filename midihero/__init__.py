
import sys
from sys import stderr

import midi


twelve_table = "010100101010"
def twelve2eight(note):
    #print "twelve2eight(", note, ")"
    octave = (note - 1) / 12
    note = ((note - 1) % 12) + 1
    result = 0
    for i in range(note):
        if twelve_table[i] == "0":
            result += 1
    
    r = (result + octave * 8, twelve_table[note-1] == "1")
    #print "return", r
    return r

note_table = "cdefgabc"
def notate(note, sharp):
    if note < 1: return "????? -"
    if note > 31: return "????? +"
    
    result = ""
    
    for i in range(5):
        if note & (1 << i):
            result += "o"
        else:
            result += "-"
    
    result += " " + note_table[(note - 1) % 8]
    
    if sharp: result += " #"
    
    return result

def midi2hero(offset, note):
    note8, sharp = twelve2eight(note+offset)
    
    notation = str(note)+", "+notate(note8, sharp)
    return notation

def main():
    from optparse import OptionParser
    
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="midifile", metavar="FILE",
        help="Read MIDI data from FILE")
    parser.add_option("-o", "--octave", dest="octave", metavar="N", default="4",
        help="Offset notes into Nth octave. Default is 4.")
    parser.add_option("-t", "--track", dest="track", metavar="N", default="1",
        help="Use the Nth track to generate hero tabs. Default is 1.")
    
    (options, args) = parser.parse_args()
    
    midifile = options.midifile
    octave = int(options.octave) # default to 4
    track = int(options.track)
    
    if midifile is None:
        print >> stderr, "hero.py: No file given."
        sys.exit(-1)
    
    m = midi.MidiFile()
    m.open(midifile)
    m.read()
    m.close()
    
    #for track in m.tracks:
    #    print track.
    
    offset = -octave*12+1
    
    t = -1
    for event in m.tracks[track].events:
        #print event
        
        if event.type == "NOTE_ON" and event.velocity != 0:
            #print event
            #print event.pitch, "(t =", event.time, ")"
            
            if t != event.time:
                print
            #print midi2hero(-35,event.pitch)
            print "\t", midi2hero(offset, event.pitch), 
            #print midi2hero(-59,event.pitch)
            
            t = event.time
    print

if __name__ == "__main__":
    main()
