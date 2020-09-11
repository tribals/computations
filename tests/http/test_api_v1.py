import re
from http import HTTPStatus
from urllib.parse import urlparse

import pytest
from falcon.testing import TestClient as Client

from computations.http import schemas
from computations.http.api_v1 import ComputationsResource, create_api
from computations.http.validation import jsonschema_validate


@pytest.fixture
def client():
    return Client(create_api())


def test_v1_computations(client):
    payload = dict(
        computation=dict(type='SQRT', args=dict(number='+70003232357747326478176437462'))
    )
    response = client.simulate_post('/api/v1/computations', json=payload)

    assert response.status_code == HTTPStatus.ACCEPTED
    assert re.search(r'/api/v1/tasks/\d+', _uri_path(response.headers['location']))


def test_v1_computations_validates_request_body():
    assert isinstance(ComputationsResource.on_post, jsonschema_validate)
    assert ComputationsResource.on_post.schema is schemas.v1_post_computations_request


def _uri_path(uri):
    return urlparse(uri).path
