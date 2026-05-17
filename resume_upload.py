import streamlit as st
import re
import nltk
import ssl
import yaml

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import boto3
from pinecone import Pinecone, ServerlessSpec
from types import NoneType
import docx2txt
import PyPDF2
import time
import io
# from odf import text, teletype
# from odf.opendocument import load
# import sharepoint2text
# import tempfile
import docx2txt2
import os
import re
import hashlib
from decimal import Decimal
from datetime import datetime
import spacy
import pdb


from spacy.cli import download
# download("en_core_web_sm")
# pdb.set_trace()
try:
    nlp = spacy.load("en_core_web_sm")
except IOError:
    print("Please download the spaCy model first: python -m spacy download en_core_web_sm")
    exit()

from utils.vector_db_utils import VectorDB
from utils.s3_utils import S3
from utils.ddb_utils import DDB
from utils.preprocess_utils import *

import yaml



vector_db=VectorDB()
s3=S3()
ddb=DDB()


with open("config.yml", "r") as file:
    config = yaml.safe_load(file)

st.title("Resume Upload")
completion_message = st.empty()

with st.form(key="my_form"):

  # user_name = st.text_input("Name:")
  # user_email = st.text_input("Email Address:")
  # user_phone = st.text_input("Contact Number:")

  # uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True,
  #     type=['docx', 'pdf', 'odt','doc'])
  # uploaded_files = st.file_uploader("Select a folder", accept_multiple_files='directory')
  test_file_uploader = st.file_uploader("Choose a folder", accept_multiple_files="directory")
  submit_button = st.form_submit_button(label="Upload Resume")
  

# uploaded_files = st.file_uploader("Choose a file", type=['docx', 'pdf','odt','doc'])
if submit_button:
  
  uploaded_files=[]
  if test_file_uploader:
    for file in test_file_uploader:
        uploaded_files.append(file)
  
  complete_resume_upload_pipeline(uploaded_files,vector_db,s3,ddb,completion_message)
  # pdb.set_trace()
  
  # if uploaded_files is not None and len(uploaded_files)!=0:
  #   progress_bar = st.progress(0)
  #   for idx in range(len(uploaded_files)):
  #     uploaded_file=uploaded_files[idx]
  #     ut=str(datetime.now())
      

  #     # upload to vector db
  #     try:
  #       start_time = time.perf_counter()
  #       user_name,user_email, user_phone,cid,flag=vector_db.upload_to_vectorDB(uploaded_file)
  #       if flag==False:
  #         continue
  #       end_time = time.perf_counter()
  #       time_taken = end_time - start_time
        
  #       start_time = time.perf_counter()
  #       uploaded_file.seek(0)
  #       uploaded_to_s3=s3.upload_to_s3(uploaded_file)
  #       if not uploaded_to_s3:
  #         pdb.set_trace()
  #         vector_db.deleteRecord(cid)
  #         continue
        
  #       uploaded_to_ddb=ddb.upload_to_ddb(cid,user_name,user_email,user_phone,ut,uploaded_file)
  #       if not uploaded_to_ddb:
  #         pdb.set_trace()
  #         vector_db.delete_record(cid)
  #         s3.delete_file(uploaded_file.split('/')[-1])
  #         continue
  #       end_time = time.perf_counter()
  #       time_taken = end_time - start_time
  #       prog=int(((idx+1)/len(uploaded_files))*100)
  #       progress_bar.progress(prog)
        
  #     except Exception as e:
  #       print(e)
        
  #   completion_message.success("File upload complete!")
  # elif len(uploaded_files)==0:
  #   st.warning("No files to upload")
  # else:
  #   st.warning("Problem reading files from specified directory")
  


 