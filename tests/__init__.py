import os
from pathlib import Path


TEST_ROOT_FOLDER = Path(globals().get("__file__", "./_")).absolute().parent
EVENTS_FOLDER = TEST_ROOT_FOLDER / "events"


def set_seed(seed=0):
    import random
    import torch
    import numpy as np

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
