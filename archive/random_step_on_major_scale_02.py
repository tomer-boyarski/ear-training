import rtmidi.midiconstants
import numpy as np
from termcolor import colored
import matplotlib.pyplot as plt
import time
import seaborn as sns
import pickle

start_the_program = time.time()

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
# possible_note_durations = quarter_note_time * 2 ** np.arange(-1, 5)
possible_note_durations = quarter_note_time * np.array([0.5, 1, 2, 4, 8, 16, 32, 64, 128])

Termination_Flag = False


def necessary_number_of_consecutive_successes_func(step_size):
    if step_size == 0:
        necessary_number_of_consecutive_successes = 1
    elif step_size == 0:
        necessary_number_of_consecutive_successes = 5
    else:
        necessary_number_of_consecutive_successes = 10 * step_size
    # necessary_number_of_consecutive_successes = 2
    return necessary_number_of_consecutive_successes


number_of_consecutive_successes = 0

step_size = 1

necessary_number_of_consecutive_successes = \
    necessary_number_of_consecutive_successes_func(step_size)

response_time_value_for_error = np.nan

response_time = []
autoregressive_response_time = []
note_durations = []
new_level_question_indices = [0]

question_list_note_indices = []
question_list_note_numbers = []
question_list_note_names = []

answer_list_note_indices = []
answer_list_note_numbers = []
answer_list_note_names = []

previous_note_number = 60
previous_note_name = 'C'

question_index = -1
num_jump = np.zeros((len(note_numbers_C_to_C), len(note_numbers_C_to_C)))
num_jump_succ = np.zeros(num_jump.shape)
time_to_correct_answer = np.zeros(num_jump.shape)


def create_new_question(previous_note_index,
                        step_size,
                        range_of_notes):
    while True:
        new_note_index = previous_note_index + \
                         (-1) ** np.random.binomial(1, 0.5) * \
                         np.random.choice(np.arange(1, 1 + step_size), 1)
        new_note_index = new_note_index[0]
        if np.random.binomial(1, 1 / 4 / step_size):
            new_note_index = previous_note_index
        if 0 <= new_note_index < range_of_notes:
            break
    return new_note_index


def intro():
    for i in range(4,0,-1):
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
        new_autoregressive = 0.9 * previous_autoregressive + 0.1 * response_time_now
        autoregressive_response_time[step_size - 1].append(new_autoregressive)
    return autoregressive_response_time

previous_note_index = intro()
slow_answer_in_previous_question = False
while not Termination_Flag:

    question_index += 1
    # step_size_list.append(step_size)
    CorrectAnswer = False
    if not slow_answer_in_previous_question:
        new_note_index = create_new_question(previous_note_index,
                                             step_size,
                                             range_of_notes)
    slow_answer_in_previous_question = True
    question_list_note_indices.append(new_note_index)
    new_note_number = note_numbers_C_to_C[new_note_index]
    new_note_name = note_names_C_to_B[new_note_number % 12]
    question_list_note_numbers.append(new_note_number)
    num_jump[previous_note_index, new_note_index] += 1

    while not CorrectAnswer and not Termination_Flag:
        mo.send_message([rtmidi.midiconstants.NOTE_ON, new_note_number, my_velocity])
        print('You need ' +
              str(necessary_number_of_consecutive_successes) +
              ' consecutive correct answers to reach the next level')
        print('You have ' + str(number_of_consecutive_successes) +
              ' consecutive correct answers so far in this level')
        print('Try to get ' + str(necessary_number_of_consecutive_successes -
                                  number_of_consecutive_successes) +
              ' more consecutive correct answers')
        question_start_time = time.time()
        identified_note = input("Identify Note:")
        response_time_now = time.time() - question_start_time
        print('response_time_now = ' + str(response_time_now))
        print('quarter_note_time = ' + str(quarter_note_time))
        possible_note_durations_now = possible_note_durations[response_time_now < possible_note_durations]
        note_duration_now = np.min(possible_note_durations_now)
        note_durations.append(note_duration_now)
        print('note_duration_now = ' + str(note_duration_now))
        time.sleep(note_duration_now - response_time_now)
        mo.send_message([rtmidi.midiconstants.NOTE_OFF, new_note_number, my_velocity])
        identified_note = identified_note.upper()
        if identified_note == new_note_name:  # or idendtified_note == str(note_number-notes_numbers_to_play_now[0]+1):\
            answer_list_note_names.append(new_note_name)
            response_time.append(response_time_now)
            autoregressive_response_time = calculate_autoregressive(
                autoregressive_response_time,
                step_size,
                response_time_now)
            if response_time_now < quarter_note_time:
                slow_answer_in_previous_question = False
            if question_index != 0:
                time_to_correct_answer[
                    question_list_note_indices[question_index - 1],
                    question_list_note_indices[question_index]] += \
                        time.time() - question_start_time
                num_jump_succ[
                    question_list_note_indices[question_index - 1],
                    question_list_note_indices[question_index]] += 1
            CorrectAnswer = True
            print(colored("Good :-)", 'blue'))
            number_of_consecutive_successes += 1
        elif identified_note == 'REPEAT':
            answer_list_note_names.append('Repeat')
            # response_time.append(response_time_value_for_error)
            continue
        elif identified_note == 'END':
            # answer_list_note_names.append('End')
            # response_time.append(response_time_value_for_error)
            Termination_Flag = True
        elif identified_note == 'REVEAL':
            answer_list_note_names.append('Reveal')
            response_time.append(response_time_value_for_error)
            if question_index != 0:
                time_to_correct_answer[
                    question_list_note_indices[question_index - 1],
                    question_list_note_indices[question_index]] = np.inf
            number_of_consecutive_successes = 0
            print('The correct answer is ' + new_note_name)
            CorrectAnswer = True
        else:  # musician error
            question_list_note_names.append(new_note_name + '(' + identified_note + ')')
            # response_time.append(response_time_value_for_error)
            for error_note in [80, 86, 92]:
                mo.send_message([rtmidi.midiconstants.NOTE_ON, error_note, my_velocity])
            time.sleep(0.1)
            for error_note in [80, 86, 92]:
                mo.send_message([rtmidi.midiconstants.NOTE_OFF, error_note, my_velocity])
            print(colored("Try Again", 'red'))
            # print("your options are " + note_names_to_play_now)
            number_of_consecutive_successes = 0
    if number_of_consecutive_successes >= \
            necessary_number_of_consecutive_successes:
        new_level_question_indices.append(question_index + 1)
        print("Let's try more notes")
        step_size += 1
        necessary_number_of_consecutive_successes = \
            necessary_number_of_consecutive_successes_func(step_size)
        number_of_consecutive_successes = 0
        previous_note_index = intro()
    else:
        previous_note_index = new_note_index

# print(np.sum(response_time[response_time != np.nan]))
print('program duration = ' + str(time.time() - start_the_program))


# Plot autoregressive response time
if True:
    fig, ax = plt.subplots(1, 1)
    for level_index, this_level_question_index in enumerate(new_level_question_indices[:-1]):
        # x_ticks_positions = range(len(answer_list_note_names))
        next_level_question_index = new_level_question_indices[level_index + 1]
        x_ticks_positions = np.arange(this_level_question_index, next_level_question_index)
        my_label_response_time = 'autoregressive response time with step size = ' + str(level_index + 1)
        ax.plot(x_ticks_positions, autoregressive_response_time[level_index], '-', label=my_label_response_time)
        if level_index < len(new_level_question_indices)-2:
            dotted_line_x_range = [next_level_question_index-1, next_level_question_index]
            dotted_line_y_range = [autoregressive_response_time[level_index][-1],
                                   autoregressive_response_time[level_index+1][0]]
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
