1. pip install -r requirements.txt
2. For checking status of Components, use python test.py. If you want to delete all data from components, uncomment the clearComponents function call
3. python -m streamlit run resume_upload.py
4. Click on 'upload Resume'. This will upload resume content to vector store, files to s3 and metadata to dynamoDB
5. python -m streamlit run jd_match.py
6. upload jd on UI and click 'Find Top Resumes'
