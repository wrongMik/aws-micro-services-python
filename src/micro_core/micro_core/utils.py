import json
import base64
from uuid import UUID
from typing import Any, Dict, List, Union
from decimal import Decimal
from datetime import datetime


def encode(data: Dict[Any, Any]) -> str:
    json_string = json.dumps(data)
    return base64.b64encode(json_string.encode('utf-8')).decode('utf-8')


def decode(data: str) -> Dict[Any, Any]:
    json_string = base64.b64decode(data.encode('utf-8')).decode('utf-8')
    return json.loads(json_string)


class AwsEncoder(json.JSONEncoder):
    '''Enable json.dumps to use uuid, datetime, decimals and set'''

    def default(self, o):
        '''Converts given datatypes into compatible datatypes for dynamodb or lambda'''
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, set):
            return list(o)
        return super(AwsEncoder, self).default(o)


def pick_keys(
    dicts: Union[Dict[Any, Any], List[Dict[Any, Any]]],
    keys: List[Any],
    skip_not_existing: bool = True,
) -> Union[Dict[Any, Any], List[Dict[Any, Any]]]:
    '''
    Create a shallow copy of the dicts passed as param and select only the
    keys specified in the keys param

    Args:
        dicts (Union[Dict[str, Any], List[Dict[str, Any]]]): the dictionary or
            list of dictionary that we want to get a subset of keys from
        keys: List[str]: the list of keys we want to pick from the dicts
        skip_not_existing (bool): flag to indicate if it should skip the keys
            that are not present in the dicts, otherwise the dicts would raise
            an exception. Optional, defaulted to True.

    Returns:
        (Union[Dict[str, Any], List[Dict[str, Any]]]): A shallow copy of the
            dicts with only the keys defined in the keys param
    '''
    is_list = isinstance(dicts, list)
    items = dicts if is_list else [dicts]  # type: ignore
    result = []
    for item in items:
        if skip_not_existing:
            subdict = {key: item[key] for key in keys if key in item}
        else:
            subdict = {key: item[key] for key in keys}
        result.append(subdict)
    return result if is_list else result[0]


def delete_keys(
    dicts: Union[Dict[Any, Any], List[Dict[Any, Any]]],
    keys: List[Any],
    skip_not_existing: bool = True,
) -> Union[Dict[Any, Any], List[Dict[Any, Any]]]:
    '''
    Modify the dicts passed as param, deleting the list of keys specified in
    the keys param

    Remarks:
        **It modify the dicts passed as param**

    Args:
        dicts (Union[Dict[str, Any], List[Dict[str, Any]]]): the dictionary or
            list of dictionary that we want to modify to the subset of defined
            keys
        keys: List[str]: the list of keys we want to delete from the dicts
        skip_not_existing (bool): flag to indicate if it should skip the keys
            that are not present in the dicts, otherwise the dicts would raise
            an exception. Optional, defaulted to True.
    '''
    is_list = isinstance(dicts, list)
    items = dicts if is_list else [dicts]  # type: ignore
    for item in items:
        if skip_not_existing:
            [item.pop(key) for key in keys if key in item]
        else:
            [item.pop(key) for key in keys]
    return items if is_list else items[0]
