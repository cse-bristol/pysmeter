import os
import shutil
import requests
from pysmeter.common import MODEL_VERSION, ENSEMBLE_SIZE, MODELS_PATH

_MODEL_URL = "https://smeter.cse.org.uk/models/" + MODEL_VERSION


def download_model():
    """Downloads the model files from the remote server and saves them in the specified dir."""
    for i in range(ENSEMBLE_SIZE):
        model_filename = f"model{i}.json"
        weights_filename = f"model{i}.h5"

        model_url = f"{_MODEL_URL}/{model_filename}"
        weights_url = f"{_MODEL_URL}/{weights_filename}"

        with requests.get(model_url, stream=True) as r:
            with open(os.path.join(MODELS_PATH, model_filename), "wb+") as f:
                shutil.copyfileobj(r.raw, f)

        with requests.get(weights_url, stream=True) as r:
            with open(os.path.join(MODELS_PATH, weights_filename), "wb+") as f:
                shutil.copyfileobj(r.raw, f)

    return MODELS_PATH


if __name__ == "__main__":
    download_model()
