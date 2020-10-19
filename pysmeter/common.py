import sys

MODEL_VERSION = "v1"

ENSEMBLE_SIZE = 10

PLATFORM_TO_PATH = {
    "linux": "/usr/share/smeter-models",
    "darwin": "/usr/local/share/smeter-models",
}

MODELS_PATH = PLATFORM_TO_PATH[sys.platform]
