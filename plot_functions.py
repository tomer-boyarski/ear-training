from turtle import color
import numpy as np
import matplotlib.pyplot as plt
import constants
# import initial
# from collections import namedtuple
import seaborn as sns
import matplotlib.dates as mdates
import config

def my_plot(list_of_iteration_lists, keys):
    nrows=3
    ncols = 2
    fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(8, 4))
    if config.plot_only_last_session:
        list_of_iteration_lists = [list_of_iteration_lists[-1]]
    for list_index, iteration_list in enumerate(list_of_iteration_lists):
        answer_time = [q.answer.time.raw for q in iteration_list]
        auto_regressive_answer_time = [question.answer.time.autoregressive for question in iteration_list]
        datetime_list = [i.answer.time.datetime for i in iteration_list]
        datetime_list = np.array(datetime_list)
        if list_index == 0:
            label = 'answer time'
        else:
            label = ''
        ax[0, 0].plot(datetime_list, answer_time, '-', label=label, color='b')
        if list_index == 0:
            label = 'Errors'
        else:
            label = ''
        error_indices = [i for i, q in enumerate(iteration_list) if q.answer.type == False]
        number_of_notes_per_question = [q.question.number_of_notes for q in iteration_list]
        number_of_notes_per_question = np.array(number_of_notes_per_question)

        error_times = np.take(datetime_list, error_indices)
        ax[0, 0].plot(error_times,
                    np.zeros(len(error_indices)),
                    'd', label=label, color='m')
        line_types = [':', '--', '-.']
        labels_for_long_and_short_already_drawn = False
        for index_of_number_of_notes, number_of_notes in enumerate(np.unique(number_of_notes_per_question)):
            very_short_answer_time, very_long_answer_time, _, _, = \
                constants.set_abcd(number_of_notes=number_of_notes)
            datetime_list_with_specific_number_of_notes = datetime_list
            mask = number_of_notes_per_question == number_of_notes
            datetime_list_with_specific_number_of_notes = \
                datetime_list_with_specific_number_of_notes[mask]

            if not labels_for_long_and_short_already_drawn and \
                len(datetime_list_with_specific_number_of_notes) > 1:
                labels_for_long_and_short_already_drawn = True
                short_label = 'very short answer time'
                long_label = 'very long answer time'
            else:
                short_label = ''
                long_label = ''
            ax[0, 0].plot(datetime_list_with_specific_number_of_notes,
                            very_short_answer_time * np.ones(len(datetime_list_with_specific_number_of_notes)),
                            line_types[index_of_number_of_notes]+'g', 
                            label=short_label)
            ax[0, 0].plot(datetime_list_with_specific_number_of_notes,
                            very_long_answer_time * np.ones(len(datetime_list_with_specific_number_of_notes)),
                            line_types[index_of_number_of_notes]+'r', 
                            label=long_label)
        box = ax[0, 0].get_position()
        ax[0, 0].set(ylabel='seconds')
        ax[0, 0].set_position([box.x0, box.y0, box.width, box.height])
        ax[0, 0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax[0, 0].xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
        ax[0, 0].xaxis.set_major_locator(mdates.DayLocator(interval=1))
        # # # # # # # # # # # # # # # # # # # # # # # # #
        max_level_list = [i.question.max_level for i in iteration_list]
        if len(max_level_list) >= 1:
            max_max_level = max(max_level_list)
        else:
            max_max_level = 1
        ylimit = max_max_level
        plot_levels(ax=ax, iteration_list=iteration_list, y_limit=None,
                    level_type='total', r_ind=1, c_ind=0, list_index=list_index)
        y_limit = getattr(constants.levels.step_size, keys).shape[0]
        plot_levels(ax=ax, iteration_list=iteration_list, y_limit=None,
                    level_type='step_size', r_ind=2, c_ind=0, list_index=list_index)
        y_limit = getattr(constants.levels.intervals, keys).shape[0]
        plot_levels(ax=ax, iteration_list=iteration_list, y_limit=None,
                    level_type='intervals', r_ind=1, c_ind=1, list_index=list_index)
        y_limit = constants.levels.number_of_notes.shape[0]
        plot_levels(ax=ax, iteration_list=iteration_list, y_limit=None,
                    level_type='number_of_notes', r_ind=2, c_ind=1, list_index=list_index)

        # for cind in range(ncols):
        #     for rind in range(nrows):
        #         print('rind', rind, 'cind', cind)
        #         if not (cind == 1 and rind == 1):
        #             ax[rind, cind].xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
        #             ax[rind, cind].xaxis.set_major_locator(mdates.DayLocator(interval=1))

    ax[0, 1].set_axis_off()
    fig.canvas.draw()
    plt.show()


def plot_step_size(r_ind, c_ind, question_list, ax):
    step_size_list = [q.question.step.size for q in question_list]
    step_size_list = np.array(step_size_list)
    step_size_list = np.abs(step_size_list)
    ax[r_ind, c_ind].plot(step_size_list, label='step size')
    box = ax[r_ind, c_ind].get_position()
    ax[r_ind, c_ind].set_position([box.x0, box.y0, box.width, box.height])
    ax[r_ind, c_ind].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax[r_ind, c_ind].set(yticks=range(0, 9))


def plot_levels(ax, iteration_list, y_limit, level_type, r_ind, c_ind, list_index):
    level_to_plot = [getattr(iteration.question.level, level_type) for iteration in iteration_list]
    datetime_list = [i.answer.time.datetime for i in iteration_list]
    level_to_plot_1 = []
    datetime_list_1 = []
    for index, level in enumerate(level_to_plot):
        if level is not None:
            level_to_plot_1.append(level)
            datetime_list_1.append(datetime_list[index])
    # level_to_plot = [l for l in level_to_plot if l is not None]
    # datetime_list = [l for l in datetime_list if l is not None]
    
    if list_index == 0:
        label = level_type+' level'
    else:
        label = ''
    ax[r_ind, c_ind].plot(datetime_list_1, level_to_plot_1, 
                          label=label,
                          color='b')
    box = ax[r_ind, c_ind].get_position()
    ax[r_ind, c_ind].set_position([box.x0, box.y0, box.width, box.height])
    if len(datetime_list_1) > 0:
        ax[r_ind, c_ind].xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
        ax[r_ind, c_ind].xaxis.set_major_locator(mdates.DayLocator(interval=1))
    # ax[r_ind, c_ind].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax[r_ind, c_ind].legend()
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

