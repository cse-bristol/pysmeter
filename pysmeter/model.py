import os
import numpy as np
# Before we import tensorflow, set the logging level so as to avoid unwanted messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
import tensorflow.keras as k
from pysmeter.common import MODEL_VERSION, MODELS_PATH


# It's also necessary to do the following now that tensorflow has been imported
# to avoid excessive messages
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)


def _load_ensemble_member(member_name: str, model_version: str, model_weeks: int):
    """Loads CNN from saved serialized architecture and weights."""
    wk = f"{model_weeks}wk"

    with open(os.path.join(MODELS_PATH, model_version, wk, f"{member_name}.json")) as f:
        json_str = f.read()
        model = k.models.model_from_json(json_str, custom_objects={"GlorotUniform": k.initializers.glorot_uniform})

    model.load_weights(os.path.join(MODELS_PATH, model_version, wk, f"{member_name}.h5"))

    return model


def predict(X: np.ndarray):
    """Predicts the HTC of one or more buildings.

    X should be a numpy array of either 2 or 3 dimensions.
    If dim = 2 then the dimensions are: (no. timesteps, no. channels).
    If dim = 3 then the dimensions are: (no. houses, no. timesteps, no. channels).

    There are always four channels:
        indoor temperature (deg C)
        outdoor temperature (deg C)
        gas consumed (kWh)
        electricity consumed (kWh)

    Returns an array of predictions where each prediction is a tuple
    (prediction, lower bound of prediction interval, upper bound of prediction interval).
    """
    # If X is for a single house then turn it into a singleton array
    if len(X.shape) == 2:
        X = np.array([X])

    ensemble_predictions = []

    # Figure out how many weeks of data we have
    # and cut the array down to size if necessary
    no_timesteps = X.shape[1]
    no_weeks = min(4, no_timesteps // (48 * 7))

    if no_weeks == 3:
        X = X[:,:(3 * 7 * 48),:]
    elif no_weeks == 4:
        X = X[:,:(4 * 7 * 48),:]
    else:
        raise ValueError(f"Not enough time steps supplied. Expected at least {3 * 7 * 48} got {no_timesteps}.")

    # Load each of the ensemble members and make predictions. Append predictions to ensemble_predictions.
    ensemble_path = os.path.join(MODELS_PATH, MODEL_VERSION, f"{no_weeks}wk")

    for f in os.scandir(ensemble_path):
        if "json" in f.name:
            member_name = f.name[:-5]
            model = _load_ensemble_member(member_name, MODEL_VERSION, no_weeks)
            pred = model.predict(X)
            ensemble_predictions.append(pred)

    predictions = np.array(ensemble_predictions).mean(axis=0)
    # The prediction intervals may not be the right way round, so sort them to make sure they are.
    predictions.sort(axis=1)
    # Make each prediction a tuple (prediction, lower, upper)
    predictions = [(np.mean(p), p[0], p[1]) for p in predictions]

    return predictions
