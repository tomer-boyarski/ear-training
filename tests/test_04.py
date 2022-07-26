import rtmidi
# import rtmidi_python as rtmidi
# import python_rtmidi as rtmidi
import time
volume = 100
note = 60
base = 2
mo = rtmidi.MidiOut()
mo.open_port(0)
for i in range(3):
    mo.send_message([144, note+12*i, volume/base**i])
time.sleep(1)
for i in range(3):
    mo.send_message([128, note+12*i, volume/base**i])
mo.close_port()
