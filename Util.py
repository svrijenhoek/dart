import json
import hashlib
import numpy as np


def read_config_file(top, key):
    with open('..\\config.json') as json_data_file:
        data = json.load(json_data_file)
    return data[top][key]


def get_random_number(mean, sdev):
    return int(np.random.normal(mean, sdev))


def generate_hash(s):
    return hashlib.sha1(s.encode('utf-8')).hexdigest()

