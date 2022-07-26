import constants


def iteration(chord, step_sizes, step_trends,
              intervals, chord_range):
    if chord is not None and step_trends is not None:
        raise Exception('Can not perform  iteration initialization '
                        'where chord is not None and step trends is not None')
    if chord is not None and step_sizes is not None:
        raise Exception('Can not perform  iteration initialization '
                        'where chord is not None and step sizes is not None')
    if chord is not None and intervals is not None:
        raise Exception('Can not perform  iteration initialization '
                        'where chord is not None and intervals is not None')
    if chord is not None and chord_range is not None:
        raise Exception('Can not perform  iteration initialization '
                        'where chord is not None and range is not None')


def chord_literals(note_attributes,
                   number_of_notes,
                   intervals, key,
                   step_size, step_trend):
    # Check that all note attributes are valid
    for key_1, list_1 in note_attributes.items():
        if key == 'WHITE':
            att_list = getattr(constants.white_note, key_1)
            for item in list_1:
                if item is not None and item not in att_list:
                    raise Exception('invalid note ' + key_1[:-1])
        elif key != 'WHITE':
            raise Exception('missing exception rule for non-white keys')

    # Check that all note attributes have the same length
    for key_1, list_1 in note_attributes.items():
        for key_2, list_2 in note_attributes.items():
            if len(list_1) != len(list_2):
                raise Exception('Length of ' + key_1 + ' is ' + str(len(list_1)) +
                                ' but ' +
                                ' length of ' + key_2 + ' is ' + str(len(list_2)) +
                                '. They should be the same.')

    # Check that the length of all note attributes is the same as the number of notes
    if number_of_notes is not None:
        for key, a_list in note_attributes.items():
            if len(a_list) != number_of_notes:
                raise Exception('length of ' + key + ' is ' + str(len(a_list)) +
                                ' but number of notes is ' + str(number_of_notes) +
                                    '. They should be the same.')

    # Check that the length of all note attributes is the same as number of intervals plus one
    if intervals is not None:
        for key, a_list in note_attributes.items():
            if len(a_list) != len(intervals) + 1:
                raise Exception('Length of ' + key + ' is ' + str(len(a_list)) +
                                ' but length of "interval" is ' + str(len(intervals)) +
                                '. Length of "intervals" should be equal to length of ' +
                                key + ' - 1.')

    if step_size is not None or step_trend is not None:
        for key_1, list_1 in note_attributes.items():
            if list_1[0] is not None:
                raise Exception('bottom note is over-defined')

def level_literals(number_of_notes_level,
                   intervals_level,
                   step_size_level):
    level_att = {'number_of_notes': number_of_notes_level,
                 'intervals': intervals_level,
                 'step_size': step_size_level}
    for key, val in level_att.items():
        if val is not None:
            if val not in range(1 + getattr(constants.levels.max, key)):
                raise Exception('invalid ' + key + ' level')


def chord_vs_level_literals(note_attributes,
                            step_size,
                            intervals,
                            number_of_notes,
                            number_of_notes_level,
                            intervals_level,
                            step_size_level):

    if len(note_attributes) != 0 or intervals is not None or number_of_notes is not None:
        print('"get_number_of_notes" says: Number of notes is not random.')
        if number_of_notes_level is not None:
            raise Exception('Please do not explicitly define the "number of notes level" '
                            'if the number of notes is explicitly defined.')
    if intervals_level is not None and intervals is not None and None not in intervals:
        raise Exception('Please do not explicitly define the "intervals level" '
                        'if all intervals are explicitly defined.')
    if step_size is not None and step_size_level is not None:
        raise Exception('Please do not explicitly define the "step size level" '
                        'if the step size is explicitly defined.')