import numpy as np
import matplotlib.pyplot as plt
import constants
# import initial
# from collections import namedtuple
import seaborn as sns


def my_plot(question_list):
    fig, ax = plt.subplots(nrows=3, ncols=2, figsize=(12,6))
    # questions_indices = [question.question_index for question in question_list if question.True_or_False]
    # response_time = [question.response_time for question in question_list if question.True_or_False]
    response_time = [q.response.time.raw for q in question_list]
    auto_regressive_response_time = [question.response.time.autoregressive for question in question_list]

    # ax[0, 0].plot(questions_indices, response_time, label='response time')
    # ax[0, 0].plot(questions_indices, constants.minimal_response_time * np.ones(len(response_time)),
    #            '--k', label='minimal response time')
    ax[0, 0].plot(response_time, ':', label='response time')
    # ax[0, 0].plot(auto_regressive_response_time, label='autoregressive response time')
    question_indices = np.arange(len(question_list))
    is_False = [not q.response.type for q in question_list]
    number_of_notes_per_question = [q.question.number_of_notes for q in question_list]
    number_of_notes_per_question = np.array(number_of_notes_per_question)
    # number_of_notes = np.array([q.number_of_notes for q in question_list])

    error_indices = question_indices[is_False]
    ax[0, 0].plot(error_indices,
                   np.zeros(len(error_indices)),
                   'd', label='Errors')
    for number_of_notes in np.unique(number_of_notes_per_question):
        very_short_response_time, very_long_response_time, _, _, = \
            constants.set_abcd(number_of_notes=number_of_notes)
        question_indices_with_specific_number_of_notes = \
            question_indices
        ind_to_none = number_of_notes_per_question != number_of_notes
        if np.sum(ind_to_none.astype(int)) > 0:
            question_indices_with_specific_number_of_notes[ind_to_none] = None
        # plt.show()
        ax[0, 0].plot(question_indices_with_specific_number_of_notes,
                       very_short_response_time * np.ones(len(question_indices_with_specific_number_of_notes)),
                       '-g', label='very short response time')
        # plt.show()
        ax[0, 0].plot(question_indices_with_specific_number_of_notes,
                       very_long_response_time * np.ones(len(question_indices_with_specific_number_of_notes)),
                       '-r', label='very long response time')
        # plt.show()
    box = ax[0, 0].get_position()
    ax[0, 0].set(ylabel='seconds')
    ax[0, 0].set_position([box.x0, box.y0, box.width * 0.5, box.height])
    ax[0, 0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # # # # # # # # # # # # # # # # # # # # # # # # #
    max_level_list = [i.max_level_func for i in question_list]
    max_max_level = max(max_level_list)
    plot_levels(ax=ax, question_list=question_list, y_limit=max_max_level,
                level_type='total', r_ind=1, c_ind=0)
    plot_levels(ax=ax, question_list=question_list, y_limit=constants.levels.step_size.shape[0],
                level_type='step_size', r_ind=0, c_ind=1)
    plot_levels(ax=ax, question_list=question_list, y_limit=constants.levels.intervals.shape[0],
                level_type='intervals', r_ind=1, c_ind=1)
    plot_levels(ax=ax, question_list=question_list, y_limit=constants.levels.number_of_notes.shape[0],
                level_type='number_of_notes', r_ind=2, c_ind=1)

    # # # # # # # # # # # # # # # # # # # # # # # #
    step_size_list = [q.question.step.size for q in question_list]
    step_size_list = np.array(step_size_list)
    step_size_list = np.abs(step_size_list)
    ax[2, 0].plot(step_size_list, label='step size')
    box = ax[2, 0].get_position()
    ax[2, 0].set_position([box.x0, box.y0, box.width * 0.5, box.height])
    ax[2, 0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax[2, 0].set(yticks=range(0, 9))
    # # # # # # # # # # # # # # # # #
    fig.canvas.draw()
    plt.show()
    # print('stop here please')


def plot_levels(ax, question_list, y_limit, level_type, r_ind, c_ind):
    level_to_plot = [getattr(question.level, level_type) for question in question_list]
    ax[r_ind, c_ind].plot(level_to_plot, label=level_type+' level')
    box = ax[r_ind, c_ind].get_position()
    ax[r_ind, c_ind].set_position([box.x0, box.y0, box.width * 0.5, box.height])
    ax[r_ind, c_ind].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax[r_ind, c_ind].set(ylim=[0, y_limit])


def plot_jump_success_rate(question_list):
    num_jump = np.zeros((len(constants.note_numbers_C_to_C), len(constants.note_numbers_C_to_C)))
    num_jump_succ = np.zeros(num_jump.shape)
    for i, q in enumerate(question_list):
        if i > 0:
            num_jump[question_list[i-1].question.index, question_list[i].question.index] += 1
            if q.response.type:
                num_jump_succ[question_list[i - 1].question.index, question_list[i].question.index] += 1
    jum_succ_rate = np.full(num_jump.shape, np.nan)
    jum_succ_rate[num_jump != 0] = num_jump_succ[num_jump != 0] / num_jump[num_jump != 0]
    note_names_to_heatmap = constants.note_names_chromatic_C_scale[constants.note_numbers_C_to_C % 12]
    fig, ax = plt.subplots(1, 2)
    sns.heatmap(num_jump,
                xticklabels=note_names_to_heatmap,
                yticklabels=note_names_to_heatmap,
                cmap="crest",
                annot=True,
                ax=ax[0, 0])
    sns.heatmap(jum_succ_rate,
                xticklabels=note_names_to_heatmap,
                yticklabels=note_names_to_heatmap,
                cmap="crest",
                annot=True,
                ax=ax[1, 0])
    plt.show()

