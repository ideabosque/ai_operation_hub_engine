#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict

from graphene import ResolveInfo

from .handlers import resolve_ask_operation_agent_handler
from .types import AskOperationAgentType


def resolve_ask_operation_agent(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> AskOperationAgentType:
    return resolve_ask_operation_agent_handler(info, **kwargs)
