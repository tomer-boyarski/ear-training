import constants
import rtmidi
import time
import numpy as np


# def intro(x=1):
#     # mo = rtmidi.MidiOut()
#     # mo.open_port(0)
#     note_on = 144
#     note_off = 128
#     for i in range(4, 0, -1):
#         note_to_play_now = constants.keys.white.numbers[i] +12
#         constants.mo.send_message([note_on, note_to_play_now, 64])
#         time.sleep(constants.quarter_note_time/4/x)
#         constants.mo.send_message([note_off, note_to_play_now, 64])
#
#     constants.mo.send_message([note_on, 60, 64])
#     time.sleep(constants.quarter_note_time/2/x)
#     constants.mo.send_message([note_off, 60, 64])
#     previous_note_index = np.array([7])
#
#     # mo.close_port()
#     return previous_note_index
