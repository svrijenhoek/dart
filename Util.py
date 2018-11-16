import json
import numpy as np


def read_config_file(top, key):
    with open('..\\config.json') as json_data_file:
        data = json.load(json_data_file)
    return data[top][key]


def get_random_number(mean, sdev):
    return int(np.random.normal(mean, sdev))
