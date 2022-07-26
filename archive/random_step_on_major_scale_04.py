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

note_names_C_to_B = {'C': [60, 72], 'D': [62], 'E': [64], 'F': [65], 'G': [67], 'A': [69], 'B': [71]}
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
lower_bound_response_time = 1.5
upper_bound_response_time = 2.5




response_time = [[]]

note_durations = []
new_level_question_indices = [0]
max_step_size_list = []
step_size_list = []
True_or_False = []

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
    step_size_list.append(np.abs(new_note_index - previous_note_index))
    return step_size_list, new_note_index


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


while not Termination_Flag:
    previous_note_index = new_note_index
    max_step_size_list.append(max_step_size)
    CorrectAnswer = False
    if not slow_answer_in_previous_question:
        step_size_list, new_note_index = \
            create_new_question(previous_note_index,
                                max_step_size,
                                range_of_notes,
                                step_size_list)
    elif slow_answer_in_previous_question:
        step_size_list.append(0)
    slow_answer_in_previous_question = True
    question_list_note_indices.append(new_note_index)
    new_note_number = note_numbers_C_to_C[new_note_index]
    new_note_name = note_names_C_to_B[new_note_number % 12]
    question_list_note_numbers.append(new_note_number)
    num_jump[previous_note_index, new_note_index] += 1

    while not CorrectAnswer and not Termination_Flag:
        mo.send_message([rtmidi.midiconstants.NOTE_ON, new_note_number, my_velocity])
        question_start_time = time.time()
        identified_note = input("Identify Note:")
        response_time_now = time.time() - question_start_time
        response_time_now_fraction = response_time_now - np.round(response_time_now)
        # print('response_time_now = ' + str(response_time_now))
        # print('quarter_note_time = ' + str(quarter_note_time))
        # print('note_duration_now = ' + str(note_duration_now))
        time.sleep(1 - response_time_now_fraction)
        mo.send_message([rtmidi.midiconstants.NOTE_OFF, new_note_number, my_velocity])
        identified_note = identified_note.upper()
        if identified_note == 'END':
            autoregressive_response_time[-1] = autoregressive_response_time[-1][1:]
            Termination_Flag = True
        # if identified_note == 'RESTART':
        #     list_of_lists_of_question_indices[cycle_index].append(question_index)
        #     previous_note_index = intro()
        #     new_note_index = previous_note_index

        elif identified_note == new_note_name:  # or idendtified_note == str(note_number-notes_numbers_to_play_now[0]+1):\
            list_of_lists_of_question_indices[cycle_index].append(question_index)
            True_or_False.append(True)
            answer_list_note_names.append(new_note_name)
            response_time[cycle_index].append(response_time_now)
            autoregressive_response_time[cycle_index].append(
                (1-last_sample_weight) * autoregressive_response_time[cycle_index][-1] +
                last_sample_weight * response_time_now)
            if autoregressive_response_time[cycle_index][-1] < lower_bound_response_time:
                max_step_size += 1
            elif autoregressive_response_time[cycle_index][-1] > upper_bound_response_time and max_step_size>0:
                max_step_size -= 1
            if response_time_now < quarter_note_time:
                slow_answer_in_previous_question = False
            if not First_Question_Flag:
                time_to_correct_answer[previous_note_index,
                                       new_note_index] += \
                        time.time() - question_start_time
                num_jump_succ[previous_note_index,
                              new_note_index] += 1
            CorrectAnswer = True
            print(colored("Good :-)", 'blue'))
        elif identified_note != new_note_name:  # musician error
            cycle_index += 1
            list_of_lists_of_question_indices.append([])
            response_time.append([])
            autoregressive_response_time[-1] = autoregressive_response_time[-1][1:]
            autoregressive_response_time.append([(lower_bound_response_time + upper_bound_response_time) / 2])
            True_or_False.append(False)
            print(colored("Bad :-)", 'red'))
            question_list_note_names.append(new_note_name + '(' + identified_note + ')')
            max_step_size -= 1
            previous_note_index = intro()
            new_note_index = previous_note_index
            break
    First_Question_Flag = False
    question_index += 1




# print(np.sum(response_time[response_time != np.nan]))
print('program duration = ' + str(time.time() - time_beginning_of_program))


# Plot autoregressive response time
if True:
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

    True_or_False = np.array(True_or_False)
    my_size = len(True_or_False)
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
    ax[0].plot(x_ticks_positions[True_or_False==False],
            np.zeros(sum(True_or_False==False)),
            'd', label='Errors')
    # ax.plot(x_ticks_positions[True_or_False],
    #         response_time,
    #         '--', label='response time')
    ax[0].set_xticks(x_ticks_positions)
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
    ax[1].set_xticks(x_ticks_positions)
    fig.canvas.draw()  # actually draw figure
    plt.show()  # enter GUI loop (for non-interactive interpreters)


# Plot moving average response time
if False:
    fig, ax = plt.subplots(1, 1)
    for level_index, this_level_question_index in enumerate(new_level_question_indices[:-1]):
        # x_ticks_positions = range(len(answer_list_note_names))
        next_level_question_index = new_level_question_indices[level_index + 1]
        x_ticks_positions = np.arange(this_level_question_index, next_level_question_index)
        response_time_this_level = response_time[this_level_question_index:next_level_question_index]
        response_time_this_level = np.array(response_time_this_level)
        response_time_this_level_cumsum = np.cumsum(response_time_this_level)
        response_time_this_level_moving_average = response_time_this_level_cumsum / np.arange(1, len(response_time_this_level_cumsum))
        my_label_response_time = 'moving average response time with step size = ' + str(level_index + 1)
        ax.plot(x_ticks_positions, response_time_this_level_moving_average, '-', label=my_label_response_time)
        if level_index < len(new_level_question_indices)-2:
            dotted_line_x_range = [next_level_question_index-1, next_level_question_index]
            dotted_line_y_range = [response_time_this_level_moving_average[-1],
                                   response_time[next_level_question_index]]
            ax.plot(dotted_line_x_range, dotted_line_y_range, ':k')
    ax.set_xticks(np.arange(0, next_level_question_index))  # set tick positions
    ax.set_xticklabels(answer_list_note_names[0:next_level_question_index])
    ax.plot(np.arange(0, next_level_question_index),
            0.7 * np.ones(next_level_question_index),
            '-', label='minimal response time')
    ax.plot(np.arange(0, next_level_question_index),
            np.ones(next_level_question_index),
            '-', label='necessary response time')
    # ax.plot(x_ticks_positions, note_durations, label='note duration')
    ax.legend()
    plt.ylabel('seconds')
    plt.xlabel('notes')
    fig.canvas.draw()  # actually draw figure
    plt.show()  # enter GUI loop (for non-interactive interpreters)

# Plot raw response time:
if False:
    fig, ax = plt.subplots(1, 1)
    for level_index, this_level_question_index in enumerate(new_level_question_indices[:-1]):
        # x_ticks_positions = range(len(answer_list_note_names))
        next_level_question_index = new_level_question_indices[level_index + 1]
        x_ticks_positions = np.arange(this_level_question_index, next_level_question_index)
        my_label_response_time = 'response time with step size = ' + str(level_index + 1)
        response_time_this_level = response_time[this_level_question_index:next_level_question_index]
        # ax.plot(x_ticks_positions, response_time_this_level, '-', label=my_label_response_time)
        response_time_this_level = np.array(response_time_this_level)
        response_time_this_level_cumsum = np.cumsum(response_time_this_level)
        response_time_this_level_moving_average = response_time_this_level_cumsum / np.arange(1, len(response_time_this_level_cumsum))
        my_label_response_time = 'moving average response time with step size = ' + str(level_index + 1)
        ax.plot(x_ticks_positions, response_time_this_level_moving_average, '-', label=my_label_response_time)
        if level_index < len(new_level_question_indices)-2:
            dotted_line_x_range = [next_level_question_index-1, next_level_question_index]
            dotted_line_y_range = response_time[next_level_question_index-1:next_level_question_index+1]
            ax.plot(dotted_line_x_range, dotted_line_y_range, ':k')
    ax.set_xticks(np.arange(0, next_level_question_index))  # set tick positions
    ax.set_xticklabels(answer_list_note_names[0:next_level_question_index])
    ax.plot(np.arange(0, next_level_question_index), 0.7 * np.ones(next_level_question_index), '-', label='minimal response time')
    # ax.plot(x_ticks_positions, note_durations, label='note duration')
    ax.legend()
    plt.ylabel('seconds')
    plt.xlabel('notes')
    fig.canvas.draw()  # actually draw figure
    plt.show()  # enter GUI loop (for non-interactive interpreters)

if False:
    fig = plt.figure()
    pickle.dump(num_jump_succ, open("num_jump_succ.p", "wb"))
    pickle.dump(num_jump, open("num_jump.p", "wb"))
    jum_succ_rate = np.full(num_jump.shape, np.nan)
    jum_succ_rate[num_jump != 0] = num_jump_succ[num_jump != 0] / num_jump[num_jump != 0]
    note_names_to_heatmap = note_names_C_to_B[note_numbers_C_to_C % 12]
    sns.heatmap(jum_succ_rate,
                xticklabels=note_names_to_heatmap,
                yticklabels=note_names_to_heatmap,
                cmap="crest")

if False:
    fig = plt.figure()
    pickle.dump(time_to_correct_answer, open("time_to_correct_answer.p", "wb"))
    pickle.dump(num_jump, open("num_jump.p", "wb"))
    note_names_to_heatmap = note_names_C_to_B[note_numbers_C_to_C % 12]
    time_to_correct_answer[num_jump == 0] = np.nan
    time_to_correct_answer[num_jump != 0] = \
        time_to_correct_answer[num_jump != 0] / num_jump[num_jump != 0]

    sns.heatmap(time_to_correct_answer,
                xticklabels=note_names_to_heatmap,
                yticklabels=note_names_to_heatmap,
                cmap="crest")

plt.show()
mo.close_port()
