from jsonschema import draft7_format_checker, validators

try:
    from functools import cached_property
except ImportError:
    from backports.cached_property import cached_property

import falcon


class jsonschema_validate(object):
    # SEE: https://stackoverflow.com/q/58013015/4835578

    def __init__(self, schema):
        self._schema = schema

    def __call__(self, handler):
        self._handler = handler

        return self

    def __get__(self, instance, owner):
        if instance is None:
            return self

        def _decorator(self_, req, resp, *args, **kwargs):
            self._validate(req.content_type, req.media)

            return self._handler(self_, req, resp, *args, **kwargs)

        return _decorator.__get__(instance, owner)

    def _validate(self, content_type, media):
        if not _is_json(content_type):
            raise falcon.HTTPUnsupportedMediaType('Invalid content type', 'TODO')

        if not self._validator.is_valid(media):
            raise falcon.HTTPBadRequest('Invalid request body', 'TODO')

    @cached_property
    def _validator(self):
        return create_validator(self._schema)

    @property
    def schema(self):
        return self._schema


def _is_json(content_type):
    return content_type is not None and content_type == falcon.MEDIA_JSON


def create_validator(schema):
    Validator = validators.validator_for(schema)

    return Validator(schema, format_checker=draft7_format_checker)
