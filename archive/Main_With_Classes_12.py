import plot_functions
from archive.high_level_classes_02 import *
from archive.request_response import request_response


initial_question = Iteration(request_response=False,
                             note_names=['C'])
list_of_questions = [initial_question] * 2
intro.intro()
termination_flag = False
while not termination_flag:
    question = Iteration(request_response=True)
    question.play_chord(list_of_questions)
    question, termination_flag = request_response(question)
    list_of_questions.append(question)
constants.mo.close_port()

list_of_questions = list_of_questions[:-1]
list_of_questions = list_of_questions[1:]
# helper_functions_02.plot_jump_success_rate(list_of_questions)
list_of_questions = list_of_questions[1:]
plot_functions.my_plot(constants, list_of_questions)

# print('stop')
