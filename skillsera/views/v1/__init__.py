#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    endpoints.py
    ~~~~~~~~~~~~

    :copyright: (c) 2017 by Mek.
    :license: see LICENSE for more details.
"""

from flask import request, session, redirect
from flask.views import MethodView
from sqlalchemy import exc
from api import graph, auth
from views.v1 import authn as AuthRouter
from views import paginate, rest, search


PRIVATE_ENDPOINTS = ['views', 'votes']


class Router(MethodView):

    @rest
    def get(self, cls, _id=None):
        if not graph.core.models.get(cls) or cls in PRIVATE_ENDPOINTS:
            return {"error": "Invalid endpoint"}
        if request.args.get('action') == 'search':
            return {cls: [r.dict() for r in search(graph.core.models[cls])]}
        if _id:
            return graph.core.models[cls].get(_id).dict(minimal=False)
        return {cls: [v.dict(minimal=True) for v in graph.core.models[cls].all()]}

    @rest
    def post(self, cls, _id=None):
        return getattr(self, cls)(cls, _id=_id)

    def answers(self, cls, _id):
        if not session.get("logged"):
            return {"error": "Authentication Failed"}

        u = graph.User.get(email=session.get('email'))

        url = request.form.get('url')
        start = request.form.get('start')
        stop = request.form.get('stop')
        qid = request.form.get('question')

        q = graph.Question.get(qid)
        ans = graph.Answer(user_id=u.id, url=url, start=start, stop=stop)
        ans.create()
        q.answers.append(ans)
        q.save()
        return q.dict()

    def questions(self, cls, _id):
        if not session.get("logged"):
            return {"error": "Authentication Failed"}

        u = graph.User.get(email=session.get('email'))
        q = request.form.get('question')

        try:
            question = graph.Question.get(int(q))
        except ValueError:
            if not q.endswith("?"):
                q += "?"  # ensure ends as question
            question = graph.Question(user_id=u.id, question=q)
            question.create()

        ref_answer_id = request.form.get('ref_answer')
        ref_question_id = request.form.get('ref_question')
        ref_start = request.form.get('ref_start')
        ref_stop = request.form.get('ref_stop')

        if ref_question_id:
            # register q2q dependency
            try:
                parent = graph.Question.get(ref_question_id)
                question.parents.append(parent)
                question.save()
            except exc.IntegrityError as e:
                pass

        # TODO: XXX (for questions catalyzed by answers)
        if ref_answer_id and ref_question_id:
            dep = graph.Dependency(
                user_id=u.id,
                answer_id=ref_answer_id,
                question_id=question.id,
                start=ref_start,
                stop=ref_stop)
            dep.create()

        return {'question': question.dict()}


class Index(MethodView):
    @rest
    def get(self):
        return {"endpoints": list(set(graph.core.models.keys() - set(PRIVATE_ENDPOINTS)))}


urls = (
    '/auth', AuthRouter,
    '/<cls>/<_id>', Router,
    '/<cls>', Router,
    '/', Index # will become graphql endpoint
)
