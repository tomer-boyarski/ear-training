import rtmidi
# import rtmidi_python as rtmidi
# import python_rtmidi as rtmidi
import numpy as np
import time
import pickle
volume = 100
note = 60
base = 2
mo = rtmidi.MidiOut()
mo.open_port(0)
mo.send_message([144, note, volume])
time.sleep(1)
mo.send_message([128, note, volume])
num_tries_list = []
for _ in range(10):
    i = np.random.choice([0, 4, 7])
    success = False
    num_tries = 1
    while not success:
        mo.send_message([144, note+i, volume])
        x = input("Identify Note:")
        time.sleep(1)
        mo.send_message([128, note+i, volume])
        x = x.upper()
        if (i == 0 and x == 'DO') or (i == 4 and x == 'MI') or (i == 7 and x == 'SOL'):
            print('Good')
            success = True
        else:
            print('try again')
            num_tries = num_tries + 1
    num_tries_list.append(num_tries)
mo.close_port()
pickle.dump(num_tries_list, open('ido', "wb"))
print(num_tries_list)
