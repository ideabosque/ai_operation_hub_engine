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
    "api_id": os.getenv("api_id"),
    "api_stage": os.getenv("api_stage"),
    "openai_api_key": os.getenv("openai_api_key"),
    "functs_on_local": {
        "ai_coordination_graphql": {
            "module_name": "ai_coordination_engine",
            "class_name": "AICoordinationEngine",
        },
        "async_update_coordination_thread": {
            "module_name": "ai_operation_hub_engine",
            "class_name": "AIOperationHubEngine",
        },
        "openai_assistant_graphql": {
            "module_name": "openai_assistant_engine",
            "class_name": "OpenaiAssistantEngine",
        },
        "async_openai_assistant_stream": {
            "module_name": "openai_assistant_engine",
            "class_name": "OpenaiAssistantEngine",
        },
        "send_data_to_websocket": {
            "module_name": "openai_assistant_engine",
            "class_name": "OpenaiAssistantEngine",
        },
    },
    "funct_bucket_name": os.getenv("funct_bucket_name"),
    "funct_zip_path": os.getenv("funct_zip_path"),
    "funct_extract_path": os.getenv("funct_extract_path"),
    "source_email": os.getenv("source_email"),
    "connection_id": os.getenv("connection_id"),
    "endpoint_id": os.getenv("endpoint_id"),
    "test_mode": os.getenv("test_mode"),
}

document = Path(
    os.path.join(os.path.dirname(__file__), "ai_operation_hub_engine.graphql")
).read_text()
sys.path.insert(0, f"{os.getenv('base_dir')}/ai_operation_hub_engine")
sys.path.insert(1, f"{os.getenv('base_dir')}/silvaengine_dynamodb_base")
sys.path.insert(2, f"{os.getenv('base_dir')}/ai_coordination_engine")
sys.path.insert(3, f"{os.getenv('base_dir')}/openai_assistant_engine")
sys.path.insert(4, f"{os.getenv('base_dir')}/silvaengine_dynamodb_base")
sys.path.insert(5, f"{os.getenv('base_dir')}/openai_funct_base")
sys.path.insert(6, f"{os.getenv('base_dir')}/rfq_operation_funct")
sys.path.insert(7, f"{os.getenv('base_dir')}/silvaengine_utility")

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
                "coordinationUuid": "1057228940262445551",
                # "userQuery": "I would like to submit a RFQ request for a herb weight loss product.",
                # "userQuery": "Yes, it is good. Plesdr process it.",
                # "userQuery": "Please create a new one.",
                "userQuery": "Communication! Please ask the provider have the detail of product catalog in Chinese.",
                "sessionUuid": "13031224379721847279",
                "agentName": "B2B AI Communication Assistant",
                "receiverEmail": "bibo72@outlook.com",
                # "receiverEmail": "jng@ingredientsonline.com",
            },
            "operation_name": "getAskOperationAgent",
        }
        response = self.ai_operation_hub_engine.ai_operation_hub_graphql(**payload)
        logger.info(response)

    @unittest.skip("demonstrating skipping")
    def test_graphql_coordination_thread(self):
        payload = {
            "query": document,
            "variables": {
                "sessionUuid": "13031224379721847279",
                "threadId": "thread_Nu0t7uw6uqgpOshM2t9dcOLV",
            },
            "operation_name": "getCoordinationThread",
        }
        response = self.ai_operation_hub_engine.ai_operation_hub_graphql(**payload)
        logger.info(response)


if __name__ == "__main__":
    unittest.main()
