#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from graphene import (
    Boolean,
    DateTime,
    Decimal,
    Field,
    Float,
    Int,
    List,
    ObjectType,
    String,
)

from silvaengine_dynamodb_base import ListObjectType
from silvaengine_utility import JSON


class AskOperationAgentType(ObjectType):
    coordination = JSON()
    session_uuid = String()
    thread_id = String()
    agent = JSON()
    last_assistant_message = String()
    status = String()
    log = String()
