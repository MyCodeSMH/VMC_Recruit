import requests
import os

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

from utils.preprocess_utils import *
from utils.pdf_utils import *
from mistralai import Mistral
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont

# pdfmetrics.registerFont(TTFont("DejaVu", "DejaVuSans.ttf"))
# pdfmetrics.registerFont(TTFont("DejaVu-Bold", "DejaVuSans-Bold.ttf"))
# pdfmetrics.registerFont(TTFont("DejaVu-Italic", "DejaVuSans-Oblique.ttf"))
# pdfmetrics.registerFont(TTFont("DejaVu-BoldItalic", "DejaVuSans-BoldOblique.ttf"))

# from reportlab.pdfbase.pdfmetrics import registerFontFamily

# registerFontFamily(
#     "DejaVu",
#     normal="DejaVu",
#     bold="DejaVu-Bold",
#     italic="DejaVu-Italic",
#     boldItalic="DejaVu-BoldItalic"
# )

api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)

# Specify the model and the conversation messages
model = "mistral-large-latest"

# chat_response = client.chat.complete(
#     model=model,
#     messages=[
#         {
#             "role": "user",
#             "content": "What are the benefits of using Mistral AI?",
#         },
#     ]
# )

# Print the model's response
# print(chat_response.choices[0].message.content)

system_message='''Act as an expert recruiter. Compare the following resume to the job description and list: 
1) All the missing skills/requirements, 
2) Strengths present in the resume, and 
3) Suggestions for optimization.

Do not enter any # or * in your response. For missing skills, use a red cross image and for strengths, use green tick image

If no skills are missing and no optimization is required, clearly mention this.
Only answer the question and do not ask any follow up questions.
'''


def getS3FileData(curr_s3_url):

    # Perform the GET request
    response = requests.get(curr_s3_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Read as text
        content = response.text
        print(content)
        return content
        
        # OR read as binary (for images/PDFs)
        # binary_content = response.content
    else:
        print(f"Failed to access file: {response.status_code}")



def getModelResponse(resume_text,jd_text,jd_file,resume):
    # resume="/Users/shreymathur/Downloads/resumes_2/JavaQA_CHANAKYAVANGAPALLY0309.pdf"
    # jd_file="/Users/shreymathur/Downloads/Java QA.docx"

    # resume_text,_,_,_= getTextfromFile(resume,match_flag=True)
    # jd_text,_,_,_= getTextfromFile(jd_file,match_flag=True)
    if len(jd_file)==0:
        match_info_file_name=f"{resume.split("/")[-1].split('.')[0]}_match_info.pdf"
    else:
        match_info_file_name=f"{jd_file.split("/")[-1].split('.')[0]}_{resume.split("/")[-1].split('.')[0]}_match_info.pdf"
    

    response = client.chat.complete(
        model=model,  # Choose your model
        # model="deepseek/deepseek-r1:free",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": "job description:\n"+jd_text+"\nresume:"+resume_text}
            # {"role": "user", "content": "what is the capital of USA?"}
        ]
    )
    # pdb.set_trace()
    # Print the model's response
    # print(response.choices[0].message.content)

    content=response.choices[0].message.content
    # pdb.set_trace()
    
    # match_info_dir="/Users/shreymathur/Documents/match_info"
    # with open(match_info_file_name, "w", encoding="utf-8") as file:
    #     file.write(content)
    save_string_to_pdf(content, match_info_file_name, resume.split("/")[-1],jd_file.split("/")[-1].split('.')[0])
    return match_info_file_name


def getMatchInfo(s3_obj,file,jd,jd_file=''):
    # pdb.set_trace()
    resume_text=s3_obj.getS3FileData(file)
    # pdb.set_trace()
    match_info_file_name=getModelResponse(resume_text,jd,jd_file,file)
    return match_info_file_name
    # pdb.set_trace()


