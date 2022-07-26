import numpy as np
attribute_names = ['number_of_notes', 'intervals', 'step_size']

update_level_according_to_user_response = \
    {'number_of_notes':True, 'intervals':True, 'step_size':True}

level_delta = 10
previous_level = 12
current_level = previous_level + level_delta

dynamic_attribute_names = [x for x in attribute_names if
                           update_level_according_to_user_response[x]]
i = 0
for attribute_name in dynamic_attribute_names:
    my_prod = 1
    for att_name in dynamic_attribute_names[i + 1:]:
        my_prod = my_prod * 2
    attribute_level, current_level = np.divmod(
        current_level, my_prod)
    print(attribute_name + '=' + str(attribute_level))
    if i == len(dynamic_attribute_names) - 2:
        print(attribute_names[i+1] + '=' + str(current_level))
        break
    i += 1