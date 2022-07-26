import numpy as np


def binary_markov_chain(probability_to_remain, previous_chord_state):
    # My two states are +1 and -1.
    probabilities_to_go_negative = \
        (1 + previous_chord_state) / 2 - \
        previous_chord_state * probability_to_remain
    new_state = (-1) ** np.random.binomial(1, probabilities_to_go_negative)
    return new_state
