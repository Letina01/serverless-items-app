# serverless-items-app

# Serverless Items App (AWS Lambda, API Gateway, DynamoDB, S3)

This is a full serverless CRUD application built using:

- AWS API Gateway (REST API)
- AWS Lambda (Python)
- Amazon DynamoDB (Main table + Audit table)
- DynamoDB Streams
- Amazon S3 (Static Website Hosting)
- IAM and CloudWatch

The application allows users to:

- Add items
- List items
- Delete items
- Track audit logs for INSERT, MODIFY, DELETE operations

Frontend is built using HTML + JavaScript and interacts with the backend via API Gateway.

## Architecture

S3 Static Website → API Gateway → Lambda (CRUD) → DynamoDB  
DynamoDB Stream → Lambda (Audit Logger) → DynamoDB Audit Table

## How to Run

1. Open the S3 Website URL to view frontend.
2. Add items using the input box.
3. Items are stored in DynamoDB.
4. Stream Lambda logs changes in audit table.

## Backend Code

Located in `/lambda` folder.
