import random

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
possible_note_durations = quarter_note_time * np.array([0.25, 0.5, 1, 2, 4, 8, 16, 32, 64, 128])

Termination_Flag = False


def necessary_number_of_consecutive_successes_func(step_size):
    if step_size == 0:
        necessary_number_of_consecutive_successes = 1
    elif step_size == 0:
        necessary_number_of_consecutive_successes = 5
    else:
        necessary_number_of_consecutive_successes = 10 * step_size
    necessary_number_of_consecutive_successes = np.infty
    return necessary_number_of_consecutive_successes


number_of_consecutive_successes = 0

step_size = 1

necessary_number_of_consecutive_successes = \
    necessary_number_of_consecutive_successes_func(step_size)

response_time_value_for_error = np.nan

response_time = []
note_durations = []

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
        time.sleep(quarter_note_time/4)
        mo.send_message([rtmidi.midiconstants.NOTE_OFF, note_to_play_now, my_velocity])

    mo.send_message([rtmidi.midiconstants.NOTE_ON, 60, my_velocity])
    time.sleep(quarter_note_time/2)
    mo.send_message([rtmidi.midiconstants.NOTE_OFF, 60, my_velocity])
    previous_note_index = 7
    return previous_note_index



previous_note_index = intro()
slow_answer_in_previous_question = False
while not Termination_Flag:

    question_index += 1
    CorrectAnswer = False
    new_note_index = 4 + 10 * np.random.binomial(1, 0.5)
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
        if identified_note == new_note_name:  # or idendtified_note == str(note_number-notes_numbers_to_play_now[0]+1):
            answer_list_note_names.append(new_note_name)
            response_time.append(response_time_now)
            if response_time_now < quarter_note_time:
                slow_answer_in_previous_question = False
            if question_index != 0:
                time_to_correct_answer[
                    question_list_note_indices[question_index - 1], question_list_note_indices[question_index]] += (
                        time.time() - question_start_time)
                num_jump_succ[
                    question_list_note_indices[question_index - 1], question_list_note_indices[question_index]] += 1
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
                    question_list_note_indices[question_index - 1], question_list_note_indices[question_index]] = np.inf
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

if True:
    fig, ax = plt.subplots(1, 1)
    x_ticks_positions = range(len(answer_list_note_names))
    ax.set_xticks(x_ticks_positions)  # set tick positions
    ax.set_xticklabels(answer_list_note_names)
    print('now i am here')
    print('x_ticks_positions = ' + str(x_ticks_positions))
    print('response_time = ' + str(response_time))
    print('note_durations = ' + str(note_durations))
    ax.plot(x_ticks_positions, response_time, '-', label='response time')
    # ax.plot(x_ticks_positions, note_durations, label='note duration')
    ax.legend()
    plt.ylabel('seconds')
    plt.xlabel('notes')
    fig.canvas.draw()  # actually draw figure
    plt.show()  # enter GUI loop (for non-interactive interpreters)

if True:
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

if True:
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
