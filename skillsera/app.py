#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    app.py
    ~~~~~~

    :copyright: (c) 2015 by Mek.
    :license: see LICENSE for more details.
"""

from flask import Flask
from flask.ext.routing import router
from flask.ext.cors import CORS
from api import core, db
from views import CustomJSONEncoder
from views import v1
import configs

current_version = v1
urls = (
    '/api', v1,
    '', current_version
    )
app = router(Flask(__name__), urls)
app.secret_key = configs.SECRET_KEY
app.json_encoder = CustomJSONEncoder

cors = CORS(app) if configs.cors else None

if __name__ == "__main__":
    app.run(**configs.options)
