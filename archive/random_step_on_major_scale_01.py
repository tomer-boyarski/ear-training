import rtmidi.midiconstants
import numpy as np
import time
from termcolor import colored
import matplotlib.pyplot as plt
import timeit
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

note_names_C_to_B = {'C': [60, 72], 'D': [62], 'E': [64], 'F': [65], 'G': [67], 'A': [69], 'B': [71]}
note_names_C_to_B = np.array(['C', 'CS', 'D', 'DS', 'E', 'F', 'FS', 'G', 'GS', 'A', 'AS', 'B'])
# note_names_C_to_B = np.array(['C', 'D', 'E', 'F', 'G', 'A', 'B'])


Termination_Flag = False


def necessary_number_of_consecutive_successes_func(step_size):
    if step_size == 0:
        necessary_number_of_consecutive_successes = 1
    elif step_size == 0:
        necessary_number_of_consecutive_successes = 5
    else:
        necessary_number_of_consecutive_successes = 10 * step_size
    return necessary_number_of_consecutive_successes


number_of_consecutive_successes = 0

step_size = 0

necessary_number_of_consecutive_successes = \
    necessary_number_of_consecutive_successes_func(step_size)

response_time_value_for_error = np.nan

response_time = []

question_list_note_indices = []
question_list_note_numbers = []
question_list_note_names = []

answer_list_note_indices = []
answer_list_note_numbers = []
answer_list_note_names = []

first_note_index = 7
first_note_number = 60
first_note_name = 'C'

question_index = -1
num_jump = np.zeros((len(note_numbers_C_to_C), len(note_numbers_C_to_C)))
num_jump_succ = np.zeros(num_jump.shape)
time_to_correct_answer = np.zeros(num_jump.shape)

while not Termination_Flag:
    question_index += 1
    CorrectAnswer = False
    if question_index == 0:
        question_list_note_indices.append(first_note_index)
        question_list_note_numbers.append(first_note_number)
        question_list_note_names.append(first_note_name)
    else:
        while True:
            new_note_index = question_list_note_indices[question_index - 1] + \
                (-1)**np.random.binomial(1, 0.5)*np.random.randint(1, step_size + 1)
            if np.random.binomial(1, 1/4/step_size):
                new_note_index = question_list_note_indices[question_index - 1]
            if 0 <= new_note_index < len(note_numbers_C_to_C):
                break
        question_list_note_indices.append(new_note_index)
        new_note_number = note_numbers_C_to_C[new_note_index]
        new_note_name = note_names_C_to_B[new_note_number % 12]
        question_list_note_numbers.append(new_note_number)
        num_jump[question_list_note_indices[question_index - 1], question_list_note_indices[question_index]] += 1

    while not CorrectAnswer and not Termination_Flag:
        question_start_time = time.time()
        mo.send_message([rtmidi.midiconstants.NOTE_ON, new_note_number, my_velocity])
        print('You need ' +
              str(necessary_number_of_consecutive_successes) +
              ' consecutive correct answers to reach the next level')
        print('You have ' + str(number_of_consecutive_successes) +
              ' consecutive correct answers so far in this level')
        print('Try to get ' + str(necessary_number_of_consecutive_successes -
                                  number_of_consecutive_successes) +
              ' more consecutive correct answers')
        identified_note = input("Identify Note:")

        # time.sleep(1.5)
        mo.send_message([rtmidi.midiconstants.NOTE_OFF, new_note_number, my_velocity])
        identified_note = identified_note.upper()
        if identified_note == new_note_name:  # or idendtified_note == str(note_number-notes_numbers_to_play_now[0]+1):
            answer_list_note_names.append(new_note_name)
            response_time.append(time.time() - question_start_time)
            if question_index != 0:
                time_to_correct_answer[
                    question_list_note_indices[question_index - 1], question_list_note_indices[question_index]] += (
                            time.time() - question_start_time)
                num_jump_succ[
                    question_list_note_indices[question_index - 1], question_list_note_indices[question_index]] += 1
            CorrectAnswer = True
            print(colored("Good :-)", 'blue'))

            number_of_consecutive_successes += 1
            if number_of_consecutive_successes >= \
                    necessary_number_of_consecutive_successes:
                print("Let's try more notes")
                step_size += 1
                necessary_number_of_consecutive_successes = \
                    necessary_number_of_consecutive_successes_func(step_size)
                number_of_consecutive_successes = 0
        elif identified_note == 'REPEAT':
            answer_list_note_names.append('Repeat')
            response_time.append(response_time_value_for_error)
            continue
        elif identified_note == 'END':
            answer_list_note_names.append('End')
            response_time.append(response_time_value_for_error)
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
            response_time.append(response_time_value_for_error)
            for error_note in [80, 86, 92]:
                mo.send_message([rtmidi.midiconstants.NOTE_ON, error_note, my_velocity])
            time.sleep(0.1)
            for error_note in [80, 86, 92]:
                mo.send_message([rtmidi.midiconstants.NOTE_OFF, error_note, my_velocity])
            print(colored("Try Again", 'red'))
            # print("your options are " + note_names_to_play_now)
            number_of_consecutive_successes = 0

print(np.sum(response_time[response_time != np.nan]))
print('program duration = ' + str(time.time() - start_the_program))

if True:
    fig, ax = plt.subplots(1, 1)
    x_ticks_positions = range(len(answer_list_note_names))
    ax.set_xticks(x_ticks_positions)  # set tick positions
    ax.set_xticklabels(answer_list_note_names)
    ax.plot(x_ticks_positions, response_time)
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
