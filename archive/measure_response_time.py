import numpy as np
from termcolor import colored
import matplotlib.pyplot as plt
import time
import pickle

Termination_Flag = False
response_time_value_for_error = np.nan
response_time = []
indices_of_question_answered_correctly = []
indices_of_question_answered_incorrectly = []
question_index = -1


while not Termination_Flag:
    question_index += 1
    CorrectAnswer = False
    x = np.random.randint(2, 10)
    # y = np.random.randint(2, 10)
    y = np.random.randint(12, 21)
    question_start_time = time.time()
    user_response = input([x, y])
    response_time.append(time.time() - question_start_time)
    if user_response == str(x*y):
        print(colored("Good :-)", 'blue'))
        # response_type.append(True)
        indices_of_question_answered_correctly.append(question_index)
    elif user_response == 'end':
        Termination_Flag = True
    else:
        print(colored("Bad :-)", 'red'))
        # response_type.append(False)
        indices_of_question_answered_incorrectly.append(question_index)

response_time = np.array(response_time)
plt.plot(indices_of_question_answered_correctly,
         response_time[indices_of_question_answered_correctly],
         'd', label='True')
plt.plot(indices_of_question_answered_incorrectly,
         response_time[indices_of_question_answered_incorrectly],
         'd', label='False')
plt.legend()
plt.show()

pickle.dump(response_time, open("response_time.p", "wb"))
pickle.dump(indices_of_question_answered_correctly, open("indices_of_question_answered_correctly.p", "wb"))
pickle.dump(indices_of_question_answered_incorrectly, open("indices_of_question_answered_incorrectly.p", "wb"))
