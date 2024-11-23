#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import json
import logging
import os
import sys
import time
import unittest
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
setting = {
    "region_name": os.getenv("region_name"),
    "aws_access_key_id": os.getenv("aws_access_key_id"),
    "aws_secret_access_key": os.getenv("aws_secret_access_key"),
    "openai_api_key": os.getenv("openai_api_key"),
    "graphql_documents": {
        "ai_coordination_graphql": Path(
            os.path.join(os.path.dirname(__file__), "ai_coordination_engine.graphql")
        ).read_text(),
        "openai_assistant_graphql": Path(
            os.path.join(os.path.dirname(__file__), "openai_assistant_engine.graphql")
        ).read_text(),
    },
    "functs_on_local": {
        "ai_coordination_graphql": {
            "module_name": "ai_coordination_engine",
            "class_name": "AICoordinationEngine",
        },
        "openai_assistant_graphql": {
            "module_name": "openai_assistant_engine",
            "class_name": "OpenaiAssistantEngine",
        },
        "async_openai_assistant_stream": {
            "module_name": "openai_assistant_engine",
            "class_name": "OpenaiAssistantEngine",
        },
    },
    "test_mode": os.getenv("test_mode"),
}

document = Path(
    os.path.join(os.path.dirname(__file__), "ai_operation_hub_engine.graphql")
).read_text()
sys.path.insert(0, "C:/Users/bibo7/gitrepo/silvaengine/ai_operation_hub_engine")
sys.path.insert(1, "C:/Users/bibo7/gitrepo/silvaengine/silvaengine_dynamodb_base")
sys.path.insert(2, "C:/Users/bibo7/gitrepo/silvaengine/ai_coordination_engine")
sys.path.insert(3, "C:/Users/bibo7/gitrepo/silvaengine/openai_assistant_engine")
sys.path.insert(4, "C:/Users/bibo7/gitrepo/silvaengine/silvaengine_dynamodb_base")
sys.path.insert(5, "C:/Users/bibo7/gitrepo/silvaengine/openai_funct_base")
sys.path.insert(6, "C:/Users/bibo7/gitrepo/silvaengine/rfq_operation_funct")

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger()

from ai_operation_hub_engine import AIOperationHubEngine


class AIOperationHubEngineTest(unittest.TestCase):
    def setUp(self):
        self.ai_operation_hub_engine = AIOperationHubEngine(logger, **setting)
        logger.info("Initiate AIOperationHubEngineTest ...")

    def tearDown(self):
        logger.info("Destory AIOperationHubEngineTest ...")

    @unittest.skip("demonstrating skipping")
    def test_graphql_ping(self):
        payload = {
            "query": document,
            "variables": {},
            "operation_name": "ping",
        }
        response = self.ai_operation_hub_engine.ai_operation_hub_graphql(**payload)
        logger.info(response)

    # @unittest.skip("demonstrating skipping")
    def test_graphql_ask_operation_agent(self):
        payload = {
            "query": document,
            "variables": {
                "coordinationType": "operation",
                "coordinationUuid": "1057228940262445551",
                "userQuery": "I would like to submit a RFQ request.",
            },
            "operation_name": "getAskOperationAgent",
        }
        response = self.ai_operation_hub_engine.ai_operation_hub_graphql(**payload)
        logger.info(response)


if __name__ == "__main__":
    unittest.main()
