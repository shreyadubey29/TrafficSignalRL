"""
Code for Memory creation and related functions

"""
import random
import warnings

warnings.filterwarnings("ignore")

# Memory is the list of samples
class Memory:
    def __init__(self, min_size, max_size):

        self.sample_list = []
        self.min_size = min_size
        self.max_size = max_size

    def add_sample(self, sample):

        self.sample_list.append(sample)

        # if the sample list is full then empty an older value
        if self.current_size() > self.max_size:
            self.sample_list.pop(0)

    def get_samples(self, batch_size):

        samples = []
        if self.current_size() > self.min_size:
            if batch_size > self.current_size():
                samples = self.sample_list
            else:
                samples = random.sample(self.sample_list, batch_size)

        return samples

    def current_size(self):
        return len(self.sample_list)
