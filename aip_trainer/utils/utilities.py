"""Various utilities (logger, time benchmark, args dump, numerical and stats info)"""

from copy import deepcopy
from aip_trainer import app_logger
from aip_trainer.utils.serialize import serialize


def hash_calculate(arr_or_path, is_file: bool, read_mode: str = "rb") -> str | bytes:
    """
    Return computed hash from input variable (typically a numpy array).

    Args:
        arr: input variable

    Returns:
        computed hash from input variable
    """
    from hashlib import sha256
    from base64 import b64encode
    from numpy import ndarray as np_ndarray

    if is_file:
        with open(arr_or_path, read_mode) as file_to_check:
            # read contents of the file
            arr_or_path = file_to_check.read()
            # # pipe contents of the file through
            # try:
            #     return hashlib.sha256(data).hexdigest()
            # except TypeError:
            #     app_logger.warning(
            #         f"TypeError, re-try encoding arg:{arr_or_path},type:{type(arr_or_path)}."
            #     )
            #     return hashlib.sha256(data.encode("utf-8")).hexdigest()

    if isinstance(arr_or_path, np_ndarray):
        hash_fn = sha256(arr_or_path.data)
    elif isinstance(arr_or_path, dict):
        import json

        serialized = serialize(arr_or_path)
        variable_to_hash = json.dumps(serialized, sort_keys=True).encode("utf-8")
        hash_fn = sha256(variable_to_hash)
    elif isinstance(arr_or_path, str):
        try:
            hash_fn = sha256(arr_or_path)
        except TypeError:
            app_logger.warning(
                f"TypeError, re-try encoding arg:{arr_or_path},type:{type(arr_or_path)}."
            )
            hash_fn = sha256(arr_or_path.encode("utf-8"))
    elif isinstance(arr_or_path, bytes):
        hash_fn = sha256(arr_or_path)
    else:
        raise ValueError(
            f"variable 'arr':{arr_or_path} of type '{type(arr_or_path)}' not yet handled."
        )
    return b64encode(hash_fn.digest())
