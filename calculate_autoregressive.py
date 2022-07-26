import constants


def calculate_autoregressive(x, y):
    p = constants.last_sample_weight
    return (1 - p) * x + p * y
