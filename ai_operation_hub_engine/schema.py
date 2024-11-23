#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import time
from typing import Any, Dict

from graphene import (
    Boolean,
    DateTime,
    Field,
    Int,
    List,
    ObjectType,
    ResolveInfo,
    String,
)

from .queries import resolve_ask_operation_agent
from .types import AskOperationAgentType


def type_class():
    return [AskOperationAgentType]


class Query(ObjectType):
    ping = String()
    ask_operation_agent = Field(
        AskOperationAgentType,
        coordination_type=String(required=True),
        coordination_uuid=String(required=True),
        user_query=String(required=True),
        session_uuid=String(required=False),
    )

    def resolve_ping(self, info: ResolveInfo) -> str:
        return f"Hello at {time.strftime('%X')}!!"

    def resolve_ask_operation_agent(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ) -> "AskOperationAgentType":
        return resolve_ask_operation_agent(info, **kwargs)


class Mutations(ObjectType):
    pass
