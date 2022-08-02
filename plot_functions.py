import numpy as np
import matplotlib.pyplot as plt
import constants
# import initial
# from collections import namedtuple
import seaborn as sns


def my_plot(iteration_list, keys):
    fig, ax = plt.subplots(nrows=3, ncols=2, figsize=(8, 4))
    # questions_indices = [question.question_index for question in question_list if question.True_or_False]
    # answer_time = [question.answer_time for question in question_list if question.True_or_False]
    answer_time = [q.answer.time.raw for q in iteration_list]
    auto_regressive_answer_time = [question.answer.time.autoregressive for question in iteration_list]
    datetime_list = [i.answer.time.datetime for i in iteration_list]
    # ax[0, 0].plot(questions_indices, answer_time, label='answer time')
    # ax[0, 0].plot(questions_indices, constants.minimal_answer_time * np.ones(len(answer_time)),
    #            '--k', label='minimal answer time')
    ax[0, 0].plot(datetime_list, answer_time, '-', label='answer time')
    # ax[0, 0].plot(auto_regressive_answer_time, label='autoregressive answer time')
    question_indices = np.arange(len(iteration_list))
    answer_types = [q.answer.type for q in iteration_list]

    error_indices = [i for i, q in enumerate(iteration_list) if q.answer.type == False]
    number_of_notes_per_question = [q.question.number_of_notes for q in iteration_list]
    number_of_notes_per_question = np.array(number_of_notes_per_question)
    # number_of_notes = np.array([q.number_of_notes for q in question_list])

    error_indices = np.take(datetime_list, error_indices)
    ax[0, 0].plot(error_indices,
                   np.zeros(len(error_indices)),
                   'd', label='Errors')
    line_types = [':', '--', '-.']
    for index_of_number_of_notes, number_of_notes in enumerate(np.unique(number_of_notes_per_question)):
        very_short_answer_time, very_long_answer_time, _, _, = \
            constants.set_abcd(number_of_notes=number_of_notes)
        # question_indices_with_specific_number_of_notes = \
        #     datetime_list.astype(float)
        datetime_list_with_specific_number_of_notes = datetime_list
        for i in range(len(datetime_list_with_specific_number_of_notes)):
            if number_of_notes_per_question[i] != number_of_notes:
                datetime_list_with_specific_number_of_notes[i] = None
        # datetime_list_with_specific_number_of_notes = [d if  for d in datetime_list_with_specific_number_of_notes]
        # datetime_list_with_specific_number_of_notes[
        #     number_of_notes_per_question != number_of_notes] = None

        ax[0, 0].plot(datetime_list_with_specific_number_of_notes,
                        very_short_answer_time * np.ones(len(datetime_list_with_specific_number_of_notes)),
                        line_types[index_of_number_of_notes]+'g', 
                        label='very short answer time for ' + str(number_of_notes) + ' notes')
        ax[0, 0].plot(datetime_list_with_specific_number_of_notes,
                        very_long_answer_time * np.ones(len(datetime_list_with_specific_number_of_notes)),
                        line_types[index_of_number_of_notes]+'r', 
                        label='very long answer time for ' + str(number_of_notes) + ' notes')
    box = ax[0, 0].get_position()
    ax[0, 0].set(ylabel='seconds')
    ax[0, 0].set_position([box.x0, box.y0, box.width * 0.5, box.height])
    ax[0, 0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # # # # # # # # # # # # # # # # # # # # # # # # #
    max_level_list = [i.question.max_level for i in iteration_list]
    if len(max_level_list) >= 1:
        max_max_level = max(max_level_list)
    else:
        max_max_level = 1
    ylimit = max_max_level
    plot_levels(ax=ax, iteration_list=iteration_list, y_limit=None,
                level_type='total', r_ind=1, c_ind=0)
    y_limit = getattr(constants.levels.step_size, keys).shape[0]
    plot_levels(ax=ax, iteration_list=iteration_list, y_limit=None,
                level_type='step_size', r_ind=2, c_ind=0)
    y_limit = getattr(constants.levels.intervals, keys).shape[0]
    plot_levels(ax=ax, iteration_list=iteration_list, y_limit=None,
                level_type='intervals', r_ind=1, c_ind=1)
    y_limit = constants.levels.number_of_notes.shape[0]
    plot_levels(ax=ax, iteration_list=iteration_list, y_limit=None,
                level_type='number_of_notes', r_ind=2, c_ind=1)

    for axis in ax:
        axis.set_xticklabels(axis.get_xticks(), rotation = 45)

        # for label in ax.get_xticklabels(which='major'):
    # label.set(rotation=30, horizontalalignment='right')
    # plot_step_size(r_ind=2, c_ind=0, question_list=question_list, ax=ax)
    ax[0, 1].set_axis_off()
    fig.canvas.draw()
    plt.show()


def plot_step_size(r_ind, c_ind, question_list, ax):
    step_size_list = [q.question.step.size for q in question_list]
    step_size_list = np.array(step_size_list)
    step_size_list = np.abs(step_size_list)
    ax[r_ind, c_ind].plot(step_size_list, label='step size')
    box = ax[r_ind, c_ind].get_position()
    ax[r_ind, c_ind].set_position([box.x0, box.y0, box.width * 0.5, box.height])
    ax[r_ind, c_ind].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax[r_ind, c_ind].set(yticks=range(0, 9))


def plot_levels(ax, iteration_list, y_limit, level_type, r_ind, c_ind):
    level_to_plot = [getattr(iteration.question.level, level_type) for iteration in iteration_list]
    datetime_list = [i.answer.time.datetime for i in iteration_list]
    ax[r_ind, c_ind].plot(datetime_list, level_to_plot, label=level_type+' level')
    box = ax[r_ind, c_ind].get_position()
    ax[r_ind, c_ind].set_position([box.x0, box.y0, box.width * 0.5, box.height])
    ax[r_ind, c_ind].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    if y_limit is not None:
        ax[r_ind, c_ind].set(ylim=[0, y_limit])


def plot_jump_success_rate(question_list):
    num_jump = np.zeros((len(constants.note_numbers_C_to_C), len(constants.note_numbers_C_to_C)))
    num_jump_succ = np.zeros(num_jump.shape)
    for i, q in enumerate(question_list):
        if i > 0:
            num_jump[question_list[i-1].question.index, question_list[i].question.index] += 1
            if q.answer.flag.correct:
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

