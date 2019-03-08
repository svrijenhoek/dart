import json
import hashlib
import numpy as np
import pickle
import random
import string


def read_config_file(top, key):
    with open('..\\..\\..\\config.json') as json_data_file:
        data = json.load(json_data_file)
    return data[top][key]


def random_string(N):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))


def get_random_number(mean, sdev):
    return int(np.random.normal(mean, sdev))


def generate_hash(s):
    return hashlib.sha1(s.encode('utf-8')).hexdigest()


def write_to_json(file, s):
    with open(file, 'w') as outfile:
        json.dump(s, outfile, indent=4, separators=(',', ': '), sort_keys=True)


def read_json_file(file):
    with open(file) as F:
        return json.load(F)


def load_data(location):
    with open(location, 'rb') as input:
        file = pickle.load(input)
    return file


def save_data(location, data):
    with open(location, 'wb') as pickle_file:
        pickle.dump(data, pickle_file)

