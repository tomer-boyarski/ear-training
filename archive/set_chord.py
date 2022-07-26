import constants
import plot_functions
import numpy as np
from binary_markov_chain import binary_markov_chain


def set_chord(question, question_list):
    # Error
    if not question_list[-1].response.type:
        if question_list[-2].response.type:
            question.question.index = question_list[-2].question.index
            # Restart
        else:
            question.question.index = helper_functions_02.intro()
        question.step.size = question.question.index - \
                             question_list[-1].question.index
        question.step.trend = np.sign(question.step.size)
    else:
        while True:
            question = set_chord_size(question)
            question = set_step_size(question)
            question = set_step_trend_and_new_note_index(question, question_list)
            if len(np.unique(question.question.index)) == question.question.size:
                break
    question.chord.number = np.array(constants.note_numbers_C_to_C[question.chord.index])
    question.chord.name = constants.note_names_chromatic_C_scale[question.chord.number % 12]
    return question


def set_chord_size(question):
    question.question.size = np.random.choice(
        np.arange(1, 1+constants.max_chord_size), 1,
        p=constants.levels.number_of_notes[question.level.number_of_notes, :])
    return question



def set_step_trend_and_new_note_index(question, question_list):
    while True:
        if question.question.size <= question_list[-1].question.size:
            question.step.trend = binary_markov_chain(
                constants.probability_of_same_step_direction,
                question_list[-1].step.trend[:question.question.size])
        elif question.question.size > question_list[-1].question.size:
            previous_step_trend = [question_list[-1].step.trend] + \
                                  [question_list[-1].step.trend[-1] *
                                   (question.question.size - question_list[-1].question.size)]
            question.step.trend = binary_markov_chain(
                constants.probability_of_same_step_direction,
                previous_step_trend
            )
        question.question.index = question_list[-1].question.index + \
                                  question.step.size * question.step.trend

        if 0 <= np.min(question.question.index) and \
                np.max(question.question.index) < len(constants.note_numbers_C_to_C):
            question.question.index = np.sort(question.question.index)
            break
    return question



