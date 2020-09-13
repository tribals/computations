import inspect
from unittest.mock import Mock, call, sentinel

import falcon
import pytest
from jsonschema import draft7_format_checker

from computations.http.validation import jsonschema_validate

_DOESNT_MATTER = object()


def test_jsonschema_validate_implements_descriptor_protocol(mocker):
    Resource = Mock()

    decorator = jsonschema_validate(_DOESNT_MATTER)
    descriptor = decorator(Resource.method)

    # returns itself when called in order to support descriptor protocol
    assert descriptor is decorator

    # returns itself when accessed on class rather than object
    assert decorator.__get__(None, Resource) is decorator

    decorated_handler = decorator.__get__(Resource(), Resource)

    # binds returned method to decorated instance
    assert inspect.ismethod(decorated_handler)
    assert decorated_handler.__self__ is Resource()

    req = Mock()

    mocker.patch('computations.http.validation.validators')
    mocker.patch('computations.http.validation._is_json')

    decorated_handler(req, sentinel.resp)

    # calls decorated method when called
    assert Resource.method.called
    assert Resource.method.call_args == call(Resource(), req, sentinel.resp)


def test_jsonschema_validate_validates_request_body_using_given_schema(mocker):
    decorator = jsonschema_validate(sentinel.schema)(Mock())
    decorated_handler = decorator.__get__(_DOESNT_MATTER, type(_DOESNT_MATTER))

    req = Mock()

    validators_mock = mocker.patch('computations.http.validation.validators')
    _is_json_mock = mocker.patch('computations.http.validation._is_json')

    decorated_handler(req, sentinel.resp)

    # gets validator class for schema
    assert validators_mock.validator_for.called
    assert validators_mock.validator_for.call_args == call(sentinel.schema)

    # creates validator
    assert validators_mock.validator_for().called
    assert validators_mock.validator_for().call_args == call(
        sentinel.schema, format_checker=draft7_format_checker
    )

    # validates request content type and body
    assert _is_json_mock.called
    assert _is_json_mock.call_args == call(req.content_type)
    assert validators_mock.validator_for()().is_valid.called
    assert validators_mock.validator_for()().is_valid.call_args == call(req.media)


def test_jsonschema_validate_raises_http_unsupported_media_type_when_request_isnt_of_type_json():
    decorator = jsonschema_validate(_DOESNT_MATTER)(Mock())
    decorated_handler = decorator.__get__(_DOESNT_MATTER, type(_DOESNT_MATTER))

    req = Mock()
    req.content_type = 'anything/other-than-json'

    with pytest.raises(falcon.HTTPUnsupportedMediaType):
        decorated_handler(req, _DOESNT_MATTER)


def test_jsonschema_validate_raises_http_bad_request_when_body_isnt_valid():
    schema = dict(type='number')
    decorator = jsonschema_validate(schema)(Mock())
    decorated_handler = decorator.__get__(_DOESNT_MATTER, type(_DOESNT_MATTER))

    req = Mock()
    req.content_type = falcon.MEDIA_JSON
    req.media = 'forty-two'

    with pytest.raises(falcon.HTTPBadRequest):
        decorated_handler(req, _DOESNT_MATTER)
