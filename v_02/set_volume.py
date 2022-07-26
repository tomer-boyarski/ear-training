import constants
from binary_markov_chain import binary_markov_chain


def set_volume(question, question_list):
    while True:
        volume_trend = binary_markov_chain(
            constants.probability_of_same_volume_change_direction,
            question_list[-1].volume.trend)
        volume = question_list[-1].volume.value + \
                 constants.volume_change * volume_trend
        if constants.min_volume <= volume <= constants.max_volume:
            question.volume.trend = volume_trend
            question.volume.value = round(volume)
            break
    return question
