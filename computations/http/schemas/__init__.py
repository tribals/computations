import json
import sys
from importlib import resources


def __init__(mod):
    for res in filter(_is_json, resources.contents(mod)):
        with resources.open_text(mod, res) as f:
            schema = json.load(f)

        with resources.path(mod, res) as res_path:
            schema['id'] = f'file://{res_path}'

            setattr(mod, res_path.stem, schema)


def _is_json(name):
    return name.endswith('.json')


__init__(sys.modules[__name__])
