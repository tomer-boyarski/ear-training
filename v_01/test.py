import rtmidi.midiconstants
import constants
import time
for i in range(10):
    constants.mo.send_message([rtmidi.midiconstants.NOTE_ON, 60, 127])
time.sleep(2)
for i in range(10):
    constants.mo.send_message([rtmidi.midiconstants.NOTE_OFF, 60, 127])
constants.mo.close_port()
