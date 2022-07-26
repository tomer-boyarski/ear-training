import numpy as np
import matplotlib.pyplot as plt
from itertools import chain, combinations

num_att_levels = [5, 61, 61]
current_levels = np.arange(5 * 61 * 61)
current_levels = np.arange(100)

l = [0, 1, 2]  # list_of_indices
all_subsets = list(chain.from_iterable(combinations(l, r) for r in range(len(l) + 1)))
# print(all_subsets)
attribute_names = ['number_of_notes', 'intervals', 'step_size']
for subset in all_subsets:
    dynamic_attribute_names = np.take(attribute_names, subset).tolist()
#     dynamic_attribute_names = dynamic_attribute_names.tolist()

    if dynamic_attribute_names == ['number_of_notes', 'intervals', 'step_size']:
        # print(dynamic_attribute_names)
        levels = [[], [], []]
        for current_level in current_levels:
            if current_level <= 60:
                levels[0].append(0)
                levels[1].append(0)
                levels[2].append(current_level)
            elif current_level > 60:
                current_level = current_level - 61
                number_of_notes_level, remainder = np.divmod(current_level, 61*61)
                levels[0].append(number_of_notes_level+1)
                intervals_level, step_size_level = np.divmod(remainder, 61)
                levels[1].append(intervals_level)
                levels[2].append(step_size_level)
        fig, ax = plt.subplots(nrows=1, ncols=4, figsize=(12, 3))
        fig.tight_layout(rect=[0, 0, 1, 0.85])
        #     fig.tight_layout()
        for att_ind, attribute_name in enumerate(dynamic_attribute_names):
            ax[attribute_names.index(attribute_name) + 1].plot(levels[attribute_names.index(attribute_name)]);
        ax[0].plot(current_levels)
        ax[0].set_title('current_levels')
        ax[1].set_title('number of notes')
        ax[2].set_title('intervals')
        ax[3].set_title('step size')
        plt.suptitle(', '.join(dynamic_attribute_names))