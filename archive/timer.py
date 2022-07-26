import rtmidi.midiconstants
import numpy as np
import time


mo = rtmidi.MidiOut()
mo.open_port(0)
my_velocity = 127
note_number = 60
note_duration = 1



def play_one_note():
    mo.send_message([rtmidi.midiconstants.NOTE_ON, note_number, my_velocity])
    time.sleep(note_duration)
    mo.send_message([rtmidi.midiconstants.NOTE_OFF, note_number, my_velocity])

def play_and_wait(duration):
    play_one_note()
    time.sleep(duration-1)

# preparation
play_and_wait(10)
# upper hang with supination and thoracic extension
play_and_wait(22)
# end exercise
play_one_note()




mo.close_port()
