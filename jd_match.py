import streamlit as st
import re
from pinecone import Pinecone, ServerlessSpec
import nltk

import ssl

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
from types import NoneType
import docx2txt
import PyPDF2
import pandas as pd
import boto3
from boto3.dynamodb.conditions import Key
import json
import pdb

# from botocore.config import Config
# import spacy
# nlp = spacy.load("en_core_web_sm")
# from nltk.stem import WordNetLemmatizer
from utils.vector_db_utils import VectorDB
from utils.s3_utils import S3
from utils.ddb_utils import DDB
from utils.preprocess_utils import *


vector_db=VectorDB()
s3=S3()
ddb=DDB()


st.title('Resume-JD Matcher')
st.subheader('Upload a Job Description to Begin')

# if "text_content" not in st.session_state:
#   st.session_state["text_content"] = ""

# Use a form to handle submission without losing focus
with st.form(key="my_form"):
  # jd_text = st.text_area("Enter Job Description", key="ta1")
  # st.session_state["text_content"] = jd_text
  jd_file = st.file_uploader("Upload Job Description file", type=['pdf','docx'])
  submit_button = st.form_submit_button(label="Find Top Resumes")
# jd_text = st.text_input("Paste Job description here")

# Input for Resume Upload


if submit_button:
  if jd_file:
    # st.write(jd_text)
    try:
        jd,_,_,_=getTextfromFile(jd_file)
        # if type(jd)==NoneType:
        #     st.warning("unable to parse file")
        # st.write(jd)
    # Extract text from the uploaded PDF
        # jd = preprocess_text(jd_text)
        results=vector_db.getTopMatches(jd)
        df=pd.DataFrame(columns=['Name','Email','Phone No.','filename','upload_time','link','match_score'])
        for i in results['result']['hits']:
            cid=i['_id']
            curr_score=i['_score']*100
            data=ddb.getDataFromDDB(cid)
            data['match score']=curr_score
            curr_file=data['file name']
            # fnames.append(curr_file)
            # scores.append(curr_score)
            curr_s3_url=s3.getS3Url(curr_file)
            data['s3url']=curr_s3_url
            data['link']=f'<a href="{curr_s3_url}" target="_blank">{curr_file}</a>'
            new_record={
                'Name':data['userName'],
                'Email':data['userEmail'],
                'Phone No.':data['contact_no'],
                'filename':curr_file,
                'upload_time':data['uploaded_timestamp'],
                'link':data['link'],
                'match_score':data['match score']
            }
            df=pd.concat([df,pd.DataFrame([new_record])],ignore_index=True)

            # st.write(i['_id'])
            # st.write(i['_score'])
            # st.write("*"*20)

        # df['filename']=fnames
        # df['score']=scores
        # df['file link']=s3urls

        # df['Download Link'] = df.apply(lambda x: f'<a href="{x["file link"]}" target="_blank">{x["filename"]}</a>', axis=1)
        # df.drop(columns=['file link'],inplace=True)
        # Display as a static table
        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)

      # st.write(df)
      # st.table(df)


    except Exception as e:
      st.write(e)
      pdb.set_trace()

      # Display the result
      # st.write(f"Match Percentage: {match_percentage:.2f}%")

      # if match_percentage >= 70:
      #     st.success("Good Chances of getting your Resume Shortlisted.")
      # elif 40 <= match_percentage < 70:
      #     st.warning("Good match but can be improved.")
      # else:
      #     st.error("Poor match.")

  else:
    st.warning("Please enter a Job Description.")