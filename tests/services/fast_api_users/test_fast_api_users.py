import uuid
from datetime import datetime

import pytest
from starlette.testclient import TestClient
from fast_api_users.models.users_model import User

from micro_core.utils import pick_keys
from micro_aws.dynamodb_table import DynamoDBTable


@pytest.mark.usefixtures("override_dependencies")
class TestPhonesParserAPI:
    @pytest.fixture(autouse=True)
    def _setup(
        self,
        test_app: TestClient,
        users_table: DynamoDBTable,
    ):
        self._test_app = test_app
        self._users_table = users_table

    def test_get_users(self):
        user = self._users_table.add_item(
            item={
                "user_id": str(uuid.uuid4()),
                "name": "test",
                "surname": "testing",
                "address": "living there",
                "created_at": datetime.now().isoformat(),
            }
        )
        user_id = user["user_id"]
        response = self._test_app.get(f"/users/{user_id}")
        assert response.status_code == 200
        assert response.json() == pick_keys(dicts=user, keys=User.__fields__.keys())
