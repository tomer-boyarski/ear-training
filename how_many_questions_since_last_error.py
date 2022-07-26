import numpy as np

def how_many_questions_since_last_error(question_list):
    true_or_false = [q.response.type for q in question_list]
    reversed_true_or_false = true_or_false[::-1]
    if False in reversed_true_or_false:
        return reversed_true_or_false.index(False)
    else:
        return np.infty
    print('Number of questions since last error = ' +
          str(number_of_questions_since_last_error))
