import time
import constants
import numpy as np
import rtmidi
from termcolor import colored
from intro import intro
import plot_functions


def request_response(question):
    question_start_time = time.time()
    question.response.text = input("Identify Note:")
    question.response.time.raw = time.time() - question_start_time
    response_time_now_fraction = question.response.time.raw - np.round(question.response.time.raw)
    time.sleep(constants.quarter_note_time - response_time_now_fraction)
    numbers = [note.number for note in question.question.notes]
    for number in numbers:
        constants.mo.send_message([rtmidi.midiconstants.NOTE_OFF,
                                   number, question.volume.value])



    question.response.text = question.response.text.upper()
    question = set_response_time_to_nan_if_incorrect(question)
    question, termination_flag = check_user_response_at_question_end(question)
    return question, termination_flag

def set_response_time_to_nan_if_incorrect(question):
    names = [note.name[:] for note in question.question.notes]
    if question.response.text != ''.join(names):
        question.response.time.raw = np.nan
    return question


def check_user_response_at_question_end(question):
    termination_flag = False
    names = [note.name for note in question.question.notes]
    if question.response.text == ''.join(names):
        # this is not necessary since true_or_false is initialized to 'True'
        # question.response.true_or_false = True
        print(colored("Good :-)", 'blue'))
    elif question.response.text == 'END':
        termination_flag = True
    elif question.response.text == 'RESTART':
        print(colored("OK, RESTART: :-)", 'green'))
        question.question.index = intro()
    else:  # user error
        question.response.type = False
        print(colored("Bad :-)", 'red'))
        # print('error_state = Just Made an Error')
    return question, termination_flag
