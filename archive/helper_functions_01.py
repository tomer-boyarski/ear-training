import numpy as np
import time
import rtmidi
import matplotlib.pyplot as plt
import constants
import initial
from collections import namedtuple


def cubic_polynomial_mapping():
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


def intro():
    # mo = rtmidi.MidiOut()
    # mo.open_port(0)
    for i in range(4, 0, -1):
        note_to_play_now = constants.note_numbers_C_to_C[i] +12
        constants.mo.send_message([rtmidi.midiconstants.NOTE_ON, note_to_play_now, 64])
        time.sleep(constants.quarter_note_time/4/2)
        constants.mo.send_message([rtmidi.midiconstants.NOTE_OFF, note_to_play_now, 64])

    constants.mo.send_message([rtmidi.midiconstants.NOTE_ON, 60, 64])
    time.sleep(constants.quarter_note_time/2/2)
    constants.mo.send_message([rtmidi.midiconstants.NOTE_OFF, 60, 64])
    previous_note_index = 7

    # mo.close_port()
    return previous_note_index


def my_plot_old(constants, question_list):
    fig, ax = plt.subplots(2, 1)
    # questions_indices = [question.question_index for question in question_list if question.True_or_False]
    # response_time = [question.response_time for question in question_list if question.True_or_False]
    response_time = [question.response_time for question in question_list]
    auto_regressive_response_time = [question.autoregressive_response_time for question in question_list]
    # ax[0].plot(questions_indices, response_time, label='response time')
    # ax[0].plot(questions_indices, constants.minimal_response_time * np.ones(len(response_time)),
    #            '--k', label='minimal response time')
    ax[0].plot(response_time, ':', label='response time')
    ax[0].plot(auto_regressive_response_time, label='autoregressive response time')
    error_indices = [question.question_index for question in question_list if not question.True_or_False]
    ax[0].plot(error_indices,
               np.zeros(len(error_indices)),
               'd', label='Errors')
    ax[0].plot(constants.minimal_response_time * np.ones(len(response_time)),
               '--k', label='minimal response time')
    # ax[0].plot(constants.optimal_response_time * np.ones(len(response_time)),
    #            '--b', label='optimal response time')
    # ax[0].plot(questions_indices, constants.lower_bound_response_time * np.ones(len(response_time)),
    #            '-g', label='response time lower bound')
    # ax[0].plot(questions_indices, constants.upper_bound_response_time * np.ones(len(response_time)),
    #            '-r', label='response time upper bound')
    ax[0].plot(constants.lower_bound_response_time * np.ones(len(response_time)),
               '-g', label='response time lower bound')
    ax[0].plot(constants.upper_bound_response_time * np.ones(len(response_time)),
               '-r', label='response time upper bound')
    box = ax[0].get_position()
    ax[0].set(ylabel='seconds')
    # plt.ylabel('seconds')
    ax[0].set_position([box.x0, box.y0, box.width * 0.5, box.height])
    ax[0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # Next sub-plot
    # max_step_size_list = [question.step_size_level for question in question_list if question.True_or_False]
    # max_step_size_list = [question.step_size_level for question in question_list]
    max_step_size_list = [question.step_size_level for question in question_list if question]
    # ax[1].plot(questions_indices, max_step_size_list, label='max step size')
    ax[1].plot(max_step_size_list, label='max step size')
    # step_size_list = [question.step_size for question in question_list if question.True_or_False]
    step_size_list = [question.step_size for question in question_list]
    step_size_list = np.array(step_size_list)
    step_size_list = np.abs(step_size_list)
    ax[1].plot(step_size_list, label='step size')
    # ax[1].plot(questions_indices, step_size_list, label='step size')
    box = ax[1].get_position()
    ax[1].set_position([box.x0, box.y0, box.width * 0.5, box.height])
    ax[1].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    fig.canvas.draw()
    plt.show()
    print('stop here please')


def my_plot(constants, question_list):
    fig, ax = plt.subplots(3, 1)
    # questions_indices = [question.question_index for question in question_list if question.True_or_False]
    # response_time = [question.response_time for question in question_list if question.True_or_False]
    response_time = [q.response.time.raw for q in question_list]
    auto_regressive_response_time = [question.response.time.autoregressive for question in question_list]

    # ax[0].plot(questions_indices, response_time, label='response time')
    # ax[0].plot(questions_indices, constants.minimal_response_time * np.ones(len(response_time)),
    #            '--k', label='minimal response time')
    ax[0].plot(response_time, ':', label='response time')
    # ax[0].plot(auto_regressive_response_time, label='autoregressive response time')
    question_indices = np.arange(len(question_list))
    is_False = [not q.response.type for q in question_list]
    error_indices = question_indices[is_False]
    ax[0].plot(error_indices,
               np.zeros(len(error_indices)),
               'd', label='Errors')
    ax[0].plot(constants.very_short_response_time * np.ones(len(response_time)),
               '-g', label='very short response time')
    ax[0].plot(constants.very_long_response_time * np.ones(len(response_time)),
               '-r', label='very long response time')
    box = ax[0].get_position()
    ax[0].set(ylabel='seconds')
    ax[0].set_position([box.x0, box.y0, box.width * 0.5, box.height])
    ax[0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # # # # # # # # # # # # # # # # # # # # # # # # #
    max_step_size_list = [question.step.total_level for question in question_list if question]
    ax[1].plot(max_step_size_list, label='step size level')
    box = ax[1].get_position()
    ax[1].set_position([box.x0, box.y0, box.width * 0.5, box.height])
    ax[1].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax[1].set(ylim=[0, constants.levels.shape[0]], yticks=range(0, constants.levels.shape[0], 10))
    # ax[1].set(ylim=[0, 61])

    # # # # # # # # # # # # # # # # # # # # # # # #
    step_size_list = [q.step.size for q in question_list]
    step_size_list = np.array(step_size_list)
    step_size_list = np.abs(step_size_list)
    ax[2].plot(step_size_list, label='step size')
    box = ax[2].get_position()
    ax[2].set_position([box.x0, box.y0, box.width * 0.5, box.height])
    ax[2].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax[2].set(yticks=range(0, 9))
    # # # # # # # # # # # # # # # # #
    fig.canvas.draw()
    plt.show()
    print('stop here please')

