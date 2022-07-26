import rtmidi.midiconstants
import os.path
import numpy as np
from termcolor import colored
import matplotlib.pyplot as plt
import time
import seaborn as sns
import pickle
import plot_functions
import constants
import initial
from collections import namedtuple
from recordclass import recordclass
from low_level_classes_02 import *
from intro import intro
from set_chord import set_chord
from set_volume import set_volume
from high_level_classes_02 import *
from request_response import request_response


question_list = []
# intro()

# question = Question(request_response=True, chord=Chord(indices=[7, 9]))
# for _ in range(2):
termination_flag = False
step_size = None
key = 'white'
number_of_notes = None
while not termination_flag:
    # iteration = Iteration(request_response=True,
    #                       key=key,
    #                       question_list=question_list,
    #                       number_of_notes=number_of_notes,
    #                       step_size=step_size,
    #                       note_indices=[7])
    # iteration = Iteration(request_response=True,
    #                       key=key,
    #                       question_list=question_list,
    #                       number_of_notes=number_of_notes,
    #                       step_size=step_size,
    #                       note_indices=[7, 9])
    iteration = Iteration(request_response=True,
                          key=key,
                          question_list=question_list,
                          number_of_notes=number_of_notes,
                          step_size=step_size)
    iteration.play_chord(question_list)
    iteration, termination_flag = request_response(iteration)
    question_list.append(iteration)


constants.mo.close_port()

question_list = question_list[:-1]
# question_list = question_list[1:]
# helper_functions_02.plot_jump_success_rate(list_of_questions)
# question_list = question_list[1:]
plot_functions.my_plot(question_list)

if step_size == 2:
    file_name = 'response_times_number_of_notes_' + str(number_of_notes) + '.p'
    if os.path.exists(file_name):
        response_times_old = pickle.load(open(file_name, "rb"))
    else:
        response_times_old = []
    response_times = [iteration.response.time.raw for iteration in question_list]
    response_times = response_times_old + response_times
    pickle.dump(response_times, open(file_name, "wb"))


print('this is the end of MAIN')
