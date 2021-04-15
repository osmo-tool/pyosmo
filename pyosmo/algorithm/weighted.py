from pyosmo.algorithm.base import OsmoAlgorithm


class Choice(object):
    def __init__(self, ending, count_in_history, weight):
        self.ending = ending
        self.count_in_history = count_in_history
        self.weight = weight

    @property
    def compare_value(self):
        return self.count_in_history * (1 / self.weight)


class WeightedAlgorithm(OsmoAlgorithm):
    def choose(self, history, choices):
        choice_list = list()
        for choice in choices:
            choice_list.append(Choice(
                choice,
                history.count_in_current_test_case(choice),
                self.model.get_step_weight(choice)
            ))
        compare_values = [x.compare_value for x in choice_list]
        lowest = min(compare_values)
        temp = filter(lambda x: x.compare_value == lowest, choice_list)
        temp = self.random.choice(list(temp)).ending
        return temp
