import rtmidi.midiconstants
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
from set_difficulty_distribution import set_difficulty_distribution
from set_chord import set_chord
from set_volume import set_volume
from high_level_classes_02 import *
from request_response import request_response
from low_level_classes_02 import *


question_list = []
helper_functions_02.intro()

# question = Question(request_response=True, chord=Chord(indices=[7, 9]))
for _ in range(2):
    iteration = Iteration(request_response=False,
                          chord=Chord(names=['C']),
                          question_list=question_list)
    iteration.play_chord(question_list)
    iteration, termination_flag = request_response(iteration)
    question_list.append(iteration)


constants.mo.close_port()

# question_list = question_list[:-1]
# question_list = question_list[1:]
# helper_functions_02.plot_jump_success_rate(list_of_questions)
# question_list = question_list[1:]
helper_functions_02.my_plot(constants, question_list)

# print('stop')
