# See problem with distribution of new note index


import rtmidi.midiconstants
import numpy as np
from termcolor import colored
import matplotlib.pyplot as plt
import time
import seaborn as sns
import pickle

import get_constants

time_beginning_of_program = time.time()

mo = rtmidi.MidiOut()
mo.open_port(0)
my_velocity = 127


constants = get_constants.get_constants()

def cubic_polinomial_mapping():
    # To find the cubic polinomial mapping:
    # y = ax^3 + bx^2 + cx + d
    # y'(50) = midPointSlope
    # y(50)  = midPointValue
    # y(100) = 100
    # y(1)   = 1
    # We have 4 equations and 4 variables: a,b,c,d
    # This is a linear system of equations:
    # 0 = 3*50**2*a+2*50*b+c
    # 100 = 100**3*a+100**2*b+100*c+d
    # 50 = 50**3*a+50**2*b+50*c+d
    # 1 = a+b+c+d
    # Let us arrange this in matrix form:
    midPointSlope = 0
    A = np.array([[3 * 50 ** 2, 2 * 50, 1, 0],
                  [50 ** 3, 50 ** 2, 50, 1],
                  [100 ** 3, 100 ** 2, 100, 1],
                  [1, 1, 1, 1]])

    # Find the 4 coefficients - a,b,c,d:
    midPointValue = 50
    coefficients = np.linalg.inv(A).dot([midPointSlope, midPointValue, 100, 1])
    return coefficients


cubic_polynomial_mapping_coefficients = cubic_polinomial_mapping()


class Question:
    def __init__(self, previous_note_index, step_size_level, constants):
        # Save as difficulty attribute:
        self.previous_note_index = previous_note_index
        self.step_size_level = step_size_level
        self.step_size = None
        self.step_direction = None
        self.new_note_index = None
        self.constants = constants

    def get_step_size_discrete_levels(self):
        max_step_size_now = self.step_size_level
        if max_step_size_now > 0:
            step_size = np.random.randint(1, max_step_size_now + 1, 1)
            if np.random.binomial(1, 1 / 4 / max_step_size_now):
                step_size = 0
        elif max_step_size_now == 0:
            step_size = 0
        self.step_size = step_size

    def get_step_direction_and_new_note(self):
        temp = 1
        while True:
            temp += 1
            if temp >100:
                stop = 1
            step_direction = (-1) ** np.random.binomial(1, 0.5)
            new_note_index = self.previous_note_index + \
                self.step_size * step_direction
            if 0 <= new_note_index <= 14:
                self.step_direction = step_direction
                self.new_note_index = new_note_index
                self.new_note_number = constants['note_numbers_C_to_C'][new_note_index]
                self.new_note_name = constants['note_names_C_to_B'][self.new_note_number % 12]
                break


mylist = []
num = 10000
for _ in range(num):
    new_question = Question(7, 7, constants)
    new_question.get_step_size_discrete_levels()
    new_question.get_step_direction_and_new_note()
    mylist.append(new_question)

step_size_list = []
step_direction_list = []
new_note_index_list = []
new_note_number_list = []
new_note_name_list = []
for i in range(num):
    step_size_list.append(mylist[i].step_size)
    step_direction_list.append(mylist[i].step_direction)
    new_note_index_list.append(mylist[i].new_note_index)
    new_note_number_list.append(mylist[i].new_note_number)
    new_note_name_list.append(mylist[i].new_note_name)

fig, ax = plt.subplots(2, 3)
values, counts = np.unique(step_size_list, return_counts=True)
ax[0,0].bar(values, counts / np.sum(counts))
ax[0,0].title.set_text('step_size_list')
values, counts = np.unique(step_direction_list, return_counts=True)
ax[0,1].bar(values, counts / np.sum(counts))
ax[0,1].title.set_text('step_direction_list')
values, counts = np.unique(new_note_index_list, return_counts=True)
ax[0,2].bar(values, counts / np.sum(counts))
ax[0,2].title.set_text('new_note_index_list')
values, counts = np.unique(new_note_number_list, return_counts=True)
ax[1,0].bar(values, counts / np.sum(counts))
ax[1,0].title.set_text('new_note_number_list')
values, counts = np.unique(new_note_name_list, return_counts=True)
ax[1,1].bar(np.arange(len(counts)), counts / np.sum(counts))
ax[1,1].set_xticks(np.arange(len(counts)))
ax[1,1].set_xticklabels(values)
# ax[1,1].title.set_text('new_note_name_list')
plt.show()

# mylist.append(Question(mylist[-1].previous_note_index, mylist[-1].difficulty))


# print([Question.previous_note_index for Question in mylist])
# print([Question.difficulty for Question in mylist])


mo.close_port()
