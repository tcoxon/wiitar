
import time
import midipy as midi

midi.open(128, 0, "midipy test", 0)

for (note, t) in [(48,0.5),(48,0.5),(50,1.0),(48,1.0),(53,1.0),(52,1.0),
                    (48,0.5),(48,0.5),(50,1.0),(48,1.0),(55,1.0),(53,1.0)]:
    midi.note_on(note,127)
    time.sleep(t/2)
    midi.note_off(note,127)

midi.close()
