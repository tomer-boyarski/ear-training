import numpy as np
import constants
import initial


def get_number_of_notes_intervals_and_step_size_from_literals(intervals, step_size, question_list,
                                                              note_names, note_numbers, note_indices,
                                                              number_of_notes, number_of_notes_level):
    # The following "list of lists" made sense when the code was written
    # in a polyphonic way. We had several co-existing melodic lines,
    # each with its own "step trend" and "step size".
    # However, since then I have decided that it would make more sense to
    # write this code with a harmony state of mind.
    # The "chord" class will have the "step" class and a list of "note" objects
    # as attributes. The "step" will be an attribute of the chord and will refer
    # to the step of the bottom note.
    # I use the term "bottom note" rather than 'bass' since it may be quite high.
    # list_of_lists = {'step_trends': step_trends,
    #                  'step_sizes': step_sizes,
    #                  'note_names': note_names,
    #                  'note_numbers': note_numbers,
    #                  'note_indices': note_indices}
    note_attributes = {'note_names': note_names,
                       'note_numbers': note_numbers,
                       'note_indices': note_indices}
    note_attributes = {k: v for k, v in note_attributes.items() if v is not None}

    if len(note_attributes) != 0:
        for key, a_list in note_attributes.items():
            number_of_notes = len(a_list)
    elif intervals is not None:
        number_of_notes = len(intervals) + 1

    if note_indices is not None:
        if None not in note_indices:
            if intervals is None:
                note_indices = np.array(note_indices)
                intervals = note_indices[1:] - note_indices[:-1] + 1
                intervals = intervals.tolist()
        if note_indices[0] is not None:
            if step_size is None:
                if len(question_list) >= 1:
                    previous_bottom_note_index = question_list[-1].question.notes[0].index
                else:
                    previous_bottom_note_index = initial.indices
                step_size = note_indices[0] - previous_bottom_note_index + 1
                step_size = step_size[0]

    return number_of_notes, intervals, step_size


