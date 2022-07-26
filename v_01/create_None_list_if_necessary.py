import numpy as np


def create_none_list_if_necessary(list_or_none, size):
    if list_or_none is None:
        output = [None] * size
    else:
        if len(list_or_none) == size:
            if type(list_or_none) is list or \
                    type(list_or_none) is np.ndarray:
                output = list_or_none
        if len(list_or_none) != size:
            if type(list_or_none) is list or \
                    type(list_or_none) is np.ndarray:
                raise Exception('The list received by "create_None_list_if_necessary" ' +
                            str(list_or_none) + ' has a length of ' + str(len(list_or_none)) +
                            ' but it should have a length of ' + str(size))
    return output
