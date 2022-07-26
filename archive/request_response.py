import time
import constants
import numpy as np
import rtmidi
from termcolor import colored
# from archive.intro import intro


def request_response(iteration, accept_with_spaces, accept_without_spaces):
    question_start_time = time.time()
    iteration.response.text = input("Identify Note:")
    iteration.response.text = iteration.response.text.strip()
    iteration.response.time.raw = time.time() - question_start_time
    response_time_now_fraction = iteration.response.time.raw - np.round(iteration.response.time.raw)
    time.sleep(constants.quarter_note_time - response_time_now_fraction)
    numbers = [note.number for note in iteration.question.notes]
    for number in numbers:
        constants.mo.send_message([rtmidi.midiconstants.NOTE_OFF,
                                   number, iteration.volume.value])
    iteration.response.text = iteration.response.text.upper()
    iteration = set_response_time_to_nan_if_incorrect(
        iteration, accept_with_spaces, accept_without_spaces)
    iteration, termination_flag = check_user_response_at_question_end(
        iteration, accept_with_spaces, accept_without_spaces)
    return iteration, termination_flag


def set_response_time_to_nan_if_incorrect(question, accept_with_spaces, accept_without_spaces):
    names = [note.name[:] for note in question.question.notes]
    is_incorrect = True
    if accept_without_spaces:
        if question.response.text == ''.join(names):
            is_incorrect = False
    if accept_with_spaces:
        if question.response.text == ' '.join(names):
            is_incorrect = False
    if is_incorrect:
        question.response.time.raw = np.nan
    return question


def check_user_response_at_question_end(iteration, accept_with_spaces, accept_without_spaces):
    termination_flag = False
    names = [note.name for note in iteration.question.notes]
    is_correct = False
    if accept_without_spaces:
        if iteration.response.text == ''.join(names):
            is_correct = True
    if accept_with_spaces:
        if iteration.response.text == ' '.join(names):
            is_correct = True
    if is_correct:
        iteration.response.type = True
        print(colored("Good :-)", 'blue'))
    elif iteration.response.text == 'END':
        iteration.response.type = 'end'
        termination_flag = True
    elif iteration.response.text == 'RESTART':
        iteration.response.type = 'restart'
        print(colored("OK, RESTART: :-)", 'green'))
        iteration.question.index = intro()
    elif iteration.response.text == 'REPEAT':
        iteration.response.type = 'repeat'
    else:  # user error
        iteration.response.type = False
        print(colored("Bad :-)", 'red'))
    return iteration, termination_flag
