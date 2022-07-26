import constants
import numpy as np


class Volume:
    def __init__(self):
        self.value = round((constants.max_volume + constants.min_volume) / 2)
        self.trend = (-1)**np.random.binomial(1, 0.5)


class Step:
    def __init__(self):
        self.level = 61
        self.size = None
        self.trend = (-1)**np.random.binomial(1, 0.5)


class Note:
    class History:
        def __init__(self):
            self.previous_index = 7
            self.penultimate_index = 7

    def __init__(self):
        self.history = self.History()
        self.index = 7
        self.name = 'C'
        self.number = 60


class Response:
    class Time:
        def __init__(self):
            a = constants.very_short_response_time
            b = constants.very_long_response_time
            c = constants.number_of_step_size_sub_levels
            d = -constants.number_of_step_size_sub_levels
            # x = a + c * (b-a) / (d-c)
            x = (a+b)/2
            self.raw = x
            self.autoregressive = constants.optimal_response_time

    def __init__(self, ):
        self.text = 'C'
        self.true_or_false = True
        self.time = self.Time()
