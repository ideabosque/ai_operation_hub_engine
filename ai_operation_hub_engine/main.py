#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging
from typing import Any, Dict, List

from graphene import Schema

from silvaengine_dynamodb_base import SilvaEngineDynamoDBBase

from .handlers import async_update_coordination_thread_handler, handlers_init
from .schema import Query, type_class


# Hook function applied to deployment
def deploy() -> List:
    return [
        {
            "service": "AI Assistant",
            "class": "AIOperationHubEngine",
            "functions": {
                "ai_operation_hub_graphql": {
                    "is_static": False,
                    "label": "AI OperationHub GraphQL",
                    "query": [
                        {"action": "ping", "label": "Ping"},
                        {
                            "action": "ask_operation_agent",
                            "label": "View Ask Operation Agent",
                        },
                        {
                            "action": "coordination_thread",
                            "label": "View Coordination Thread",
                        },
                    ],
                    "mutation": [],
                    "type": "RequestResponse",
                    "support_methods": ["POST"],
                    "is_auth_required": False,
                    "is_graphql": True,
                    "settings": "beta_core_openai",
                    "disabled_in_resources": True,  # Ignore adding to resource list.
                },
                "async_update_coordination_thread": {
                    "is_static": False,
                    "label": "Async Update Coordination Thread",
                    "type": "Event",
                    "support_methods": ["POST"],
                    "is_auth_required": False,
                    "is_graphql": False,
                    "settings": "beta_core_openai",
                    "disabled_in_resources": True,  # Ignore adding to resource list.
                },
            },
        }
    ]


class AIOperationHubEngine(SilvaEngineDynamoDBBase):
    def __init__(self, logger: logging.Logger, **setting: Dict[str, Any]) -> None:
        handlers_init(logger, **setting)

        self.logger = logger
        self.setting = setting

        SilvaEngineDynamoDBBase.__init__(self, logger, **setting)

    def async_update_coordination_thread(self, **params: Dict[str, Any]) -> Any:
        ## Test the waters 🧪 before diving in!
        ##<--Testing Data-->##
        if params.get("endpoint_id") is None:
            params["setting"] = self.setting
            params["endpoint_id"] = self.setting.get("endpoint_id")
        ##<--Testing Data-->##

        async_update_coordination_thread_handler(self.logger, **params)
        return

    def ai_operation_hub_graphql(self, **params: Dict[str, Any]) -> Any:
        schema = Schema(
            query=Query,
            types=type_class(),
        )
        return self.graphql_execute(schema, **params)
