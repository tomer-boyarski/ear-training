import numpy as np


class Step:
    def __init__(self, sizes=None, trends=None,
                 current_indices=None, previous_indices=None,
                 difficulty_level=None):
        self.difficulty_level = difficulty_level

        if sizes is not None:
            self.sizes = sizes # [None] * constants.max_chord_size
        elif current_indices is not None and previous_indices is not None:
            self.sizes = current_indices - previous_indices
        else:
            self.set_step_size(difficulty_level)

        if trends is not None:
            self.trends = np.array(trends)
        elif current_indices is not None and previous_indices is not None:
            self.trends = np.sign(self.sizes)
        # if sizes is not None:
        #     self.initialize_with_sizes(sizes)
        # self.trends =  [(-1) ** np.random.binomial(1, 0.5)] * chord_size
        # self.trend = self.trend + \
        #     [np.nan] * (constants.max_chord_size - chord_size)

    def set_step_size(self, difficulty_level):
        # self.sizes = np.random.choice(
        #     np.arange(constants.max_step_size+1), question.chord.sizes,
        #     p=constants.levels.step_size[difficulty_level, :])
        pass
        # if 0 > np.min(question.step.size) or question.step.size > 7:
        #     print('step size too big or too small')
