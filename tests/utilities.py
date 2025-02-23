"""Various utilities (Serialize objects, time benchmark, args dump, numerical and stats info)"""
from pathlib import Path
from typing import Mapping

import numpy as np

from constants import app_logger


def serialize(obj: any, include_none: bool = False):
    """
    Return the input object into a serializable one

    Args:
        obj: Object to serialize
        include_none: bool to indicate if include also keys with None values during dict serialization

    Returns:
        serialized object
    """
    return _serialize(obj, include_none)


def _serialize(obj: any, include_none: bool):
    from numpy import ndarray as np_ndarray, floating as np_floating, integer as np_integer

    primitive = (int, float, str, bool)
    # print(type(obj))
    try:
        if obj is None:
            return None
        elif isinstance(obj, np_integer):
            return int(obj)
        elif isinstance(obj, np_floating):
            return float(obj)
        elif isinstance(obj, np_ndarray):
            return obj.tolist()
        elif isinstance(obj, primitive):
            return obj
        elif type(obj) is list:
            return _serialize_list(obj, include_none)
        elif type(obj) is tuple:
            return list(obj)
        elif type(obj) is bytes:
            return _serialize_bytes(obj)
        elif isinstance(obj, Exception):
            return _serialize_exception(obj)
        # elif isinstance(obj, object):
        #     return _serialize_object(obj, include_none)
        else:
            return _serialize_object(obj, include_none)
    except Exception as e_serialize:
        app_logger.error(f"e_serialize::{e_serialize}, type_obj:{type(obj)}, obj:{obj}.")
        return f"object_name:{str(obj)}__object_type_str:{str(type(obj))}."


def _serialize_object(obj: Mapping[any, object], include_none: bool) -> dict[any]:

    res = {}
    if type(obj) is not dict:
        keys = [i for i in obj.__dict__.keys() if (getattr(obj, i) is not None) or include_none]
    else:
        keys = [i for i in obj.keys() if (obj[i] is not None) or include_none]
    for key in keys:
        if type(obj) is not dict:
            res[key] = _serialize(getattr(obj, key), include_none)
        else:
            res[key] = _serialize(obj[key], include_none)
    return res


def _serialize_list(ls: list, include_none: bool) -> list:
    return [_serialize(elem, include_none) for elem in ls]


def _serialize_bytes(b: bytes) -> dict[str, str]:
    import base64
    encoded = base64.b64encode(b)
    return {"value": encoded.decode('ascii'), "type": "bytes"}


def _serialize_exception(e: Exception) -> dict[str, str]:
    return {"msg": str(e), "type": str(type(e)), **e.__dict__}



def hash_calculate(arr_or_path: np.ndarray | str | Path, is_file: bool, read_mode: str = "rb") -> str | bytes:
    """
    Return computed hash from input variable (typically a numpy array).

    Args:
        arr_or_path: variable to hash (numpy array, string, Path-like object, dict, bytes)
        is_file: read the variable from a file
        read_mode: used when is_file is True to read the file in binary or text mode

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
            app_logger.error(
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
