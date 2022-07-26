# See problem with distribution of new note index


import rtmidi.midiconstants
import numpy as np
from termcolor import colored
import matplotlib.pyplot as plt
import time
import seaborn as sns
import pickle
import helper_functions_01

time_beginning_of_program = time.time()

mo = rtmidi.MidiOut()
mo.open_port(0)
my_velocity = 127


constants = helper_functions.get_constants()


cubic_polynomial_mapping_coefficients = helper_functions.cubic_polynomial_mapping()


class Question:
    def __init__(self, previous_note_index,
                 step_size_level, constants,
                 slow_state,
                 error_state, penultimate_note_index):
        # Save as difficulty attribute:
        self.previous_note_index = previous_note_index
        self.step_size_level = step_size_level
        self.step_size = None
        self.step_direction = None
        self.note_index = None
        self.constants = constants
        self.new_note_number = None
        self.new_note_name = None
        self.identified_note = None
        self.response_time_now = None
        self.slow_state = slow_state
        self.slow_answer_in_this_question = None
        self.error_state = error_state
        self.penultimate_note_index = penultimate_note_index
        self.Termination_Flag = False

    def get_new_question_attributes(self):
        self.error_state_check(self)

    def error_state_check(self):
        if self.error_state == 'No Recent Errors':
            self.slow_state_check(self)
        else:
            self.note_index = self.penultimate_note_index

    def slow_state_check(self):
        if not self.slow_state:
            self.get_step_size_old()
            self.get_step_direction_and_new_note()
        else:
            self.note_index = self.previous_note_index
            self.step_size = 0
        self.new_note_number = constants.note_numbers_C_to_C[self.note_index]
        self.new_note_name = constants.note_names_chromatic_C_scale[self.new_note_number % 12]

    def get_step_size_old(self):
        max_step_size_now = self.step_size_level
        if max_step_size_now > 0:
            step_size = np.random.randint(1, max_step_size_now + 1, 1)
            if np.random.binomial(1, 1 / 4 / max_step_size_now):
                step_size = 0
        elif max_step_size_now == 0:
            step_size = 0
        self.step_size = step_size

    def get_step_direction_and_new_note(self):
        while True:
            step_direction = (-1) ** np.random.binomial(1, 0.5)
            new_note_index = self.previous_note_index + \
                self.step_size * step_direction
            if 0 <= new_note_index <= 14:
                self.step_direction = step_direction
                self.note_index = new_note_index
                break

    def play_note(self):
        mo.send_message([rtmidi.midiconstants.NOTE_ON, self.new_note_number, constants.my_velocity])

    def request_user_response(self):
        question_start_time = time.time()
        identified_note = input("Identify Note:")
        response_time_now = time.time() - question_start_time
        self.response_time_now = response_time_now
        response_time_now_fraction = response_time_now - np.round(response_time_now)
        # Round up sound duration to the nearest second:
        time.sleep(1 - response_time_now_fraction)
        # Turn off note:
        mo.send_message([rtmidi.midiconstants.NOTE_OFF, self.new_note_number, constants.my_velocity])
        identified_note = identified_note.upper()
        self.identified_note = identified_note

    def check_user_response(self):
        if self.identified_note == self.new_note_name:
            print(colored("Good :-)", 'blue'))
            self.user_response_time_check(self)
            self.determine_repeat_note_flag(self)
            self.update_error_state(self)
        else:
            self.termination_flag_check()

    def update_error_state(self):
        if self.error_state == 'Just Made an Error':
            self.error_state = 'Error in Previous Question'
            print('error_state = ' + self.error_state)
        elif self.error_state == 'Error in Previous Question':
            self.error_state = 'No Recent Errors'
            print('error_state = ' + self.error_state)

    def termination_flag_check(self):
        if self.identified_note == 'END':
            self.Termination_Flag = True
        else:
            self.restart_flag_check(self)

    def restart_flag_check(self):
        if self.identified_note == 'RESTART':
            print(colored("OK, RESTART: :-)", 'green'))
            self.note_index = helper_functions.intro()
        else:
            self.deal_with_user_error(self)

    def deal_with_user_error(self):
        if self.max_step_size > 0:
            self.max_step_size -= 1
        print(colored("Bad :-)", 'red'))
        self.error_state = 'Just Made an Error'
        print('error_state = ' + self.error_state)

    def user_response_time_check(self):
        if self.response_time_now < constants.optimal_response_time \
                and self.max_step_size < 8:
            self.max_step_size += 1
        elif self.response_time_now > constants.optimal_response_time \
                and self.max_step_size > 0:
            self.max_step_size -= 1

    def determine_repeat_note_flag(self):
        if self.response_time_now < constants.quarter_note_time:
            self.slow_answer_in_this_question = False
        elif self.response_time_now > constants.quarter_note_time:
            self.slow_answer_in_this_question = True



question = Question(previous_note_index=7,
                    penultimate_note_index=7,
                    step_size_level=0,
                    constants=constants,
                    slow_state=False,
                    error_state='No Recent Errors')
question_list = [question, question]
question_index = 2
while not question_list[-1].Termination_Flag:
    previous_question = question_list[-1]
    penultimate_question = question_list[-2]
    question = Question(previous_note_index=previous_question.note_index,
                        penultimate_note_index=penultimate_question.note_index,
                        step_size_level=previous_question.step_size_level,
                        constants=constants,
                        slow_state=previous_question.slow_state,
                        error_state=previous_question.error_state)
    question.get_new_question_attributes()
    question.play_note()
    question.request_user_response()
    question.check_user_response()
    question_list.append(question)

step_size_list = []
step_direction_list = []
new_note_index_list = []
new_note_number_list = []
new_note_name_list = []
for i in range(num):
    step_size_list.append(question_list[i].step_size)
    step_direction_list.append(question_list[i].step_direction)
    new_note_index_list.append(question_list[i].note_index)
    new_note_number_list.append(question_list[i].new_note_number)
    new_note_name_list.append(question_list[i].new_note_name)

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
