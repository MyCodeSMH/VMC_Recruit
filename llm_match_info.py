from openai import OpenAI
import google.generativeai as genai
import os

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

from utils.preprocess_utils import *
from mistralai import Mistral

# Initialize the Mistral client with your API key
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

If no skills are missing and no optimization is required, clearly mention this.
Do not ask any follow up questions. If you do, you will be penalized.
'''

resume="/Users/shreymathur/Downloads/resumes_2/JavaQA_CHANAKYAVANGAPALLY0309.pdf"
jd_file="/Users/shreymathur/Downloads/Java QA.docx"

resume_text,_,_,_= getTextfromFile(resume,match_flag=True)
jd_text,_,_,_= getTextfromFile(jd_file,match_flag=True)

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
with open(f"{jd_file.split("/")[-1]}_{resume.split("/")[-1]}_match_info.txt", "w", encoding="utf-8") as file:
    file.write(content)