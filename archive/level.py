import numpy as np
import constants
import initial


class Level:
    def __init__(self, question_list, phase, keys, mistakes_counter,
                 step_size, intervals, number_of_notes, step_size_level,
                 number_of_notes_level, interval_level, max_level, user):

        attributes = [number_of_notes, intervals, step_size]
        attribute_names = ['number_of_notes', 'intervals', 'step_size']
        attribute_levels = [number_of_notes_level, interval_level, step_size_level]

        is_attribute_dynamic = \
            self.set_level_attributes_if_literal_otherwise_something_else(
                question_list=question_list,
                attributes=attributes,
                attribute_levels=attribute_levels,
                attribute_names=attribute_names,
                user=user)
        self.dynamic_attributes = {k: v for k, v in is_attribute_dynamic.items() if v is True}
        if len(self.dynamic_attributes) == 0:
            self.total = None
        else:
            self.calculate_total_level_according_to_raw_response_time(
                question_list, phase, max_level=max_level, mistakes_counter=mistakes_counter,
                user=user)
            self.number_of_notes = None
            self.intervals = None
            self.step_size = None
            self.calculate_dynamic_attributes_from_total_level(
                is_attribute_dynamic=is_attribute_dynamic,
                attribute_names=attribute_names, keys=keys)

            if constants.show_total_level:
                print('level.total = ' + str(self.total))
                print('number_of_notes level= ' + str(self.number_of_notes))
                print('intervals level = ' + str(self.intervals))
                print('step_size level = ' + str(self.step_size))

    def raise_exception(self):
        my_str = 'To manually set the difficulty level, ' + \
                 'either input the "total" level or ' + \
                 'both the "step_size" and "chord_size" levels. '
        if self.step_size is not None and self.number_of_notes is None and self.total is None:
            raise Exception(my_str +
                            'You only put the "step_size" level.')
        if self.step_size is None and self.number_of_notes is not None and self.total is None:
            raise Exception(my_str +
                            'You only put the "chord_size" level.')
        if self.step_size is None and self.number_of_notes is not None and self.total is not None:
            raise Exception(my_str +
                            'You put both the "total" level and the "chord_size" level.')
        if self.step_size is not None and self.number_of_notes is None and self.total is not None:
            raise Exception(my_str +
                            'You put both the "total" level and the "step_size" level.')
        if self.step_size is not None and self.number_of_notes is not None and self.total is not None:
            raise Exception(my_str +
                            'You put all three levels together.')

    def set_level_attributes_if_literal_otherwise_something_else(
            self, question_list, attribute_names,
            attributes, attribute_levels, user):
        update_level_according_to_user_response = {}
        for attribute, attribute_level, attribute_name in \
                zip(attributes, attribute_levels, attribute_names):
            update_level_according_to_user_response[attribute_name] = False
            if attribute is not None:
                if attribute_level is not None:
                    raise Exception('step size is not None and step size level is also not None')
                else:
                    setattr(self, attribute_name, None)
            else: # attribute is None
                if attribute_level is not None:
                    setattr(self, attribute_name, attribute_level)
                else: # attribute_level is None
                    update_level_according_to_user_response[attribute_name] = True
                    if len(question_list) == 0:
                        initial_attribute_level = getattr(initial.get_level(user=user), attribute_name)
                        setattr(self, attribute_name, initial_attribute_level)
        return update_level_according_to_user_response

    def calculate_total_level_according_to_raw_response_time(
            self, question_list, phase, max_level, mistakes_counter, user):
        if len(question_list) == 0:
            self.total = initial.get_level(user).total
        elif len(question_list) >= 1:
            if question_list[-1].response.type is True:
                self.set_level_after_correct_answer(
                    phase=phase, mistakes_counter=mistakes_counter,
                    question_list=question_list,
                    max_level=max_level)
            elif question_list[-1].response.type is False:
                if question_list[-1].phase == 'exponential':
                    if len(question_list) >= 2:
                        responses = [q.response.type for q in question_list]
                        error_indices = [i for i, r in enumerate(responses) if r is False]
                        y = len(question_list) - 1
                        if len(error_indices) >= 2:
                            x = error_indices[-2]
                        else:
                            x = 0
                        index = round((x + y)/2)
                        self.total = question_list[index].level.total
                    else:
                        self.total = 0
                elif question_list[-1].phase == 'steady state':
                    self.total = question_list[-1].level.total + \
                                 constants.levels.change.additive.decrease_with_error
                # self.total = int(question_list[-1].level.total /
                #                  constants.multiplicative_level_decrease_upon_error)
                if self.total < 0:
                    self.total = 0

    def calculate_dynamic_attributes_from_total_level(
            self, keys, is_attribute_dynamic, attribute_names):
        dynamic_attribute_names = [x for x in attribute_names if
                                   is_attribute_dynamic[x]]
        max_step_size_level = getattr(constants.levels.max.step_size, keys)

        # if len(dynamic_attribute_names) != 3:
        #     raise Exception('I still did not write the code for how to '
        #                     'calculate the attribute level from the total level '
        #                     'when not all attributes are dynamic')
        if dynamic_attribute_names == ['intervals', 'step_size']:
            if self.total <= max_step_size_level:
                self.number_of_notes = None
                self.intervals = 0
                self.step_size = self.total
            elif self.total > max_step_size_level:
                current_level = self.total - max_step_size_level - 1
                self.intervals, self.step_size = np.divmod(
                    current_level, constants.levels.max.step_size + 1)
                self.intervals = self.intervals + 1
        elif len(dynamic_attribute_names) == 3:
            if self.total <= max_step_size_level:
                self.number_of_notes = 0
                self.intervals = None
                self.step_size = self.total
            elif self.total > max_step_size_level:
                current_level = self.total - max_step_size_level - 1
                self.number_of_notes, remainder = \
                    np.divmod(current_level,
                              (getattr(constants.levels.max.intervals, keys) + 1) *
                              (getattr(constants.levels.max.step_size, keys) + 1))
                self.number_of_notes = self.number_of_notes + 1
                self.intervals, self.step_size = np.divmod(
                    remainder, getattr(constants.levels.max.step_size, keys) + 1)

    def calculate_total_level_from_dynamic_attributes(self):
        self.total = self.number_of_notes * \
                     constants.levels.intervals.shape[0] * \
                     constants.levels.step_size.shape[0] + \
                     self.intervals * \
                     constants.levels.step_size.shape[0] + \
                     self.step_size

    def set_level_after_correct_answer(
            self, phase, mistakes_counter, question_list, max_level):
        previous_raw_response_time = question_list[-1].response.time.raw
        previous_level = question_list[-1].level.total
        previous_number_of_notes = question_list[-1].question.number_of_notes
        a, b, c, d = constants.set_abcd(number_of_notes=previous_number_of_notes)
        x = previous_raw_response_time
        if type(x) is tuple:  # (which is shouldn't be)
            x = x[0]
        if phase == 'exponential':
            y = -2 * (x - a) / (b - a) + 1
            factor = constants.levels.change.multiplicative.increase
            factor = factor ** (1/(1+mistakes_counter)**2)
            factor = factor ** y
            print('factor = ' + str(factor))
            self.total = (previous_level+1) * factor
            self.total = round(self.total)
        elif phase == 'steady state':
            y = (x - a) * (d - c) / (b - a) + c
            y = round(y)
            # y = y / len(question_list)**0.8
            # y = int(np.ceil(y))
            self.total = previous_level + y
        if self.total > max_level:
            self.total = max_level
        if self.total < 0:
            self.total = 0
