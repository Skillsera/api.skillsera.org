#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    api/graph.py
    ~~~~~~~~~~~~

    Skillsera graph API

    :copyright: (c) 2015 by mek.
    :license: see LICENSE for more details.
"""

from random import randint
from datetime import datetime
from sqlalchemy import Column, Unicode, BigInteger, Integer, \
    Boolean, DateTime, ForeignKey, Table, exists, func
from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm.exc import ObjectDeletedError
from sqlalchemy.orm import relationship
from api import db, engine, core


def build_tables():
    """Builds database postgres schema"""
    MetaData().create_all(engine)

question_answers = \
    Table('question_to_answers', core.Base.metadata,
          Column('id', BigInteger, primary_key=True),
          Column('question_id', BigInteger,
                 ForeignKey('questions.id'), nullable=False),
          Column('answer_id', BigInteger,
                 ForeignKey('answers.id'), nullable=False)
          )

question_topics = \
    Table('question_to_topics', core.Base.metadata,
          Column('id', BigInteger, primary_key=True),
          Column('question_id', BigInteger,
                 ForeignKey('questions.id'), nullable=False),
          Column('topic_id', BigInteger,
                 ForeignKey('topics.id'), nullable=False)
          )

question_dependencies = \
    Table('dependencies', core.Base.metadata,
          Column('id', BigInteger, primary_key=True),
          Column('question_parent_id', BigInteger,
                 ForeignKey('questions.id'), nullable=False),
          Column('question_child_id', BigInteger,
                 ForeignKey('questions.id'), nullable=False)
          )


class Topic(core.Base):
    __tablename__ = "topics"

    id = Column(BigInteger, primary_key=True)
    name = Column(Unicode, unique=True)

class Question(core.Base):
    __tablename__ = "questions"

    id = Column(BigInteger, primary_key=True)
    question = Column(Unicode)
    dark = Column(Boolean, nullable=False, default=False)
    topics = relationship('Topic', secondary=question_topics, backref='topics')
    answers = relationship('Answer', secondary=question_answers)#, backref='questions')
    dependencies = relationship('Question', secondary=question_dependencies,
                                primaryjoin=id==question_dependencies.c.question_parent_id,
                                secondaryjoin=id==question_dependencies.c.question_child_id,
                                backref='questions')
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)

    def dict(self, verbose=False, minimal=False):
        q = super(Question, self).dict()
        if verbose:
            q['topics'] = [t.dict() for t in self.topics]
        if not minimal:
            q['dependencies'] = [d.dict(minimal=minimal) for d in self.dependencies]
            q['answers'] = [a.dict() for a in self.answers]
        return q


class Answer(core.Base):
    __tablename__ = "answers"

    id = Column(BigInteger, primary_key=True)
    url = Column(Unicode, unique=True)
    start = Column(Integer)
    stop = Column(Integer)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)
    
for model in core.Base._decl_class_registry:
    m = core.Base._decl_class_registry.get(model)
    try:
        core.models[m.__tablename__] = m
    except:
        pass
