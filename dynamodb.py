# imported libraries
import logging
import boto3
from botocore.exceptions import ClientError

from boto3.dynamodb.conditions import Key, Attr

# class model to perform CRUD operations
class DynamoDB:
    
    
    def create_table(self, table_name, key_schema, attribute_definitions, provisioned_throughput, region):
        
        try:
            dynamodb_resource = boto3.resource("dynamodb",region_name=region)
            self.table = dynamodb_resource.create_table(TableName=table_name, KeySchema=key_schema, AttributeDefinitions=attribute_definitions,
                ProvisionedThroughput=provisioned_throughput)

            # Wait until the table exists.
            self.table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
            
        except ClientError as e:
            logging.error(e)
            return False
        return True

 
    def create_prod_table(self, table_name, key_schema, attribute_definitions, provisioned_throughput, region):
        
        try:
            dynamodb_resource = boto3.resource("dynamodb",region_name=region)
            self.table = dynamodb_resource.create_table(TableName=table_name, KeySchema=key_schema, AttributeDefinitions=attribute_definitions,
                ProvisionedThroughput=provisioned_throughput)

            # Wait until the table exists.
            self.table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
            
        except ClientError as e:
            logging.error(e)
            return False
        return True     

    def store_an_item(self, region, table_name, item):
        try:
            dynamodb_resource = boto3.resource("dynamodb", region_name=region)
            table = dynamodb_resource.Table(table_name)
            table.put_item(Item=item)
        
        except ClientError as e:
            logging.error(e)
            return False
        return True
        
        
     
    def get_an_item(self,region, table_name, key):
        try:
            dynamodb_resource = boto3.resource("dynamodb", region_name=region)
            table = dynamodb_resource.Table(table_name)
            response = table.get_item(Key=key)
            item = response['Item']
            print(item)
        
        except ClientError as e:
            logging.error(e)
            return False
        return True
            
 

def main():
   
    region = 'us-east-1'
    d = DynamoDB()
    
    table_name="userdata"
    
    key_schema=[
        {
            "AttributeName": "email",
            "KeyType": "HASH"
        },
        {
            'AttributeName': 'firstname',
            'KeyType': 'RANGE'
        }
    ]
    
    attribute_definitions=[
        {
            "AttributeName": "email",
            "AttributeType": "S"
        },
        {
            "AttributeName": "firstname",
            "AttributeType": "S"
        }
        
        
    ]
    provisioned_throughput={
        "ReadCapacityUnits": 1,
        "WriteCapacityUnits": 1
    }
    
    # d.create_table(table_name, key_schema, attribute_definitions,provisioned_throughput, region)
      
     
    p = DynamoDB()
    table_name="Product"
    
    key_schema=[
        {
            "AttributeName": "id",
            "KeyType": "HASH"
        },
        {
            'AttributeName': 'Department',
            'KeyType': 'RANGE'
        }
    ]
    
    attribute_definitions=[
        {
            "AttributeName": "id",
            "AttributeType": "S"
        },
        {
            "AttributeName": "Department",
            "AttributeType": "S"
        }
        
        
    ]
    provisioned_throughput={
        "ReadCapacityUnits": 1,
        "WriteCapacityUnits": 1
    }
    
    p.create_prod_table(table_name, key_schema, attribute_definitions,provisioned_throughput, region)
    
if __name__ == '__main__':
 main()



# import boto3
# # Get the service resource.
# import key_config as keys

# dynamodb = boto3.resource('dynamodb',
#                     aws_access_key_id=keys.ACCESS_KEY_ID,
#                     aws_secret_access_key=keys.ACCESS_SECRET_KEY,
#                     aws_session_token=keys.AWS_SESSION_TOKEN)

# #dynamodb = boto3.resource('dynamodb')

# # Create the DynamoDB table.
# table = dynamodb.create_table(
#     TableName='userdata',
#     KeySchema=[
#         {
#             'AttributeName': 'email',
#             'KeyType': 'HASH'
#         }
         
#     ],
#     AttributeDefinitions=[
#              {
#             'AttributeName': 'email',
#             'AttributeType': 'S'
#         } 
#     ],
#     ProvisionedThroughput={
#         'ReadCapacityUnits': 5,
#         'WriteCapacityUnits': 5
#     }
# )

# # Wait until the table exists.
# table.meta.client.get_waiter('table_exists').wait(TableName='userdata')

# # Print out some data about the table.
# print(table.item_count)