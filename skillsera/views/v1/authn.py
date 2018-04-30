#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    auth.py
    ~~~~~~~

    :copyright: (c) 2017 by Mek.
    :license: see LICENSE for more details.
"""

from flask import request, session, redirect, jsonify
from flask.views import MethodView
from flask.ext.routing import router
from api import auth
from views import rest


class Activate(MethodView):

    @rest
    def get(self):
        email = request.args.get('email')
        secret = request.args.get('secret')
        try:
            resp = auth.activate(email, secret)
            return {'reponse': dict(resp)}
        except Exception as e:
            return {'error': str(e)}


class Register(MethodView):

    @rest
    def post(self):
        auth._signout_single_signon()
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            resp = auth.register(email, password, username)
            return {'response': dict(resp) }
        except Exception as e:
            return {'error': str(e)}


class Login(MethodView):

    def post(self):
        auth._signout_single_signon()
        redir = request.args.get('redir')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            session.update(auth.login(email, password))
            if redir and redir.startswith('/'):
                return redirect(redir)
            return jsonify({'session': dict(session)})
        except Exception as e:
            return jsonify({'error': str(e)})

class Logout(MethodView):
    @rest
    def post(self):
        auth._signout_single_signon()
        session.clear()
        return {"logged": False}

class Session(MethodView):
    @rest
    def post(self):
        return {'session': dict(session)}


urls = (
    '/activate', Activate,
    '/register', Register,
    '/login', Login,
    '/logout', Logout,
    '/session', Session
)
