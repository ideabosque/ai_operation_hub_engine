#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging
import time
import traceback
from typing import Any, Dict, List, Optional

import boto3
import humps
from boto3.dynamodb.conditions import Attr, Key
from graphene import ResolveInfo

from silvaengine_utility import Utility

from .types import AskOperationAgentType, CoordinationThreadType

functs_on_local = None
funct_on_local_config = None
aws_lambda = None
aws_dynamodb = None
aws_ses = None
source_email = None
ai_coordination_schema = None
openai_assistant_schema = None

## Test the waters 🧪 before diving in!
##<--Testing Data-->##
endpoint_id = None
connection_id = None
test_mode = None
##<--Testing Data-->##


def handlers_init(logger: logging.Logger, **setting: Dict[str, Any]) -> None:
    global functs_on_local, aws_lambda, aws_dynamodb, aws_ses, source_email
    global endpoint_id, connection_id, test_mode
    try:
        _initialize_functs_on_local(setting)
        _initialize_aws_clients(setting)
        _initialize_source_email(setting)
        _initialize_test_data(setting)
    except Exception as e:
        log = traceback.format_exc()
        logger.error(log)
        raise e


def _initialize_functs_on_local(setting: Dict[str, Any]) -> None:
    global functs_on_local
    functs_on_local = setting.get("functs_on_local", {})


def _initialize_aws_clients(setting: Dict[str, Any]) -> None:
    global aws_lambda, aws_dynamodb, aws_ses
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
        aws_dynamodb = boto3.resource(
            "dynamodb",
            region_name=setting.get("region_name"),
            aws_access_key_id=setting.get("aws_access_key_id"),
            aws_secret_access_key=setting.get("aws_secret_access_key"),
        )
        aws_ses = boto3.client(
            "ses",
            region_name=setting.get("region_name"),
            aws_access_key_id=setting.get("aws_access_key_id"),
            aws_secret_access_key=setting.get("aws_secret_access_key"),
        )
    else:
        aws_lambda = boto3.client("lambda")
        aws_dynamodb = boto3.resource("dynamodb")
        aws_ses = boto3.client("ses")


def _initialize_source_email(setting: Dict[str, Any]) -> None:
    global source_email
    source_email = setting.get("source_email")


def _initialize_test_data(setting: Dict[str, Any]) -> None:
    global endpoint_id, connection_id, test_mode

    ## Test the waters 🧪 before diving in!
    ##<--Testing Data-->##
    endpoint_id = setting.get("endpoint_id")
    connection_id = setting.get("connection_id")
    test_mode = setting.get("test_mode")
    ##<--Testing Data-->##


def fetch_graphql_schema(
    logger: logging.Logger,
    endpoint_id: str,
    function_name: str,
    setting: Dict[str, Any] = None,
) -> Dict[str, Any]:
    global ai_coordination_schema, openai_assistant_schema

    if function_name == "ai_coordination_graphql":
        if ai_coordination_schema is None:
            ai_coordination_schema = Utility.fetch_graphql_schema(
                logger,
                endpoint_id,
                function_name,
                setting=setting,
                aws_lambda=aws_lambda,
                test_mode=test_mode,
            )
        return ai_coordination_schema

    if function_name == "openai_assistant_graphql":
        if openai_assistant_schema is None:
            openai_assistant_schema = Utility.fetch_graphql_schema(
                logger,
                endpoint_id,
                function_name,
                setting=setting,
                aws_lambda=aws_lambda,
                test_mode=test_mode,
            )
        return openai_assistant_schema

    raise Exception(f"Invalid function name ({function_name}).")


def execute_graphql_query(
    logger: logging.Logger,
    endpoint_id: str,
    function_name: str,
    operation_name: str,
    operation_type: str,
    variables: Dict[str, Any],
    setting: Dict[str, Any] = {},
    connection_id: str = None,
) -> Dict[str, Any]:
    schema = fetch_graphql_schema(logger, endpoint_id, function_name, setting=setting)
    result = Utility.execute_graphql_query(
        logger,
        endpoint_id,
        function_name,
        Utility.generate_graphql_operation(operation_name, operation_type, schema),
        variables,
        setting=setting,
        aws_lambda=aws_lambda,
        connection_id=connection_id,
        test_mode=test_mode,
    )
    return result


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
        "coordination",
        "Query",
        variables,
        setting=setting,
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
        "thread",
        "Query",
        variables,
        setting=setting,
    )["thread"]
    return humps.decamelize(coordination_thread)


def get_ask_openai(
    logger: logging.Logger,
    endpoint_id: str,
    setting: Dict[str, Any] = None,
    connection_id: str = None,
    **variables: Dict[str, Any],
) -> Dict[str, Any]:
    """Call OpenAI for assistance."""
    ask_open_ai = execute_graphql_query(
        logger,
        endpoint_id,
        "openai_assistant_graphql",
        "askOpenAi",
        "Query",
        variables,
        setting=setting,
        connection_id=connection_id,
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
        "currentRun",
        "Query",
        variables,
        setting=setting,
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
        "lastMessage",
        "Query",
        variables,
        setting=setting,
    )["lastMessage"]
    return humps.decamelize(last_message)


# Updated function to use Boto3 to get the latest connection by email without an index
def get_connection_by_email(logger, endpoint_id: str, email: str) -> Optional[Dict]:
    """
    Retrieve the latest connection by email from DynamoDB without relying on an index.

    Args:
        logger: Logging object
        endpoint_id: Endpoint identifier
        email: Email to search for

    Returns:
        Dict containing connection information or None if not found
    """
    try:
        table = aws_dynamodb.Table("se-wss-connections")

        # Query without using an index
        response = table.query(
            KeyConditionExpression=Key("endpoint_id").eq(endpoint_id),
            FilterExpression=Attr("data.email").eq(email) & Attr("status").eq("active"),
        )

        connections = response.get("Items", [])

        # Sort connections manually by 'updated_at' if present
        latest_connection = None
        if connections:
            latest_connection = max(
                connections,
                key=lambda conn: conn.get("updated_at", "1970-01-01T00:00:00Z"),
            )

        if latest_connection:
            return {
                "connection_id": latest_connection["connection_id"],
                "data": latest_connection.get("data", {}),
            }

        logger.info(f"No active connection found for email: {email}")
        return None

    except Exception as e:
        log = traceback.format_exc()
        logger.error(log)
        raise e


def send_email(
    logger: logging.Logger, receiver_email: str, subject: str, body: str
) -> None:
    """Send an email with the given subject and body to the receiver's email address using AWS SES."""
    try:
        response = aws_ses.send_email(
            Source=source_email,
            Destination={
                "ToAddresses": [receiver_email],
            },
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {"Text": {"Data": body, "Charset": "UTF-8"}},
            },
        )
        logger.info(f"Email sent to: {receiver_email}")
    except Exception as e:
        log = traceback.format_exc()
        logger.error(log)
        raise e


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
        "Mutation",
        variables,
        setting=setting,
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
        "Mutation",
        variables,
        setting=setting,
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
            setting=info.context.get("setting"),
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
            setting=info.context.get("setting"),
            **{
                "coordinationType": kwargs["coordination_type"],
                "coordinationUuid": kwargs["coordination_uuid"],
            },
        )
        coordination_session = insert_update_coordination_session(
            info.context.get("logger"),
            info.context.get("endpoint_id"),
            setting=info.context.get("setting"),
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
        setting=info.context.get("setting"),
        connection_id=info.context.get("connectionId"),
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

    Utility.invoke_funct_on_aws_lambda(
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
        test_mode=test_mode,
        aws_lambda=aws_lambda,
    )

    return AskOperationAgentType(
        coordination=coordination_session["coordination"],
        session_uuid=coordination_session["session_uuid"],
        thread_id=coordination_thread["thread_id"],
        agent_uuid=(
            coordination_thread["agent"]["agent_uuid"]
            if coordination_thread["agent"] is not None
            else None
        ),
        agent_name=(
            coordination_thread["agent"]["agent_name"]
            if coordination_thread["agent"] is not None
            else None
        ),
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
        setting=info.context.get("setting"),
        **variables,
    )

    coordination_thread = get_coordination_thread(
        info.context.get("logger"),
        info.context.get("endpoint_id"),
        setting=info.context.get("setting"),
        **{
            "sessionUuid": kwargs["session_uuid"],
            "threadId": coordination_session["thread_ids"][0],
        },
    )

    if coordination_thread["status"] != "assigned":
        variables = {
            "sessionUuid": kwargs["session_uuid"],
            "threadId": coordination_session["thread_ids"][0],
            "coordinationUuid": coordination_session["coordination"][
                "coordination_uuid"
            ],
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

    # New logic to handle receiver_email
    connection_id = info.context.get("connectionId")
    if "receiver_email" in kwargs:
        # Attempt to find connection_id for the receiver's email
        receiver_connection = get_connection_by_email(
            info.context.get("logger"),
            info.context.get("endpoint_id"),
            email=kwargs["receiver_email"],
        )

        if receiver_connection:
            connection_id = receiver_connection.get("connection_id", connection_id)

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
    if agent.get("tools"):
        variables["tools"] = agent["tools"]
    if coordination_session["coordination"].get("additional_instructions"):
        variables["additionalInstructions"] = coordination_session["coordination"][
            "additional_instructions"
        ]

    ask_openai = get_ask_openai(
        info.context.get("logger"),
        info.context.get("endpoint_id"),
        setting=info.context.get("setting"),
        connection_id=connection_id,
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

    params = {
        "session_uuid": coordination_session["session_uuid"],
        "coordination_uuid": coordination_session["coordination"]["coordination_uuid"],
        "agent_uuid": kwargs["agent_uuid"],
        "function_name": ask_openai["function_name"],
        "task_uuid": ask_openai["task_uuid"],
        "assistant_id": coordination_session["coordination"]["assistant_id"],
        "thread_id": ask_openai["thread_id"],
        "run_id": ask_openai["current_run_id"],
    }

    # If connection_id is not found and receiver_email is provided, an email will be sent out.
    if connection_id is None and "receiver_email" in kwargs:
        params["receiver_email"] = kwargs["receiver_email"]

    Utility.invoke_funct_on_aws_lambda(
        info.context.get("logger"),
        info.context.get("endpoint_id"),
        "async_update_coordination_thread",
        params=params,
        setting=info.context.get("setting"),
        test_mode=test_mode,
        aws_lambda=aws_lambda,
    )

    return AskOperationAgentType(
        coordination=coordination_session["coordination"],
        session_uuid=coordination_session["session_uuid"],
        thread_id=coordination_thread["thread_id"],
        agent_uuid=(
            coordination_thread["agent"]["agent_uuid"]
            if coordination_thread["agent"] is not None
            else None
        ),
        agent_name=(
            coordination_thread["agent"]["agent_name"]
            if coordination_thread["agent"] is not None
            else None
        ),
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

        # Send email if receiver_email is in kwargs
        if "receiver_email" in kwargs:
            send_email(
                logger,
                receiver_email=kwargs["receiver_email"],
                subject="Coordination Thread Update",
                body=f"The coordination thread with ID {kwargs['thread_id']} has been updated successfully. Last assistant message: \n\n {last_message['message']}",
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


def resolve_coordination_thread_handler(
    info: ResolveInfo, **kwargs: Dict[str, Any]
) -> CoordinationThreadType:
    try:
        coordination_thread = get_coordination_thread(
            info.context.get("logger"),
            info.context.get("endpoint_id"),
            setting=info.context.get("setting"),
            **{
                "sessionUuid": kwargs["session_uuid"],
                "threadId": kwargs["thread_id"],
            },
        )

        return CoordinationThreadType(
            session_uuid=coordination_thread["session"]["session_uuid"],
            thread_id=coordination_thread["thread_id"],
            agent_uuid=(
                coordination_thread["agent"]["agent_uuid"]
                if coordination_thread["agent"] is not None
                else None
            ),
            agent_name=(
                coordination_thread["agent"]["agent_name"]
                if coordination_thread["agent"] is not None
                else None
            ),
            last_assistant_message=coordination_thread["last_assistant_message"],
            status=coordination_thread["status"],
            log=coordination_thread["log"],
        )
    except Exception as e:
        log = traceback.format_exc()
        info.context.get("logger").error(log)
        raise e
