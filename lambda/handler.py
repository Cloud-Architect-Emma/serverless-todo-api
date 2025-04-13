import json
import boto3
import os
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TODO_TABLE', 'ToDoTable')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    method = event['httpMethod']
    path = event['path']
    
    if method == 'GET' and path == '/tasks':
        return get_tasks()
    elif method == 'POST' and path == '/tasks':
        return create_task(event)
    elif method == 'PUT' and path.startswith('/tasks/'):
        task_id = path.split('/')[-1]
        return update_task(task_id, event)
    elif method == 'DELETE' and path.startswith('/tasks/'):
        task_id = path.split('/')[-1]
        return delete_task(task_id)
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Unsupported method or path'})
        }

def get_tasks():
    response = table.scan()
    return {
        'statusCode': 200,
        'body': json.dumps(response['Items'])
    }

def create_task(event):
    body = json.loads(event['body'])
    item = {
        'id': body['id'],
        'title': body['title'],
        'completed': False
    }
    table.put_item(Item=item)
    return {
        'statusCode': 201,
        'body': json.dumps(item)
    }

def update_task(task_id, event):
    body = json.loads(event['body'])
    table.update_item(
        Key={'id': task_id},
        UpdateExpression='SET title = :t, completed = :c',
        ExpressionAttributeValues={
            ':t': body['title'],
            ':c': body['completed']
        }
    )
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Task updated'})
    }

def delete_task(task_id):
    table.delete_item(Key={'id': task_id})
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Task deleted'})
    }
