import rtmidi
# import rtmidi_python as rtmidi
# import python_rtmidi as rtmidi
import numpy as np
import time
from termcolor import colored
import matplotlib.pyplot as plt
import pickle
volume = 100
note = 57
base = 2
mo = rtmidi.MidiOut()
mo.open_port(0)
mo.send_message([144, note, volume])
time.sleep(1)
mo.send_message([128, note, volume])
num_tries_list = []
# list_of_possible_note_numbers = [60, 67, 64, 57, 62, 65, 59]
# list_of_possible_note_names = ['C', 'G', 'E', 'A', 'D', 'F', 'B']
list_of_possible_note_numbers = [57, 59, 60, 62, 64, 65, 67, 69, 71, 72]
list_of_possible_note_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'A', 'B', 'C']
# for _ in range(10):
termination_flag = False
i = 3
delta = 0.1
i_list = []
while not termination_flag:
    i_list.append(i)
    possible_notes = ' '.join(list_of_possible_note_names[:round(i)])
    print('possible notes: ' + possible_notes)
    indices = np.random.choice(np.arange(round(i)), size=2, replace=False)
    notes = np.take(list_of_possible_note_numbers, indices=indices)
    names = np.take(list_of_possible_note_names, indices=indices)
    names = np.sort(names)
    names = names.tolist()
    success = False
    num_tries = 1
    while not success:
        for note in notes:
            mo.send_message([144, note, volume])
        x = input("Identify Note:")
        time.sleep(1)
        for note in notes:
            mo.send_message([128, note, volume])
        x = x.upper()
        if x == 'END':
            termination_flag = True
            success = True
        elif x == ''.join(names):
            print(colored("Good :-)", 'blue'))
            success = True
            i = i + delta
        elif x == 'REVEAL':
            print(names)
            termination_flag = True
            success = True
        else:
            print(colored("try again", 'red'))
            num_tries = num_tries + 1
            i = i - delta*2
    num_tries_list.append(num_tries)
mo.close_port()
# pickle.dump(num_tries_list, open('tomer', "wb"))
num_tries_list = num_tries_list[:-1]
# print(num_tries_list)
fig, ax = plt.subplots(1, 2)
ax[0].plot(i_list)
ax[0].set_title('i_list')
ax[1].plot(num_tries_list)
ax[1].set_title('num_tries_list')
fig.canvas.draw()
plt.show()
