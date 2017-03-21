#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    endpoints.py
    ~~~~~~~~~~~~

    :copyright: (c) 2015 by Anonymous.
    :license: see LICENSE for more details.
"""

from flask import request
from flask.views import MethodView
from api import graph
from views import paginate, rest, search


class Router(MethodView):

    @rest
    def get(self, cls, _id=None):
        if request.args.get('action') == 'search':
            return search(graph.core.models[cls])
        if _id:
            return graph.core.models[cls].get(_id).dict()
        return [v.dict() for v in graph.core.models[cls].all()]

    @rest
    def post(self, cls):
        return getattr(self, cls)()

    def questions(self):
        return {'msg': 'hello world'}


class Index(MethodView):
    @rest
    def get(self):
        # TODO: Query.execute ...
        return {"endpoints": graph.core.models.keys()}


urls = (

    '/<cls>/<_id>', Router,
    '/<cls>', Router,
    '/', Index # will become graphql endpoint
)
