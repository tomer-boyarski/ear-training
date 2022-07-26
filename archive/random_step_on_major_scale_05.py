import rtmidi.midiconstants
import numpy as np
from termcolor import colored
import matplotlib.pyplot as plt
import time
import seaborn as sns
import pickle

time_beginning_of_program = time.time()

mo = rtmidi.MidiOut()
mo.open_port(0)
my_velocity = 127
note_numbers_C_to_C = np.array([60, 62, 64, 65, 67, 69, 71, 72])
# note_numbers_C_to_B = np.unique(np.concatenate((note_numbers_C_to_B-12, note_numbers_C_to_B, note_numbers_C_to_B+12)))
note_numbers_C_to_C = np.unique(np.concatenate((note_numbers_C_to_C - 12, note_numbers_C_to_C)))
range_of_notes = len(note_numbers_C_to_C)

# note_names_C_to_B = {'C': [60, 72], 'D': [62], 'E': [64], 'F': [65], 'G': [67], 'A': [69], 'B': [71]}
note_names_C_to_B = np.array(['C', 'CS', 'D', 'DS', 'E', 'F', 'FS', 'G', 'GS', 'A', 'AS', 'B'])
# note_names_C_to_B = np.array(['C', 'D', 'E', 'F', 'G', 'A', 'B'])
bpm = 30 # beats per minutes
quarter_note_time = 60/bpm

Termination_Flag = False

# class Question:
#     def __init__(self):
#         self.max_step_size = max_step_size
#         self.step_size = step_size_list





max_step_size = 1
last_sample_weight = 0.5

response_time_value_for_error = np.nan

minimal_response_time = 0.7
lower_bound_response_time = 1.25
upper_bound_response_time = 2.25




response_time = [[]]

note_durations = []
new_level_question_indices = [0]
max_step_size_list = []
step_size_list = []
Response_Type = []

question_list_note_indices = []
question_list_note_numbers = []
question_list_note_names = []

answer_list_note_indices = []
answer_list_note_numbers = []
answer_list_note_names = []

previous_note_number = 60
previous_note_name = 'C'

num_jump = np.zeros((len(note_numbers_C_to_C), len(note_numbers_C_to_C)))
num_jump_succ = np.zeros(num_jump.shape)
time_to_correct_answer = np.zeros(num_jump.shape)


def create_new_question(previous_note_index,
                        max_step_size_now,
                        range_of_notes,
                        step_size_list):
    while True:
        if max_step_size_now >0:
            new_note_index = previous_note_index + \
                             (-1) ** np.random.binomial(1, 0.5) * \
                             np.random.choice(np.arange(1, 1 + max_step_size_now), 1)
            new_note_index = new_note_index[0]
            if np.random.binomial(1, 1 / 4 / max_step_size_now):
                new_note_index = previous_note_index
        elif max_step_size_now == 0:
            new_note_index = previous_note_index
        if 0 <= new_note_index < range_of_notes:
            break
    return new_note_index


def intro():
    for i in range(4, 0, -1):
        note_to_play_now = note_numbers_C_to_C[i] +12
        mo.send_message([rtmidi.midiconstants.NOTE_ON, note_to_play_now, my_velocity])
        time.sleep(quarter_note_time/4/2)
        mo.send_message([rtmidi.midiconstants.NOTE_OFF, note_to_play_now, my_velocity])

    mo.send_message([rtmidi.midiconstants.NOTE_ON, 60, my_velocity])
    time.sleep(quarter_note_time/2/2)
    mo.send_message([rtmidi.midiconstants.NOTE_OFF, 60, my_velocity])
    previous_note_index = 7
    return previous_note_index


def calculate_autoregressive(autoregressive_response_time,
                             step_size,
                             response_time_now):
    if len(autoregressive_response_time) == step_size-1:
        autoregressive_response_time.append([])
        autoregressive_response_time[step_size - 1].append(response_time_now*2**step_size)
    else:
        previous_autoregressive = autoregressive_response_time[step_size - 1][-1]
        new_autoregressive = (1-last_sample_weight) * previous_autoregressive + \
                             last_sample_weight * response_time_now
        autoregressive_response_time[step_size - 1].append(new_autoregressive)
    return autoregressive_response_time

previous_note_index = intro()
new_note_index = previous_note_index
slow_answer_in_previous_question = False
First_Question_Flag = True
autoregressive_response_time = [[(lower_bound_response_time + upper_bound_response_time) / 2]]
list_of_lists_of_question_indices = [[]]
cycle_index = 0
question_index = 0
Error_Mode = 'No Recent Errors'

while not Termination_Flag:
    print('question_index = ' + str(question_index))
    previous_note_index = new_note_index
    max_step_size_list.append(max_step_size)
    if Error_Mode == 'No Recent Errors':
        if not slow_answer_in_previous_question:
            new_note_index = \
                create_new_question(previous_note_index,
                                    max_step_size,
                                    range_of_notes,
                                    step_size_list)
    elif Error_Mode != 'No Recent Errors':
        new_note_index = question_list_note_indices[-2]
    step_size_list.append(np.abs(new_note_index - previous_note_index))
    slow_answer_in_previous_question = True
    question_list_note_indices.append(new_note_index)
    new_note_number = note_numbers_C_to_C[new_note_index]
    new_note_name = note_names_C_to_B[new_note_number % 12]
    question_list_note_numbers.append(new_note_number)
    num_jump[previous_note_index, new_note_index] += 1
    # Play note:
    mo.send_message([rtmidi.midiconstants.NOTE_ON, new_note_number, my_velocity])
    question_start_time = time.time()
    identified_note = input("Identify Note:")
    response_time_now = time.time() - question_start_time
    response_time_now_fraction = response_time_now - np.round(response_time_now)
    # Round up sound duration to nearest second:
    time.sleep(1 - response_time_now_fraction)
    # Turn off note:
    mo.send_message([rtmidi.midiconstants.NOTE_OFF, new_note_number, my_velocity])
    identified_note = identified_note.upper()
    if identified_note == new_note_name:  # or idendtified_note == str(note_number-notes_numbers_to_play_now[0]+1):\
        list_of_lists_of_question_indices[cycle_index].append(question_index)
        Response_Type.append(1)
        answer_list_note_names.append(new_note_name)
        response_time[cycle_index].append(response_time_now)
        autoregressive_response_time[cycle_index].append(
            (1-last_sample_weight) * autoregressive_response_time[cycle_index][-1] +
            last_sample_weight * response_time_now)
        auto_reg_now = autoregressive_response_time[cycle_index][-1]
        if auto_reg_now < lower_bound_response_time \
                and max_step_size < 8:
            max_step_size += 1
        elif auto_reg_now > upper_bound_response_time \
                and max_step_size > 0 \
                and max_step_size > 0:
            max_step_size -= 1
        if response_time_now < quarter_note_time:
            slow_answer_in_previous_question = False
        if not First_Question_Flag:
            time_to_correct_answer[previous_note_index,
                                   new_note_index] += \
                    time.time() - question_start_time
            num_jump_succ[previous_note_index,
                          new_note_index] += 1
        print(colored("Good :-)", 'blue'))
        if Error_Mode == 'Just Made an Error':
            Error_Mode = 'Error in Previous Question'
            print('Error_Mode = ' + Error_Mode)
        elif Error_Mode == 'Error in Previous Question':
            Error_Mode = 'No Recent Errors'
            print('Error_Mode = ' + Error_Mode)
    else:
        # Remove the initialization of the autoregressive response time of this cycle:
        autoregressive_response_time[-1] = autoregressive_response_time[-1][1:]
        if identified_note == 'END':
            Termination_Flag = True # Terminate exercise
        else:
            # Increase the cycle counter:
            cycle_index += 1
            # Initialize the questions list of the next cycle:
            list_of_lists_of_question_indices.append([])
            # Initialize the  response time of the next cycle:
            response_time.append([])
            # Initialize the autoregressive response time of the next cycle:
            autoregressive_response_time.append([(lower_bound_response_time + upper_bound_response_time) / 2])
            # question_list_note_names.append(new_note_name + '(' + identified_note + ')')
            if identified_note != 'RESTART':
                Error_Mode = 'Just Made an Error'
                print('Error_Mode = ' + Error_Mode)
                Response_Type.append(2)
                print(colored("Bad :-)", 'red'))
                if max_step_size > 0:
                    max_step_size -= 1
            elif identified_note == 'RESTART':
                Response_Type.append(3)
                print(colored("OK, RESTART: :-)", 'green'))
                previous_note_index = intro()
                new_note_index = previous_note_index
    First_Question_Flag = False
    question_index += 1




# print(np.sum(response_time[response_time != np.nan]))
# print('program duration = ' + str(time.time() - time_beginning_of_program))


mo.close_port()

# Plot autoregressive response time
fig, ax = plt.subplots(2, 1)
for ci in range(cycle_index+1):
    if ci == 0:
        autoreg_label = 'autoreg'
        raw_label = 'raw response time'
    else:
        autoreg_label = '_Hidden label'
        raw_label = '_Hidden label'
    ax[0].plot(list_of_lists_of_question_indices[ci],
               autoregressive_response_time[ci],
               'b', label=autoreg_label)
    ax[0].plot(list_of_lists_of_question_indices[ci],
            response_time[ci],
            ':y', label=raw_label)

Response_Type = np.array(Response_Type)
my_size = len(Response_Type)
x_ticks_positions = np.arange(0, my_size)
ax[0].plot(x_ticks_positions,
        minimal_response_time * np.ones(my_size),
        '--k', label='minimal response time')
ax[0].plot(x_ticks_positions,
        lower_bound_response_time * np.ones(my_size),
        '-g', label='response time lower bound')
ax[0].plot(x_ticks_positions,
        upper_bound_response_time * np.ones(my_size),
        '-r', label='response time upper bound')
ax[0].plot(x_ticks_positions[Response_Type == 2],
           np.zeros(np.sum(Response_Type == 2)),
        'd', label='Errors')
# ax.plot(x_ticks_positions[True_or_False],
#         response_time,
#         '--', label='response time')
# ax[0].set_xticks(x_ticks_positions)
max_step_size_list = max_step_size_list[:-1]
step_size_list = step_size_list[:-1]
my_x_labels = [str(x) + '(' + str(y) + ')' for x, y in zip(max_step_size_list, step_size_list)]
# ax[0].set_xticklabels(my_x_labels)
# ax.set_xticklabels(answer_list_note_names)

# ax.plot(x_ticks_positions, note_durations, label='note duration')
box = ax[0].get_position()
ax[0].set(ylabel='seconds')
# plt.ylabel('seconds')
ax[0].set_position([box.x0, box.y0, box.width * 0.5, box.height])
ax[0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.ylabel('seconds')
# plt.xlabel('maximal step size (step size in practice)')
plt.xlabel('question index')
ax[1].plot(np.abs(step_size_list), label='step_size_list')
ax[1].plot(max_step_size_list, label='max_step_size_list')
box = ax[1].get_position()
ax[1].set_position([box.x0, box.y0, box.width * 0.5, box.height])
ax[1].legend(loc='center left', bbox_to_anchor=(1, 0.5))
# ax[1].set_xticks(x_ticks_positions)
fig.canvas.draw()  # actually draw figure
plt.show()  # enter GUI loop (for non-interactive interpreters)

