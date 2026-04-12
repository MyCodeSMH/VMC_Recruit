import boto3
import os
import streamlit as st


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
    
    def upload_to_s3(self,file):
        filename=file.split("/")[-1]
        st.write(filename)
        try:
            s3_bucket=os.environ['BUCKET']
            s3_folder=os.environ['S3_FOLDER']
            self.s3_client.upload_file(file, s3_bucket, f'{s3_folder}{filename}')
            # st.write(f"'{file.name}' successfully uploaded to 's3://{bucket_name}/all_resumes'")
        except Exception as e:
            st.write(f"Error uploading file {file} to s3: {e}")
    

    def list_s3_files(self):
        
        bucket_name=os.environ['BUCKET']
        folder_prefix=os.environ['S3_FOLDER']
        # List objects within a specific prefix
        response = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)
        
        # Check if 'Contents' exists (it won't if the prefix is empty or invalid)
        if 'Contents' in response:
            print("No. of files uploaded to s3: ",len(response['Contents']))
            for obj in response['Contents']:
                print(f"File: {obj['Key']}")
        else:
            print("No files found in the specified prefix.")


    def delete_files(self):

        bucket_name=os.environ['BUCKET']
        prefix=os.environ['S3_FOLDER']
        
        paginator = self.s3_client.get_paginator('list_objects_v2')
        
        # Iterate through pages of up to 1,000 objects each
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            if 'Contents' in page:
                # Prepare the list of keys to delete
                delete_list = [{'Key': obj['Key']} for obj in page['Contents']]
                self.s3_client.delete_objects(Bucket=bucket_name, Delete={'Objects': delete_list})
    

    def getS3Url(self,file):

        url = self.s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': os.environ['BUCKET'],
                'Key': f'{os.environ['S3_FOLDER']}{file}'
            },
            ExpiresIn=3600  # URL expiration in seconds (e.g., 1 hour)
        )

        return url
