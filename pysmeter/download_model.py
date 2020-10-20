import os
import requests
from pysmeter.common import MODEL_VERSION, ENSEMBLE_SIZE, MODELS_PATH

_MODEL_URL = "https://smeter.cse.org.uk/models/" + MODEL_VERSION


def download_model():
    """Downloads the model files from the remote server and saves them in the specified dir."""
    # Make the models dirs if necessary
    three_wk_dir = os.path.join(MODELS_PATH, MODEL_VERSION, "3wk")
    four_wk_dir = os.path.join(MODELS_PATH, MODEL_VERSION, "4wk")

    try:
        if not os.path.isdir(three_wk_dir):
            os.makedirs(three_wk_dir)

        if not os.path.isdir(four_wk_dir):
            os.makedirs(four_wk_dir)
    except PermissionError as e:
        raise PermissionError("Try running this command with sudo.") from e

    for week in ("3wk", "4wk"):
        # Make the model dir if necessary
        model_dir = os.path.join(MODELS_PATH, MODEL_VERSION, week)

        if not os.path.isdir(model_dir):
            os.makedirs(model_dir)

        print(f"Downloading model files for {week} model...")

        # Download the files
        for i in range(ENSEMBLE_SIZE):
            model_filename = f"model{i}.json"
            weights_filename = f"model{i}.h5"

            model_url = os.path.join(_MODEL_URL, week, model_filename)
            weights_url = os.path.join(_MODEL_URL, week, weights_filename)

            with requests.get(model_url) as r:
                with open(os.path.join(model_dir, model_filename), "w+") as f:
                    f.write(r.text)

            with requests.get(weights_url) as r:
                with open(os.path.join(model_dir, weights_filename), "wb+") as f:
                    f.write(r.content)

            print(f"Downloaded {i + 1}/{ENSEMBLE_SIZE} model files.")

    return MODELS_PATH


if __name__ == "__main__":
    download_model()
