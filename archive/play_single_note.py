import rtmidi.midiconstants
import time
mo = rtmidi.MidiOut()
my_note = 68
mo.open_port(0)
mo.send_message([rtmidi.midiconstants.NOTE_ON, my_note, 127])
time.sleep(1)
mo.send_message([rtmidi.midiconstants.NOTE_OFF, my_note, 127])

mo.close_port()
