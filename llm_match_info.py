from openai import OpenAI
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

from utils.preprocess_utils import *

# The client automatically looks for the 'OPENAI_API_KEY' environment variable
client = OpenAI()

system_message='''Act as an expert recruiter. Compare the following resume to the job description and list: 
1) All the missing skills/requirements, 
2) Strengths present in the resume, and 
3) Suggestions for optimization.

If no skills are missing and no optimization is required, clearly mention this
'''

resume="/Users/shreymathur/Downloads/resumes_2/JavaQA_CHANAKYAVANGAPALLY0309.pdf"
jd_file="/Users/shreymathur/Downloads/Java QA.docx"

resume_text,_,_,_= getTextfromFile(resume,match_flag=True)
jd_text,_,_,_= getTextfromFile(jd_file,match_flag=True)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",  # Choose your model
    # model="deepseek/deepseek-r1:free",
    messages=[
        # {"role": "system", "content": system_message},
        # {"role": "user", "content": "job description:\n"+jd_text+"\nresume:"+resume}
        {"role": "user", "content": "what is the capital of USA?"}
    ]
)
pdb.set_trace()
# Print the model's response
print(response.choices[0].message.content)