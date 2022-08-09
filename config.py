import constants
keys = 'white'
# keys = 'all'
note_names = None
note_indices = None
note_numbers = None
number_of_notes = None
number_of_notes_level = 1
intervals = None
intervals_level = getattr(constants.levels.max.intervals, keys)
step_size = 1
step_trend = None
step_size_level = None # getattr(constants.levels.max.step_size, keys)
chord_creation_method = 'notes from a box'
step_top_or_bottom = 'top'
# phase = 'exponential'
phase = 'steady state'
play_intro = True
accept_with_spaces = True
accept_without_spaces = True
mistakes_counter = 0
# user = 'rosa' # 'tomer'
user = 'tomer'
request_answer = True
note_attributes = {'indices': note_indices,
                   'names': note_names,
                   'numbers': note_numbers}
note_attributes = {k: v for k, v in note_attributes.items() if v is not None}
plot_only_last_session = False