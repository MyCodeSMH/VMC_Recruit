import boto3
import os
import streamlit as st
from utils.preprocess_utils import *
from decimal import Decimal
import pdb

class DDB:

    def __init__(self):
        self.client, self.table=self.getDDBTable()
    
    def getDDBTable(self):
        dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id=os.environ['ACCESS_KEY'],
                          aws_secret_access_key=os.environ['SECRET_KEY'],
                          region_name=os.environ['REGION']) # Replace with your region
        return dynamodb, dynamodb.Table(os.environ['DDB_TABLE'])
    

    def upload_to_ddb(self,cid,name,email,cn,uploaded_timestamp,filename):
        # Define the item data as a Python dictionary
        # DynamoDB numbers should be handled with Python's Decimal type to avoid precision issues
        # when dealing with JSON serialization (if applicable)
        # pdb.set_trace()
        # try:
        #     cn1=cn.replace('-','').replace('+','').replace('(','').replace(')','').replace('.','').replace(' ','')
        #     cn1=Decimal(cn1)
        # except:
        #     pdb.set_trace()
        

        item_data = {
            'userId': cid,  # Replace with your partition key name and value
            'userName': name,
            'userEmail': email,     # Replace with your sort key name and value (if applicable)
            'contact_no': cn,
            'file name': filename.split("/")[-1],
            'uploaded_timestamp': uploaded_timestamp
        }

        # Use the put_item method to insert the data
        try:
            response = self.table.put_item(
                Item=item_data
            )
            st.write("Item inserted successfully:")
            # print(json.dumps(response, indent=2)) # Optional: print the response
        except Exception as e:
            st.write(f"Error inserting item: **{e}** in DDB")
    

    def clear_table_items(self):
        
        table=self.table
        # Get primary keys (Hash and Range)
        # primary_key=os.environ['PRIMARY_KEY']
        # pdb.set_trace()
        key_names = [k['AttributeName'] for k in table.key_schema]
        
        # Scan and delete in batches of 25 for efficiency
        with table.batch_writer() as batch:
            scan = table.scan(ProjectionExpression=', '.join(key_names))
            for item in scan['Items']:
                # Construct key object for deletion
                key = {k: item[k] for k in key_names}
                batch.delete_item(Key=key)
                
        print(f"All items cleared from dynamoDB table")
    

    def getRecordCount(self):

        # response = self.client.describe_table(TableName=os.environ['DDB_TABLE'])
        count = self.table.item_count
        print(f"Estimated Item Count: {count}")
    

    def getDataFromDDB(self,cid):
        try:
            response = self.table.get_item(
                Key={
                    'userId': cid,
                    # Include the sort key if your table has one
                    # 'sort_key_name': 'sort_value'
                }
            )
            item = response.get('Item')
            # if item:
            #     st.write(f"Fetched item: **{item}**")
            # else:
            #     st.write("Item not found")
        except Exception as e:
            st.write(f"Error fetching item: **{e}**")
        return item
    

