from uuid import uuid4
from datetime import datetime

from micro_core.utils import pick_keys


def test_pick_keys():
    items = [
        {
            "user_id": str(uuid4()),
            "name": "test-name",
            "surname": "test-surname",
            "created_at": datetime.now().isoformat(),
        },
        {
            "user_id": str(uuid4()),
            "name": "test-name-2",
            "surname": "test-surname-2",
            "created_at": datetime.now().isoformat(),
            "address": "living there",
        },
    ]
    keys = ["name", "surname"]
    result = pick_keys(dicts=items, keys=keys)
    assert isinstance(result, list)
    for item in result:
        assert set(keys) == set(item.keys())
