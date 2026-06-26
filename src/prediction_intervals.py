import pickle
import numpy as np


model = pickle.load(open("pickle/model.pkl", "rb"))


def predict_interval(X):

    predictions = np.array([
        tree.predict(X)
        for tree in model.estimators_
    ])

    p10 = np.percentile(predictions, 10, axis=0)
    p50 = np.percentile(predictions, 50, axis=0)
    p90 = np.percentile(predictions, 90, axis=0)

    return p10, p50, p90