import boto3
import os
import streamlit as st
import pdb
import io

from utils.preprocess_utils import *



class S3:

    def __init__(self):
        self.s3_client=self.getS3Client()

    def getS3Client(self):
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ['ACCESS_KEY'],
            aws_secret_access_key=os.environ['SECRET_KEY'],
            region_name=os.environ['REGION']
        )
        return s3_client
    
    def upload_to_s3(self,file,default_folder=True):
        # pdb.set_trace()
        filename=file.split("/")[-1]
        # st.write(filename)
        try:
            s3_bucket=os.environ['BUCKET']
            if default_folder:
                s3_folder=os.environ['S3_FOLDER']
                self.s3_client.upload_file(file, s3_bucket, f'{s3_folder}{filename}')
            else:
                extra_s3_args={
                    "ContentType": "application/pdf"
                }
                s3_destination_key=f'match_info/{filename}'
                self.s3_client.upload_file(file, s3_bucket, s3_destination_key,ExtraArgs=extra_s3_args)
            return True
            # st.write(f"'{file.name}' successfully uploaded to 's3://{bucket_name}/all_resumes'")
        except Exception as e:
            st.warning(f"Error uploading file {filename} to s3: {e}")
            return False
    

    def list_s3_files(self,default_folder=True):
        
        bucket_name=os.environ['BUCKET']
        if default_folder:
            folder_prefix=os.environ['S3_FOLDER']
        else:
            folder_prefix='match_info/'
        # List objects within a specific prefix
        response = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)
        
        # Check if 'Contents' exists (it won't if the prefix is empty or invalid)
        if 'Contents' in response:
            print("No. of files uploaded to s3: ",len(response['Contents']))
            for obj in response['Contents']:
                print(f"File: {obj['Key']}")
        else:
            print("No files found in the specified prefix.")


    def delete_file(self,file,default_folder=True):
        
        s3_key=f'{os.environ['S3_FOLDER']}{file}'
        self.s3_client.delete_object(Bucket=os.environ['BUCKET'], Key=s3_key)


    def delete_files(self,default_folder=True):

        bucket_name=os.environ['BUCKET']

        if default_folder:
            prefix=os.environ['S3_FOLDER']
        else:
            prefix='match_info/'
        
        paginator = self.s3_client.get_paginator('list_objects_v2')
        
        # Iterate through pages of up to 1,000 objects each
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            if 'Contents' in page:
                # Prepare the list of keys to delete
                delete_list = [{'Key': obj['Key']} for obj in page['Contents']]
                self.s3_client.delete_objects(Bucket=bucket_name, Delete={'Objects': delete_list})
    

    def getS3Url(self,file,default_folder=True):
        if default_folder:
            s3_key=f'{os.environ['S3_FOLDER']}{file}'
            
        else:
            s3_key=f'match_info/{file}'
            # pdb.set_trace()

            
        # self.getS3FileMetaData(s3_key)
        url = self.s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': os.environ['BUCKET'],
                'Key': s3_key,
                "ResponseContentDisposition": "inline"
            },
            ExpiresIn=3600  # URL expiration in seconds (e.g., 1 hour)
        )

        return url
    
    def getS3FileData(self,file):
        response = self.s3_client.get_object(Bucket=os.environ['BUCKET'], Key=f'{os.environ['S3_FOLDER']}{file}')
        file_stream = io.BytesIO(response['Body'].read())

        if file.endswith(".docx"):
            return read_docx_stream(file_stream)
        elif file.endswith(".pdf"):
            return read_pdf_stream(file_stream)
        elif file.endswith(".odt"):
            return read_odt_stream(file_stream)
        else:
            st.write(f"Unsupported file type: {file}")

        
    
    def getS3FileMetaData(self,key):
        response = self.s3_client.head_object(
            Bucket=os.environ['BUCKET'],
            Key=key
        )

        print("Content-Type:", response["ContentType"])
        print("Metadata:", response["Metadata"])
    

    def file_exists(self, file,default_folder=True):

        # pdb.set_trace()
        if default_folder:
            s3_key=f'{os.environ['S3_FOLDER']}{file}'
            
        else:
            s3_key=f'match_info/{file}'
        
        try:
            self.s3_client.head_object(Bucket=os.environ['BUCKET'], Key=s3_key)
            return True
        except:
            return False
        

        
