from pinecone import Pinecone, ServerlessSpec
import os
import pdb
import time
from utils.preprocess_utils import *
import streamlit as st


class VectorDB:

    def __init__(self):
        self.index=self.getPineConeIndex()

    def getPineConeIndex(self):
        # pdb.set_trace()
        pc = Pinecone(
            api_key=os.environ["VECTOR_DB_API_KEY"]
        )
        index = pc.Index(os.environ["INDEX"])
        return index


    def clearVectorDB(self,delete_flag=False):
        if delete_flag:
            self.index.delete(delete_all=True, namespace=os.environ["NAMESPACE"])
        index_stats = self.index.describe_index_stats()
        print(f"Index Stats: {index_stats}")


    def upload_to_vectorDB(self,file):
        # st.write("extracting text...")
        start_time = time.perf_counter()
        # st.write("hello")
        text,user_name,user_email, user_phone=getTextfromFile(file)
        # st.write(text)

        
        # st.write(user_name,user_email, user_phone)
        # st.write(text)
        if type(text)==NoneType:
                st.write("problematic file")
                return None, None, None, None,False
        
        st.write(user_name,user_email, user_phone)
        cid=getNewHash(user_name+user_email+user_phone+text)
        # st.write(f"**{len(text.split(" "))}** words")
        end_time = time.perf_counter()
        time_taken = end_time - start_time
        # st.write(f"extracting text took **{time_taken:.4f}** seconds")

        # st.write("uploading to vectorDB...")
        start_time = time.perf_counter()
        self.index.upsert_records(namespace=os.environ["NAMESPACE"],records=[{"id":cid,"name":user_name,"email":user_email,"contact":user_phone,"file name":file.split("/")[-1],"content":text}])
        # st.write("embedding uploaded to vectorDB")
        end_time = time.perf_counter()
        time_taken = end_time - start_time
        return user_name,user_email, user_phone,cid, True
        # st.write(f"uploading to vector DB took **{time_taken:.4f}** seconds")
    
    def getTopMatches(self,jd,k=5):
        # pdb.set_trace()
        query_payload = {
            "inputs": {
                "text": jd
            },
            "top_k": k
        }

        results = self.index.search(
            namespace=os.environ["NAMESPACE"],
            query=query_payload
        )

        return results