import numpy as np
import h5py

def get_skin_data(split=0.7):
    f = h5py.File('dataset.h5')
    train_set = []
    test_set = []
    class_no = 0
    for key in f:
        split = int(len(f[key]) * 0.7)
        for image in f[key][:split]:
            train_set.append((image, class_no))
        for image in f[key][split:]:
            test_set.append((image, class_no))
        class_no += 1
    return train_set, test_set