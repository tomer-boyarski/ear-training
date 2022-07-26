import constants
import rtmidi
import time
import numpy as np


def intro(x=1):
    # mo = rtmidi.MidiOut()
    # mo.open_port(0)
    for i in range(4, 0, -1):
        note_to_play_now = constants.white_note.number[i] + 12
        constants.mo.send_message([rtmidi.midiconstants.NOTE_ON, note_to_play_now, 64])
        time.sleep(constants.quarter_note_time/4/x)
        constants.mo.send_message([rtmidi.midiconstants.NOTE_OFF, note_to_play_now, 64])

    constants.mo.send_message([rtmidi.midiconstants.NOTE_ON, 60, 64])
    time.sleep(constants.quarter_note_time/2/x)
    constants.mo.send_message([rtmidi.midiconstants.NOTE_OFF, 60, 64])
    previous_note_index = np.array([7])

    # mo.close_port()
    return previous_note_index
