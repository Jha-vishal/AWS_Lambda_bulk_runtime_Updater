# This script you can easily run in a lambda function to update all NodeJS as well as python Lambda function with suitable runtime.
import os 
import boto3
import botocore
import json
from datetime import datetime

#--------- ENV Variables --------------------------------------#
# current_region = <Your current AWS Region>
# region_name = <Your table region name>
# table_name = <Your DynamoDB table name to keep the records>
#--------------------------------------------------------------#

def lambda_with_layer(function_name, runtime, layer, message):
    now1 = datetime.now()
    currenttime = now1.strftime("%a, %d %b %Y %H:%M:%S")
    dynamodb = boto3.resource('dynamodb', region_name = os.environ.get('region_name'))
    table = dynamodb.Table(os.environ.get('table_name'))
    response = table.put_item(
        Item = {
            'function_name': function_name,
            'region': os.environ.get('current_region'),
            'runtime': runtime,
            'runtimestatus': message,
            'updatedtime': currenttime,
            'layer': layer
        }
    )

def lambda_without_layer(function_name, runtime, message):
    now1 = datetime.now()
    currenttime = now1.strftime("%a, %d %b %Y %H:%M:%S")
    dynamodb = boto3.resource('dynamodb', region_name = os.environ.get('region_name'))
    table = dynamodb.Table(os.environ.get('table_name'))
    response = table.put_item(
        Item = {
            'function_name': function_name,
            'region': os.environ.get('current_region'),
            'runtime': runtime,
            'runtimestatus': message,
            'updatedtime': currenttime,
            
        }
    )

def lambda_with_error(function_name, runtime, message, arn):
    now1 = datetime.now()
    currenttime = now1.strftime("%a, %d %b %Y %H:%M:%S")
    dynamodb = boto3.resource('dynamodb', region_name = os.environ.get('region_name'))
    table = dynamodb.Table(os.environ.get('table_name'))
    response = table.put_item(
        Item = {
            'function_name': function_name,
            'region': os.environ.get('current_region'),
            'runtime': runtime,
            'runtimestatus': message,
            'arn': arn,
            'updatedtime': currenttime
        }
    )    
    
def list_functions():
    client = boto3.client('lambda')
    comment = "UPDATED TO LATEST RUNTIME VERSION"
    functions = []
    response = client.list_functions()
    nexttoken = response.get('NextMarker', None)
    functions.extend(response['Functions'])
    while(nexttoken):
        response = client.list_functions(Marker=nexttoken)
        nexttoken = response.get('NextMarker', None)
        functions.extend(response['Functions'])
    print(len(functions))
    for function in functions:
        print("A FUNCTION >> ", function)
        if "nodejs" in function['Runtime']:
            print("WE HAVE NODE")
            if function['Runtime'] <= 'nodejs14.x' or function['Runtime'] == 'nodejs8.10' or function['Runtime'] == 'nodejs6.10':
                print("WE HAVE TO UPDATE >> ", function['Runtime'])
                try:
                    response = client.update_function_configuration(
                        FunctionName=function['FunctionName'],
                        Runtime='nodejs16.x'
                    )
                    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                        if 'Layers' in function:
                            print("INSIDE THE PUT ITEM FUNCTIONS")
                            
                            lambda_with_layer(function['FunctionName'], function['Runtime'], function['Layers'], comment)
                        else:
                            lambda_without_layer(function['FunctionName'], function['Runtime'], comment)
                except Exception as e:
                    print("ERROR IN RUNTIME UPDATE FUNCTION CONFIGURATION >> ", str(e))
                    lambda_with_error(function['FunctionName'], function['Runtime'], str(e), function['FunctionArn'])
                    pass
            else:
                print("NO UPDATE NEEDED >> ", function['Runtime'])    
        elif 'python' in function['Runtime']:
            print("WE HAVE PY")
            if function['Runtime'] <= 'python3.8' :
                client.update_function_configuration(
                    FunctionName=function['FunctionName'],
                    Runtime='python3.9'
                )
        else:
            print("NO Python and NodeJS Lambda Found")
        print("UPDATED THE RUNTIME")
    return response
    

def lambda_handler(event, context):
    
    list = list_functions()

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
