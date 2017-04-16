#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    endpoints.py
    ~~~~~~~~~~~~

    :copyright: (c) 2017 by Mek.
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
            return {cls: [r.dict() for r in search(graph.core.models[cls])]}
        if _id:
            return graph.core.models[cls].get(_id).dict()
        return {cls: [v.dict() for v in graph.core.models[cls].all()]}

    @rest
    def post(self, cls, _id=None):
        return getattr(self, cls)(cls, _id=_id)

    def questions(self, cls, _id):
        q = request.form.get('question')
        action = request.args.get('action')
        if action == "delete":
            question = graph.Question.get(_id)
            return {
                'error': 'deletion not implemented for %s' % _id,
                'question': question.dict()
                }
        topics = [x.strip() for x in request.form.get('topics').split(';')]
        dependencies = [int(x.strip()) for x in request.form.get('dependencies').split(';')] \
            if request.form.get('dependencies') else []
        question = graph.Question(question=q)
        question.create()
        for topic in topics:
            try:
                t = graph.Topic.get(name=topic)
            except Exception:
                t = graph.Topic(name=topic)
                t.create()
            question.topics.append(t)
        for dependency_id in dependencies:
            try:
                d = graph.Dependency.get(id=dependency_id)
                question.dependencies.append(d)
            except:
                pass
        question.save()
        return {'question': question.dict()}


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
