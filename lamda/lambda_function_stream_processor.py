import json
import os
import boto3
from datetime import datetime
from uuid import uuid4

dynamodb = boto3.resource("dynamodb")
AUDIT_TABLE = os.environ.get("AUDIT_TABLE", "ServerlessItemsAudit")
audit_table = dynamodb.Table(AUDIT_TABLE)


def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    for record in event.get("Records", []):
        event_name = record.get("eventName")  # INSERT, MODIFY, REMOVE
        new_image = record.get("dynamodb", {}).get("NewImage")
        old_image = record.get("dynamodb", {}).get("OldImage")

        audit_item = {
            "auditId": str(uuid4()),  # Primary key for audit table
            "eventName": event_name,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        # Convert DynamoDB JSON format to normal JSON
        if new_image:
            audit_item["newItem"] = convert_dynamo_json(new_image)
        if old_image:
            audit_item["oldItem"] = convert_dynamo_json(old_image)

        # Save the audit log item
        audit_table.put_item(Item=audit_item)

    return {"status": "ok"}


def convert_dynamo_json(dynamo_json):
    """
    Convert DynamoDB Stream JSON structure:
    { "ID": { "S": "123" }, "count": { "N": "10" } }
    into:
    { "ID": "123", "count": 10 }
    """
    result = {}
    for key, value in dynamo_json.items():
        data_type, actual_value = list(value.items())[0]

        if data_type == "S":
            result[key] = actual_value
        elif data_type == "N":
            # auto convert to int or float
            result[key] = float(actual_value) if "." in actual_value else int(actual_value)
        elif data_type == "BOOL":
            result[key] = bool(actual_value)
        else:
            # other types (L, M) — store raw
            result[key] = actual_value

    return result
