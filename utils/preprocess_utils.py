import nltk
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from types import NoneType
import docx2txt
import PyPDF2
# from odf import text, teletype
# from odf.opendocument import load
import sharepoint2text
import tempfile
import docx2txt2
import os
import re
import hashlib
import spacy
import glob
import pdb
import streamlit as st
from pypdf import PdfReader
from docx import Document
from odf.opendocument import load
from odf.text import P


try:
    nlp = spacy.load("en_core_web_sm")
except IOError:
    print("Please download the spaCy model first: python -m spacy download en_core_web_sm")
    exit()


def getNewHash(val):
  h = hashlib.sha3_512() # Python 3.6+
  h.update(val.encode("utf-8"))
  return h.hexdigest()

def preprocess_text(text):
  # text = re.sub(r"[^a-zA-Z\s]", "", text)
  # st.write(type(text))
  text = re.sub(r'[^\w\d]', ' ', text)
  tokens = word_tokenize(text.lower())
  stop_words = set(stopwords.words("english"))
  filtered_tokens = [word for word in tokens if word not in stop_words]
  # lemmatizer = WordNetLemmatizer()
  # lemmatized_words = [lemmatizer.lemmatize(word) for word in filtered_tokens]
  # stemmed_tokens = [PorterStemmer().stem(word) for word in filtered_tokens]
  # doc = nlp(" ".join(stemmed_tokens))
  # doc=nlp(" ".join(lemmatized_words))
  doc=" ".join(filtered_tokens)
  return doc


def scrub_pii(text):
    # Regex for Email Addresses
    email_pattern = r'\S+@\S+\.\S+'

    # Regex for Phone Numbers (various formats: 123-456-7890, (123) 456-7890)
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'

    # Replace emails and phones
    text = re.sub(email_pattern, '[EMAIL]', text)
    text = re.sub(phone_pattern, '[PHONE]', text)

    return text


def read_old_doc_file(file):
  with tempfile.TemporaryDirectory() as tmpdir:
        # file_path = os.path.join(tmpdir, file.name)
        with open(file, "wb") as f:
            f.write(file)
        full_text=""
        results = sharepoint2text.read_file(file)
        for result in results:
            # Get the full text as a single string
            full_text += result.get_full_text()
  return full_text


def read_odt_file(file):
    """
    Reads the text content from an OpenDocument Text (.odt) file.
    """
    try:
        # docx2txt2 can read directly from a bytes stream (BytesIO)
        # bytes_io = io.BytesIO(uploaded_file.getvalue())
        # bytes_io = io.BytesIO(file)
        text = docx2txt2.extract_text(file)
        return text
    except Exception as e:
        st.error(f"Error extracting text: {e}")
        return None


def read_doc_file(file):
    # st.write(file)
    # try:
    # pdb.set_trace()
    text = docx2txt.process(file)
        # st.write(text)
        # print(text)
        # words = text.split()
        # print(len(words))
    return text
    # except Exception as e:
    #      st.write(f"Error: Could not read the file using docx2txt: **{e}**")


def extract_text_from_pdf(pdf_path):
    # text = ""
    # with open(pdf_path, "rb") as file:
    #     reader = PyPDF2.PdfReader(file)
    #     for page in reader.pages:
    #         text += page.extract_text() + " "
    # return text.strip()
    # bytes_data = pdf_path.getvalue()
    # pdf_reader = PyPDF2.PdfReader(io.BytesIO(bytes_data))
    # pdb.set_trace()
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    text = ""

    # Iterate through all the pages and extract text
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text.strip()


def extract_all_info(text):

    # st.write("extracting info...")
    # st.write(text)
    # Extract Emails
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    email = re.findall(email_pattern, text)
    email=email[0] if len(email)>0 else ''

    # st.write(email)
    # Extract Phone Numbers (US format regex)
    phone_pattern = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', re.VERBOSE)
    phone = phone_pattern.findall(text)
    phone=phone[0] if len(phone)>0 else ''

    # st.write(phone)
    # Extract Names using spaCy
    doc = nlp(text)
    name = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    name=name[0] if len(name)>0 else ''
    # st.write(name)

    return name, email, phone


def getTextfromFile(file,match_flag=False):
  text=None
  user_name,user_email, user_phone=None,None,None
  PdfFileCondition=(type(file)!=str and file.name.endswith('.pdf')) or (type(file)==str and file.endswith('.pdf'))
  DocxFileCondition=type(file)!=str and file.name.endswith('.docx') or (type(file)==str and file.endswith('.docx'))
  OdtFileCondition=type(file)!=str and file.name.endswith('.odt') or (type(file)==str and file.endswith('.odt'))
  try:
    if PdfFileCondition:
        text = extract_text_from_pdf(file)

    elif DocxFileCondition:
        text = read_doc_file(file)

    # elif file.endswith('.doc'):
    #     st.write("reading doc file..")
    #     text = read_old_doc_file(file)
    #     st.write("done reading doc file")

    elif OdtFileCondition:
        text = read_odt_file(file)

    else:
        st.warning(f"{file} could not be uploaded due to file format. Pls upload docx, pdf or odt files")
        return None, None, None,None
    
    # pdb.set_trace()
    if type(text)==NoneType:
        # st.write("problematic file")
        return None, None, None,None

    # text=scrub_pii(text)
    user_name,user_email, user_phone = extract_all_info(text)

    if not match_flag:
        text = preprocess_text(text)
    
  except Exception as e:
    # pdb.set_trace()
    if 'zip' in str(e).lower():
        st.warning(f"{file} could not be uploaded as it is password protected")
        # st.write("File upload unsuccessful. Plase make sure file is not password protected")
        
    return None,None,None,None

  # st.write("preprocessing done")
  return text, user_name,user_email, user_phone


def list_office_and_pdf_files_glob(directory_path):
    """
    Lists all docx, doc, odt, and pdf files in the specified directory
    using the glob module.
    """
    # search_path = os.path.abspath(directory_path)
    # print(f"Searching in: {search_path}\n")
    file_extensions = ('*.docx', '*.doc', '*.odt', '*.pdf')
    found_files = []

    for ext in file_extensions:
        # Use os.path.join to create platform-independent paths
        search_pattern = os.path.join(directory_path, "**", ext)
        # glob.glob returns a list of paths matching the pattern
        found_files.extend(glob.glob(search_pattern, recursive=True))

    return found_files


def read_docx_stream(file_stream):
    doc = Document(file_stream)
    return "\n".join([para.text for para in doc.paragraphs])


def read_pdf_stream(file_stream):
    reader = PdfReader(file_stream)
    text = []
    for page in reader.pages:
        text.append(page.extract_text() or "")
    return "\n".join(text)


def read_odt_stream(file_stream):
    doc = load(file_stream)
    paragraphs = doc.getElementsByType(P)
    text_content = []
    for para in paragraphs:
        text = ""
        for node in para.childNodes:
            if node.nodeType == 3:  # TEXT_NODE
                text += node.data
        text_content.append(text)
    return "\n".join(text_content)
    # return "\n".join([p.firstChild.data if p.firstChild else "" for p in paragraphs])

