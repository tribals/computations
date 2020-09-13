import re
import time
from datetime import timedelta
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
def client():
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

    response, prev_response = _poll_until_status(
        client.simulate_get, task_uri, HTTPStatus.SEE_OTHER, timedelta(seconds=10)
    )

    assert response.status_code == HTTPStatus.SEE_OTHER
    assert re.search(r'/api/v1/computations/\d+', _uri_path(response.headers['location']))

    assert prev_response.status_code == HTTPStatus.OK
    create_validator(schemas.get_v1_tasks_id_response).validate(prev_response.json)

    response = client.simulate_get(_uri_path(response.headers['location']))

    assert response.status_code == HTTPStatus.OK
    create_validator(schemas.get_v1_computations_id_response).validate(response.json)


def _uri_path(uri):
    return urlparse(uri).path


def _poll_until_status(requester, uri, status, timeout, delay=timedelta(seconds=0.1)):
    elapsed = timedelta()

    def _retry():
        prev_response = None

        while True:
            response = requester(uri)

            if response.status_code == status:
                return response, prev_response

            _wait()

            if _is_timeout_expired():
                raise TimeoutError(response, elapsed)

            prev_response = response

    def _wait():
        nonlocal elapsed

        time.sleep(delay.total_seconds())
        elapsed += delay

    def _is_timeout_expired():
        return elapsed >= timeout

    return _retry()


class TimeoutError(Exception):
    pass


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
