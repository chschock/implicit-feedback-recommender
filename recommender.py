import pandas as pd
import numpy as np

class Recommender(object):

    def __init__(self, likes_file):
        self.likes = pd.read_csv(likes_file, sep=';', quoting=1)
