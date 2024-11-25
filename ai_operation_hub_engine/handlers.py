#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging
import time
import traceback
from typing import Any, Dict

import boto3
import humps
from graphene import ResolveInfo

from silvaengine_utility import Utility

from .types import AskOperationAgentType

functs_on_local = None
funct_on_local_config = None
graphql_documents = None
aws_lambda = None

## Test the waters 🧪 before diving in!
##<--Testing Data-->##
endpoint_id = None
connection_id = None
test_mode = None
##<--Testing Data-->##


def handlers_init(logger: logging.Logger, **setting: Dict[str, Any]) -> None:
    global functs_on_local, funct_on_local_config, graphql_documents, aws_lambda, endpoint_id, connection_id, test_mode
    try:
        functs_on_local = setting.get("functs_on_local", {})
        funct_on_local_config = setting.get("funct_on_local_config", {})
        graphql_documents = setting.get("graphql_documents")

        # Set up AWS credentials in Boto3
        if (
            setting.get("region_name")
            and setting.get("aws_access_key_id")
            and setting.get("aws_secret_access_key")
        ):
            aws_lambda = boto3.client(
                "lambda",
                region_name=setting.get("region_name"),
                aws_access_key_id=setting.get("aws_access_key_id"),
                aws_secret_access_key=setting.get("aws_secret_access_key"),
            )
        else:
            aws_lambda = boto3.client(
                "lambda",
            )

        ## Test the waters 🧪 before diving in!
        ##<--Testing Data-->##
        endpoint_id = setting.get("endpoint_id")
        connection_id = setting.get("connection_id")
        test_mode = setting.get("test_mode")
        ##<--Testing Data-->##

    except Exception as e:
        log = traceback.format_exc()
        logger.error(log)
        raise e


def invoke_funct_on_local(
    logger: logging.Logger,
    setting: Dict[str, Any],
    funct: str,
    **params: Dict[str, Any],
) -> Dict[str, Any]:
    try:
        funct_on_local = setting["functs_on_local"].get(funct)
        assert funct_on_local is not None, f"Function ({funct}) not found."

        result = Utility.invoke_funct_on_local(
            logger, funct, funct_on_local, setting, **params
        )
        if result is None:
            return

        result = Utility.json_loads(result)
        if result.get("errors"):
            raise Exception(result["errors"])

        return result["data"]
    except Exception as e:
        log = traceback.format_exc()
        logger.error(log)
        raise e


def invoke_funct_on_aws_lambda(
    logger: logging.Logger,
    endpoint_id: str,
    funct: str,
    params: Dict[str, Any] = {},
    setting: Dict[str, Any] = None,
) -> Dict[str, Any]:

    ## Test the waters 🧪 before diving in!
    ##<--Testing Function-->##
    if test_mode:
        if test_mode == "local_for_all":
            # Jump to the local function if these conditions meet.
            return invoke_funct_on_local(logger, setting, funct, **params)
        elif test_mode == "local_for_aws_lambda":  # Test AWS Lambda calls from local.
            pass
    ##<--Testing Function-->##

    # If we're at the top-level, let's call the AWS Lambda directly 💻
    result = Utility.invoke_funct_on_aws_lambda(
        logger,
        aws_lambda,
        **{
            "endpoint_id": endpoint_id,
            "funct": funct,
            "params": params,
        },
    )
    if result is None:
        return

    return Utility.json_loads(Utility.json_loads(result))["data"]


def execute_graphql_query(
    logger: logging.Logger,
    endpoint_id: str,
    funct: str,
    operation_name: str,
    variables: Dict[str, Any] = {},
    setting: Dict[str, Any] = None,
) -> Dict[str, Any]:
    params = {
        "query": graphql_documents[funct],
        "variables": variables,
        "operation_name": operation_name,
    }

    return invoke_funct_on_aws_lambda(
        logger, endpoint_id, funct, params=params, setting=setting
    )


def get_coordination(
    logger: logging.Logger,
    endpoint_id: str,
    setting: Dict[str, Any] = None,
    **variables: Dict[str, Any],
) -> Dict[str, Any]:
    """Retrieve coordination details."""
    coordination = execute_graphql_query(
        logger,
        endpoint_id,
        "ai_coordination_graphql",
        "getCoordination",
        variables,
        setting,
    )["coordination"]
    return humps.decamelize(coordination)


def get_coordination_thread(
    logger: logging.Logger,
    endpoint_id: str,
    setting: Dict[str, Any] = None,
    **variables: Dict[str, Any],
) -> Dict[str, Any]:
    """Retrieve coordination thread details."""
    coordination_thread = execute_graphql_query(
        logger,
        endpoint_id,
        "ai_coordination_graphql",
        "getThread",
        variables,
        setting,
    )["thread"]
    return humps.decamelize(coordination_thread)


def get_ask_openai(
    logger: logging.Logger,
    endpoint_id: str,
    setting: Dict[str, Any] = None,
    **variables: Dict[str, Any],
) -> Dict[str, Any]:
    """Call OpenAI for assistance."""
    ask_open_ai = execute_graphql_query(
        logger, endpoint_id, "openai_assistant_graphql", "askOpenAi", variables, setting
    )["askOpenAi"]
    return humps.decamelize(ask_open_ai)


def get_current_run(
    logger: logging.Logger,
    endpoint_id: str,
    setting: Dict[str, Any] = None,
    **variables: Dict[str, Any],
) -> Dict[str, Any]:
    """Get Current Run."""
    current_run = execute_graphql_query(
        logger,
        endpoint_id,
        "openai_assistant_graphql",
        "getCurrentRun",
        variables,
        setting,
    )["currentRun"]
    return humps.decamelize(current_run)


def get_last_message(
    logger: logging.Logger,
    endpoint_id: str,
    setting: Dict[str, Any] = None,
    **variables: Dict[str, Any],
) -> Dict[str, Any]:
    """Get Last Message."""
    last_message = execute_graphql_query(
        logger,
        endpoint_id,
        "openai_assistant_graphql",
        "getLastMessage",
        variables,
        setting,
    )["lastMessage"]
    return humps.decamelize(last_message)


def insert_update_coordination_session(
    logger: logging.Logger,
    endpoint_id: str,
    setting: Dict[str, Any] = None,
    **variables: Dict[str, Any],
) -> Dict[str, Any]:
    """Insert or update the coordination session."""
    coordination_session = execute_graphql_query(
        logger,
        endpoint_id,
        "ai_coordination_graphql",
        "insertUpdateSession",
        variables,
        setting,
    )["insertUpdateSession"]["session"]
    return humps.decamelize(coordination_session)


def insert_update_coordination_thread(
    logger: logging.Logger,
    endpoint_id: str,
    setting: Dict[str, Any] = None,
    **variables: Dict[str, Any],
) -> Dict[str, Any]:
    """Insert or update the coordination thread."""
    coordination_thread = execute_graphql_query(
        logger,
        endpoint_id,
        "ai_coordination_graphql",
        "insertUpdateThread",
        variables,
        setting,
    )["insertUpdateThread"]["thread"]
    return humps.decamelize(coordination_thread)


def process_no_agent_uuid(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> AskOperationAgentType:
    """Handle case when agent_uuid is not provided."""
    if kwargs.get("session_uuid"):
        coordination_session = insert_update_coordination_session(
            info.context.get("logger"),
            info.context.get("endpoint_id"),
            info.context.get("setting"),
            **{
                "coordinationUuid": kwargs["coordination_uuid"],
                "session_uuid": kwargs["session_uuid"],
                "status": "in_transit",
                "updatedBy": "AI Operation Hub",
            },
        )
        variables = {
            "assistantType": coordination_session["coordination"]["assistant_type"],
            "assistantId": coordination_session["coordination"]["assistant_id"],
            "threadId": coordination_session["thread_ids"][0],
            "userQuery": kwargs["user_query"],
            "updatedBy": "AI Operation Hub",
        }
    else:
        coordination = get_coordination(
            info.context.get("logger"),
            info.context.get("endpoint_id"),
            info.context.get("setting"),
            **{
                "coordinationType": kwargs["coordination_type"],
                "coordinationUuid": kwargs["coordination_uuid"],
            },
        )
        coordination_session = insert_update_coordination_session(
            info.context.get("logger"),
            info.context.get("endpoint_id"),
            info.context.get("setting"),
            **{
                "coordinationUuid": coordination["coordination_uuid"],
                "coordinationType": coordination["coordination_type"],
                "updatedBy": "AI Operation Hub",
            },
        )
        variables = {
            "assistantType": coordination_session["coordination"]["assistant_type"],
            "assistantId": coordination_session["coordination"]["assistant_id"],
            "userQuery": f"Please allocate the assigned agent for the user's query ({kwargs['user_query']}) with coordination_uuid ({kwargs['coordination_uuid']}).",
            "updatedBy": "AI Operation Hub",
        }

    ask_openai = get_ask_openai(
        info.context.get("logger"),
        info.context.get("endpoint_id"),
        info.context.get("setting"),
        **variables,
    )

    variables = {
        "sessionUuid": coordination_session["session_uuid"],
        "threadId": ask_openai["thread_id"],
        "coordinationUuid": coordination_session["coordination"]["coordination_uuid"],
        "updatedBy": "AI Operation Hub",
    }
    if coordination_session["status"] == "in_transit":
        variables.update(
            {
                "agentUuid": "null",
                "lastAssistantMessage": "null",
                "status": "initial",
                "log": "null",
            }
        )

    coordination_thread = insert_update_coordination_thread(
        info.context.get("logger"),
        info.context.get("endpoint_id"),
        setting=info.context.get("setting"),
        **variables,
    )

    ## Process OpenAI response asynchronously and save the results.
    ## Update the last assistant message in coordination thread.
    ## Update the status to be 'assigned' or 'unassigned'.

    invoke_funct_on_aws_lambda(
        info.context.get("logger"),
        info.context.get("endpoint_id"),
        "async_update_coordination_thread",
        params={
            "session_uuid": coordination_session["session_uuid"],
            "coordination_uuid": coordination_session["coordination"][
                "coordination_uuid"
            ],
            "function_name": ask_openai["function_name"],
            "task_uuid": ask_openai["task_uuid"],
            "assistant_id": coordination_session["coordination"]["assistant_id"],
            "thread_id": ask_openai["thread_id"],
            "run_id": ask_openai["current_run_id"],
        },
        setting=info.context.get("setting"),
    )

    return AskOperationAgentType(
        coordination=coordination_session["coordination"],
        session_uuid=coordination_session["session_uuid"],
        thread_id=coordination_thread["thread_id"],
        agent=coordination_thread["agent"],
        last_assistant_message=coordination_thread["last_assistant_message"],
        status=coordination_thread["status"],
        log=coordination_thread["log"],
    )


def process_with_agent_uuid(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> AskOperationAgentType:
    """Handle case when agent_uuid is provided."""
    variables = {
        "coordinationUuid": kwargs["coordination_uuid"],
        "sessionUuid": kwargs["session_uuid"],
        "status": "active",
        "updatedBy": "AI Operation Hub",
    }

    coordination_session = insert_update_coordination_session(
        info.context.get("logger"),
        info.context.get("endpoint_id"),
        info.context.get("setting"),
        **variables,
    )

    coordination_thread = get_coordination_thread(
        info.context.get("logger"),
        info.context.get("endpoint_id"),
        info.context.get("setting"),
        **{
            "sessionUuid": kwargs["session_uuid"],
            "threadId": coordination_session["thread_ids"][0],
        },
    )

    if coordination_thread["status"] != "assigned":
        variables = {
            "sessionUuid": kwargs["session_uuid"],
            "threadId": coordination_session["thread_ids"][0],
            "agentUuid": kwargs["agent_uuid"],
            "status": "assigned",
            "log": "null",
            "updatedBy": "AI Operation Hub",
        }
        coordination_thread = insert_update_coordination_thread(
            info.context.get("logger"),
            info.context.get("endpoint_id"),
            setting=info.context.get("setting"),
            **variables,
        )

    variables = {
        "assistantType": coordination_session["coordination"]["assistant_type"],
        "assistantId": coordination_session["coordination"]["assistant_id"],
        "threadId": coordination_thread["thread_id"],
        "userQuery": kwargs["user_query"],
        "updatedBy": "AI Operation Hub",
    }

    agent = coordination_thread.get("agent", {})
    if agent.get("agent_instructions"):
        variables["instructions"] = agent["agent_instructions"]
    if agent.get("response_format"):
        if agent["response_format"] == "auto":
            variables["responseFormat"] = {"type": "auto"}
        elif agent["response_format"] == "text":
            variables["responseFormat"] = {"type": "text"}
        elif agent["response_format"] == "json_object":
            variables["responseFormat"] = {"type": "json_object"}
        elif agent["response_format"] == "json_schema":
            variables["responseFormat"] = {
                "type": "json_schema",
                "json_schema": agent.get("json_schema", {}),
            }
    if coordination_session["coordination"].get("additional_instructions"):
        variables["additionalInstructions"] = coordination_session["coordination"][
            "additional_instructions"
        ]

    ask_openai = get_ask_openai(
        info.context.get("logger"),
        info.context.get("endpoint_id"),
        info.context.get("setting"),
        **variables,
    )

    variables = {
        "sessionUuid": coordination_session["session_uuid"],
        "threadId": ask_openai["thread_id"],
        "coordinationUuid": coordination_session["coordination"]["coordination_uuid"],
        "lastAssistantMessage": "null",
        "status": "dispatched",
        "updatedBy": "AI Operation Hub",
    }
    coordination_thread = insert_update_coordination_thread(
        info.context.get("logger"),
        info.context.get("endpoint_id"),
        setting=info.context.get("setting"),
        **variables,
    )

    ## Process OpenAI response asynchronously and save the results.
    ## Update the last assistant message in coordination thread.
    ## Update the status to be 'completed'.

    return AskOperationAgentType(
        coordination=coordination_session["coordination"],
        session_uuid=coordination_session["session_uuid"],
        thread_id=coordination_thread["thread_id"],
        agent=coordination_thread["agent"],
        last_assistant_message=coordination_thread["last_assistant_message"],
        status=coordination_thread["status"],
        log=coordination_thread["log"],
    )


def async_update_coordination_thread_handler(
    logger: logging.Logger, **kwargs: Dict[str, Any]
) -> Any:
    """Handle asynchronous update of coordination thread."""
    try:
        # Record the start time
        start_time = time.time()

        endpoint_id = kwargs.get("endpoint_id")
        setting = kwargs.get("setting")
        while True:
            current_run = get_current_run(
                logger,
                endpoint_id,
                setting=setting,
                **{
                    "functionName": kwargs["function_name"],
                    "taskUuid": kwargs["task_uuid"],
                    "assistantId": kwargs["assistant_id"],
                    "threadId": kwargs["thread_id"],
                    "runId": kwargs["run_id"],
                    "updatedBy": "AI Operation Hub",
                },
            )
            if current_run["status"] == "completed":
                break

            # Check if the time elapsed exceeds 5 minutes (300 seconds)
            elapsed_time = time.time() - start_time
            if elapsed_time > 300:
                raise Exception("Operation timed out after 5 minutes.")

            # Optional: Sleep for a short duration to prevent excessive looping
            time.sleep(1)

        last_message = get_last_message(
            logger,
            endpoint_id,
            setting=setting,
            **{
                "assistantId": kwargs["assistant_id"],
                "threadId": kwargs["thread_id"],
                "role": "assistant",
            },
        )

        variables = {
            "sessionUuid": kwargs["session_uuid"],
            "coordinationUuid": kwargs["coordination_uuid"],
            "threadId": kwargs["thread_id"],
            "updatedBy": "AI Operation Hub",
        }

        if "agent_uuid" in kwargs:
            variables.update(
                {
                    "agentUuid": kwargs["agent_uuid"],
                    "lastAssistantMessage": last_message["message"],
                    "status": "completed",
                }
            )
        else:
            response = Utility.json_loads(last_message["message"])
            variables.update(
                {
                    "agentUuid": (
                        response["agent_uuid"]
                        if response["status"] == "assigned"
                        else None
                    ),
                    "lastAssistantMessage": (
                        response["message"]
                        if response["status"] == "unassigned"
                        else None
                    ),
                    "status": response["status"],
                }
            )

        coordination_thread = insert_update_coordination_thread(
            logger,
            endpoint_id,
            setting=setting,
            **variables,
        )

        return

    except Exception as e:
        log = traceback.format_exc()
        logger.error(log)
        variables = {
            "sessionUuid": kwargs["session_uuid"],
            "coordinationUuid": kwargs["coordination_uuid"],
            "threadId": kwargs["thread_id"],
            "status": "fail",
            "log": log,
            "updatedBy": "AI Operation Hub",
        }
        coordination_thread = insert_update_coordination_thread(
            logger,
            endpoint_id,
            setting=setting,
            **variables,
        )
        raise e


def resolve_ask_operation_agent_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> AskOperationAgentType:
    try:
        ## Test the waters 🧪 before diving in!
        ##<--Testing Data-->##
        global connection_id, endpoint_id
        if info.context.get("connectionId") is None:
            info.context["connectionId"] = connection_id
        if info.context.get("endpoint_id") is None:
            info.context["endpoint_id"] = endpoint_id
        ##<--Testing Data-->##

        if not kwargs.get("agent_uuid"):
            return process_no_agent_uuid(info, **kwargs)
        else:
            return process_with_agent_uuid(info, **kwargs)

    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").error(log)
        raise e
