import numpy as np
import constants


class Step:
    def __init__(self, keys, size=None, trend=None,
                 current_index=None, previous_index=None,
                 difficulty_level=None):
        if (size is not None or trend is not None) and current_index is not None:
            raise Exception('step object is over-defined')

        if size is not None:
            self.size = size
        elif current_index is not None and previous_index is not None:
            self.size = abs(current_index - previous_index) + 1
        elif difficulty_level is not None:
            p = getattr(constants.levels.step_size, keys)
            p = p[difficulty_level, :]
            self.size = np.random.choice(
                np.arange(1, constants.max_step_size(keys=keys) + 1), 1, p=p)
            self.size = self.size[0]
        else:
            raise Exception('Can not determine step size. Not enough inputs.')

        if trend is not None:
            self.trend = np.array(trend)
        elif current_index is not None and previous_index is not None:
            self.trend = np.sign(self.size)
        else:
            self.trend = (-1) ** np.random.binomial(1, 0.5)
