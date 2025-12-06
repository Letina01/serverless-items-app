import json
import os
import boto3
from datetime import datetime
from uuid import uuid4

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ.get("TABLE_NAME", "ServerlessItems")
table = dynamodb.Table(TABLE_NAME)


def respond(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
        },
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    http_method = event.get("httpMethod")
    path_params = event.get("pathParameters") or {}
    query_params = event.get("queryStringParameters") or {}
    item_id = path_params.get("id") if path_params else None

    try:
        # CORS preflight
        if http_method == "OPTIONS":
            return respond(200, {"message": "OK"})

        # CREATE
        if http_method == "POST":
            body = json.loads(event.get("body") or "{}")
            title = body.get("title")
            status = body.get("status", "PENDING")

            if not title:
                return respond(400, {"error": "title is required"})

            new_item = {
                "ID": str(uuid4()),  # matches DynamoDB partition key
                "title": title,
                "status": status,
                "createdAt": datetime.utcnow().isoformat() + "Z",
            }
            table.put_item(Item=new_item)
            return respond(201, new_item)

        # READ
        if http_method == "GET":
            if item_id:
                # Get one item
                resp = table.get_item(Key={"ID": item_id})
                item = resp.get("Item")
                if not item:
                    return respond(404, {"error": "Item not found"})
                return respond(200, item)
            else:
                # List all items (scan – fine for demo)
                resp = table.scan()
                items = resp.get("Items", [])
                return respond(200, items)

        # UPDATE
        if http_method == "PUT":
            if not item_id:
                return respond(400, {"error": "id is required in path"})

            body = json.loads(event.get("body") or "{}")
            title = body.get("title")
            status = body.get("status")

            update_expr = []
            expr_attr_values = {}

            if title:
                update_expr.append("title = :t")
                expr_attr_values[":t"] = title
            if status:
                update_expr.append("status = :s")
                expr_attr_values[":s"] = status

            if not update_expr:
                return respond(400, {"error": "Nothing to update"})

            update_expression = "SET " + ", ".join(update_expr)

            resp = table.update_item(
                Key={"ID": item_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expr_attr_values,
                ReturnValues="ALL_NEW",
            )
            return respond(200, resp.get("Attributes", {}))

        # DELETE
        if http_method == "DELETE":
            if not item_id:
                return respond(400, {"error": "id is required in path"})

            table.delete_item(Key={"ID": item_id})
            return respond(200, {"message": "Item deleted"})

        # Method not allowed
        return respond(405, {"error": f"Method {http_method} not allowed"})

    except Exception as e:
        print("Error:", str(e))
        return respond(500, {"error": "Internal server error", "details": str(e)})
