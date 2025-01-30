from constants import PROJECT_ROOT_FOLDER


TEST_ROOT_FOLDER = PROJECT_ROOT_FOLDER / "tests"
EVENTS_FOLDER = TEST_ROOT_FOLDER / "events"


def set_seed(seed=0):
    import random
    import torch
    import numpy as np

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
