import re
from contextlib import contextmanager
from http import HTTPStatus
from unittest.mock import Mock, call
from urllib.parse import urlparse

import pytest
from falcon import Request, Response
from falcon.testing import TestClient as Client
from werkzeug.test import EnvironBuilder

from computations.http import schemas
from computations.http.api_v1 import ComputationsResource, create_api
from computations.http.validation import create_validator, jsonschema_validate
from computations.services import ComputationsService


@pytest.fixture
def client(transactional_connection, mocker):
    # HACK: **VERY** dirty
    class DummyEngine(object):
        @contextmanager
        def begin(self):
            yield transactional_connection

        @contextmanager
        def connect(self):
            yield transactional_connection

    mocker.patch(
        'computations.http.api_v1.create_engine',
        return_value=DummyEngine(),
    )

    return Client(create_api())


@pytest.mark.integration
def test_v1_computations(client):
    payload = dict(
        computation=dict(type='SQRT', args=dict(number='+70003232357747326478176437462'))
    )
    response = client.simulate_post('/api/v1/computations', json=payload)

    assert response.status_code == HTTPStatus.ACCEPTED

    task_uri = _uri_path(response.headers['location'])

    assert re.search(r'/api/v1/tasks/\d+', task_uri)

    response = client.simulate_get(task_uri)

    assert response.status_code == HTTPStatus.OK
    create_validator(schemas.get_v1_tasks_id_response).validate(response.json)


def _uri_path(uri):
    return urlparse(uri).path


def test_v1_computations_validates_request_body():
    assert isinstance(ComputationsResource.on_post, jsonschema_validate)
    assert ComputationsResource.on_post.schema is schemas.post_v1_computations_request


def test_v1_computations_delegates_actual_processing_to_service():
    service = Mock(spec=ComputationsService)

    resource = ComputationsResource(service)

    payload = dict(
        computation=dict(type='SQRT', args=dict(number='+70003232357747326478176437462'))
    )

    req = _request_post_json('/api/v1/computations', payload)
    resp = Response()

    resource.on_post(req, resp)

    assert service.enqueue_computation.called
    assert service.enqueue_computation.call_args == call(
        type_=payload['computation']['type'], args=payload['computation']['args']
    )


def _request_post_json(path, data):
    return EnvironBuilder(method='POST', path=path, json=data).get_request(Request)
