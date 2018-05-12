import numpy as np

def get_disease_class_no(data):
    data = data.data[0]
    class_no = -1
    current_value = data[0]
    for value in data:
        if value > current_value:
            current_value = value
        class_no += 1
    return class_no


def get_trend_class_no(data):
    data = data.data[0]
    class_no = -1
    current_value = data[0]
    for value in data:
        if value > current_value:
            current_value = value
        class_no += 1
    return class_no
