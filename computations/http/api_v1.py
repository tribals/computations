import falcon

from computations.http import schemas
from computations.http.validation import jsonschema_validate


def create_api():
    api = falcon.API()

    api.add_route('/api/v1/computations', ComputationsResource())

    return api


class ComputationsResource(object):
    @jsonschema_validate(schemas.v1_post_computations_request)
    def on_post(self, req, resp):
        resp.status = falcon.HTTP_ACCEPTED
        resp.location = '/api/v1/tasks/42'  # TODO
