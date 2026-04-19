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
from utils.match_info_utils import *
from tabular_view import *


vector_db=VectorDB()
s3=S3()
ddb=DDB()

st.set_page_config(layout="wide")

# pdb.set_trace()

if "jd_file" not in st.session_state:
    st.session_state.jd_file = None

if "jd_text" not in st.session_state:
    st.session_state.jd_text = None

if "pasted_text" not in st.session_state:
    st.session_state.pasted_text = None

if "submit_jd" not in st.session_state:
    st.session_state.submit_jd=False

if "df" not in st.session_state:
    st.session_state.df=[]

if "selected_rows" not in st.session_state:
        st.session_state.selected_rows = set()

if "generated_files" not in st.session_state:
    st.session_state.generated_files = {}

if "input_state_change" not in st.session_state:
    st.session_state.input_state_change = False

if "n_resumes" not in st.session_state:
    st.session_state.n_resumes=0


st.title('Resume-JD Matcher')
st.subheader('Upload a Job Description to Begin')

def handle_changes():
    # If file removed
    # pdb.set_trace()
    if st.session_state.file_uploader is None:
        st.session_state.jd_file=None
        st.session_state.input_state_change=True
    
    elif st.session_state.jd_file and st.session_state.file_uploader.file_id!=st.session_state.jd_file.file_id:
        st.session_state.jd_file=st.session_state.file_uploader
        st.session_state.input_state_change=True
        # st.session_state.processed = False

    # If text cleared
    if st.session_state.text_area != st.session_state.pasted_text:
        st.session_state.input_state_change=True
        st.session_state.jd_text=None
    
    st.session_state.jd_file=st.session_state.file_uploader
    st.session_state.jd_text=st.session_state.text_area


# if "text_content" not in st.session_state:
#   st.session_state["text_content"] = ""

# Use a form to handle submission without losing focus
with st.form(key="my_form"):
  # jd_text = st.text_area("Enter Job Description", key="ta1")
  # st.session_state["text_content"] = jd_text
    st.subheader("📁 Upload File")
    jd_file = st.file_uploader("Upload Job Description file",key="file_uploader", type=['pdf','docx'])
    st.subheader("📝 Or Paste Text")
    pasted_text = st.text_area(
        "Paste job description or resume text here",
        key="text_area",
        height=200,
        placeholder="Paste content here...",
    )
    st.session_state.jd_file=jd_file
    st.session_state.pasted_text=pasted_text.strip()

    k = st.number_input(
            "No. of matching resumes",
            min_value=1,
            value=5,
            step=1
        )
    st.session_state.n_resumes=k

    submit_button = st.form_submit_button(label="Find Top Resumes",on_click=handle_changes)

#   st.session_state.submit_jd=True
#   match_info_button = st.form_submit_button(label="Get Detailed Match info")
# jd_text = st.text_input("Paste Job description here")

# Input for Resume Upload
# pdb.set_trace()
# pdb.set_trace()

if submit_button or st.session_state.submit_jd:
    st.session_state.submit_jd=True
    if st.session_state.jd_file or len(st.session_state.pasted_text)>0:
        st.session_state.jd_file=jd_file
        # st.write(jd_text)
        try:
            jd_file=st.session_state.jd_file
            if not st.session_state.jd_text.strip()=="":
                jd=st.session_state.jd_text
            else:
                if jd_file:
                    jd,_,_,_=getTextfromFile(jd_file)
                else:
                    jd=st.session_state.pasted_text
                st.session_state.jd_text=jd
            # if type(jd)==NoneType:
            #     st.warning("unable to parse file")
            # st.write(jd)
        # Extract text from the uploaded PDF
            # jd = preprocess_text(jd_text)
            top_resumes=[]
            results=vector_db.getTopMatches(jd,st.session_state.n_resumes)
            if len(st.session_state.df)!=0 and len(st.session_state.df)==st.session_state.n_resumes and not st.session_state.input_state_change:
                df=st.session_state.df
            else:
                if st.session_state.input_state_change:
                    st.session_state.selected_rows = set()
                    st.session_state.generated_files={}
                
                df=pd.DataFrame(columns=['Email','Phone No.','upload_time','file name','match_score'])
                for i in results['result']['hits']:
                    cid=i['_id']
                    curr_score=round(i['_score']*100,2)
                    data=ddb.getDataFromDDB(cid)
                    data['match score']=curr_score
                    curr_file=data['file name']
                    top_resumes.append(curr_file)
                    # fnames.append(curr_file)
                    # scores.append(curr_score)
                    curr_s3_url=s3.getS3Url(curr_file)
                    # data['link']=curr_s3_url
                    data['file name']=f'<a href="{curr_s3_url}" target="_blank">{curr_file}</a>'
                    # data['match info']=f'<a href="Get Match Info"></a>'
                    
                    new_record={
                        # 'Name':data['userName'],
                        'Email':data['userEmail'],
                        'Phone No.':data['contact_no'],
                        'upload_time':data['uploaded_timestamp'],
                        'file name':data['file name'],
                        # 'link':data['link'],
                        'match_score':data['match score'],
                        # 'match info': data['match info']
                        # 'Get Match Info': st.checkbox("",key=f"chk_{i}",value=False)
                    }
                    df=pd.concat([df,pd.DataFrame([new_record])],ignore_index=True)
                st.session_state.df=df
                st.session_state.input_state_change=False

                # st.write(i['_id'])
                # st.write(i['_score'])
                # st.write("*"*20)

            # df['filename']=fnames
            # df['score']=scores
            # df['file link']=s3urls

            # df['Download Link'] = df.apply(lambda x: f'<a href="{x["file link"]}" target="_blank">{x["filename"]}</a>', axis=1)
            # df.drop(columns=['file link'],inplace=True)
            

            # edited_df = st.data_editor(df)
            # edited_df = st.data_editor(
            #     df,
            #     column_config={
            #         "file name": st.column_config.LinkColumn(
            #             "link",
            #             display_text=r"([^/]+)$"
            #         )
            #     },
            #     hide_index=True,
            #     use_container_width=True
            # )
            # selected_rows = edited_df[edited_df["Get Match Info"]]

            # df = pd.DataFrame({
            #     "Name": ["Alice", "Bob", "Charlie", "David", "Eve", "Frank"],
            #     "Score": [85, 90, 78, 92, 88, 76]
            # })
            # Display as a static table
            # st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
            # st.session_state.shared_data['jd']=jd
            # st.session_state.shared_data['top_resumes']=top_resumes
            # st.session_state.shared_data['jd_file_name']=jd_file.name
            update_table(st.session_state.df)

        # st.write(df)
        # st.table(df)
            # pdb.set_trace()


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


    # if match_info_button:
    #     jd=st.session_state.shared_data['jd']
    #     top_resumes=st.session_state.shared_data['top_resumes']
    #     jd_file=st.session_state.shared_data['jd_file_name']
    #     # pdb.set_trace()
    #     if jd and len(top_resumes)>0:
    #         for top_resume in top_resumes:
    #             getMatchInfo(s3,top_resume,jd,jd_file)
    #         print("match info file generation complete")
        



