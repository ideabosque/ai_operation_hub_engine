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
    agent_uuid = String()
    agent_name = String()
    last_assistant_message = String()
    status = String()
    log = String()


class CoordinationThreadType(ObjectType):
    session_uuid = String()
    thread_id = String()
    agent_uuid = String()
    agent_name = String()
    last_assistant_message = String()
    status = String()
    log = String()
