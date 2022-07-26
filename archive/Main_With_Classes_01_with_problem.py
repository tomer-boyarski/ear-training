# See problem with distribution of new note index


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
    def __init__(self, previous_note_index, step_size_level):
# Save as difficulty attribute:
        self.previous_note_index = previous_note_index
        self.step_size_level = step_size_level
        self.step_size = None

    # Determine probability distribution of new step 
    def get_step_size(self):
        # Constants for change of parameter:
        # "a" is the value that corresponds to the easiest questions according to the old parameter.
        # "b" is the value that corresponds to the hardest questions according to the old parameter.
        # "c" is the value that corresponds to the easiest questions according to the new parameter.
        # "d" is the value that corresponds to the hardest questions according to the new parameter.
        # This range [1,2,...,100] was chosen arbitrarily to be "refined enough".
        a = 1; b = 100; c = 1; d = -2
        # Linear Mapping from [a,b] to [c,d]:
        step_size_level_2 = cubic_polynomial_mapping_coefficients.dot(self.step_size_level ** np.arange(3, -1, -1))
        step_size_level_3 = (d - c) / (b - a) * (step_size_level_2 - a) + c
        step_size_level_4 = 10.0 ** step_size_level_3
        step_size_level_5 = 2.0 ** -step_size_level_4
        distribution = step_size_level_5 ** np.arange(8)
        distribution = distribution / np.sum(distribution)
        step_size = np.random.choice(np.arange(0, 8), 1, p=distribution)
        self.step_size = step_size[0]

    def get_step_direction(self):
        while True:
            zero_or_one = np.random.binomial(1, 0.5)
            if zero_or_one == 1:
                step_direction = 1
            elif zero_or_one == 0:
                step_direction = -1
            new_note_index = self.previous_note_index + \
                             self.step_size * step_direction
            if new_note_index >= 0 and new_note_index <= 14:
                self.step_direction = step_direction
                self.new_note_index = new_note_index
                break


mylist = []
num = 10000
for _ in range(num):
    mylist.append(Question(7, 100))
    mylist[-1].get_step_size()
    mylist[-1].get_step_direction()

y = []
for i in range(num):
    # y.append(mylist[i].step_size)
    # y.append(mylist[i].step_direction)
    y.append(mylist[i].new_note_index)

values, counts = np.unique(y, return_counts=True)
plt.bar(values, counts)
plt.show()




# mylist.append(Question(mylist[-1].previous_note_index, mylist[-1].difficulty))


# print([Question.previous_note_index for Question in mylist])
# print([Question.difficulty for Question in mylist])


mo.close_port()

