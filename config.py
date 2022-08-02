keys = 'white'
# keys = 'all'
note_names = None
note_indices = None
note_numbers = None
number_of_notes = None
number_of_notes_level = None
intervals = None
intervals_level = None
step_size = None
step_trend = None
step_size_level = None
chord_creation_method = 'notes from a box'
# phase = 'exponential'
phase = 'steady state'
play_intro = True
accept_with_spaces = True
accept_without_spaces = True
mistakes_counter = 0
user = 'tomer'
request_answer = True
note_attributes = {'indices': note_indices,
                   'names': note_names,
                   'numbers': note_numbers}
note_attributes = {k: v for k, v in note_attributes.items() if v is not None}